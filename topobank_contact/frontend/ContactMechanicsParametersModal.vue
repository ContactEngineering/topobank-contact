<script>

import {v4 as uuid4} from 'uuid';

import {BAlert, BFormSelect, BFormTags, BPopover} from 'bootstrap-vue-next';

export default {
  name: 'contact-mechanics-parameters-modal',
  components: {
    BAlert,
    BFormSelect,
    BFormTags,
    BPopover
  },
  props: {
    limitsCalcKwargs: Object,
    uid: {
      type: String,
      default() {
        return uuid4();
      }
    }
  },
  data() {
    return {
      enableHardness: 0,
      hardness: undefined,
      maxNbIter: 100,
      nsteps: 10,
      periodicity: "nonperiodic",
      periodicityOptions: [
        {value: "periodic", text: "Periodic (repeating array of the measurement)"},
        {value: "nonperiodic", text: "Free boundaries (flat punch with measurement)"}
      ],
      pressureSelection: "automatic",
      pressures: [],
      recalculateWarning: false
    }
  },
  methods: {
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
  }
};
</script>

<template>
  <div class="modal fade"
       tabindex="-1"
       role="dialog"
       :aria-labelledby="`contact-mechanics-parameters-modal-label-${uid}`"
       aria-hidden="true">
    <div class="modal-dialog modal-xl" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title"
              :id="`contact-mechanics-parameters-modal-label-${uid}`">
            Bibliography
          </h5>
          <button class="close" type="button" data-dismiss="modal" aria-label="Close">
            <span aria-hidden="true">×</span>
          </button>
        </div>

        <div class="modal-body">
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
                    <b-form-select v-model="periodicity"
                                   :options="periodicityOptions"
                                   class="form-control">
                    </b-form-select>
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
                    <!--
                    <div class="input-group-append ">
                      <div class="input-group-text">
                        <b-icon-info-circle-fill
                            title="Maximum number of iterations"
                            v-b-popover.hover="`Maximum number of iterations (<=${limitsCalcKwargs.maxiter.max}).`">
                        </b-icon-info-circle-fill>
                      </div>
                    </div>
                    -->
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
</template>