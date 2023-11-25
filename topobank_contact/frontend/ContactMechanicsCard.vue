<script setup>

import {v4 as uuid4} from 'uuid';
import axios from "axios";
import {computed, onMounted, ref} from "vue";

import {BTab, BTabs} from "bootstrap-vue-next";

import BokehPlot from 'topobank/components/BokehPlot.vue';
import BibliographyModal from 'topobank/analysis/BibliographyModal.vue';
import CardExpandButton from 'topobank/analysis/CardExpandButton.vue';
import ContactMechanicsParametersModal from 'topobank_contact/ContactMechanicsParametersModal.vue';
import DeepZoomImage from 'topobank/components/DeepZoomImage.vue';
import TasksButton from 'topobank/analysis/TasksButton.vue';

const props = defineProps({
    apiUrl: {
        type: String,
        default: '/plugins/topobank_contact/card/contact-mechanics'
    },
    detailUrl: {
        type: String,
        default: '/analysis/html/detail/'
    },
    enlarged: {
        type: Boolean,
        default: true
    },
    functionId: Number,
    functionName: String,
    subjects: String,
    txtDownloadUrl: String,
    uid: {
        type: String,
        default() {
            return uuid4();
        }
    },
    xlsxDownloadUrl: String
});

const _analyses = ref(null);
const _api = ref({});
const _cardStatus = ref('mounted');  // 'mounted', 'waiting-for-first-result', 'analyses-partially-available', 'analyses-finished'
const _dois = ref([]);
const _dataSources = ref([]);
const _functionKwargs = ref(null);
const _limitsToFunctionKwargs = ref(null);
const _nbFailed = ref(0);
const _nbRunningOrPending = ref(0);
const _nbSuccess = ref(0);
const _outputBackend = ref("svg");
const _selection = ref(null);
const _sidebarVisible = ref(false);

onMounted(() => {
    updateCard();
});

function updateCard() {
    updateCardWithFunctionKwargs(_functionKwargs.value);
}

function updateCardWithFunctionKwargs(functionKwargs = null) {
    _functionKwargs.value = functionKwargs;
    _analyses.value = null;  // Need to reset analyses, otherwise modal does not update properly

    /* Fetch JSON describing the card */
    let functionKwargsBase64 = btoa(JSON.stringify(functionKwargs));
    axios.get(`${props.apiUrl}/${props.functionId}?subjects=${props.subjects}&function_kwargs=${functionKwargsBase64}`)
        .then(response => {
            _analyses.value = response.data.analyses;
            _dois.value = response.data.dois;
            if (_functionKwargs.value === null) {
                _functionKwargs.value = response.data.uniqueKwargs;
            } else {
                _functionKwargs.value = {
                    ..._functionKwargs.value,
                    ...response.data.uniqueKwargs  // override since the server may report changes
                };
            }
            _limitsToFunctionKwargs.value = response.data.limitsToFunctionKwargs;
            _api.value = response.data.api;

            if (response.data.plotConfiguration !== undefined) {
                if (_analyses.value.map(a => a.task_state == 'pe' || a.task_state == 'st').some(v => v)) {
                    _cardStatus.value = 'analyses-partially-available';
                } else {
                    _cardStatus.value = 'analyses-finished';
                }
                _dataSources.value = response.data.plotConfiguration.dataSources;
                _outputBackend.value = response.data.plotConfiguration.outputBackend;
            } else {
                _cardStatus.value = 'waiting-for-first-result';
            }
        });
}

function onSelected(obj, data) {
    const name = data.source.name;
    const path = data.source.data.dataPath[data.source.selected.indices[0]];
    const splitPath = path.split('/');
    _selection.value = {
        analysisId: name.split('-')[1],
        dataPath: splitPath[splitPath.length - 1]  // We need to do some name mangling
    };
}

function taskStateChanged(nbRunningOrPending, nbSuccess, nbFailed) {
    if (nbRunningOrPending === 0 && _nbRunningOrPending.value > 0) {
        // All tasks finished, reload card
        updateCard();
    }
    _nbRunningOrPending.value = nbRunningOrPending;
    _nbSuccess.value = nbSuccess;
    _nbFailed.value = nbFailed;
}

const contactMechanicsPlots = computed(() => {
    return [{
        title: "Contact area vs load",
        xData: "data.mean_pressures",
        yData: "data.total_contact_areas",
        auxiliaryDataColumns: {
            dataPath: "data.data_paths"
        },
        alphaData: "data.converged.map((value) => value ? 1.0 : 0.3)",
        xAxisLabel: "$$p/E^*$$",
        yAxisLabel: "$$A/A_0$$",
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
        xAxisLabel: "$$u/h_\\text{rms}$$",
        yAxisLabel: "$$p/E^*$$",
        xAxisType: "linear",
        yAxisType: "log"
    }]
});

