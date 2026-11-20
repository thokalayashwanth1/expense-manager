<script setup>
import { createResource } from "frappe-ui";
import { formatMoney } from "../format";

const props = defineProps({ profile: { type: Object, required: true } });

const balance = createResource({
  url: "expense_manager.expense_manager.doctype.dependent.dependent.get_pocket_money_balance",
  params: { dependent: props.profile.dependent },
  auto: true,
});
</script>

<template>
  <div class="mx-auto max-w-md p-6">
    <p class="text-sm text-gray-600">Hi {{ profile.full_name }}, you have left</p>
    <p class="mt-1 text-4xl font-semibold">{{ formatMoney(balance.data?.balance) }}</p>
    <p class="mt-2 text-sm text-gray-600">
      Allocated {{ formatMoney(balance.data?.allocated) }} · Spent {{ formatMoney(balance.data?.spent) }}
    </p>
  </div>
</template>
