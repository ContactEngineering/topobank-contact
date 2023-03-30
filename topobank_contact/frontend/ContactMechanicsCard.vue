<script>

import {v4 as uuid4} from 'uuid';

import {BAlert, BFormSelect, BFormTags} from 'bootstrap-vue-next';

import BokehPlot from 'topobank/components/BokehPlot.vue';
import BibliographyModal from 'topobank/analysis/BibliographyModal.vue';
import DeepZoomImage from 'topobank/components/DeepZoomImage.vue';
import TasksButton from 'topobank/analysis/TasksButton.vue';

export default {
  name: 'contact-mechanics-card',
  components: {
    BAlert,
    BFormSelect,
    BFormTags,
    BibliographyModal,
    BokehPlot,
    DeepZoomImage,
    TasksButton
  },
  props: {
    apiUrl: String,
    csrfToken: String,
    detailUrl: String,
    enlarged: {
      type: Boolean,
      default: true
    },
    functionId: Number,
    functionName: String,
    subjects: Object,
    txtDownloadUrl: String,
    uid: {
      type: String,
      default() {
        return uuid4();
      }
    },
    xlsxDownloadUrl: String
  },
  data() {
    return {
      analyses: [],
      analysesAvailable: false,
      api: {},
      dois: [],
      dataSources: [],
      enableHardness: 0,
      hardness: undefined,
      initialCalcKwargs: null,
      limitsCalcKwargs: null,
      maxNbIter: 100,
      nsteps: 10,
      outputBackend: "svg",
      periodicity: "nonperiodic",
      selection: null,
      periodicityOptions: [
        {value: "periodic", text: "Periodic (repeating array of the measurement)"},
        {value: "nonperiodic", text: "Free boundaries (flat punch with measurement)"}
      ],
      pressureSelection: "automatic",
      pressures: []
    }
  },
  mounted() {
    this.updateCard();
  },
  methods: {
    updateCard() {
      /* Fetch JSON describing the card */
      fetch(this.apiUrl, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'X-CSRFToken': this.csrfToken
        },
        body: JSON.stringify({
          function_id: this.functionId,
          subjects: this.subjects
        })
      })
          .then(response => response.json())
          .then(data => {
            this.analyses = data.analyses;
            this.dataSources = data.plotConfiguration.dataSources;
            this.outputBackend = data.plotConfiguration.outputBackend;
            this.dois = data.dois;
            this.initialCalcKwargs = data.initialCalcKwargs;
            this.limitsCalcKwargs = data.limitsCalcKwargs;
            this.api = data.api;
            this.analysesAvailable = true;
          });
    },
    recalculate() {
      this.recalculateWarning = false;

      if (this.pressureSelection == "automatic") {
        if (this.nsteps < this.limitsCalcKwargs.nsteps.min) {
          this.nsteps = this.limitsCalcKwargs.nsteps.min;
          this.recalculateWarning = true;
        }
        if (this.nsteps > this.limitsCalcKwargs.nsteps.max) {
          this.nsteps = this.limitsCalcKwargs.nsteps.max;
          this.recalculateWarning = true;
        }
      } else { // pressure_selection_mode == "manual"
        const originalLength = this.pressures.length;
        this.pressures = this.pressures.map(parseFloat);
        this.pressures = this.pressures.filter((p) => {
          return (p != null) && (p > 0)
        });
        if (originalLength > this.pressures.length) {
          this.recalculateWarning = true;
        }
        if (this.pressures.length < 1) {
          this.pressures = [1];
          this.recalculateWarning = true;
        } else if (this.pressures.length > this.limitsCalcKwargs.pressures.maxlen) {
          this.pressures.length = this.limitsCalcKwargs.pressures.maxlen;
          this.recalculateWarning = true;
        }
      }

      if (this.maxNbIter < this.limitsCalcKwargs.maxiter.min) {
        this.maxNbIter = this.limitsCalcKwargs.maxiter.min;
        this.recalculateWarning = true;
      }
      if (this.maxNbIter > this.limitsCalcKwargs.maxiter.max) {
        this.maxNbIter = this.limitsCalcKwargs.maxiter.max;
        this.recalculateWarning = true;
      }

      if (this.recalculateWarning) {
        // Return here if some parameters were modified
        return;
      }

      const functionKwargs = {
        substrate_str: this.periodicity,
        hardness: parseFloat(this.hardness),
        nsteps: this.pressureSelection == "automatic" ? parseInt(this.nsteps) : null,
        pressures: this.pressureSelection == "manual" ? this.pressures : null,
        maxiter: parseInt(this.maxNbIter)
      };

      // FIXME! Switch to fetch API, but there is some weirdness with CSRF tokens going on
      /*
      $.ajax({
        type: "POST",
        url: this.api.submitUrl,
        timeout: 0,
        data: {
          function_id: this.functionId,
          subjects: this.subjects,
          function_kwargs: functionKwargs,
          csrfmiddlewaretoken: this.csrfToken
        },
        success: (data, textStatus, xhr) => {
          // debug_msg("Job submission successful. Status: "+xhr.status+" textStatus: "+textStatus);
          if (xhr.status == 200) {
            submit_analyses_card_ajax(
                "{% url 'analysis:card' %}",
                "card-wrapper", "contact-mechanics-card",
                "detail", {{ function.id }}, {{ subjects_ids_json|safe }}, 0, "{{ csrf_token }}");
            // debug_msg("Triggered card reload. Status: "+xhr.status+" textStatus: "+textStatus);
          } else {
            this.errorMessage = "Triggering calculation failed, status: " + xhr.status + " response:" + xhr.responseText;
          }
        },
        error: (xhr, textStatus, errorThrown) => {
          console.log("AJAX error when submitting jobs: errorThrown: " + errorThrown + " status: " + xhr.status + " responseText: " + xhr.responseText);
          this.errorMessage = "Please report this error: " + errorThrown + xhr.status + xhr.responseText;
        }
      });
       */
    },
    onSelected(obj, data) {
      const name = data.source.name;
      const path = data.source.data.dataPath[data.source.selected.indices[0]];
      const splitPath = path.split('/');
      this.selection = {
        analysisId: name.split('-')[1],
        dataPath: splitPath[splitPath.length - 1]  // We need to do some name mangling
      };
    }
  },
  computed: {
    contactMechanicsPlots: function () {
      return [{
        title: "Contact area vs load",
        xData: "data.mean_pressures",
        yData: "data.total_contact_areas",
        auxiliaryDataColumns: {
          dataPath: "data.data_paths"
        },
        alphaData: "data.converged.map((value) => value ? 1.0 : 0.3)",
        xAxisLabel: "Normalized pressure p/E*",
        yAxisLabel: "Fractional contact area A/A0",
        xAxisType: "log",
        yAxisType: "log"
      }, {
        title: "Load vs displacement",
        xData: "data.mean_gaps",
        yData: "data.mean_pressures",
        auxiliaryDataColumns: {
          dataPath: "data.data_paths"
        },
        alphaData: "data.converged.map((value) => value ? 1.0 : 0.3)",
        xAxisLabel: "Normalized mean gap u/h_rms",
        yAxisLabel: "Normalized pressure p/E*",
        xAxisType: "linear",
        yAxisType: "log"
      }]
    },
    contactMechanicsCategories: function () {
      return [{key: "subjectName", title: "Measurements"}];
    },
    distributionPlots: function () {
      return [{
        title: "Pressure",
        xData: "data.pressure",
        yData: "data.pressureProbabilityDensity",
        xAxisLabel: "Pressure p (E*)",
        yAxisLabel: "Probability density P(p) (E*⁻¹)"
      }, {
        title: "Gap",
        xData: "data.gap.map((value) => data.gapSIScaleFactor * value)",
        yData: "data.gapProbabilityDensity.map((value) => data.gapProbabilityDensitySIScaleFactor * value)",
        xAxisLabel: "Gap g (m)",
        yAxisLabel: "Probability density P(g) (m⁻¹)"
      }, {
        title: "Cluster area",
        xData: "data.clusterArea.map((value) => data.clusterAreaSIScaleFactor * value)",
        yData: "data.clusterAreaProbabilityDensity.map((value) => data.clusterAreaProbabilityDensitySIScaleFactor * value)",
        xAxisLabel: "Cluster area A (m²)",
        yAxisLabel: "Probability density P(A) (m⁻²)"
      }];
    },
    distributionDataSources: function () {
      return [{
        url: `/analysis/data/${this.selection.analysisId}/${this.selection.dataPath}/json/distributions.json`
      }];
    },
    analysisIds() {
      console.log(this.analyses);
      return this.analyses.map(a => a.id).join();
    }
  }
};
</script>

