<template>
  <q-page class="column flex content-center justify-start">
    <stations-list />
  </q-page>
</template>

<script lang="ts">
import StationsList from '@components/AdminTools/StationsList.vue';

export default {
  name: 'ManageStations',
  components: { StationsList },
};
</script>
