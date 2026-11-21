<script setup>
import { computed, reactive, ref } from "vue";
import { Button, FormControl, createListResource, createResource } from "frappe-ui";

const show = defineModel({ type: Boolean, default: false });
const emit = defineEmits(["added"]);

const form = reactive({ category: "", amount: "", description: "" });
const error = ref("");

const categories = createListResource({
  doctype: "Expense Category",
  fields: ["name"],
  orderBy: "name asc",
  pageLength: 100,
  auto: true,
});

const addExpense = createResource({
  url: "expense_manager.api.add_expense",
  onSuccess: () => {
    Object.assign(form, { category: "", amount: "", description: "" });
    error.value = "";
    show.value = false;
    emit("added");
  },
  onError: (err) => (error.value = err.messages?.[0] || "Could not add the expense"),
});

const categoryOptions = computed(() =>
  (categories.data || []).map((row) => ({ label: row.name, value: row.name })),
);
const submit = () => addExpense.submit({ ...form });
</script>

<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
    @click.self="show = false"
  >
    <div class="w-full max-w-sm space-y-3 rounded-lg bg-white p-5 shadow-xl">
      <h2 class="text-lg font-semibold">Quick add expense</h2>
      <FormControl v-model="form.category" type="select" :options="categoryOptions" placeholder="Category" />
      <FormControl v-model="form.amount" type="number" placeholder="Amount" />
      <FormControl v-model="form.description" type="text" placeholder="What was it for?" />
      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
      <div class="flex justify-end gap-2">
        <Button variant="subtle" @click="show = false">Cancel</Button>
        <Button
          variant="solid"
          :disabled="!form.category || !form.amount"
          :loading="addExpense.loading"
          @click="submit"
        >
          Add expense
        </Button>
      </div>
    </div>
  </div>
</template>
