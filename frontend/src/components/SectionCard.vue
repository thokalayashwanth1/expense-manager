<script setup>
defineProps({
  title: { type: String, default: "" },
  loading: { type: Boolean, default: false },
  emptyText: { type: String, default: "" },
});
</script>

<template>
  <section class="rounded-lg border bg-white p-4 shadow-sm">
    <h2 v-if="title" class="mb-3 text-sm font-semibold text-gray-700">{{ title }}</h2>
    <p v-if="loading" class="text-sm text-gray-500">Loading…</p>
    <p v-else-if="emptyText" class="text-sm text-gray-500">{{ emptyText }}</p>
    <slot v-else />
  </section>
</template>
