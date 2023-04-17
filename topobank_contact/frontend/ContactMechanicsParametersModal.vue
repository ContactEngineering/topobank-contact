<script>

import {v4 as uuid4} from 'uuid';

//import {BAlert, BFormSelect, BFormTags, BPopover} from 'bootstrap-vue';

export default {
  name: 'contact-mechanics-parameters-modal',
  /*
  components: {
    BAlert,
    BFormSelect,
    BFormTags,
    BPopover
  },
  */
  props: {
    csrfToken: String,
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
      hardness: null,
      maxNbIter: 100,
      nsteps: 10,
      periodicity: "nonperiodic",
      periodicityOptions: [
        {value: "periodic", text: "Periodic (repeating array of the measurement)"},
        {value: "nonperiodic", text: "Free boundaries (flat punch with measurement)"}
      ],
      pressureSelection: "automatic",
      pressures: null,
      recalculateWarning: false
    }
  },
  methods: {
    runCalculation() {
      let pressures = null;
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
        if (this.pressures === null) {
          pressures = [1];
        } else {
          pressures = this.pressures.split(/[,;]/).map(parseFloat).filter(p => {
            return (p != null) && (p > 0)
          });
        }
        if (pressures.length < 1) {
          pressures = [1];
        } else if (pressures.length > this.limitsCalcKwargs.pressures.maxlen) {
          pressures.length = this.limitsCalcKwargs.pressures.maxlen;
        }
        if (this.pressures > pressures.join()) {
          this.recalculateWarning = true;
        }
        this.pressures = pressures.join();
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
        hardness: this.enableHardness ? parseFloat(this.hardness) : null,
        nsteps: this.pressureSelection == "automatic" ? parseInt(this.nsteps) : null,
        pressures: this.pressureSelection == "manual" ? pressures : null,
        maxiter: parseInt(this.maxNbIter)
      };

      this.$emit('updateContactKwargs', functionKwargs);
      this.$refs.close.click();
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
            Contact mechanics
          </h5>
          <button ref="close" class="close" type="button" data-dismiss="modal" aria-label="Close">
            <span aria-hidden="true">×</span>
          </button>
        </div>

        <div class="modal-body">
          <!-- ELEMENTS FOR TRIGGERING A CALCULATION -->
          <div class="row p-3">
            <div class="col-12">

              <form>
                <div class="form-group">

                  <!-- Substrate selection -->

                  <div class="row">
                    <div class="input-group col-12">
                      <div class="input-group-prepend">
                        <div class="input-group-text">
                          Type
                        </div>
                      </div>
                      <select v-model="periodicity" class="form-control form-select">
                        <option v-for="p in periodicityOptions" :value="p.value">{{ p.text }}</option>
                      </select>
                    </div>
                  </div>
                  <div class="row mb-3">
                    <div class="col-12">
                      <small>
                        This option determines how the elastic interactions are calculated. This affects edge effects
                        that may show up in the results at large contact area. Calculations can assume that the surface
                        repeats periodically or that it is pushing down on a nonperiodic, infinitely expanded
                        half-space.
                        The latter option corresponds to mapping the surface topography on a flat punch.
                      </small>
                    </div>
                  </div>

                  <!-- Hardness input -->
                  <div class="row">
                    <div class="input-group col-12">
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
                      </div>
                    </div>
                  </div>
                  <div class="row mb-3">
                    <div class="col-12">
                      <small>
                        Setting a hardness enables plastic calculations. Local pressure cannot exceed the hardness
                        value.
                      </small>
                    </div>
                  </div>

                  <!-- Step selection -->
                  <div class="row">
                    <div class="input-group col-12">
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
                    </div>
                  </div>
                  <div class="row mb-3">
                    <div class="col-12">
                      <small>
                        Select this option to run a fully automatic calculation. External pressures are selected such
                        that contact area vs. pressure is approximately equally spaced on a log-log plot.
                      </small>
                    </div>
                  </div>
                  <div class="row">
                    <div class="input-group col-12">
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
                      <input v-model="pressures"
                             class="form-control"
                             :disabled="pressureSelection != 'manual'">
                      <div class="input-group-append">
                        <div class="input-group-text">
                          E<sup>*</sup>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="row mb-3">
                    <div class="col-12">
                      <small>
                        Enter positive pressure values for which you need results. You can also copy/paste a
                        comma-separated list of values with a comma after every number. Use dot as decimal separator.
                        The maximum number of values is {{ limitsCalcKwargs.pressures.maxlen }}.
                      </small>
                    </div>
                  </div>

                  <!-- Input of maximum number of iterations -->
                  <div class="row">
                    <div class="input-group col-12">
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
                    </div>
                  </div>
                  <div class="row">
                    <div class="col-12">
                      <small>
                        The calculation will stop if converged or after this maximum number of iterations. Data points
                        that are not converged are shown translucent in the resulting plots. The maximum number of
                        iterations is limited to {{ limitsCalcKwargs.maxiter.max }}.
                      </small>
                    </div>
                  </div>
                </div>
              </form>

              <div class="alert alert-warning" v-if="recalculateWarning">
                Some of the input parameters were invalid. We have updated those parameters for you. Please double-check
                the parameters and click <b>Run calculation</b> when ready.
              </div>
              <button title="Trigger calculation with given arguments"
                      class="btn btn-primary btn-block btn-lg"
                      v-on:click="runCalculation">
                Run calculation
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>