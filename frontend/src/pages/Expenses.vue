<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { Button, FormControl, createListResource, createResource } from "frappe-ui";
import QuickAddExpense from "../components/QuickAddExpense.vue";
import { categoryIcon, categoryTone } from "../categoryIcons";
import { dayLabel, formatDate, formatRupees } from "../format";

const showAdd = ref(false);
const categoryFilter = ref("");
const search = ref("");

// Needed only to show "by Paras" on expenses added by someone else.
const profile = createResource({ url: "expense_manager.api.get_profile", auto: true });
const me = computed(() => profile.data?.user);

const expenses = createListResource({
  doctype: "Expense",
  fields: ["name", "amount", "category", "description", "spent_by", "source", "expense_date", "creation"],
  orderBy: "expense_date desc, creation desc",
  pageLength: 100,
  auto: true,
});

let timer;
onMounted(() => (timer = setInterval(() => expenses.reload(), 10000)));
onUnmounted(() => clearInterval(timer));

const personName = (user = "") => {
  const name = user.split("@")[0];
  return name.charAt(0).toUpperCase() + name.slice(1);
};

const filterOptions = computed(() => {
  const names = [...new Set((expenses.data || []).map((expense) => expense.category))].sort();
  return [
    { label: "All categories", value: "" },
    ...names.map((name) => ({ label: `${categoryIcon(name)} ${name}`, value: name })),
  ];
});

const visible = computed(() => {
  const term = search.value.trim().toLowerCase();
  return (expenses.data || []).filter((expense) => {
    if (categoryFilter.value && expense.category !== categoryFilter.value) return false;
    if (!term) return true;
    return [expense.description, expense.category, expense.spent_by].some((text) =>
      (text || "").toLowerCase().includes(term),
    );
  });
});

// One block per day, with that day's total. The list is already sorted newest first.
const groups = computed(() => {
  const byDate = new Map();
  for (const expense of visible.value) {
    if (!byDate.has(expense.expense_date)) {
      byDate.set(expense.expense_date, { date: expense.expense_date, total: 0, items: [] });
    }
    const group = byDate.get(expense.expense_date);
    group.items.push(expense);
    group.total += expense.amount;
  }
  return [...byDate.values()];
});

const visibleTotal = computed(() => visible.value.reduce((sum, expense) => sum + expense.amount, 0));
const average = computed(() => (visible.value.length ? visibleTotal.value / visible.value.length : 0));

const topCategory = computed(() => {
  const totals = {};
  for (const expense of visible.value) totals[expense.category] = (totals[expense.category] || 0) + expense.amount;
  const best = Object.entries(totals).sort((a, b) => b[1] - a[1])[0];
  return best ? { name: best[0], total: best[1] } : null;
});

const hasFilters = computed(() => search.value || categoryFilter.value);
const clearFilters = () => {
  search.value = "";
  categoryFilter.value = "";
};
</script>

