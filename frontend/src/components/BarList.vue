<script setup>
import { computed } from "vue";
import { formatMoney } from "../format";

const props = defineProps({
  title: { type: String, required: true },
  items: { type: Array, required: true },
});

const max = computed(() => Math.max(...props.items.map((item) => item.total), 1));
</script>

<template>
  <section class="rounded-lg border p-4">
    <h2 class="mb-3 text-sm font-semibold text-gray-700">{{ title }}</h2>
    <p v-if="!items.length" class="text-sm text-gray-500">No expenses in this period.</p>
    <ul class="space-y-3">
      <li v-for="item in items" :key="item.label">
        <div class="flex justify-between text-sm">
          <span>{{ item.label }}</span>
          <span class="font-medium">{{ formatMoney(item.total) }}</span>
        </div>
        <div class="mt-1 h-2 rounded bg-gray-100">
          <div class="h-2 rounded bg-gray-900" :style="{ width: `${(item.total / max) * 100}%` }" />
        </div>
      </li>
    </ul>
  </section>
</template>
