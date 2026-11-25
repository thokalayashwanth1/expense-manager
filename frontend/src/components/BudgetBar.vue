<script setup>
import { computed } from "vue";
import { categoryIcon, categoryTone } from "../categoryIcons";
import { formatRupees, percentUsed } from "../format";

const props = defineProps({ budget: { type: Object, required: true } });

const ratio = computed(() => (props.budget.amount ? props.budget.spent / props.budget.amount : 0));
const over = computed(() => ratio.value > 1);
const barColor = computed(() => (over.value ? "bg-red-500" : ratio.value >= 0.8 ? "bg-orange-500" : "bg-green-500"));
</script>

<template>
  <div class="flex items-center gap-3">
    <span
      class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-base"
      :class="categoryTone(budget.category)"
    >
      {{ categoryIcon(budget.category) }}
    </span>
    <div class="min-w-0 flex-1">
      <div class="flex items-baseline justify-between gap-2 text-sm">
        <span class="truncate font-medium text-gray-900">{{ budget.category }}</span>
        <span class="shrink-0 text-xs tabular-nums" :class="over ? 'font-semibold text-red-600' : 'text-gray-500'">
          {{ formatRupees(budget.spent) }} of {{ formatRupees(budget.amount) }}
        </span>
      </div>
      <div class="mt-1.5 h-2 overflow-hidden rounded-full bg-gray-100">
        <div class="h-2 rounded-full transition-all" :class="barColor" :style="{ width: `${percentUsed(budget)}%` }" />
      </div>
      <p class="mt-1 text-xs" :class="over ? 'text-red-600' : 'text-gray-400'">
        {{
          over
            ? `${formatRupees(budget.spent - budget.amount)} over budget`
            : `${Math.round(ratio * 100)}% used · ${formatRupees(budget.amount - budget.spent)} left`
        }}
      </p>
    </div>
  </div>
</template>
