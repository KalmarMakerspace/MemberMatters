<template>
  <q-page class="column flex justify-start items-center">
    <div class="column flex content-start justify-center">
      <q-banner
        v-if="
          profile.memberStatus !== 'active' &&
          profile.memberStatus !== 'accountonly'
        "
        inline-actions
        rounded
        class="bg-orange text-white q-ma-md"
      >
        <template v-slot:avatar>
          <q-icon :name="icons.warning" />
        </template>
        {{ $t('access.inactive') }}
      </q-banner>

      <q-banner
        v-if="profile.memberStatus === 'accountonly'"
        inline-actions
        rounded
        class="bg-blue text-white q-ma-md"
      >
        <template v-slot:avatar>
          <q-icon :name="icons.info" />
        </template>
        {{ $t('paymentPlans.profileAccountOnlyWarning') }}
      </q-banner>
    </div>

    <profile-form class="q-mb-lg" />

    <q-btn
      push
      color="primary"
      :label="$t('changePasswordCard.pageTitle')"
      @click="changePassword = true"
    />

    <q-dialog v-model="changePassword">
      <change-password-card />
    </q-dialog>
  </q-page>
</template>

<script>
import ProfileForm from '@components/ProfileForm.vue';
import icons from '../icons';
import ChangePasswordCard from '@components/ChangePasswordCard.vue';
import { mapGetters } from 'vuex';

export default {
  name: 'ProfilePage',
  components: { ChangePasswordCard, ProfileForm },
  data() {
    return {
      text: '',
      changePassword: false,
    };
  },
  computed: {
    ...mapGetters('profile', ['loggedIn', 'profile']),
    icons() {
      return icons;
    },
  },
};
</script>
