<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { Button, FormControl, createListResource } from "frappe-ui";
import QuickAddExpense from "../components/QuickAddExpense.vue";
import { formatMoney } from "../format";

const showAdd = ref(false);
const categoryFilter = ref("");

const expenses = createListResource({
  doctype: "Expense",
  fields: ["name", "amount", "category", "description", "spent_by", "source", "expense_date", "creation"],
  orderBy: "creation desc",
  pageLength: 50,
  auto: true,
});

let timer;
onMounted(() => (timer = setInterval(() => expenses.reload(), 10000)));
onUnmounted(() => clearInterval(timer));

const filterOptions = computed(() => {
  const names = [...new Set((expenses.data || []).map((expense) => expense.category))].sort();
  return [{ label: "All categories", value: "" }, ...names.map((name) => ({ label: name, value: name }))];
});

const visible = computed(() =>
  (expenses.data || []).filter((expense) => !categoryFilter.value || expense.category === categoryFilter.value),
);
const visibleTotal = computed(() => visible.value.reduce((sum, expense) => sum + expense.amount, 0));
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-xl font-semibold">Expenses</h1>
        <p class="text-sm text-gray-600">
          {{ visible.length }} shown · {{ formatMoney(visibleTotal) }} · refreshes every 10 seconds
        </p>
      </div>
      <div class="flex items-center gap-2">
        <FormControl v-model="categoryFilter" type="select" :options="filterOptions" />
        <Button variant="solid" @click="showAdd = true">+ Add expense</Button>
      </div>
    </div>

    <section class="rounded-lg border p-4">
      <p v-if="expenses.data && !visible.length" class="text-sm text-gray-500">No expenses found.</p>
      <ul class="divide-y">
        <li v-for="expense in visible" :key="expense.name" class="flex items-center justify-between py-3 text-sm">
          <div>
            <p class="font-medium">{{ expense.description || expense.category }}</p>
            <p class="text-xs text-gray-500">
              {{ expense.category }} · {{ expense.spent_by }} · {{ expense.creation.slice(0, 16) }}
              <span
                class="ml-1 rounded px-1.5 py-0.5"
                :class="expense.source === 'Telegram' ? 'bg-blue-50 text-blue-700' : 'bg-gray-100 text-gray-600'"
              >
                {{ expense.source }}
              </span>
            </p>
          </div>
          <span class="font-medium">{{ formatMoney(expense.amount) }}</span>
        </li>
      </ul>
    </section>

    <QuickAddExpense v-model="showAdd" @added="expenses.reload()" />
  </div>
</template>
