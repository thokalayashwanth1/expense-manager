<script setup>
import { computed, ref } from "vue";
import { Button, createResource } from "frappe-ui";
import { BarChart } from "frappe-ui/charts";
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
const trend = createResource({ url: "expense_manager.api.get_monthly_trend", auto: true });
const budgets = createResource({ url: "expense_manager.api.get_budget_status", auto: true });

const rows = computed(() => report.data || []);
const grandTotal = computed(() => rows.value.reduce((sum, row) => sum + row.total, 0));

const totalsBy = (key) => {
  const totals = {};
  for (const row of rows.value) totals[row[key]] = (totals[row[key]] || 0) + row.total;
  return Object.entries(totals)
    .map(([label, total]) => ({ label, total }))
    .sort((a, b) => b.total - a.total);
};
const byCategory = computed(() => totalsBy("category"));
const byPerson = computed(() => totalsBy("spent_by"));

const selectPeriod = (value) => {
  period.value = value;
  report.submit({ period: value });
};

const percentUsed = (budget) => Math.min((budget.spent / budget.amount) * 100, 100);

const downloadCsv = () => {
  const lines = ["person,category,total", ...rows.value.map((row) => `${row.spent_by},${row.category},${row.total}`)];
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob([lines.join("\n")], { type: "text/csv" }));
  link.download = `expense-report-${period.value}.csv`;
  link.click();
  URL.revokeObjectURL(link.href);
};
</script>

<template>
  <div class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-xl font-semibold">Reports</h1>
        <p class="text-sm text-gray-600">
          {{ formatMoney(grandTotal) }} spent {{ period === "week" ? "this week" : "this month" }}
        </p>
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
        <Button variant="outline" :disabled="!rows.length" @click="downloadCsv">Download CSV</Button>
      </div>
    </div>

    <div class="h-80 rounded-lg border p-4">
      <BarChart
        title="Spending trend"
        subtitle="Last 6 months"
        :data="trend.data || []"
        x="month"
        y="total"
        :y-axis="{ format: formatMoney }"
        :loading="trend.loading"
      />
    </div>

    <div class="grid gap-4 md:grid-cols-2">
      <div class="h-80 rounded-lg border p-4">
        <BarChart
          title="By category"
          :data="byCategory"
          x="label"
          y="total"
          horizontal
          :y-axis="{ format: formatMoney }"
          :loading="report.loading"
        />
      </div>

      <section class="rounded-lg border p-4">
        <h2 class="mb-3 text-sm font-semibold text-gray-700">By person</h2>
        <p v-if="!byPerson.length" class="text-sm text-gray-500">No expenses in this period.</p>
        <ul class="divide-y">
          <li v-for="person in byPerson" :key="person.label" class="flex justify-between py-2 text-sm">
            <span>{{ person.label }}</span>
            <span class="font-medium">{{ formatMoney(person.total) }}</span>
          </li>
        </ul>
      </section>
    </div>

    <section class="rounded-lg border p-4">
      <h2 class="mb-3 text-sm font-semibold text-gray-700">Budget utilisation this month</h2>
      <p v-if="budgets.data && !budgets.data.length" class="text-sm text-gray-500">No budgets set.</p>
      <ul class="space-y-4">
        <li v-for="budget in budgets.data" :key="budget.name">
          <div class="flex justify-between text-sm">
            <span>{{ budget.category }}</span>
            <span :class="budget.spent > budget.amount ? 'font-medium text-red-600' : ''">
              {{ Math.round((budget.spent / budget.amount) * 100) }}% ·
              {{ formatMoney(budget.spent) }} of {{ formatMoney(budget.amount) }}
            </span>
          </div>
          <div class="mt-1 h-2 rounded bg-gray-100">
            <div
              class="h-2 rounded"
              :class="budget.spent > budget.amount ? 'bg-red-500' : 'bg-gray-900'"
              :style="{ width: `${percentUsed(budget)}%` }"
            />
          </div>
        </li>
      </ul>
    </section>
  </div>
</template>
