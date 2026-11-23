<script setup>
import { Button, createResource } from "frappe-ui";

const logout = createResource({
  url: "logout",
  onSuccess: () => (window.location.href = "/login"),
});
</script>

<template>
  <Button variant="subtle" :loading="logout.loading" @click="logout.submit()">Sign out</Button>
</template>
