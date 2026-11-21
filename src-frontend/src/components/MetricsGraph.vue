<template>
  <apexchart
    style="width: 100%"
    type="line"
    :options="options"
    :series="series"
    @zoomed="onZoomed"
  ></apexchart>
</template>

<script>
import apexEn from 'apexcharts/dist/locales/en.json';
import apexSe from 'apexcharts/dist/locales/se.json';

const ONE_DAY = 24 * 60 * 60 * 1000;

export default {
  name: 'MetricsGraph',
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
    // Initially zoom to the last N days (0 = show all).
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
      // series names are translated, so hide them by their translated name
      ['inactive', 'accountonly', 'noob'].forEach((state) =>
        chart.hideSeries(this.$t('stats.labels.' + state))
      );
    }, 0); // triggers on the next dom update
  },
  methods: {
    // ApexCharts zooms out symmetrically around the centre, which pushes the
    // view past the last date. vue3-apexcharts replaces options.chart.events
    // (so beforeZoom can't be used), so instead we correct the range after
    // the zoom. The corrected zoom is within bounds, so this doesn't loop.
    onZoomed(chartContext, { xaxis } = {}) {
      const bounds = this.dateBounds;
      if (!bounds || !xaxis || xaxis.min == null || xaxis.max == null) return;

      let { min, max } = xaxis;
      if (max - min >= bounds.max - bounds.min) {
        min = bounds.min;
        max = bounds.max;
      } else if (max > bounds.max) {
        min -= max - bounds.max;
        max = bounds.max;
      } else if (min < bounds.min) {
        max += bounds.min - min;
        min = bounds.min;
      }

      // only re-zoom if the range actually changed (avoid float noise)
      if (
        Math.abs(min - xaxis.min) > 1000 ||
        Math.abs(max - xaxis.max) > 1000
      ) {
        chartContext.zoomX(min, max);
      }
    },
  },
  computed: {
    // ApexCharts locale (axis month/day names, toolbar texts)
    apexLocale() {
      return String(this.$i18n.locale).toLowerCase().startsWith('sv')
        ? 'se'
        : 'en';
    },
    // First/last date as timestamps with half a day of padding, so the
    // first and last bars aren't cut in half. Null when there is no data.
    dateBounds() {
      if (this.metricsData.length === 0) return null;
      const first = new Date(this.metricsData[0].date).getTime();
      const last = new Date(
        this.metricsData[this.metricsData.length - 1].date
      ).getTime();
      return { min: first - ONE_DAY / 2, max: last + ONE_DAY / 2 };
    },
    hasColumns() {
      return Object.values(this.seriesTypes).includes('column');
    },
    options() {
      const options = {
        chart: {
          id: 'metrics-graph-' + this.id,
          locales: [apexEn, apexSe],
          defaultLocale: this.apexLocale,
        },
        // datetime axis: ApexCharts picks localized ticks (via the locale)
        xaxis: {
          type: 'datetime',
          categories: this.metricsData.map((item) => item.date),
        },
        tooltip: {
          x: { format: 'yyyy-MM-dd' },
          y: {
            formatter: (val) =>
              Number.isInteger(val) ? val : Number(val).toFixed(1),
          },
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

      const bounds = this.dateBounds;
      if (
        bounds &&
        this.defaultDays > 0 &&
        this.metricsData.length > this.defaultDays
      ) {
        options.xaxis.min = bounds.max - this.defaultDays * ONE_DAY;
        options.xaxis.max = bounds.max;
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