const contactMechanicsCategories = computed(() => {
    return [{key: "subjectName", title: "Measurements"}];
});

const distributionPlots = computed(() => {
    return [{
        title: "Pressure",
        xData: "data.pressure",
        yData: "data.pressureProbabilityDensity",
        xAxisLabel: "$$p\\text{ (}E^*\\text{)}$$",
        yAxisLabel: "$$P(p)\\text{ (}E^{*-1}\\text{)}$$"
    }, {
        title: "Gap",
        xData: "data.gap.map((value) => data.gapSIScaleFactor * value)",
        yData: "data.gapProbabilityDensity.map((value) => data.gapProbabilityDensitySIScaleFactor * value)",
        xAxisLabel: "$$g\\text{ (m)}$$",
        yAxisLabel: "$$P(g)\\text{ (m}^{-1}\\text{)}$$"
    }, {
        title: "Cluster area",
        xData: "data.clusterArea.map((value) => data.clusterAreaSIScaleFactor * value)",
        yData: "data.clusterAreaProbabilityDensity.map((value) => data.clusterAreaProbabilityDensitySIScaleFactor * value)",
        xAxisLabel: "$$A\\text{ (m}^2\\text{)}$$",
        yAxisLabel: "$$P(A)\\text{ (m}^{-2}\\text{)}$$"
    }];
});

const distributionDataSources = computed(() => {
    return [{
        url: `/analysis/data/${_selection.value.analysisId}/${_selection.value.dataPath}/json/distributions.json`
    }];
});

const analysisIds = computed(() => {
    return _analyses.value.map(a => a.id).join();
});

</script>

