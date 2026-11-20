<script setup>
import { reactive, ref } from "vue";
import { Button, FormControl, createResource } from "frappe-ui";
import { formatMoney } from "../format";

const form = reactive({ full_name: "", email: "", password: "" });
const allowances = reactive({});
const error = ref("");

const dependents = createResource({ url: "expense_manager.api.get_dependents", auto: true });

const addDependent = createResource({
  url: "expense_manager.api.add_dependent",
  onSuccess: () => {
    Object.assign(form, { full_name: "", email: "", password: "" });
    error.value = "";
    dependents.reload();
  },
  onError: (err) => (error.value = err.messages?.[0] || "Could not add the dependent"),
});

const setPocketMoney = createResource({
  url: "expense_manager.api.set_pocket_money",
  onSuccess: () => dependents.reload(),
});

const submitDependent = () => addDependent.submit({ ...form });

const submitAllowance = (dependent) =>
  setPocketMoney.submit({ dependent: dependent.name, amount: allowances[dependent.name] });
</script>

<template>
  <div class="space-y-6">
    <section class="space-y-3 rounded-lg border p-4">
      <h2 class="text-sm font-semibold text-gray-700">Add a dependent</h2>
      <div class="grid gap-3 md:grid-cols-3">
        <FormControl v-model="form.full_name" type="text" placeholder="Full name" />
        <FormControl v-model="form.email" type="email" placeholder="Email (their login)" autocomplete="off" />
        <FormControl v-model="form.password" type="password" placeholder="Password" autocomplete="new-password" />
      </div>
      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
      <Button
        variant="solid"
        :disabled="!form.full_name || !form.email || !form.password"
        :loading="addDependent.loading"
        @click="submitDependent"
      >
        Add dependent
      </Button>
    </section>

    <section class="rounded-lg border p-4">
      <h2 class="mb-3 text-sm font-semibold text-gray-700">Pocket money this month</h2>
      <p v-if="dependents.data && !dependents.data.length" class="text-sm text-gray-500">
        No dependents yet.
      </p>
      <ul class="divide-y">
        <li
          v-for="dependent in dependents.data"
          :key="dependent.name"
          class="flex flex-wrap items-center justify-between gap-3 py-3"
        >
          <div>
            <p class="font-medium">{{ dependent.dependent_name }}</p>
            <p class="text-sm text-gray-600">
              {{ formatMoney(dependent.balance) }} left of {{ formatMoney(dependent.allocated) }}
              · spent {{ formatMoney(dependent.spent) }}
            </p>
          </div>
          <div class="flex items-center gap-2">
            <FormControl v-model="allowances[dependent.name]" type="number" placeholder="Amount" />
            <Button
              variant="subtle"
              :disabled="!allowances[dependent.name]"
              :loading="setPocketMoney.loading"
              @click="submitAllowance(dependent)"
            >
              Set
            </Button>
          </div>
        </li>
      </ul>
    </section>
  </div>
</template>
