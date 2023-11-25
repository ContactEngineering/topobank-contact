<script>

import {v4 as uuid4} from 'uuid';

export default {
    name: 'contact-mechanics-parameters-modal',
    emits: [
        'updateContactKwargs'
    ],
    props: {
        functionKwargs: Object,
        limitsToFunctionKwargs: Object,
        uid: {
            type: String,
            default() {
                return uuid4();
            }
        }
    },
    data() {
        return {
            _enableHardness: this.functionKwargs === undefined ? false : this.functionKwargs.hardness !== null,
            _hardness: this.functionKwargs === undefined ? null : this.functionKwargs.hardness,
            _maxNbIter: this.functionKwargs === undefined ? 100 : this.functionKwargs.maxiter,
            _nbSteps: this.functionKwargs === undefined ? 10 : this.functionKwargs.nsteps,
            _periodicity: this.unctionKwargs === undefined ? "nonperiodic" : this.functionKwargs.substrate_str,
            _periodicityOptions: [
                {value: "periodic", text: "Periodic (repeating array of the measurement)"},
                {value: "nonperiodic", text: "Free boundaries (flat punch with measurement)"}
            ],
            _pressureSelection:
                this.functionKwargs === undefined ? "automatic" :
                    (this.functionKwargs.pressures === null ? "automatic" : "manual"),
            _pressures: this.functionKwargs === undefined ? null : this.functionKwargs.pressures,
            _recalculateWarning: false
        }
    },
    methods: {
        runCalculation() {
            let _pressures = null;
            this._recalculateWarning = false;

            if (this._pressureSelection == "automatic") {
                if (this._nbSteps < this.limitsToFunctionKwargs.nsteps.min) {
                    this._nbSteps = this.limitsToFunctionKwargs.nsteps.min;
                    this._recalculateWarning = true;
                }
                if (this._nbSteps > this.limitsToFunctionKwargs.nsteps.max) {
                    this._nbSteps = this.limitsToFunctionKwargs.nsteps.max;
                    this._recalculateWarning = true;
                }
            } else { // pressure_selection_mode == "manual"
                if (this._pressures === null) {
                    _pressures = [1];
                } else {
                    _pressures = String(this._pressures).split(/[,;]/).map(parseFloat).filter(p => {
                        return (p != null) && (p > 0)
                    });
                }
                if (_pressures.length < 1) {
                    _pressures = [1];
                } else if (_pressures.length > this.limitsToFunctionKwargs.pressures.maxlen) {
                    _pressures.length = this.limitsToFunctionKwargs.pressures.maxlen;
                }
                if (String(this._pressures) !== String(_pressures)) {
                    this._recalculateWarning = true;
                }
                this._pressures = _pressures;
            }

            if (this._maxNbIter < this.limitsToFunctionKwargs.maxiter.min) {
                this._maxNbIter = this.limitsToFunctionKwargs.maxiter.min;
                this._recalculateWarning = true;
            }
            if (this._maxNbIter > this.limitsToFunctionKwargs.maxiter.max) {
                this._maxNbIter = this.limitsToFunctionKwargs.maxiter.max;
                this._recalculateWarning = true;
            }

            if (this._recalculateWarning) {
                // Return here if some parameters were modified
                return;
            }

            const functionKwargs = {
                substrate_str: this._periodicity,
                hardness: this._enableHardness ? parseFloat(this._hardness) : null,
                nsteps: this._pressureSelection == "automatic" ? parseInt(this._nbSteps) : null,
                pressures: this._pressureSelection == "manual" ? _pressures : null,
                maxiter: parseInt(this._maxNbIter)
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
                                            <div class="input-group-text">
                                                Type
                                            </div>
                                            <select v-model="_periodicity" class="form-control form-select">
                                                <option v-for="p in _periodicityOptions" :value="p.value">{{
                                                    p.text
                                                    }}
                                                </option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <div class="col-12">
                                            <small>
                                                This option determines how the elastic interactions are calculated. This
                                                affects edge effects
                                                that may show up in the results at large contact area. Calculations can
                                                assume that the surface
                                                repeats periodically or that it is pushing down on a nonperiodic,
                                                infinitely expanded
                                                half-space.
                                                The latter option corresponds to mapping the surface topography on a
                                                flat punch.
                                            </small>
                                        </div>
                                    </div>

                                    <!-- _hardness input -->
                                    <div class="row">
                                        <div class="input-group col-12">
                                            <div class="input-group-text">
                                                Hardness
                                            </div>
                                            <div class="input-group-text">
                                                <input type="checkbox" v-model="_enableHardness">
                                            </div>
                                            <input id="_hardness-input" type="number" min="0" step="0.1"
                                                   class="form-control"
                                                   v-model="_hardness" :disabled="!_enableHardness">
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
                                                Setting a hardness enables plastic calculations. Local pressure cannot
                                                exceed the hardness
                                                value.
                                            </small>
                                        </div>
                                    </div>

                                    <!-- Step selection -->
                                    <div class="row">
                                        <div class="input-group col-12">
                                            <!-- Automatic -->
                                            <div class="input-group-text">
                                                <input type="radio"
                                                       name="pressure-selection"
                                                       value="automatic"
                                                       checked="checked"
                                                       v-model="_pressureSelection"
                                                       aria-label="Radio button for automatic step selection">
                                            </div>
                                            <div class="input-group-text">
                                                Number of steps
                                            </div>
                                            <input type="number"
                                                   :min="limitsToFunctionKwargs.nsteps.min"
                                                   :max="limitsToFunctionKwargs.nsteps.max"
                                                   step="1" class="form-control"
                                                   v-model="_nbSteps"
                                                   :disabled="_pressureSelection != 'automatic'">
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <div class="col-12">
                                            <small>
                                                Select this option to run a fully automatic calculation. External
                                                pressures are selected such
                                                that contact area vs. pressure is approximately equally spaced on a
                                                log-log plot.
                                            </small>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="input-group col-12">
                                            <!-- Fixed list -->
                                            <div class="input-group-text">
                                                <input type="radio"
                                                       name="pressure-selection"
                                                       value="manual"
                                                       v-model="_pressureSelection"
                                                       aria-label="Radio button for list of values">
                                            </div>
                                            <div class="input-group-text">
                                                Pressures
                                            </div>
                                            <input v-model="_pressures"
                                                   class="form-control"
                                                   :disabled="_pressureSelection != 'manual'">
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
                                                Enter positive pressure values for which you need results. You can also
                                                copy/paste a
                                                comma-separated list of values with a comma after every number. Use dot
                                                as decimal separator.
                                                The maximum number of values is
                                                {{ limitsToFunctionKwargs.pressures.maxlen }}.
                                            </small>
                                        </div>
                                    </div>

                                    <!-- Input of maximum number of iterations -->
                                    <div class="row">
                                        <div class="input-group col-12">
                                            <!-- Automatic -->
                                            <div class="input-group-text">
                                                Max. number of iterations
                                            </div>
                                            <input id='maxiter-input' type="number"
                                                   :min="limitsToFunctionKwargs.maxiter.min"
                                                   :max="limitsToFunctionKwargs.maxiter.max"
                                                   step="100" class="form-control"
                                                   v-model="_maxNbIter">
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-12">
                                            <small>
                                                The calculation will stop if converged or after this maximum number of
                                                iterations. Data points
                                                that are not converged are shown translucent in the resulting plots. The
                                                maximum number of
                                                iterations is limited to {{ limitsToFunctionKwargs.maxiter.max }}.
                                            </small>
                                        </div>
                                    </div>
                                </div>
                            </form>

                            <div class="alert alert-warning" v-if="_recalculateWarning">
                                Some of the input parameters were invalid. We have updated those parameters for you.
                                Please double-check
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