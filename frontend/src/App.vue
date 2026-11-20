<script setup>
import { Button, createResource } from "frappe-ui";

const user = createResource({ url: "frappe.auth.get_logged_user", auto: true });
</script>

<template>
  <div class="p-6">
    <h1 class="text-xl font-semibold">Expense Manager</h1>
    <p class="mt-2 text-gray-700">Signed in as {{ user.data }}</p>
    <Button class="mt-4" variant="solid" @click="user.reload()">Reload</Button>
  </div>
</template>