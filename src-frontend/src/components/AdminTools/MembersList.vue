<template>
  <div style="max-width: 100%">
    <q-table
      :rows="displayMemberList"
      :no-data-label="$t('adminTools.noMembers')"
      :columns="columns"
      row-key="email"
      :filter="filter"
      v-model:pagination="pagination"
      :loading="loading"
      :grid="$q.screen.lt.md"
      class="full-width"
      @row-click="
        (evt, row) => {
          $router.push({
            name: 'manageMember',
            params: { memberId: row.id },
          });
        }
      "
    >
      <template v-slot:top-left>
        <div class="row flex items-start">
          <template v-if="$q.screen.lt.md">
            <div class="full-width">
              <q-btn-dropdown
                class="q-mb-sm"
                color="primary"
                :label="$t('adminTools.exportOptions')"
              >
                <q-list>
                  <q-item v-close-popup clickable @click="exportCsv">
                    <q-item-section>
                      <q-item-label>{{
                        $t('adminTools.exportCsv')
                      }}</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item
                    v-close-popup
                    clickable
                    @click="importDialogOpen = true"
                  >
                    <q-item-section>
                      <q-item-label>{{
                        $t('adminTools.importCsv')
                      }}</q-item-label>
                    </q-item-section>
                  </q-item>

                  <q-item
                    v-close-popup
                    clickable
                    @click="copyEmailsToClipboard"
                  >
                    <q-item-section>
                      <q-item-label>{{
                        $t('adminTools.emailAddresses')
                      }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-btn-dropdown>
            </div>
            <div class="full-width">
              <q-select
                v-model="memberState"
                class="q-mb-sm"
                outlined
                emit-value
                :options="filterOptions"
                :label="$t('adminTools.filterOptions')"
                dense
              />
            </div>
          </template>

          <template v-else>
            <q-btn
              class="q-mr-sm q-mb-sm"
              color="primary"
              :icon="icons.export"
              :label="$t('adminTools.exportCsv')"
              @click="exportCsv"
            />
            <q-btn
              class="q-mr-sm q-mb-sm"
              color="primary"
              :icon="icons.upload"
              :label="$t('adminTools.importCsv')"
              @click="importDialogOpen = true"
            />
            <q-btn
              class="q-mr-sm q-mb-sm"
              color="primary"
              :icon="icons.email"
              :label="$t('adminTools.emailAddresses')"
              @click="copyEmailsToClipboard"
            />
          </template>
        </div>
      </template>
      <template v-slot:top-right>
        <q-select
          v-if="$q.screen.gt.sm"
          v-model="memberState"
          class="q-mr-sm"
          style="min-width: 100px"
          outlined
          emit-value
          :options="filterOptions"
          :label="$t('adminTools.filterOptions')"
          dense
        />

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
    </q-table>

    <q-dialog v-model="importDialogOpen" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">{{ $t('adminTools.importCsv') }}</div>
          <div class="text-caption q-mt-xs">
            {{ $t('adminTools.importCsvDescription') }}
          </div>
        </q-card-section>
        <q-card-section>
          <q-file
            v-model="importFile"
            accept=".csv"
            outlined
            :label="$t('adminTools.importCsvFileLabel')"
          />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn
            flat
            :label="$t('button.cancel')"
            @click="importDialogOpen = false; importFile = null"
          />
          <q-btn
            color="primary"
            :label="$t('button.import')"
            :loading="importLoading"
            :disable="!importFile"
            @click="importCsv"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script lang="ts">
import { copyToClipboard } from 'quasar';
import icons from '@icons';
import formatMixin from '@mixins/formatMixin';
import { exportFile } from 'quasar';
import { stringify } from 'csv-stringify';
import { mapGetters } from 'vuex';
import { MemberProfile } from 'types/member';
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'MembersList',
  mixins: [formatMixin],
  data() {
    return {
      members: [],
      filter: '',
      memberState: 'active',
      loading: false,
      importDialogOpen: false,
      importFile: null,
      importLoading: false,
      pagination: {
        sortBy: 'date',
        descending: true,
        rowsPerPage: this.$q.screen.xs ? 3 : 10,
      },
    };
  },
  computed: {
    ...mapGetters('config', ['features']),
    displayMemberList() {
      if (this.memberState === 'all') return this.members;
      return this.members.filter(
        (member: MemberProfile) => member.state === this.memberState
      );
    },
    memberEmails() {
      return this.displayMemberList
        .filter((member: MemberProfile) => !member.excludeFromEmailExport)
        .map((member: MemberProfile) => member.email)
        .join(',');
    },
    icons() {
      return icons;
    },
    filterOptions() {
      return [
        { label: this.$t('adminTools.all'), value: 'all' },
        { label: this.$t('adminTools.active'), value: 'active' },
        { label: this.$t('adminTools.inactive'), value: 'inactive' },
        { label: this.$t('adminTools.new'), value: 'noob' },
        { label: this.$t('adminTools.accountOnly'), value: 'accountonly' },
      ];
    },
    columns() {
      return [
        {
          name: 'name',
          label: this.$t('tableHeading.name'),
          field: (row: MemberProfile) => row.name.full,
          sortable: true,
          format: (val: string, row: MemberProfile) =>
            `${val} (${row.screenName})`,
        },
        {
          name: 'rfid',
          label: this.$t('tableHeading.rfid'),
          field: 'rfid',
          sortable: true,
        },
        {
          name: 'email',
          label: this.$t('tableHeading.email'),
          field: 'email',
          sortable: true,
        },
        // this is weird syntax, but cleanest way to do it
        ...(this.features?.signup?.collectVehicleRegistrationPlate
          ? [
              {
                name: 'vehicleRegistration',
                label: this.$t('form.vehicleRegistrationPlate'),
                field: 'vehicleRegistrationPlate',
                sortable: true,
              },
            ]
          : []),
        {
          name: 'subscriptionStatus',
          label: this.$t('tableHeading.subscriptionStatus'),
          field: 'subscriptionStatus',
          sortable: true,
        },
        {
          name: 'status',
          label: this.$t('tableHeading.status'),
          field: 'state',
          sortable: true,
        },
      ];
    },
  },
  mounted() {
    this.getMembers();
  },
  methods: {
    getMembers() {
      this.loading = true;
      this.$axios
        .get('/api/admin/members/')
        .then((response) => {
          this.members = response.data;
        })
        .catch(() => {
          this.$q.dialog({
            title: this.$t('error.error'),
            message: this.$t('error.requestFailed'),
          });
        })
        .finally(() => {
          this.loading = false;
        });
    },
    exportCsv() {
      console.log(this.displayMemberList);
      stringify(
        this.displayMemberList,
        {
          columns: ['name.full', 'email', 'state'],
        },
        (err, output) => {
          const status = exportFile('member-export.csv', output, 'text/csv');

          if (status !== true) {
            this.$q.notify({
              message: this.$t('error.downloadFailed'),
              color: 'negative',
              icon: 'warning',
            });
          }
        }
      );
    },
    importCsv() {
      if (!this.importFile) return;
      this.importLoading = true;
      const formData = new FormData();
      formData.append('file', this.importFile);
      this.$axios
        .post('/api/admin/members/import/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
        .then((response) => {
          const { created, updated, errors } = response.data;
          let message = this.$t('adminTools.importCsvSuccess', {
            created,
            updated,
          });
          if (errors.length) {
            message +=
              '\n\n' +
              this.$t('adminTools.importCsvErrors', { count: errors.length }) +
              '\n' +
              errors
                .map(
                  (e: { row: number; email?: string; error: string }) =>
                    `Row ${e.row}${e.email ? ` (${e.email})` : ''}: ${e.error}`
                )
                .join('\n');
          }
          this.$q.dialog({
            title: this.$t('adminTools.importCsvResultTitle'),
            message,
            style: 'white-space: pre-wrap',
          });
          this.importDialogOpen = false;
          this.importFile = null;
          this.getMembers();
        })
        .catch(() => {
          this.$q.dialog({
            title: this.$t('error.error'),
            message: this.$t('error.requestFailed'),
          });
        })
        .finally(() => {
          this.importLoading = false;
        });
    },
    copyEmailsToClipboard() {
      copyToClipboard(this.memberEmails)
        .then(() => {
          this.$q.dialog({
            dark: true,
            title: this.$tc(
              'adminTools.copyEmailListSuccess',
              this.displayMemberList.length
            ),
            message: this.$tc(
              'adminTools.copyEmailListSuccessDescription',
              this.displayMemberList.length -
                this.displayMemberList.filter(
                  (member: MemberProfile) => !member.excludeFromEmailExport
                ).length
            ),
          });
        })
        .catch(() => {
          this.$q.dialog({
            dark: true,
            title: this.$t('error.copyToClipboard'),
            message: this.$t('error.copyToClipboardDescription'),
          });
        });
    },
  },
});
</script>

<style scoped lang="scss">
.td {
  padding: 0;
}
</style>
