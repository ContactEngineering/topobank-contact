<script>

import {v4 as uuid4} from 'uuid';

import BokehPlot from 'topobank/components/BokehPlot.vue';
import BibliographyModal from 'topobank/analysis/BibliographyModal.vue';
import TasksButton from 'topobank/analysis/TasksButton.vue';

export default {
  name: 'contact-mechanics-card',
  components: {
    BibliographyModal,
    BokehPlot,
    TasksButton
  },
  props: {
    apiUrl: String,
    csrfToken: String,
    detailUrl: String,
    enlargeButton: {
      type: Boolean,
      default: false
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
      dois: [],
      dataSources: [],
      outputBackend: "svg"
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
            console.log(data);
            this.dataSources = data.plotConfiguration.dataSources;
            this.outputBackend = data.plotConfiguration.outputBackend;
            this.dois = data.dois;
            this.analysesAvailable = true;
          });
    }
  },
  computed: {
    contactMechanicsPlots: function () {
      return [{
        title: "Contact area vs load",
        xData: "data.mean_pressures",
        yData: "data.total_contact_areas",
        alphaData: "data.converged.map((value) => value ? 1.0 : 0.3)",
        xAxisLabel: "Normalized pressure p/E*",
        yAxisLabel: "Fractional contact area A/A0",
        xAxisType: "log",
        yAxisType: "log"
      }, {
        title: "Load vs displacement",
        xData: "data.mean_gaps",
        yData: "data.mean_pressures",
        alphaData: "data.converged.map((value) => value ? 1.0 : 0.3)",
        xAxisLabel: "Normalized mean gap u/h_rms",
        yAxisLabel: "Normalized pressure p/E*",
        xAxisType: "linear",
        yAxisType: "log"
      }]
    },
    contactMechanicsCategories: function () {
      return [{key: "subjectName", title: "Measurements"}];
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
        <div v-if="enlargeButton" class="btn-group btn-group-sm float-right">
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

      <div v-if="analysesAvailable" class="tab-content">
        <div class="tab-pane show active" id="plot-{{ card_id }}" role="tabpanel" aria-labelledby="card-tab">
          <bokeh-plot
              :plots="contactMechanicsPlots"
              :categories="contactMechanicsCategories"
              :data-sources="dataSources"
              :options-widgets="['layout', 'legend', 'lineWidth', 'symbolSize']"
              :output-backend="outputBackend">
          </bokeh-plot>
        </div>
      </div>
    </div>
  </div>
  <bibliography-modal
      :id="`bibliography-modal-${uid}`"
      :dois="dois">
  </bibliography-modal>
</template>
