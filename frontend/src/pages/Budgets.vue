<script setup>
import { computed, ref } from "vue";
import { Button, FormControl, createListResource, createResource } from "frappe-ui";
import { formatMoney } from "../format";

const newCategory = ref("");
const category = ref("");
const amount = ref("");

const categories = createListResource({
  doctype: "Expense Category",
  fields: ["name"],
  orderBy: "name asc",
  pageLength: 100,
  auto: true,
});

const status = createResource({ url: "expense_manager.api.get_budget_status", auto: true });

const saveBudget = createResource({
  url: "expense_manager.api.set_budget",
  onSuccess: () => {
    amount.value = "";
    status.reload();
  },
});

const categoryOptions = computed(() =>
  (categories.data || []).map((row) => ({ label: row.name, value: row.name })),
);

const addCategory = () =>
  categories.insert.submit(
    { category_name: newCategory.value },
    { onSuccess: () => (newCategory.value = "") },
  );

const submitBudget = () =>
  saveBudget.submit({ category: category.value, amount: amount.value });

const percentUsed = (budget) => Math.min((budget.spent / budget.amount) * 100, 100);
</script>

<template>
  <div class="space-y-6">
    <div class="grid gap-4 md:grid-cols-2">
      <section class="space-y-3 rounded-lg border p-4">
        <h2 class="text-sm font-semibold text-gray-700">Add category</h2>
        <FormControl v-model="newCategory" type="text" placeholder="e.g. Groceries" />
        <Button
          variant="solid"
          :disabled="!newCategory"
          :loading="categories.insert.loading"
          @click="addCategory"
        >
          Add category
        </Button>
      </section>
      <section class="space-y-3 rounded-lg border p-4">
        <h2 class="text-sm font-semibold text-gray-700">Budget for this month</h2>
        <FormControl v-model="category" type="select" :options="categoryOptions" placeholder="Category" />
        <FormControl v-model="amount" type="number" placeholder="Amount" />
        <Button
          variant="solid"
          :disabled="!category || !amount"
          :loading="saveBudget.loading"
          @click="submitBudget"
        >
          Save budget
        </Button>
      </section>
    </div>

    <section class="rounded-lg border p-4">
      <h2 class="mb-3 text-sm font-semibold text-gray-700">This month</h2>
      <p v-if="status.data && !status.data.length" class="text-sm text-gray-500">
        No budgets set for this month.
      </p>
      <ul class="space-y-4">
        <li v-for="budget in status.data" :key="budget.name">
          <div class="flex justify-between text-sm">
            <span>{{ budget.category }}</span>
            <span :class="budget.spent > budget.amount ? 'font-medium text-red-600' : ''">
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
