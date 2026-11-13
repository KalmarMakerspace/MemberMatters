<template>
  <apexchart
    style="width: 100%"
    type="line"
    :options="options"
    :series="series"
  ></apexchart>
</template>

<script>
import formatMixin from 'src/mixins/formatMixin';

export default {
  name: 'MetricsGraph',
  mixins: [formatMixin],
  props: {
    metricsData: {
      type: Array,
      default: () => [],
    },
    id: {
      type: String,
      default: '',
    },
    // Optional map of series key -> ApexCharts series type ('column' | 'line')
    seriesTypes: {
      type: Object,
      default: () => ({}),
    },
    // Use a datetime x-axis (better for long daily series)
    datetimeAxis: {
      type: Boolean,
      default: false,
    },
    // With datetimeAxis: initially zoom to the last N days (0 = show all).
    // All data is still loaded, so users can zoom out / reset to see more.
    defaultDays: {
      type: Number,
      default: 0,
    },
  },
  data() {
    return {};
  },
  mounted() {
    setTimeout(() => {
      const chart = ApexCharts.getChartByID('metrics-graph-' + this.id);
      chart.hideSeries('Inactive Member');
      chart.hideSeries('Account Only');
      chart.hideSeries('New Member');
    }, 0); // triggers on the next dom update
  },
  computed: {
    hasColumns() {
      return Object.values(this.seriesTypes).includes('column');
    },
    options() {
      const options = {
        chart: {
          id: 'metrics-graph-' + this.id,
        },
        xaxis: this.datetimeAxis
          ? {
              type: 'datetime',
              categories: this.metricsData.map((item) => item.date),
            }
          : {
              categories: this.metricsData.map((item) =>
                this.formatDate(item.date)
              ),
            },
        theme: {
          mode: this.$q.dark.isActive ? 'dark' : 'light',
        },
        yaxis: {
          labels: {
            formatter: function (val) {
              return val.toFixed(0);
            },
            min: 0,
          },
        },
      };

      if (this.datetimeAxis) {
        options.tooltip = {
          x: { format: 'yyyy-MM-dd' },
          y: {
            formatter: (val) =>
              Number.isInteger(val) ? val : Number(val).toFixed(1),
          },
        };

        const dates = this.metricsData.map((item) => item.date);
        if (this.defaultDays > 0 && dates.length > this.defaultDays) {
          const oneDay = 24 * 60 * 60 * 1000;
          const last = new Date(dates[dates.length - 1]).getTime();
          // half-day padding so the first/last bars aren't cut in half
          options.xaxis.min = last - (this.defaultDays - 0.5) * oneDay;
          options.xaxis.max = last + 0.5 * oneDay;
        }
      }

      if (this.hasColumns) {
        options.dataLabels = { enabled: false };
        options.stroke = {
          width: this.series.map((s) => (s.type === 'column' ? 0 : 3)),
        };
        options.plotOptions = { bar: { columnWidth: '90%' } };
      }

      return options;
    },
    series() {
      let states = {};
      this.metricsData.map((item) => {
        if (Array.isArray(item.data)) {
          item.data.forEach((state) => {
            if (!state?.state && !state?.type) return;
            if (states[state?.state ?? state?.type] === undefined) {
              states[state?.state ?? state?.type] = [];
            }
            states[state?.state ?? state?.type].push(state.total);
          });
        } else {
          if (states['value'] === undefined) {
            states['value'] = [];
          }
          states['value'].push(item.data.value);
        }
      });
      return Object.keys(states).map((state) => {
        const series = {
          name: this.$t('stats.labels.' + state),
          data: states[state],
        };
        if (this.seriesTypes[state]) {
          series.type = this.seriesTypes[state];
        }
        return series;
      });
    },
  },
};
</script>
