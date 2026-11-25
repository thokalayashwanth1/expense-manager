<script setup>
import { computed, ref } from "vue";
import { Button, createListResource, createResource } from "frappe-ui";
import { BarChart, DonutChart } from "frappe-ui/charts";
import BudgetBar from "../components/BudgetBar.vue";
import QuickAddExpense from "../components/QuickAddExpense.vue";
import StatCard from "../components/StatCard.vue";
import { categoryIcon, categoryTone } from "../categoryIcons";
import { formatDate, formatRupees, totalsBy } from "../format";

const periods = [
  { value: "week", label: "This week" },
  { value: "month", label: "This month" },
];
const period = ref("month");
const showQuickAdd = ref(false);

const profile = createResource({ url: "expense_manager.api.get_profile", auto: true });
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
  orderBy: "expense_date desc, creation desc",
  pageLength: 6,
  auto: true,
});

// ---- greeting ----
const greeting = computed(() => {
  const hour = new Date().getHours();
  return hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";
});
const firstName = computed(() => (profile.data?.full_name || "").split(" ")[0]);
const today = new Date().toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long" });

// ---- numbers ----
const rows = computed(() => report.data || []);
const grandTotal = computed(() => rows.value.reduce((sum, row) => sum + row.total, 0));

const sumOf = (items, key) => (items || []).reduce((sum, item) => sum + item[key], 0);
const budgetTotal = computed(() => sumOf(budgets.data, "amount"));
const budgetSpent = computed(() => sumOf(budgets.data, "spent"));
const budgetPercent = computed(() => (budgetTotal.value ? (budgetSpent.value / budgetTotal.value) * 100 : 0));
const overspent = computed(() => (budgets.data || []).filter((budget) => budget.spent > budget.amount));

const byCategory = computed(() => totalsBy(rows.value, "category"));
const byPerson = computed(() => totalsBy(rows.value, "spent_by"));

const topCategories = computed(() =>
  byCategory.value.slice(0, 6).map((row) => ({
    ...row,
    share: grandTotal.value ? (row.total / grandTotal.value) * 100 : 0,
  })),
);

// Most-used budgets first, so the ones in trouble are on top.
const budgetsByUsage = computed(() =>
  [...(budgets.data || [])]
    .sort((a, b) => b.spent / b.amount - a.spent / a.amount)
    .slice(0, 5),
);

const personName = (user = "") => {
  const name = user.split("@")[0];
  return name.charAt(0).toUpperCase() + name.slice(1);
};