<template>
    <div class="card search-result-card">
        <div class="card-header">
            <div class="btn-group btn-group-sm float-end">
                <tasks-button v-if="_analyses !== null && _analyses.length > 0"
                              :analyses="_analyses"
                              @task-state-changed="taskStateChanged">
                </tasks-button>
                <button v-if="_analyses !== null && _analyses.length > 0"
                        @click="updateCard"
                        class="btn btn-default float-end ms-1">
                    <i class="fa fa-redo"></i>
                </button>
                <card-expand-button v-if="!enlarged"
                                    :detail-url="detailUrl"
                                    :function-id="functionId"
                                    :subjects="subjects"
                                    class="btn-group btn-group-sm float-end">
                </card-expand-button>
            </div>
            <h5 v-if="_analyses === null"
                class="text-dark">
                Contact mechanics
            </h5>
            <a v-if="_analyses !== null && _analyses.length > 0"
               class="text-dark text-decoration-none"
               href="#"
               @click="_sidebarVisible=true">
                <h5><i class="fa fa-bars"></i> Contact mechanics</h5>
            </a>
        </div>
        <div class="card-body">
            <div v-if="_cardStatus === 'mounted'" class="tab-content">
                <span class="spinner"></span>
                <div>Please wait...</div>
            </div>
            <div v-if="_cardStatus === 'waiting-for-first-result'" class="tab-content">
                <span class="spinner"></span>
                <div>
                    Analyses are not yet available, but tasks are scheduled or running.
                    Please wait...
                </div>
            </div>

            <div v-if="_cardStatus !== 'waiting-for-first-result' && _dataSources.length > 0" class="tab-content row">
                <div :class="{ 'col-sm-5': enlarged, 'col-sm-12': !enlarged }">
                    <div class="tab-pane show active" id="plot-{{ card_id }}" role="tabpanel"
                         aria-labelledby="card-tab">
                        <bokeh-plot
                            :plots="contactMechanicsPlots"
                            :categories="contactMechanicsCategories"
                            :data-sources="_dataSources"
                            :selectable="enlarged"
                            @selected="onSelected"
                            :options-widgets="['layout', 'legend', 'lineWidth', 'symbolSize']"
                            :output-backend="_outputBackend"
                            ref="plot">
                        </bokeh-plot>
                    </div>
                </div>

                <!-- Right with simulation details and actions -->
                <div v-if="enlarged" class="col-sm-7">
                    <div v-if="_selection == null" id="geometry" class="alert alert-info">Select a point
                        in the graphs on the left for more details.
                    </div>
                    <b-tabs v-if="_selection != null"
                            class="nav-pills-custom"
                            content-class="w-100"
                            fill
                            pills
                            vertical>
                        <b-tab title="Contact geometry">
                            <deep-zoom-image v-if="_selection != null"
                                             :prefix-url="`/analysis/data/${_selection.analysisId}/${_selection.dataPath}/dzi/contacting-points/`"
                                             ref="contactingPoints">
                            </deep-zoom-image>
                            <div v-if="_selection != null" class="pull-right">
                                <a class="btn btn-default btn-block btn-lg mt-3"
                                   v-on:click="$refs.contactingPoints.download()">
                                    Download PNG
                                </a>
                            </div>
                        </b-tab>
                        <b-tab title="Contact pressure">
                            <deep-zoom-image v-if="_selection != null"
                                             :prefix-url="`/analysis/data/${_selection.analysisId}/${_selection.dataPath}/dzi/pressure/`"
                                             :colorbar="true"
                                             ref="pressure">
                            </deep-zoom-image>
                            <div v-if="_selection != null" class="pull-right">
                                <a class="btn btn-default btn-block btn-lg" v-on:click="$refs.pressure.download()">
                                    Download PNG
                                </a>
                            </div>
                        </b-tab>
                        <b-tab title="Displacement">
                            <deep-zoom-image v-if="_selection != null"
                                             :prefix-url="`/analysis/data/${_selection.analysisId}/${_selection.dataPath}/dzi/displacement/`"
                                             :colorbar="true"
                                             ref="displacement">
                            </deep-zoom-image>
                            <div v-if="_selection != null" class="pull-right">
                                <a class="btn btn-default btn-block btn-lg" v-on:click="$refs.displacement.download()">
                                    Download PNG
                                </a>
                            </div>
                        </b-tab>
                        <b-tab title="Gap">
                            <deep-zoom-image v-if="_selection != null"
                                             :prefix-url="`/analysis/data/${_selection.analysisId}/${_selection.dataPath}/dzi/gap/`"
                                             :colorbar="true"
                                             ref="gap">
                            </deep-zoom-image>
                            <div v-if="_selection != null" class="pull-right">
                                <a class="btn btn-default btn-block btn-lg" v-on:click="$refs.gap.download()">
                                    Download PNG
                                </a>
                            </div>
                        </b-tab>
                        <b-tab title="Distribution functions">
                            <bokeh-plot
                                v-if="_selection != null"
                                :plots="distributionPlots"
                                :data-sources="distributionDataSources"
                                :options-widgets='["layout", "lineWidth", "symbolSize"]'
                                :output-backend="_outputBackend">
                            </bokeh-plot>
                        </b-tab>
                    </b-tabs>
                </div>
            </div>
        </div>
        <div v-if="_sidebarVisible"
             class="position-absolute h-100">
            <nav class="card-header navbar navbar-toggleable-xl bg-light flex-column align-items-start h-100">
                <ul class="flex-column navbar-nav">
                    <a class="text-dark text-decoration-none"
                       href="#"
                       @click="_sidebarVisible=false">
                        <h5><i class="fa fa-bars"></i> Contact mechanics</h5>
                    </a>
                    <li class="nav-item mb-1 mt-1">
                        Download
                        <div class="btn-group ms-1"
                             role="group"
                             aria-label="Download formats">
                            <a class="btn btn-default"
                               :href="`/analysis/download/${analysisIds}/zip`"
                               @click="_sidebarVisible=false">
                                ZIP
                            </a>
                            <a class="btn btn-default"
                               @click="_sidebarVisible=false; $refs.plot.download()">
                                SVG
                            </a>
                        </div>
                    </li>
                    <li class="nav-item mb-1 mt-1">
                        <a class="btn btn-default w-100"
                           href="#"
                           data-toggle="modal"
                           :data-target="`#bibliography-modal-${uid}`"
                           @click="_sidebarVisible=false">
                            Bibliography
                        </a>
                    </li>
                    <hr>
                    <li class="nav-item mb-1 mt-1">
                        <a class="btn btn-primary w-100"
                           href="#"
                           data-toggle="modal"
                           :data-target="`#contact-mechanics-parameters-modal-${uid}`"
                           @click="_sidebarVisible=false">
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
        :dois="_dois">
    </bibliography-modal>
    <contact-mechanics-parameters-modal
        v-if="_limitsToFunctionKwargs !== null && _functionKwargs !== null"
        :id="`contact-mechanics-parameters-modal-${uid}`"
        :limits-to-function-kwargs="_limitsToFunctionKwargs"
        :function-kwargs="_functionKwargs"
        @update-contact-kwargs="updateCardWithFunctionKwargs">
    </contact-mechanics-parameters-modal>
</template>