<template>
  <div class="card search-result-card">
    <div class="card-header">
      <div class="btn-group btn-group-sm float-right">
        <tasks-button :analyses="analyses"
                      :csrf-token="csrfToken">
        </tasks-button>
        <button @click="updateCard" class="btn btn-default float-right ml-1">
          <i class="fa fa-redo"></i>
        </button>
        <div v-if="!enlarged" class="btn-group btn-group-sm float-right">
          <a :href="detailUrl" class="btn btn-default float-right">
            <i class="fa fa-expand"></i>
          </a>
        </div>
      </div>
      <a class="text-dark" href="#" data-toggle="collapse" :data-target="`#sidebar-${uid}`">
        <h5><i class="fa fa-bars"></i> Contact mechanics</h5>
      </a>
    </div>
    <div class="card-body">
      <div v-if="!analysesAvailable" class="tab-content">
        <span class="spinner"></span>
        <div>Please wait...</div>
      </div>

      <div v-if="analysesAvailable" class="tab-content row">
        <div :class="{ 'col-sm-5': enlarged, 'col-sm-12': !enlarged }">
          <div class="tab-pane show active" id="plot-{{ card_id }}" role="tabpanel" aria-labelledby="card-tab">
            <bokeh-plot
                :plots="contactMechanicsPlots"
                :categories="contactMechanicsCategories"
                :data-sources="dataSources"
                :selectable="enlarged"
                @selected="onSelected"
                :options-widgets="['layout', 'legend', 'lineWidth', 'symbolSize']"
                :output-backend="outputBackend"
                ref="plot">
            </bokeh-plot>
          </div>
        </div>

        <!-- Middle with group of tabs -->
        <div v-if="enlarged" class="col-2 col-sm-2 col-md-2 col-lg-2">

          <div class="nav nav-pills nav-pills-custom flex-column" aria-orientation="vertical">
            <a class="nav-link mb-3 p-3 shadow active" data-toggle="pill" href="#contacting-points-tab" role="tab"
               aria-selected="true">
              Contact geometry
            </a>
            <a class="nav-link mb-3 p-3 shadow" data-toggle="pill" href="#pressure-tab" role="tab"
               aria-selected="false">
              Contact pressure
            </a>
            <a class="nav-link mb-3 p-3 shadow" data-toggle="pill" href="#displacement-tab" role="tab"
               aria-selected="false">
              Displacement
            </a>
            <a class="nav-link mb-3 p-3 shadow" data-toggle="pill" href="#gap-tab" role="tab" aria-selected="false">
              Gap
            </a>
            <a class="nav-link mb-3 p-3 shadow" data-toggle="pill" href="#distribution-function-tab" role="tab"
               aria-selected="false">
              Distribution functions
            </a>
            <hr>
            <a class="nav-link mb-3 p-3 shadow" data-toggle="pill" href="#actions-tab" role="tab" aria-selected="false">
              Parameters
            </a>
          </div>

        </div>

        <!-- Right with simulation details and actions -->
        <div v-if="enlarged" class="col-sm-5">
          <!-- Tab contents on right side -->
          <div class="tab-content">
            <div class="tab-pane fade active show" id="contacting-points-tab">
              <div v-if="selection === null" id="geometry" class="alert alert-info">For contact geometry, select a point
                in the graphs on the left!
              </div>
              <deep-zoom-image v-if="selection !== null"
                               :prefix-url="`/analysis/data/${selection.analysisId}/${selection.dataPath}/dzi/contacting-points/`"
                               ref="contactingPoints">
              </deep-zoom-image>
              <div v-if="selection !== null" class="pull-right">
                <a class="btn btn-default btn-block btn-lg mt-3" v-on:click="$refs.contactingPoints.download()">
                  Download PNG
                </a>
              </div>
            </div>
            <div class="tab-pane fade" id="pressure-tab">
              <div v-if="selection === null" id="pressure" class="alert alert-info">For contact pressure, select a point
                in the graphs on the left!
              </div>
              <deep-zoom-image v-if="selection !== null"
                               :prefix-url="`/analysis/data/${selection.analysisId}/${selection.dataPath}/dzi/pressure/`"
                               :colorbar="true"
                               ref="pressure">
              </deep-zoom-image>
              <div v-if="selection !== null" class="pull-right">
                <a class="btn btn-default btn-block btn-lg" v-on:click="$refs.pressure.download()">
                  Download PNG
                </a>
              </div>
            </div>
            <div class="tab-pane fade" id="displacement-tab">
              <div v-if="selection === null" id="displacement" class="alert alert-info">For displacement, select a point
                in the graphs on the left!
              </div>
              <deep-zoom-image v-if="selection !== null"
                               :prefix-url="`/analysis/data/${selection.analysisId}/${selection.dataPath}/dzi/displacement/`"
                               :colorbar="true"
                               ref="displacement">
              </deep-zoom-image>
              <div v-if="selection !== null" class="pull-right">
                <a class="btn btn-default btn-block btn-lg" v-on:click="$refs.displacement.download()">
                  Download PNG
                </a>
              </div>
            </div>
            <div class="tab-pane fade" id="gap-tab">
              <div v-if="selection === null" id="gap" class="alert alert-info">For gap, select a point in the graphs on
                the left!
              </div>
              <deep-zoom-image v-if="selection !== null"
                               :prefix-url="`/analysis/data/${selection.analysisId}/${selection.dataPath}/dzi/gap/`"
                               :colorbar="true"
                               ref="gap">
              </deep-zoom-image>
              <div v-if="selection !== null" class="pull-right">
                <a class="btn btn-default btn-block btn-lg" v-on:click="$refs.gap.download()">
                  Download PNG
                </a>
              </div>
            </div>
            <div class="tab-pane fade" id="distribution-function-tab">
              <div v-if="selection === null" id="distribution-function" class="alert alert-info">For pressure
                distribution, select a point in the graphs on the left!
              </div>
              <bokeh-plot
                  v-if="selection !== null"
                  :plots="distributionPlots"
                  :data-sources="distributionDataSources"
                  :output-backend="outputBackend">
              </bokeh-plot>
            </div>
            <div class="tab-pane fade" id="actions-tab">

              <!-- ELEMENTS FOR TRIGGERING A CALCULATION -->
              <div class="row p-3">
                <div class="col-12">

                  <form>
                    <div class="form-group row">

                      <!-- Substrate selection -->

                      <div class="input-group col-auto mb-3">
                        <div class="input-group-prepend">
                          <div class="input-group-text">
                            Type
                          </div>

                        </div>
                        <b-form-select v-model="periodicity" :options="periodicityOptions"></b-form-select>
                        <!--
                        <div class="input-group-append">
                          <div class="input-group-text">
                            <b-icon-info-circle-fill
                                title="Type of calculation"
                                v-b-popover.hover="'This option determines how the elastic interactions are calculated. This affects edge effects that may show up in the results at large contact area. Calculations can assume that the surface repeats periodically or that it is pushing down on a nonperiodic, infinitely expanded half-space. The latter option corresponds to mapping the surface topography on a flat punch. If not given, this value is automatically chosen as periodic for periodic topographies, else non-periodic.'">
                            </b-icon-info-circle-fill>
                          </div>
                        </div>
                        -->
                      </div>

                      <!-- Hardness input -->
                      <div class="input-group col-auto mb-3">

                        <div class="input-group-prepend">
                          <div class="input-group-text">
                            Hardness
                          </div>
                          <div class="input-group-text">
                            <input type="checkbox" v-model="enableHardness">
                          </div>
                        </div>
                        <input id="hardness-input" type="number" min="0" step="0.1" class="form-control"
                               v-model="hardness" :disabled="!enableHardness">
                        <div class="input-group-append ">
                          <div class="input-group-text">
                            E<sup>*</sup>
                          </div>
                          <!--
                          <div class="input-group-text">
                            <b-icon-info-circle-fill
                                v-b-popover.hover="'Setting a hardness enables plastic calculations. Local pressure cannot exceed hardness value.'"
                                title="Hardness">
                            </b-icon-info-circle-fill>
                          </div>
                          -->
                        </div>
                      </div>

                      <!-- Step selection -->
                      <div class="input-group col-auto mb-3">
                        <!-- Automatic -->
                        <div class="input-group-prepend">
                          <div class="input-group-text">
                            <input type="radio"
                                   name="pressure-selection"
                                   value="automatic"
                                   checked="checked"
                                   v-model="pressureSelection"
                                   aria-label="Radio button for automatic step selection">
                          </div>
                          <div class="input-group-text">
                            Number of steps
                          </div>
                        </div>
                        <input id='nsteps-input' type="number"
                               :min="limitsCalcKwargs.nsteps.min"
                               :max="limitsCalcKwargs.nsteps.max"
                               step="1" class="form-control"
                               v-model="nsteps"
                               :disabled="pressureSelection != 'automatic'">
                        <!--
                        <div class="input-group-append ">
                          <div class="input-group-text">
                            <b-icon-info-circle-fill
                                title="Automatic step selection"
                                v-b-popover.hover="'Number of pressure steps which are chosen automatically.'">
                            </b-icon-info-circle-fill>
                          </div>
                        </div>
                        -->
                      </div>
                      <div class="input-group col-auto mb-3">
                        <!-- Fixed list -->
                        <div class="input-group-prepend">
                          <div class="input-group-text">
                            <input type="radio"
                                   name="pressure-selection"
                                   value="manual"
                                   v-model="pressureSelection"
                                   aria-label="Radio button for list of values">
                          </div>
                          <div class="input-group-text">
                            Pressures
                          </div>
                        </div>
                        <b-form-tags class="form-control"
                                     placeholder=""
                                     separator=" ,;"
                                     v-model="pressures"
                                     :disabled="pressureSelection != 'manual'">
                        </b-form-tags>
                        <div class="input-group-append">
                          <div class="input-group-text">
                            E<sup>*</sup>
                          </div>
                          <!--
                          <div class="input-group-text">
                            <b-icon-info-circle-fill
                                title="Manual step selection"
                                v-b-popover.hover="'Enter positive pressure values for which you need results. You can also copy/paste a comma-separated list of values with a comma after every number. Use dot as decimal separator. The maximum number of values is {{ limitsCalcKwargs.pressures.maxlen }}.'">
                            </b-icon-info-circle-fill>
                          </div>
                          -->
                        </div>
                      </div>

                      <!-- Input of maximum number of iterations -->
                      <div class="input-group col-auto">
                        <!-- Automatic -->
                        <div class="input-group-prepend">
                          <div class="input-group-text">
                            Max. number of iterations
                          </div>
                        </div>
                        <input id='maxiter-input' type="number"
                               :min="limitsCalcKwargs.maxiter.min"
                               :max="limitsCalcKwargs.maxiter.max"
                               step="100" class="form-control"
                               v-model="maxNbIter">
                        <div class="input-group-append ">
                          <!--
                          <div class="input-group-text">
                            <b-icon-info-circle-fill
                                title="Maximum number of iterations"
                                v-b-popover.hover="`Maximum number of iterations (<=${limitsCalcKwargs.maxiter.max}).`">
                            </b-icon-info-circle-fill>
                          </div>
                          -->
                        </div>
                      </div>
                    </div>
                  </form>

                  <b-alert variant="warning"
                           :show="recalculateWarning"
                           dismissible
                           v-on:dismissed="recalculateWarning = false">
                    Some of the input parameters were invalid. We have updated those parameters for you. Please
                    double-check the parameters and click <b>Recalculate</b> when ready.
                  </b-alert>
                  <button title="Trigger calculation with given arguments"
                          class="btn btn-primary btn-block btn-lg"
                          v-on:click="recalculate">
                    Recalculate
                  </button>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
    <div :id="`sidebar-${uid}`" class="collapse position-absolute h-100">
      <!-- card-header sets the margins identical to the card so the title appears at the same position -->
      <nav class="card-header navbar navbar-toggleable-xl bg-light flex-column align-items-start h-100">
        <ul class="flex-column navbar-nav">
          <a class="text-dark" href="#" data-toggle="collapse" :data-target="`#sidebar-${uid}`">
            <h5><i class="fa fa-bars"></i> Contact mechanics</h5>
          </a>
          <li class="nav-item mb-1 mt-1">
            Download
            <div class="btn-group ml-1" role="group" aria-label="Download formats">
              <a :href="`/analysis/download/${analysisIds}/zip`" class="btn btn-default">
                ZIP
              </a>
              <a v-on:click="$refs.plot.download()" class="btn btn-default">
                SVG
              </a>
            </div>
          </li>
          <li class="nav-item mb-1 mt-1">
            <a href="#" data-toggle="modal" :data-target="`#bibliography-modal-${uid}`" class="btn btn-default  w-100">
              Bibliography
            </a>
          </li>
        </ul>
      </nav>
    </div>
  </div>
  <bibliography-modal
      :id="`bibliography-modal-${uid}`"
      :dois="dois">
  </bibliography-modal>
</template>
