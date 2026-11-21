<script setup>
defineProps({ profile: { type: Object, required: true } });

const links = [
  { to: "/", label: "Dashboard" },
  { to: "/expenses", label: "Expenses" },
  { to: "/categories", label: "Categories" },
  { to: "/budgets", label: "Budgets" },
  { to: "/dependents", label: "Dependents" },
  { to: "/reports", label: "Reports" },
  { to: "/telegram", label: "Telegram" },
];
</script>

<template>
  <div class="mx-auto max-w-5xl p-6">
    <header class="mb-6 flex items-center justify-between border-b pb-3">
      <nav class="flex gap-4">
        <router-link
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          class="text-sm text-gray-600"
          active-class="font-semibold text-gray-900"
          exact-active-class="font-semibold text-gray-900"
        >
          {{ link.label }}
        </router-link>
      </nav>
      <span class="text-sm text-gray-600">{{ profile.full_name }}</span>
    </header>
    <router-view />
  </div>
</template>
