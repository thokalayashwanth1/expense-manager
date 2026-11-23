<script setup>
import { computed, ref } from "vue";
import { Button, FormControl, createResource } from "frappe-ui";
import { createAction } from "../api";
import BudgetBar from "../components/BudgetBar.vue";
import SectionCard from "../components/SectionCard.vue";

const category = ref("");
const amount = ref("");

const categories = createResource({ url: "expense_manager.api.get_allowed_categories", auto: true });
const status = createResource({ url: "expense_manager.api.get_budget_status", auto: true });

const saveBudget = createAction({
  success: "Budget saved",
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
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-xl font-semibold">Budgets</h1>

    <SectionCard title="Budget for this month">
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
    </SectionCard>

    <SectionCard
      title="This month"
      :loading="status.loading && !status.data"
      :empty-text="status.data && !status.data.length ? 'No budgets set for this month.' : ''"
    >
      <ul class="space-y-4">
        <li v-for="budget in status.data" :key="budget.name">
          <BudgetBar :budget="budget" />
        </li>
      </ul>
    </SectionCard>
  </div>
</template>
