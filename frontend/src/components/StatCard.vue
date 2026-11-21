<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  hint: { type: String, default: "" },
  alert: { type: Boolean, default: false },
});
</script>

<template>
  <div class="rounded-lg border p-4">
    <p class="text-sm text-gray-600">{{ label }}</p>
    <p class="mt-1 text-2xl font-semibold" :class="alert ? 'text-red-600' : ''">{{ value }}</p>
    <p v-if="hint" class="mt-1 text-xs text-gray-500">{{ hint }}</p>
  </div>
</template>
