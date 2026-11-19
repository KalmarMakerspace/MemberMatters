<template>
  <div>
    <q-dialog v-model="addStationDialog" persistent>
      <q-card>
        <q-card-section class="row items-center">
          <span class="q-ml-sm">{{ $t('stations.add') }}</span>
        </q-card-section>

        <q-card-actions align="right">
          <q-form ref="formRef" @submit="submitStation()">
            <q-input
              v-model="form.name"
              outlined
              :debounce="debounceLength"
              :label="$t('form.name')"
              :rules="[
                (val) =>
                  validateNotEmpty(val) || $t('validation.cannotBeEmpty'),
              ]"
              :disable="form.success"
            />

            <q-banner
              v-if="form.success"
              class="bg-positive text-white q-my-md"
            >
              {{ $t('stationForm.success') }}
            </q-banner>

            <q-banner v-if="form.error" class="bg-negative text-white q-my-md">
              {{ $t('stationForm.fail') }}
            </q-banner>

            <q-card-actions
              v-if="!form.success"
              align="right"
              class="text-primary"
            >
              <q-btn
                v-close-popup
                flat
                :label="$t('button.cancel')"
                :disable="loading"
              />
              <q-btn
                color="primary"
                :label="$t('button.submit')"
                :loading="loading"
                :disable="loading"
                type="submit"
              />
            </q-card-actions>

            <q-card-actions v-else align="right" class="text-primary">
              <q-btn
                v-close-popup
                flat
                :label="$t('button.close')"
                @click="resetForm()"
              />
            </q-card-actions>
          </q-form>
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="renameStationDialog">
      <q-card>
        <q-card-section class="row items-center">
          <span class="q-ml-sm">{{ $t('stations.rename') }}</span>
        </q-card-section>

        <q-card-actions align="right">
          <q-form ref="renameFormRef" @submit="submitRename()">
            <q-input
              v-model="renameForm.name"
              outlined
              :debounce="debounceLength"
              :label="$t('form.name')"
              :rules="[
                (val) =>
                  validateNotEmpty(val) || $t('validation.cannotBeEmpty'),
              ]"
            />

            <q-card-actions align="right" class="text-primary">
              <q-btn v-close-popup flat :label="$t('button.cancel')" />
              <q-btn
                color="primary"
                :label="$t('button.submit')"
                :loading="renameLoading"
                :disable="renameLoading"
                type="submit"
              />
            </q-card-actions>
          </q-form>
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-table
      :rows="stations"
      :columns="[
        { name: 'name', label: 'Name', field: 'name', sortable: true },
        { name: 'actions', label: '', field: 'id' },
      ]"
      row-key="id"
      :filter="filter"
      v-model:pagination="pagination"
      :grid="$q.screen.xs"
      :no-data-label="$t('stations.nodata')"
    >
      <template v-slot:top-right>
        <q-input
          v-model="filter"
          outlined
          dense
          debounce="300"
          placeholder="Search"
        >
          <template v-slot:append>
            <q-icon :name="icons.search" />
          </template>
        </q-input>
      </template>
      <template v-slot:top-left>
        <q-btn
          @click="addStationDialog = true"
          round
          color="primary"
          :icon="icons.addAlternative"
        >
          <q-tooltip :delay="500">{{ $t('stations.add') }}</q-tooltip>
        </q-btn>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props" class="text-right">
          <q-btn
            flat
            round
            dense
            :icon="icons.edit"
            @click="openRenameDialog(props.row)"
          />
          <q-btn
            flat
            round
            dense
            color="negative"
            :icon="icons.delete"
            @click="deleteStation(props.row)"
          />
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import icons from '../../icons';
import formatMixin from '../../mixins/formatMixin';
import formMixin from '../../mixins/formMixin';
import { api } from 'boot/axios';
import { Station } from 'types/member';

export default defineComponent({
  name: 'StationsList',
  mixins: [formatMixin, formMixin],
  data() {
    return {
      stations: [] as Station[],
      addStationDialog: false,
      renameStationDialog: false,
      loading: false,
      renameLoading: false,
      form: {
        error: false,
        success: false,
        name: '',
      },
      renameForm: {
        id: null as number | null,
        name: '',
      },
      filter: '',
      pagination: {
        sortBy: 'name',
        descending: false,
        rowsPerPage: this.$q.screen.xs ? 3 : 10,
      },
    };
  },
  beforeMount() {
    this.getStations();
  },
  computed: {
    icons() {
      return icons;
    },
  },
  methods: {
    getStations() {
      api.get('/api/admin/stations/').then((res) => {
        this.stations = res.data;
      });
    },
    submitStation() {
      this.loading = true;

      api
        .post('/api/admin/stations/', this.form)
        .then(() => {
          this.form.error = false;
          this.form.success = true;
          this.getStations();
        })
        .catch(() => {
          this.form.error = true;
        })
        .finally(() => {
          this.loading = false;
        });
    },
    resetForm() {
      this.form = {
        error: false,
        success: false,
        name: '',
      };
      this.loading = false;
    },
    openRenameDialog(station: Station) {
      this.renameForm.id = station.id;
      this.renameForm.name = station.name;
      this.renameStationDialog = true;
    },
    submitRename() {
      this.renameLoading = true;

      api
        .put(`/api/admin/stations/${this.renameForm.id}/`, {
          name: this.renameForm.name,
        })
        .then(() => {
          this.renameStationDialog = false;
          this.getStations();
        })
        .finally(() => {
          this.renameLoading = false;
        });
    },
    deleteStation(station: Station) {
      this.$q
        .dialog({
          title: this.$t('stations.remove'),
          message: station.name,
          cancel: true,
          persistent: true,
        })
        .onOk(() => {
          api.delete(`/api/admin/stations/${station.id}/`).then(() => {
            this.getStations();
          });
        });
    },
  },
});
</script>
