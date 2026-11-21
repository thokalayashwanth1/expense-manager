<script setup>
import { computed, ref } from "vue";
import { Button, createListResource, createResource } from "frappe-ui";
import { BarChart, DonutChart } from "frappe-ui/charts";
import StatCard from "../components/StatCard.vue";
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
const budgets = createResource({ url: "expense_manager.api.get_budget_status", auto: true });
const dependents = createResource({ url: "expense_manager.api.get_dependents", auto: true });
const recent = createListResource({
  doctype: "Expense",
  fields: ["name", "amount", "category", "description", "spent_by", "expense_date"],
  orderBy: "creation desc",
  pageLength: 5,
  auto: true,
});

const rows = computed(() => report.data || []);
const grandTotal = computed(() => rows.value.reduce((sum, row) => sum + row.total, 0));

const sumOf = (items, key) => (items || []).reduce((sum, item) => sum + item[key], 0);
const budgetTotal = computed(() => sumOf(budgets.data, "amount"));
const budgetSpent = computed(() => sumOf(budgets.data, "spent"));
const overBudget = computed(() => (budgets.data || []).filter((b) => b.spent > b.amount).length);

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
      <h1 class="text-xl font-semibold">Dashboard</h1>
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

    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatCard label="Total spent" :value="formatMoney(grandTotal)" :hint="`${rows.length} entries grouped`" />
      <StatCard
        label="Remaining budget"
        :value="formatMoney(budgetTotal - budgetSpent)"
        :hint="`of ${formatMoney(budgetTotal)} this month`"
      />
      <StatCard
        label="Over budget"
        :value="overBudget"
        :hint="`of ${(budgets.data || []).length} budgets`"
        :alert="overBudget > 0"
      />
      <StatCard label="Dependents" :value="(dependents.data || []).length" hint="on your plan" />
    </div>

    <div class="grid gap-4 md:grid-cols-2">
      <div class="h-80 rounded-lg border p-4">
        <DonutChart
          title="By category"
          :data="byCategory"
          category="label"
          value="total"
          :format="formatMoney"
          :loading="report.loading"
        />
      </div>
      <div class="h-80 rounded-lg border p-4">
        <BarChart
          title="By person"
          :data="byPerson"
          x="label"
          y="total"
          horizontal
          :y-axis="{ format: formatMoney }"
          :loading="report.loading"
        />
      </div>
    </div>

    <section class="rounded-lg border p-4">
      <h2 class="mb-3 text-sm font-semibold text-gray-700">Recent expenses</h2>
      <p v-if="recent.data && !recent.data.length" class="text-sm text-gray-500">No expenses yet.</p>
      <ul class="divide-y">
        <li v-for="expense in recent.data" :key="expense.name" class="flex justify-between py-2 text-sm">
          <div>
            <p class="font-medium">{{ expense.description || expense.category }}</p>
            <p class="text-xs text-gray-500">
              {{ expense.category }} · {{ expense.spent_by }} · {{ expense.expense_date }}
            </p>
          </div>
          <span class="font-medium">{{ formatMoney(expense.amount) }}</span>
        </li>
      </ul>
    </section>
  </div>
</template>
