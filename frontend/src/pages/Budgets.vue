<script setup>
import { computed, ref } from "vue";
import { Button, FormControl, createResource } from "frappe-ui";
import { formatMoney } from "../format";

const category = ref("");
const amount = ref("");

const categories = createResource({ url: "expense_manager.api.get_allowed_categories", auto: true });
const status = createResource({ url: "expense_manager.api.get_budget_status", auto: true });

const saveBudget = createResource({
  url: "expense_manager.api.set_budget",
  onSuccess: () => {
    amount.value = "";
    status.reload();
  },
});

const categoryOptions = computed(() =>
  (categories.data || []).map((name) => ({ label: name, value: name })),
);
const submitBudget = () => saveBudget.submit({ category: category.value, amount: amount.value });
const percentUsed = (budget) => Math.min((budget.spent / budget.amount) * 100, 100);
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-xl font-semibold">Budgets</h1>

    <section class="space-y-3 rounded-lg border p-4">
      <h2 class="text-sm font-semibold text-gray-700">Budget for this month</h2>
      <div class="grid gap-3 md:grid-cols-3">
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
      </div>
    </section>

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
