<script>

import {v4 as uuid4} from 'uuid';

import BokehPlot from 'topobank/components/BokehPlot.vue';
import BibliographyModal from 'topobank/analysis/BibliographyModal.vue';
import DeepZoomImage from 'topobank/components/DeepZoomImage.vue';
import TasksButton from 'topobank/analysis/TasksButton.vue';
import ContactMechanicsParametersModal from "topobank_contact/ContactMechanicsParametersModal.vue";

export default {
  name: 'contact-mechanics-card',
  components: {
    ContactMechanicsParametersModal,
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
      _lastFunctionKwargs: null,
      limitsCalcKwargs: null,
      maxNbIter: 100,
      nsteps: 10,
      outputBackend: "svg",
      periodicity: "nonperiodic",
      selection: null,
      sidebarVisible: false,
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
      this.updateCardWithFunctionKwargs(this._lastFunctionKwargs);
    },
    updateCardWithFunctionKwargs(functionKwargs = null) {
      this.analysesAvailable = false;
      this._lastFunctionKwargs = functionKwargs;

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
          subjects: this.subjects,
          function_kwargs: functionKwargs

        })
      })
          .then(response => response.json())
          .then(data => {
            this.analyses = data.analyses;
            this.dois = data.dois;
            this.initialCalcKwargs = data.initialCalcKwargs;
            this.limitsCalcKwargs = data.limitsCalcKwargs;
            this.api = data.api;

            if (data.plotConfiguration !== undefined) {
              this.analysesAvailable = true;
              this.dataSources = data.plotConfiguration.dataSources;
              this.outputBackend = data.plotConfiguration.outputBackend;
            }
          });
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
      <a class="text-dark" href="#" @click="sidebarVisible=true">
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
          </div>
        </div>
      </div>
    </div>
    <div v-if="sidebarVisible" class="position-absolute h-100">
      <nav class="card-header navbar navbar-toggleable-xl bg-light flex-column align-items-start h-100">
        <ul class="flex-column navbar-nav">
          <a class="text-dark"
             href="#"
             @click="sidebarVisible=false">
            <h5><i class="fa fa-bars"></i> Contact mechanics</h5>
          </a>
          <li class="nav-item mb-1 mt-1">
            Download
            <div class="btn-group ml-1"
                 role="group"
                 aria-label="Download formats">
              <a class="btn btn-default"
                 :href="`/analysis/download/${analysisIds}/zip`"
                 @click="sidebarVisible=false">
                ZIP
              </a>
              <a class="btn btn-default"
                 @click="sidebarVisible=false; $refs.plot.download()">
                SVG
              </a>
            </div>
          </li>
          <li class="nav-item mb-1 mt-1">
            <a class="btn btn-default w-100"
               href="#"
               data-toggle="modal"
               :data-target="`#bibliography-modal-${uid}`"
               @click="sidebarVisible=false">
              Bibliography
            </a>
          </li>
          <hr>
          <li class="nav-item mb-1 mt-1">
            <a class="btn btn-primary w-100"
               href="#"
               data-toggle="modal"
               :data-target="`#contact-mechanics-parameters-modal-${uid}`"
               @click="sidebarVisible=false">
              Parameters
            </a>
          </li>
        </ul>
      </nav>
    </div>
    <!-- card-header sets the margins identical to the card so the title appears at the same position -->
  </div>
  <bibliography-modal
      :id="`bibliography-modal-${uid}`"
      :dois="dois">
  </bibliography-modal>
  <contact-mechanics-parameters-modal
      v-if="limitsCalcKwargs !== null && initialCalcKwargs !== null"
      :id="`contact-mechanics-parameters-modal-${uid}`"
      :limits-calc-kwargs="limitsCalcKwargs"
      :initial-calc-kwargs="initialCalcKwargs"
      @update-contact-kwargs="updateCardWithFunctionKwargs"
      :csrf-token="csrfToken">
  </contact-mechanics-parameters-modal>
</template>
