<script setup>
import SignOutButton from "./SignOutButton.vue";

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
  <div class="shell">
    <aside class="shell-sidebar">
      <div class="flex items-center gap-2 px-5 py-4">
        <span class="flex size-8 items-center justify-center rounded-lg bg-gray-900 text-sm font-semibold text-white">E</span>
        <div>
          <p class="text-sm font-semibold">Expense Manager</p>
          <p class="text-xs text-gray-500">Family money, in one place</p>
        </div>
      </div>
      <nav class="flex-1 space-y-1 px-3 py-2">
        <router-link
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          class="block rounded-md px-3 py-2 text-sm text-gray-600 hover:bg-gray-100"
          exact-active-class="bg-gray-100 font-semibold text-gray-900"
        >
          {{ link.label }}
        </router-link>
      </nav>
      <div class="space-y-2 border-t p-4">
        <p class="truncate text-sm font-medium">{{ profile.full_name }}</p>
        <SignOutButton />
      </div>
    </aside>

    <header class="shell-topbar">
      <div class="flex items-center justify-between px-4 py-3">
        <span class="text-sm font-semibold">Expense Manager</span>
        <SignOutButton />
      </div>
      <nav class="flex gap-1 overflow-x-auto px-3 pb-2">
        <router-link
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          class="shrink-0 rounded-md px-3 py-1.5 text-sm text-gray-600"
          exact-active-class="bg-gray-100 font-semibold text-gray-900"
        >
          {{ link.label }}
        </router-link>
      </nav>
    </header>

    <main class="shell-main">
      <div class="mx-auto max-w-5xl">
        <router-view />
      </div>
    </main>
  </div>
</template>
