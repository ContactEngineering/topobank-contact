<script setup>

import axios from "axios";
import {computed, onMounted, ref} from "vue";

import {BDropdownDivider, BDropdownItem, BTab, BTabs} from "bootstrap-vue-next";

import BokehPlot from 'topobank/components/BokehPlot.vue';
import ContactMechanicsParametersModal from 'topobank_contact/ContactMechanicsParametersModal.vue';
import DeepZoomImage from 'topobank/components/DeepZoomImage.vue';
import AnalysisCard from "topobank/analysis/AnalysisCard.vue";

const props = defineProps({
    apiUrl: {
        type: String,
        default: '/plugins/contact/card/contact-mechanics'
    },
    detailUrl: {
        type: String,
        default: '/ui/html/analysis-detail/'
    },
    enlarged: {
        type: Boolean,
        default: true
    },
    functionId: Number,
    functionName: String,
    subjects: String,
    txtDownloadUrl: String,
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

// GUI logic
const _nbPendingAjaxRequests = ref(0);
const _parametersVisible = ref(false);

onMounted(() => {
    updateCard();
});

function updateCard() {
    /* Fetch JSON describing the card */
    let functionKwargsBase64 = btoa(JSON.stringify(_functionKwargs.value));
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
        xData: "mean_pressures",
        yData: "total_contact_areas",
        auxiliaryDataColumns: {
            dataPath: "data_paths"
        },
        alphaData: "converged",
        alphaDataMap: (value) => value ? 1.0 : 0.3,
        xAxisLabel: "$$p/E^*$$",
        yAxisLabel: "$$A/A_0$$",
        xAxisType: "log",
        yAxisType: "log"
    }, {
        title: "Load vs displacement",
        xData: "mean_gaps",
        yData: "mean_pressures",
        auxiliaryDataColumns: {
            dataPath: "data_paths"
        },
        alphaData: "converged",
        alphaDataMap: (value) => value ? 1.0 : 0.3,
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
        xData: "pressure",
        yData: "pressureProbabilityDensity",
        xAxisLabel: "$$p\\text{ (}E^*\\text{)}$$",
        yAxisLabel: "$$P(p)\\text{ (}E^{*-1}\\text{)}$$"
    }, {
        title: "Gap",
        xData: "gap",
        xDataMap: (value) => gapSIScaleFactor * value,
        yData: "gapProbabilityDensity",
        yDataMap: (value) => gapProbabilityDensitySIScaleFactor * value,
        xAxisLabel: "$$g\\text{ (m)}$$",
        yAxisLabel: "$$P(g)\\text{ (m}^{-1}\\text{)}$$"
    }, {
        title: "Cluster area",
        xData: "clusterArea",
        xDataMap: (value) => clusterAreaSIScaleFactor * value,
        yData: "clusterAreaProbabilityDensity",
        yDataMap: (value) => clusterAreaProbabilityDensitySIScaleFactor * value,
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
    if (_analyses.value == null) {
        return [];
    }
    return _analyses.value.map(a => a.id).join();
});

</script>

<template>
    <AnalysisCard v-model:analyses="_analyses"
                  :detailUrl="detailUrl"
                  :dois="_dois"
                  :enlarged="enlarged"
                  :functionId="functionId"
                  :subjects="subjects"
                  :showLoadingSpinner="_nbPendingAjaxRequests > 0"
                  title="Contact mechanics"
                  @allTasksFinished="updateCard"
                  @someTasksFinished="updateCard"
                  @refreshButtonClicked="updateCard">
        <template #dropdowns>
            <BDropdownDivider></BDropdownDivider>
            <BDropdownItem @click="_parametersVisible = true">
                Parameters...
            </BDropdownItem>
            <BDropdownDivider></BDropdownDivider>
            <BDropdownItem :href="`/analysis/download/${analysisIds}/zip`">
                Download ZIP
            </BDropdownItem>
            <BDropdownItem @click="$refs.plot.download()">
                Download SVG
            </BDropdownItem>
        </template>
        <div class="row">
            <div :class="{ 'col-6': enlarged, 'col-12': !enlarged }">
                <BokehPlot
                    :plots="contactMechanicsPlots"
                    :categories="contactMechanicsCategories"
                    :data-sources="_dataSources"
                    :selectable="enlarged"
                    @selected="onSelected"
                    :options-widgets="['layout', 'legend', 'lineWidth', 'symbolSize']"
                    :output-backend="_outputBackend"
                    ref="plot">
                </BokehPlot>
            </div>

            <!-- Right with simulation details and actions -->
            <div v-if="enlarged" class="col-6">
                <div v-if="_selection == null" id="geometry" class="alert alert-info">Select a point
                    in the graphs on the left for more details.
                </div>
                <BTabs v-if="_selection != null">
                    <BTab title="Contact geometry">
                        <DeepZoomImage v-if="_selection != null"
                                       :prefix-url="`/analysis/data/${_selection.analysisId}/${_selection.dataPath}/dzi/contacting-points/`"
                                       ref="contactingPoints">
                        </DeepZoomImage>
                        <div v-if="_selection != null" class="pull-right">
                            <a class="btn btn-default btn-block btn-lg mt-3"
                               v-on:click="$refs.contactingPoints.download()">
                                Download PNG
                            </a>
                        </div>
                    </BTab>
                    <BTab title="Contact pressure">
                        <DeepZoomImage v-if="_selection != null"
                                       :prefix-url="`/analysis/data/${_selection.analysisId}/${_selection.dataPath}/dzi/pressure/`"
                                       :colorbar="true"
                                       ref="pressure">
                        </DeepZoomImage>
                        <div v-if="_selection != null" class="pull-right">
                            <a class="btn btn-default btn-block btn-lg" v-on:click="$refs.pressure.download()">
                                Download PNG
                            </a>
                        </div>
                    </BTab>
                    <BTab title="Displacement">
                        <DeepZoomImage v-if="_selection != null"
                                       :prefix-url="`/analysis/data/${_selection.analysisId}/${_selection.dataPath}/dzi/displacement/`"
                                       :colorbar="true"
                                       ref="displacement">
                        </DeepZoomImage>
                        <div v-if="_selection != null" class="pull-right">
                            <a class="btn btn-default btn-block btn-lg" v-on:click="$refs.displacement.download()">
                                Download PNG
                            </a>
                        </div>
                    </BTab>
                    <BTab title="Gap">
                        <DeepZoomImage v-if="_selection != null"
                                       :prefix-url="`/analysis/data/${_selection.analysisId}/${_selection.dataPath}/dzi/gap/`"
                                       :colorbar="true"
                                       ref="gap">
                        </DeepZoomImage>
                        <div v-if="_selection != null" class="pull-right">
                            <a class="btn btn-default btn-block btn-lg" v-on:click="$refs.gap.download()">
                                Download PNG
                            </a>
                        </div>
                    </BTab>
                    <BTab title="Distribution functions">
                        <BokehPlot
                            v-if="_selection != null"
                            :plots="distributionPlots"
                            :data-sources="distributionDataSources"
                            :options-widgets='["layout", "lineWidth", "symbolSize"]'
                            :output-backend="_outputBackend">
                        </BokehPlot>
                    </BTab>
                </BTabs>
            </div>
        </div>
    </AnalysisCard>
    <ContactMechanicsParametersModal v-if="_limitsToFunctionKwargs !== null && _functionKwargs !== null"
                                     v-model:visible="_parametersVisible"
                                     v-model:kwargs="_functionKwargs"
                                     :limits-to-function-kwargs="_limitsToFunctionKwargs"
                                     @updateKwargs="updateCard">
    </ContactMechanicsParametersModal>
</template>
