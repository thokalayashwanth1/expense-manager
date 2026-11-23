<script setup>
import { computed, reactive, ref } from "vue";
import { Button, FormControl, createListResource, createResource } from "frappe-ui";
import { createAction } from "../api";
import { formatMoney } from "../format";
import TelegramLink from "../components/TelegramLink.vue";

const props = defineProps({ profile: { type: Object, required: true } });
const form = reactive({ category: "", amount: "", description: "" });
const error = ref("");

const balance = createResource({
  url: "expense_manager.expense_manager.doctype.dependent.dependent.get_pocket_money_balance",
  params: { dependent: props.profile.dependent },
  auto: true,
});

const categories = createResource({ url: "expense_manager.api.get_allowed_categories", auto: true });

const expenses = createListResource({
  doctype: "Expense",
  fields: ["name", "amount", "category", "description", "expense_date"],
  orderBy: "creation desc",
  pageLength: 10,
  auto: true,
});

const refresh = () => {
  balance.reload();
  expenses.reload();
};

const addExpense = createAction({
  success: "Expense added",
  url: "expense_manager.api.add_expense",
  onSuccess: () => {
    Object.assign(form, { category: "", amount: "", description: "" });
    error.value = "";
    refresh();
  },
  onError: (err) => (error.value = err.messages?.[0] || "Could not add the expense"),
});

const rollOver = createAction({
  success: "Moved to savings",
  url: "expense_manager.expense_manager.doctype.dependent.dependent.roll_over_to_savings",
  params: { dependent: props.profile.dependent },
  onSuccess: refresh,
});

const categoryOptions = computed(() =>
  (categories.data || []).map((name) => ({ label: name, value: name })),
);
const submitExpense = () => addExpense.submit({ ...form });
</script>

<template>
  <div class="mx-auto max-w-md space-y-6 p-6">
    <section>
      <p class="text-sm text-gray-600">Hi {{ profile.full_name }}, you have left</p>
      <p class="mt-1 text-4xl font-semibold">{{ formatMoney(balance.data?.balance) }}</p>
      <p class="mt-2 text-sm text-gray-600">
        Allocated {{ formatMoney(balance.data?.allocated) }} · Spent
        {{ formatMoney(balance.data?.spent) }}
      </p>
      <p class="mt-1 text-sm text-gray-600">
        Savings: {{ formatMoney(balance.data?.total_savings) }}
      </p>
      <Button
        class="mt-3"
        variant="subtle"
        :disabled="!(balance.data?.balance > 0)"
        :loading="rollOver.loading"
        @click="rollOver.submit()"
      >
        Roll over to savings
      </Button>
    </section>

    <section class="space-y-3 rounded-lg border p-4">
      <h2 class="text-sm font-semibold text-gray-700">Add an expense</h2>
      <FormControl v-model="form.category" type="select" :options="categoryOptions" placeholder="Category" />
      <FormControl v-model="form.amount" type="number" placeholder="Amount" />
      <FormControl v-model="form.description" type="text" placeholder="What was it for?" />
      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
      <Button
        variant="solid"
        :disabled="!form.category || !form.amount"
        :loading="addExpense.loading"
        @click="submitExpense"
      >
        Add expense
      </Button>
    </section>

    <section class="rounded-lg border p-4">
      <h2 class="mb-3 text-sm font-semibold text-gray-700">Recent expenses</h2>
      <p v-if="expenses.data && !expenses.data.length" class="text-sm text-gray-500">
        Nothing spent yet.
      </p>
      <ul class="divide-y">
        <li v-for="expense in expenses.data" :key="expense.name" class="flex justify-between py-2 text-sm">
          <span>{{ expense.category }}<span v-if="expense.description"> · {{ expense.description }}</span></span>
          <span class="font-medium">{{ formatMoney(expense.amount) }}</span>
        </li>
      </ul>
    </section>

    <TelegramLink />
  </div>
</template>