const pocketPercent = (dependent) =>
  dependent.allocated ? Math.min((dependent.spent / dependent.allocated) * 100, 100) : 0;

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
    <!-- Header -->
    <div class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">
          {{ greeting }}<span v-if="firstName">, {{ firstName }}</span> 👋
        </h1>
        <p class="text-sm text-gray-500">{{ today }} · here's where your money went</p>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <div class="inline-flex rounded-lg bg-gray-100 p-1">
          <button
            v-for="option in periods"
            :key="option.value"
            class="rounded-md px-3 py-1.5 text-sm font-medium transition"
            :class="period === option.value ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
            @click="selectPeriod(option.value)"
          >
            {{ option.label }}
          </button>
        </div>
        <Button variant="solid" @click="showQuickAdd = true">+ New expense</Button>
      </div>
    </div>

    <!-- Over budget alert -->
    <div v-if="overspent.length" role="alert" class="rounded-xl border border-red-200 bg-red-50 p-4">
      <p class="text-sm font-semibold text-red-800">
        ⚠️ {{ overspent.length }} {{ overspent.length === 1 ? "budget is" : "budgets are" }} over the limit
      </p>
      <ul class="mt-2 space-y-1 text-sm text-red-700">
        <li v-for="budget in overspent" :key="budget.name">
          {{ categoryIcon(budget.category) }} {{ budget.category }}:
          {{ formatRupees(budget.spent) }} of {{ formatRupees(budget.amount) }}
          (<span class="font-semibold">{{ formatRupees(budget.spent - budget.amount) }} over</span>)
        </li>
      </ul>
    </div>

    <!-- Stat cards -->
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatCard
        label="Total spent"
        icon="💸"
        tone="blue"
        :value="formatRupees(grandTotal)"
        :hint="period === 'week' ? 'this week' : 'this month'"
        :loading="report.loading && !report.data"
      />
      <StatCard
        label="Remaining budget"
        icon="🎯"
        tone="green"
        :value="formatRupees(budgetTotal - budgetSpent)"
        :hint="`${Math.round(budgetPercent)}% of ${formatRupees(budgetTotal)} used`"
        :progress="budgetTotal ? budgetPercent : null"
        :loading="budgets.loading && !budgets.data"
      />
      <StatCard
        label="Over budget"
        :icon="overspent.length ? '⚠️' : '✅'"
        :tone="overspent.length ? 'red' : 'green'"
        :value="overspent.length"
        :hint="`of ${(budgets.data || []).length} budgets`"
        :alert="overspent.length > 0"
        :loading="budgets.loading && !budgets.data"
      />
      <StatCard
        label="Dependents"
        icon="👨‍👩‍👧"
        tone="purple"
        :value="(dependents.data || []).length"
        hint="on your plan"
        :loading="dependents.loading && !dependents.data"
      />
    </div>

    <!-- Category donut + top categories -->
    <div class="grid gap-4 lg:grid-cols-2">
      <div class="h-80 rounded-xl border bg-white p-4 shadow-sm">
        <DonutChart
          title="By category"
          :data="byCategory"
          category="label"
          value="total"
          :max-slices="7"
          :format="formatRupees"
          :loading="report.loading"
        />
      </div>

      <section class="h-80 overflow-y-auto rounded-xl border bg-white p-4 shadow-sm">
        <h2 class="mb-3 text-sm font-semibold text-gray-700">Top categories</h2>
        <p v-if="report.data && !topCategories.length" class="py-10 text-center text-sm text-gray-500">
          Nothing spent {{ period === "week" ? "this week" : "this month" }} yet.
        </p>
        <ul class="space-y-3">
          <li v-for="row in topCategories" :key="row.label" class="flex items-center gap-3">
            <span
              class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-base"
              :class="categoryTone(row.label)"
            >
              {{ categoryIcon(row.label) }}
            </span>
            <div class="min-w-0 flex-1">
              <div class="flex items-baseline justify-between gap-2 text-sm">
                <span class="truncate font-medium text-gray-900">{{ row.label }}</span>
                <span class="shrink-0 tabular-nums text-gray-900">{{ formatRupees(row.total) }}</span>
              </div>
              <div class="mt-1 flex items-center gap-2">
                <div class="h-1.5 flex-1 overflow-hidden rounded-full bg-gray-100">
                  <div class="h-1.5 rounded-full bg-gray-900" :style="{ width: `${row.share}%` }" />
                </div>
                <span class="w-9 text-right text-xs tabular-nums text-gray-500">{{ Math.round(row.share) }}%</span>
              </div>
            </div>
          </li>
        </ul>
      </section>
    </div>

    <!-- By person + budgets -->
    <div class="grid gap-4 lg:grid-cols-2">
      <div class="h-80 rounded-xl border bg-white p-4 shadow-sm">
        <BarChart
          title="By person"
          :data="byPerson"
          x="label"
          y="total"
          horizontal
          :y-axis="{ format: formatRupees }"
          :loading="report.loading"
        />
      </div>

      <section class="h-80 overflow-y-auto rounded-xl border bg-white p-4 shadow-sm">
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-sm font-semibold text-gray-700">Budgets this month</h2>
          <router-link to="/budgets" class="text-sm text-blue-600 hover:underline">Manage</router-link>
        </div>
        <div v-if="budgets.data && !budgetsByUsage.length" class="py-10 text-center">
          <p class="text-3xl">🎯</p>
          <p class="mt-2 text-sm text-gray-500">No budgets set yet.</p>
          <router-link to="/budgets" class="text-sm text-blue-600 hover:underline">Set your first budget</router-link>
        </div>
        <ul class="space-y-4">
          <li v-for="budget in budgetsByUsage" :key="budget.name"><BudgetBar :budget="budget" /></li>
        </ul>
      </section>
    </div>

    <!-- Pocket money (only when you have dependents) -->
    <section v-if="(dependents.data || []).length">
      <div class="mb-3 flex items-center justify-between">
        <h2 class="text-sm font-semibold text-gray-700">Pocket money this month</h2>
        <router-link to="/dependents" class="text-sm text-blue-600 hover:underline">Manage</router-link>
      </div>
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div v-for="dependent in dependents.data" :key="dependent.name" class="rounded-xl border bg-white p-4 shadow-sm">
          <div class="flex items-center gap-3">
            <span
              class="flex h-10 w-10 items-center justify-center rounded-full bg-purple-50 text-sm font-semibold text-purple-700"
            >
              {{ dependent.dependent_name.charAt(0).toUpperCase() }}
            </span>
            <div class="min-w-0 flex-1">
              <p class="truncate text-sm font-medium text-gray-900">{{ dependent.dependent_name }}</p>
              <p class="text-xs text-gray-500">
                {{ dependent.allocated ? `${formatRupees(dependent.allocated)} allocated` : "No pocket money set" }}
              </p>
            </div>
            <div class="text-right">
              <p
                class="text-lg font-semibold tabular-nums"
                :class="dependent.balance < 0 ? 'text-red-600' : 'text-gray-900'"
              >
                {{ formatRupees(dependent.balance) }}
              </p>
              <p class="text-xs text-gray-500">left</p>
            </div>
          </div>
          <div class="mt-3 h-1.5 overflow-hidden rounded-full bg-gray-100">
            <div
              class="h-1.5 rounded-full"
              :class="pocketPercent(dependent) >= 100 ? 'bg-red-500' : pocketPercent(dependent) >= 80 ? 'bg-orange-500' : 'bg-green-500'"
              :style="{ width: `${pocketPercent(dependent)}%` }"
            />
          </div>
          <p class="mt-1.5 text-xs text-gray-500">
            Spent {{ formatRupees(dependent.spent) }} · Saved {{ formatRupees(dependent.total_savings) }} in total
          </p>
        </div>
      </div>
    </section>

    <!-- Recent expenses -->
    <section class="overflow-hidden rounded-xl border bg-white shadow-sm">
      <div class="flex items-center justify-between border-b px-4 py-3">
        <h2 class="text-sm font-semibold text-gray-700">Recent expenses</h2>
        <router-link to="/expenses" class="text-sm text-blue-600 hover:underline">View all →</router-link>
      </div>
      <div v-if="recent.data && !recent.data.length" class="px-4 py-10 text-center">
        <p class="text-3xl">🧾</p>
        <p class="mt-2 text-sm text-gray-500">No expenses yet. Add one with the button above.</p>
      </div>
      <ul class="divide-y">
        <li
          v-for="expense in recent.data"
          :key="expense.name"
          class="flex items-center gap-3 px-4 py-3 transition-colors hover:bg-gray-50"
        >
          <span
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-lg"
            :class="categoryTone(expense.category)"
          >
            {{ categoryIcon(expense.category) }}
          </span>
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-medium text-gray-900">{{ expense.description || expense.category }}</p>
            <p class="text-xs text-gray-500">
              {{ expense.category }} · {{ personName(expense.spent_by) }} · {{ formatDate(expense.expense_date) }}
            </p>
          </div>
          <span class="text-sm font-semibold tabular-nums text-gray-900">{{ formatRupees(expense.amount) }}</span>
        </li>
      </ul>
    </section>

    <QuickAddExpense v-model="showQuickAdd" @added="refreshAll" />
  </div>
</template>
