<script setup>
import { computed, reactive, ref } from "vue";
import { Button, FormControl, createListResource, createResource, dialog } from "frappe-ui";
import { createAction } from "../api";
import SectionCard from "../components/SectionCard.vue";
import TelegramLink from "../components/TelegramLink.vue";
import { formatMoney } from "../format";

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

const remaining = computed(() => balance.data?.balance ?? 0);
const overspent = computed(() => remaining.value < 0);
const percentUsed = computed(() => {
  const allocated = balance.data?.allocated || 0;
  return allocated ? Math.min(((allocated - remaining.value) / allocated) * 100, 100) : 0;
});
const categoryOptions = computed(() =>
  (categories.data || []).map((name) => ({ label: name, value: name })),
);

const submitExpense = () => addExpense.submit({ ...form });

const confirmRollOver = () =>
  dialog.confirm({
    title: `Move ${formatMoney(remaining.value)} to savings?`,
    message: "This uses up what is left of this month's pocket money.",
    confirmLabel: "Move to savings",
    onConfirm: () => rollOver.submit(),
  });
</script>

<template>
  <div class="mx-auto max-w-md space-y-6 p-6">
    <section>
      <p class="text-sm text-gray-600">Hi {{ profile.full_name }}</p>
      <p v-if="overspent" class="mt-1 text-4xl font-semibold text-red-600">
        Overspent by {{ formatMoney(-remaining) }}
      </p>
      <template v-else>
        <p class="mt-1 text-4xl font-semibold">{{ formatMoney(remaining) }}</p>
        <p class="text-sm text-gray-600">left this month</p>
      </template>

      <div class="mt-3 h-2 rounded bg-gray-100">
        <div
          class="h-2 rounded"
          :class="overspent ? 'bg-red-500' : 'bg-gray-900'"
          :style="{ width: `${percentUsed}%` }"
        />
      </div>
      <p class="mt-2 text-sm text-gray-600">
        Allocated {{ formatMoney(balance.data?.allocated) }} · Spent
        {{ formatMoney(balance.data?.spent) }} · Saved this month
        {{ formatMoney(balance.data?.saved) }}
      </p>
      <p class="mt-1 text-sm text-gray-600">
        Total savings: <span class="font-medium">{{ formatMoney(balance.data?.total_savings) }}</span>
      </p>
      <Button class="mt-3" variant="subtle" :disabled="!(remaining > 0)" @click="confirmRollOver">
        Roll over to savings
      </Button>
    </section>

    <SectionCard title="Add an expense">
      <div class="space-y-3">
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
      </div>
    </SectionCard>

    <SectionCard
      title="Recent expenses"
      :empty-text="expenses.data && !expenses.data.length ? 'Nothing spent yet.' : ''"
    >
      <ul class="divide-y">
        <li v-for="expense in expenses.data" :key="expense.name" class="flex justify-between py-2 text-sm">
          <span>{{ expense.category }}<span v-if="expense.description"> · {{ expense.description }}</span></span>
          <span class="font-medium">{{ formatMoney(expense.amount) }}</span>
        </li>
      </ul>
    </SectionCard>

    <TelegramLink />
  </div>
</template>
