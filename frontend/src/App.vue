<script setup>
import { createResource } from "frappe-ui";
import AppShell from "./components/AppShell.vue";
import Portal from "./pages/Portal.vue";

const profile = createResource({ url: "expense_manager.api.get_profile", auto: true });
</script>

<template>
  <template v-if="profile.data">
    <Portal v-if="profile.data.dependent" :profile="profile.data" />
    <AppShell v-else :profile="profile.data" />
  </template>
</template>
