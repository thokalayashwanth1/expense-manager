<script setup>
import { Button, createResource, dialog } from "frappe-ui";

const logout = createResource({
  url: "logout",
  onSuccess: () => (window.location.href = "/login"),
});

const confirmSignOut = () =>
  dialog.confirm({
    title: "Sign out?",
    message: "You will need to log in again to continue.",
    confirmLabel: "Sign out",
    onConfirm: () => logout.submit(),
  });
</script>

<template>
  <Button variant="subtle" :loading="logout.loading" @click="confirmSignOut">Sign out</Button>
</template>
