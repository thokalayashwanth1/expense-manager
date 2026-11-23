<script setup>
import { computed } from "vue";
import { formatMoney, percentUsed } from "../format";

const props = defineProps({ budget: { type: Object, required: true } });
const over = computed(() => props.budget.spent > props.budget.amount);
</script>

<template>
  <div>
    <div class="flex justify-between text-sm">
      <span>{{ budget.category }}</span>
      <span :class="over ? 'font-medium text-red-600' : ''">
        {{ Math.round((budget.spent / budget.amount) * 100) }}% ·
        {{ formatMoney(budget.spent) }} of {{ formatMoney(budget.amount) }}
      </span>
    </div>
    <div class="mt-1 h-2 rounded bg-gray-100">
      <div
        class="h-2 rounded"
        :class="over ? 'bg-red-500' : 'bg-gray-900'"
        :style="{ width: `${percentUsed(budget)}%` }"
      />
    </div>
  </div>
</template>
