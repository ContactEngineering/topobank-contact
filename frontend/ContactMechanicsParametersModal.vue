<script setup>

import {BModal} from "bootstrap-vue-next";

const visible = defineModel('visible', {required: true});
const kwargs = defineModel('kwargs', {required: true});

const emit = defineEmits(['updateKwargs']);

const props = definedProps({
    limitsToFunctionKwargs: Object,
});

const _enableHardness = ref(kwargs.value === undefined ? false : kwargs.value.hardness !== null);
const _hardness = ref(kwargs.value === undefined ? null : kwargs.value.hardness);
const _maxNbIter = ref(kwargs.value === undefined ? 100 : kwargs.value.maxiter);
const _nbSteps = ref(kwargs.value === undefined ? 10 : kwargs.value.nsteps);
const _periodicity = ref(kwargs.value === undefined ? "nonperiodic" : kwargs.value.substrate_str);
const _periodicityOptions = ref([
    {value: "periodic", text: "Periodic (repeating array of the measurement)"},
    {value: "nonperiodic", text: "Free boundaries (flat punch with measurement)"}
]);
const _pressureSelection = ref(kwargs.value === undefined ? "automatic" :
    (kwargs.value.pressures === null ? "automatic" : "manual"));
const _pressures = ref(kwargs.value === undefined ? null : kwargs.value.pressures);
const _recalculateWarning = ref(false);

function validateParameters(event) {
    let pressures = null;
    _recalculateWarning.value = false;

    if (_pressureSelection.value == "automatic") {
        if (_nbSteps.value < props.limitsToFunctionKwargs.nsteps.min) {
            _nbSteps.value = props.limitsToFunctionKwargs.nsteps.min;
            _recalculateWarning.value = true;
        }
        if (_nbSteps > props.limitsToFunctionKwargs.nsteps.max) {
            _nbSteps.value = props.limitsToFunctionKwargs.nsteps.max;
            _recalculateWarning.value = true;
        }
    } else { // pressure_selection_mode == "manual"
        if (pressures === null) {
            pressures = [1];
        } else {
            pressures = String(pressures).split(/[,;]/).map(parseFloat).filter(p => {
                return (p != null) && (p > 0)
            });
        }
        if (pressures.length < 1) {
            pressures = [1];
        } else if (pressures.length > props.limitsToFunctionKwargs.pressures.maxlen) {
            pressures.length = props.limitsToFunctionKwargs.pressures.maxlen;
        }
        if (String(pressures) !== String(pressures)) {
            _recalculateWarning.value = true;
        }
        _pressures.value = pressures;
    }

    if (_maxNbIter.value < props.limitsToFunctionKwargs.maxiter.min) {
        _maxNbIter.value = props.limitsToFunctionKwargs.maxiter.min;
        _recalculateWarning.value = true;
    }
    if (_maxNbIter.value > props.limitsToFunctionKwargs.maxiter.max) {
        _maxNbIter.value = props.limitsToFunctionKwargs.maxiter.max;
        _recalculateWarning.value = true;
    }

    if (_recalculateWarning.value) {
        // Return here if some parameters were modified
        return;
    }

    _kwargs.value.substrate_str = _periodicity.value;
    _kwargs.value.hardness = _enableHardness.value ? parseFloat(_hardness.value) : null;
    _kwargs.value.nsteps = _pressureSelection.value == "automatic" ? parseInt(_nbSteps.value) : null;
    _kwargs.value.pressures = _pressureSelection.value == "manual" ? _pressures.value : null;
    _kwargs.value.maxiter = parseInt(_maxNbIter.value);

    emit('updateKwargs', kwargs);
}

</script>

<template>
    <BModal v-model="visible"
            size="xl"
            title="Contact mechanics"
            @ok="validateParameters">
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
    </BModal>
</template>