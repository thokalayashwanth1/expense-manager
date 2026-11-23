<script setup>
import { computed, ref } from "vue";
import { Button, createListResource, createResource } from "frappe-ui";
import { BarChart, DonutChart } from "frappe-ui/charts";
import QuickAddExpense from "../components/QuickAddExpense.vue";
import StatCard from "../components/StatCard.vue";
import { formatMoney, totalsBy } from "../format";

const periods = [
  { value: "week", label: "This week" },
  { value: "month", label: "This month" },
];
const period = ref("month");
const showQuickAdd = ref(false);

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
const overspent = computed(() => (budgets.data || []).filter((budget) => budget.spent > budget.amount));

const byCategory = computed(() => totalsBy(rows.value, "category"));
const byPerson = computed(() => totalsBy(rows.value, "spent_by"));

const selectPeriod = (value) => {
  period.value = value;
  report.submit({ period: value });
};

const refreshAll = () => {
  report.reload();
  budgets.reload();
  dependents.reload();
  recent.reload();
};
</script>

<template>
  <div class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
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
        <Button variant="solid" theme="green" @click="showQuickAdd = true">+ Quick add expense</Button>
      </div>
    </div>

    <div
      v-for="budget in overspent"
      :key="budget.name"
      role="alert"
      class="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700"
    >
      <span class="font-semibold">Over budget:</span>
      {{ budget.category }} is at {{ formatMoney(budget.spent) }} of {{ formatMoney(budget.amount) }}
      ({{ formatMoney(budget.spent - budget.amount) }} over).
    </div>

    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatCard
        label="Total spent"
        :value="formatMoney(grandTotal)"
        :hint="period === 'week' ? 'this week' : 'this month'"
      />
      <StatCard
        label="Remaining budget"
        :value="formatMoney(budgetTotal - budgetSpent)"
        :hint="`of ${formatMoney(budgetTotal)} this month`"
      />
      <StatCard
        label="Over budget"
        :value="overspent.length"
        :hint="`of ${(budgets.data || []).length} budgets`"
        :alert="overspent.length > 0"
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
          :max-slices="7"
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
      <div class="mb-3 flex items-center justify-between">
        <h2 class="text-sm font-semibold text-gray-700">Recent expenses</h2>
        <router-link to="/expenses" class="text-sm text-blue-600">View all</router-link>
      </div>
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

    <QuickAddExpense v-model="showQuickAdd" @added="refreshAll" />
  </div>
</template>
