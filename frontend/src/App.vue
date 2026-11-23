<script setup>
import { createResource } from "frappe-ui";
import AppShell from "./components/AppShell.vue";
import SignOutButton from "./components/SignOutButton.vue";
import Portal from "./pages/Portal.vue";

const profile = createResource({ url: "expense_manager.api.get_profile", auto: true });
</script>

<template>
  <template v-if="profile.data">
    <div v-if="profile.data.dependent" class="fixed inset-0 z-[2000] overflow-y-auto bg-gray-50">
      <header class="flex items-center justify-between border-b bg-white px-6 py-3">
        <span class="text-sm font-semibold">Expense Manager</span>
        <SignOutButton />
      </header>
      <Portal :profile="profile.data" />
    </div>
    <AppShell v-else :profile="profile.data" />
  </template>
</template>