<template>
  <div class="space-y-5">
    <!-- Header -->
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-xl font-semibold text-gray-900">Expenses</h1>
        <p class="flex items-center gap-1.5 text-sm text-gray-500">
          <span class="h-1.5 w-1.5 animate-pulse rounded-full bg-green-500"></span>
          Live · {{ expenses.data?.length || 0 }} expenses
        </p>
      </div>
      <Button variant="solid" @click="showAdd = true">+ New expense</Button>
    </div>

    <!-- Summary cards -->
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
      <div class="rounded-xl border bg-white p-4 shadow-sm">
        <p class="text-xs font-medium uppercase tracking-wide text-gray-500">Total shown</p>
        <p class="mt-1 text-2xl font-semibold tabular-nums text-gray-900">{{ formatRupees(visibleTotal) }}</p>
        <p class="text-xs text-gray-500">{{ visible.length }} expenses</p>
      </div>
      <div class="rounded-xl border bg-white p-4 shadow-sm">
        <p class="text-xs font-medium uppercase tracking-wide text-gray-500">Average expense</p>
        <p class="mt-1 text-2xl font-semibold tabular-nums text-gray-900">{{ formatRupees(Math.round(average)) }}</p>
        <p class="text-xs text-gray-500">per entry</p>
      </div>
      <div class="rounded-xl border bg-white p-4 shadow-sm">
        <p class="text-xs font-medium uppercase tracking-wide text-gray-500">Top category</p>
        <p v-if="topCategory" class="mt-1 text-2xl font-semibold text-gray-900">
          {{ categoryIcon(topCategory.name) }} {{ topCategory.name }}
        </p>
        <p v-else class="mt-1 text-2xl font-semibold text-gray-300">—</p>
        <p class="text-xs text-gray-500">{{ topCategory ? formatRupees(topCategory.total) : "No data yet" }}</p>
      </div>
    </div>

    <!-- Search + filter -->
    <div class="flex flex-wrap items-center gap-2">
      <div class="min-w-[200px] flex-1">
        <FormControl v-model="search" type="text" placeholder="🔍  Search description, category or person" />
      </div>
      <div class="w-full sm:w-56">
        <FormControl v-model="categoryFilter" type="select" :options="filterOptions" />
      </div>
      <Button v-if="hasFilters" variant="subtle" @click="clearFilters">Clear</Button>
    </div>

    <!-- List -->
    <section class="overflow-hidden rounded-xl border bg-white shadow-sm">
      <!-- Column headings (desktop) -->
      <div
        class="hidden grid-cols-[1fr_190px_130px] gap-4 border-b bg-gray-50 px-4 py-2.5 text-xs font-medium uppercase tracking-wide text-gray-500 md:grid"
      >
        <span>Description</span>
        <span>Category</span>
        <span class="text-right">Amount</span>
      </div>

      <!-- Loading skeleton -->
      <div v-if="expenses.loading && !expenses.data" class="divide-y">
        <div v-for="n in 6" :key="n" class="flex animate-pulse items-center gap-3 px-4 py-4">
          <div class="h-10 w-10 rounded-xl bg-gray-100"></div>
          <div class="flex-1 space-y-2">
            <div class="h-3 w-1/3 rounded bg-gray-100"></div>
            <div class="h-3 w-1/5 rounded bg-gray-100"></div>
          </div>
          <div class="h-3 w-16 rounded bg-gray-100"></div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-else-if="!visible.length" class="px-4 py-14 text-center">
        <p class="text-4xl">🧾</p>
        <p class="mt-2 font-medium text-gray-900">
          {{ hasFilters ? "No expenses match your search" : "No expenses yet" }}
        </p>
        <p class="mt-1 text-sm text-gray-500">
          {{ hasFilters ? "Try a different word or clear the filters." : "Add your first expense to get started." }}
        </p>
        <div class="mt-4">
          <Button v-if="hasFilters" variant="subtle" @click="clearFilters">Clear filters</Button>
          <Button v-else variant="solid" @click="showAdd = true">+ New expense</Button>
        </div>
      </div>

      <!-- Day groups -->
      <div v-else>
        <div v-for="group in groups" :key="group.date">
          <div class="flex items-center justify-between border-b bg-gray-50/70 px-4 py-1.5 text-xs">
            <span class="font-semibold text-gray-700">
              {{ dayLabel(group.date) }}
              <span class="ml-1 font-normal text-gray-400">{{ formatDate(group.date) }}</span>
            </span>
            <span class="font-medium tabular-nums text-gray-600">{{ formatRupees(group.total) }}</span>
          </div>

          <ul class="divide-y">
            <li
              v-for="expense in group.items"
              :key="expense.name"
              class="grid grid-cols-[1fr_auto] items-center gap-4 px-4 py-3 transition-colors hover:bg-gray-50 md:grid-cols-[1fr_190px_130px]"
            >
              <!-- Icon + description -->
              <div class="flex min-w-0 items-center gap-3">
                <span
                  class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-lg"
                  :class="categoryTone(expense.category)"
                >
                  {{ categoryIcon(expense.category) }}
                </span>
                <div class="min-w-0">
                  <p class="truncate text-sm font-medium text-gray-900">
                    {{ expense.description || expense.category }}
                  </p>
                  <p class="flex flex-wrap items-center gap-x-1.5 text-xs text-gray-500">
                    <span>{{ expense.source === "Telegram" ? "✈️ Telegram" : "✍️ Manual" }}</span>
                    <span v-if="expense.spent_by !== me">· by {{ personName(expense.spent_by) }}</span>
                    <!-- Category shown here only on phones -->
                    <span class="md:hidden">· {{ expense.category }}</span>
                  </p>
                </div>
              </div>

              <!-- Category chip (desktop) -->
              <div class="hidden md:block">
                <span
                  class="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium"
                  :class="categoryTone(expense.category)"
                >
                  {{ categoryIcon(expense.category) }} {{ expense.category }}
                </span>
              </div>

              <!-- Amount -->
              <span class="text-right text-sm font-semibold tabular-nums text-gray-900">
                {{ formatRupees(expense.amount) }}
              </span>
            </li>
          </ul>
        </div>
      </div>
    </section>

    <QuickAddExpense v-model="showAdd" @added="expenses.reload()" />
  </div>
</template>
