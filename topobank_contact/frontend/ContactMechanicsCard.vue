<script>

import {v4 as uuid4} from 'uuid';

import BokehPlot from 'topobank/components/BokehPlot.vue';
import BibliographyModal from 'topobank/analysis/BibliographyModal.vue';
import CardExpandButton from 'topobank/analysis/CardExpandButton.vue';
import ContactMechanicsParametersModal from 'topobank_contact/ContactMechanicsParametersModal.vue';
import DeepZoomImage from 'topobank/components/DeepZoomImage.vue';
import TasksButton from 'topobank/analysis/TasksButton.vue';

export default {
    name: 'contact-mechanics-card',
    components: {
        CardExpandButton,
        ContactMechanicsParametersModal,
        BibliographyModal,
        BokehPlot,
        DeepZoomImage,
        TasksButton
    },
    props: {
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
    },
    inject: ['csrfToken'],
    data() {
        return {
            _analyses: null,
            _api: {},
            _cardStatus: 'mounted',  // 'mounted', 'waiting-for-first-result', 'analyses-partially-available', 'analyses-finished'
            _dois: [],
            _dataSources: [],
            _enable_hardness: 0,
            _hardness: undefined,
            _functionKwargs: null,
            _limitsToFunctionKwargs: null,
            _maxNbIter: 100,
            _nbFailed: 0,
            _nbRunningOrPending: 0,
            _nbSteps: 10,
            _nbSuccess: 0,
            _outputBackend: "svg",
            _periodicity: "nonperiodic",
            _selection: null,
            _sidebarVisible: false,
            _periodicityOptions: [
                {value: "periodic", text: "Periodic (repeating array of the measurement)"},
                {value: "nonperiodic", text: "Free boundaries (flat punch with measurement)"}
            ],
            _pressureselection: "automatic",
            _pressures: []
        }
    },
    mounted() {
        this.updateCard();
    },
    methods: {
        updateCard() {
            this.updateCardWithFunctionKwargs(this._functionKwargs);
        },
        updateCardWithFunctionKwargs(functionKwargs = null) {
            this._functionKwargs = functionKwargs;

            /* Fetch JSON describing the card */
            console.log(functionKwargs);
            let functionKwargsBase64 = btoa(JSON.stringify(functionKwargs));
            fetch(`${this.apiUrl}/${this.functionId}?subjects=${this.subjects}&function_kwargs=${functionKwargsBase64}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'X-CSRFToken': this.csrfToken
                }
            })
                .then(response => response.json())
                .then(data => {
                    this._analyses = data.analyses;
                    this._dois = data.dois;
                    if (this._functionKwargs === null) {
                        this._functionKwargs = data.uniqueKwargs;
                    } else {
                        this._functionKwargs = {
                            ...this._functionKwargs,
                            ...data.uniqueKwargs  // override since the server may report changes
                        };
                    }
                    this._limitsToFunctionKwargs = data.limitsToFunctionKwargs;
                    this._api = data.api;

                    if (data.plotConfiguration !== undefined) {
                        if (this._analyses.map(a => a.task_state == 'pe' || a.task_state == 'st').some(v => v)) {
                            this._cardStatus = 'analyses-partially-available';
                        } else {
                            this._cardStatus = 'analyses-finished';
                        }
                        this._dataSources = data.plotConfiguration.dataSources;
                        this._outputBackend = data.plotConfiguration.outputBackend;
                    } else {
                        this._cardStatus = 'waiting-for-first-result';
                    }
                });
        },
        onSelected(obj, data) {
            const name = data.source.name;
            const path = data.source.data.dataPath[data.source.selected.indices[0]];
            const splitPath = path.split('/');
            this._selection = {
                analysisId: name.split('-')[1],
                dataPath: splitPath[splitPath.length - 1]  // We need to do some name mangling
            };
        },
        taskStateChanged(nbRunningOrPending, nbSuccess, nbFailed) {
            if (nbRunningOrPending == 0 && this._nbRunningOrPending > 0) {
                // All tasks finished, reload card
                this.updateCard();
            }
            this._nbRunningOrPending = nbRunningOrPending;
            this._nbSuccess = nbSuccess;
            this._nbFailed = nbFailed;
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
        },
        contactMechanicsCategories: function () {
            return [{key: "subjectName", title: "Measurements"}];
        },
        distributionPlots: function () {
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
        },
        distributionDataSources: function () {
            return [{
                url: `/analysis/data/${this._selection.analysisId}/${this._selection.dataPath}/json/distributions.json`
            }];
        },
        analysisIds() {
            return this._analyses.map(a => a.id).join();
        }
    }
};
</script>

<template>
    <div class="card search-result-card">
        <div class="card-header">
            <div class="btn-group btn-group-sm float-right">
                <tasks-button v-if="_analyses !== null && _analyses.length > 0"
                              :analyses="_analyses"
                              :csrf-token="csrfToken"
                              @task-state-changed="taskStateChanged">
                </tasks-button>
                <button v-if="_analyses !== null && _analyses.length > 0"
                        @click="updateCard"
                        class="btn btn-default float-right ml-1">
                    <i class="fa fa-redo"></i>
                </button>
                <card-expand-button v-if="!enlarged"
                                    :detail-url="detailUrl"
                                    :function-id="functionId"
                                    :subjects="subjects"
                                    class="btn-group btn-group-sm float-right">
                </card-expand-button>
            </div>
            <h5 v-if="_analyses === null"
                class="text-dark">
                Contact mechanics
            </h5>
            <a v-if="_analyses !== null && _analyses.length > 0"
               class="text-dark"
               href="#"
               @click="_sidebarVisible=true">
                <h5><i class="fa fa-bars"></i> Contact mechanics</h5>
            </a>
        </div>
        <div class="card-body">
            <div v-if="_cardStatus == 'mounted'" class="tab-content">
                <span class="spinner"></span>
                <div>Please wait...</div>
            </div>
            <div v-if="_cardStatus == 'waiting-for-first-result'" class="tab-content">
                <span class="spinner"></span>
                <div>
                    Analyses are not yet available, but tasks are scheduled or running.
                    Please wait...
                </div>
            </div>

            <div v-if="_cardStatus != 'waiting-for-first-result' && _dataSources.length > 0" class="tab-content row">
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

                <!-- Middle with group of tabs -->
                <div v-if="enlarged"
                     class="col-2 col-sm-2 col-md-2 col-lg-2">

                    <div class="nav nav-pills nav-pills-custom flex-column" aria-orientation="vertical">
                        <a class="nav-link mb-3 p-3 shadow active" data-toggle="pill" href="#contacting-points-tab"
                           role="tab"
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
                        <a class="nav-link mb-3 p-3 shadow" data-toggle="pill" href="#gap-tab" role="tab"
                           aria-selected="false">
                            Gap
                        </a>
                        <a class="nav-link mb-3 p-3 shadow" data-toggle="pill" href="#distribution-function-tab"
                           role="tab"
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
                            <div v-if="_selection === null" id="geometry" class="alert alert-info">For contact geometry,
                                select a point
                                in the graphs on the left!
                            </div>
                            <deep-zoom-image v-if="_selection !== null"
                                             :prefix-url="`/analysis/data/${_selection.analysisId}/${_selection.dataPath}/dzi/contacting-points/`"
                                             ref="contactingPoints">
                            </deep-zoom-image>
                            <div v-if="_selection !== null" class="pull-right">
                                <a class="btn btn-default btn-block btn-lg mt-3"
                                   v-on:click="$refs.contactingPoints.download()">
                                    Download PNG
                                </a>
                            </div>
                        </div>
                        <div class="tab-pane fade" id="pressure-tab">
                            <div v-if="_selection === null" id="pressure" class="alert alert-info">For contact pressure,
                                select a point
                                in the graphs on the left!
                            </div>
                            <deep-zoom-image v-if="_selection !== null"
                                             :prefix-url="`/analysis/data/${_selection.analysisId}/${_selection.dataPath}/dzi/pressure/`"
                                             :colorbar="true"
                                             ref="pressure">
                            </deep-zoom-image>
                            <div v-if="_selection !== null" class="pull-right">
                                <a class="btn btn-default btn-block btn-lg" v-on:click="$refs.pressure.download()">
                                    Download PNG
                                </a>
                            </div>
                        </div>
                        <div class="tab-pane fade" id="displacement-tab">
                            <div v-if="_selection === null" id="displacement" class="alert alert-info">For displacement,
                                select a point
                                in the graphs on the left!
                            </div>
                            <deep-zoom-image v-if="_selection !== null"
                                             :prefix-url="`/analysis/data/${_selection.analysisId}/${_selection.dataPath}/dzi/displacement/`"
                                             :colorbar="true"
                                             ref="displacement">
                            </deep-zoom-image>
                            <div v-if="_selection !== null" class="pull-right">
                                <a class="btn btn-default btn-block btn-lg" v-on:click="$refs.displacement.download()">
                                    Download PNG
                                </a>
                            </div>
                        </div>
                        <div class="tab-pane fade" id="gap-tab">
                            <div v-if="_selection === null" id="gap" class="alert alert-info">For gap, select a point in
                                the graphs on
                                the left!
                            </div>
                            <deep-zoom-image v-if="_selection !== null"
                                             :prefix-url="`/analysis/data/${_selection.analysisId}/${_selection.dataPath}/dzi/gap/`"
                                             :colorbar="true"
                                             ref="gap">
                            </deep-zoom-image>
                            <div v-if="_selection !== null" class="pull-right">
                                <a class="btn btn-default btn-block btn-lg" v-on:click="$refs.gap.download()">
                                    Download PNG
                                </a>
                            </div>
                        </div>
                        <div class="tab-pane fade" id="distribution-function-tab">
                            <div v-if="_selection === null" id="distribution-function" class="alert alert-info">For
                                pressure
                                distribution, select a point in the graphs on the left!
                            </div>
                            <bokeh-plot
                                v-if="_selection !== null"
                                :plots="distributionPlots"
                                :data-sources="distributionDataSources"
                                :output-backend="_outputBackend">
                            </bokeh-plot>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div v-if="_sidebarVisible"
             class="position-absolute h-100">
            <nav class="card-header navbar navbar-toggleable-xl bg-light flex-column align-items-start h-100">
                <ul class="flex-column navbar-nav">
                    <a class="text-dark"
                       href="#"
                       @click="_sidebarVisible=false">
                        <h5><i class="fa fa-bars"></i> Contact mechanics</h5>
                    </a>
                    <li class="nav-item mb-1 mt-1">
                        Download
                        <div class="btn-group ml-1"
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
        @update-contact-kwargs="updateCardWithFunctionKwargs"
        :csrf-token="csrfToken">
    </contact-mechanics-parameters-modal>
</template>
