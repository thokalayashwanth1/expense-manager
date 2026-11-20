<script setup>
import { computed, ref } from "vue";
import { Button, createResource } from "frappe-ui";
import BarList from "../components/BarList.vue";
import { formatMoney } from "../format";

const periods = [
  { value: "week", label: "This week" },
  { value: "month", label: "This month" },
];
const period = ref("month");

const report = createResource({
  url: "expense_manager.api.get_expense_report",
  params: { period: period.value },
  auto: true,
});

const rows = computed(() => report.data || []);
const grandTotal = computed(() => rows.value.reduce((sum, row) => sum + row.total, 0));

const totalsBy = (key) => {
  const totals = {};
  for (const row of rows.value) totals[row[key]] = (totals[row[key]] || 0) + row.total;
  return Object.entries(totals).map(([label, total]) => ({ label, total }));
};
const byCategory = computed(() => totalsBy("category"));
const byPerson = computed(() => totalsBy("spent_by"));

const selectPeriod = (value) => {
  period.value = value;
  report.submit({ period: value });
};
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm text-gray-600">Total spent</p>
        <p class="text-3xl font-semibold">{{ formatMoney(grandTotal) }}</p>
      </div>
      <div class="flex gap-2">
        <Button
          v-for="option in periods"
          :key="option.value"
          :variant="period === option.value ? 'solid' : 'subtle'"
          @click="selectPeriod(option.value)"
        >
          {{ option.label }}
        </Button>
      </div>
    </div>
    <div class="grid gap-4 md:grid-cols-2">
      <BarList title="By category" :items="byCategory" />
      <BarList title="By person" :items="byPerson" />
    </div>
  </div>
</template>
