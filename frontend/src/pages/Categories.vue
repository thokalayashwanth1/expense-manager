<script setup>
import { computed, ref } from "vue";
import { Button, FormControl, createListResource, createResource } from "frappe-ui";
import { createAction } from "../api";

const newCategory = ref("");

const categories = createListResource({
  doctype: "Expense Category",
  fields: ["name", "enabled"],
  orderBy: "name asc",
  pageLength: 100,
  auto: true,
});

const setEnabled = createAction({
  success: "Category updated",
  url: "expense_manager.api.set_category_enabled",
  onSuccess: () => categories.reload(),
});

const active = computed(() => (categories.data || []).filter((row) => row.enabled));
const archived = computed(() => (categories.data || []).filter((row) => !row.enabled));

const addCategory = () =>
  categories.insert.submit(
    { category_name: newCategory.value, enabled: 1 },
    { onSuccess: () => (newCategory.value = "") },
  );
const toggle = (row, enabled) => setEnabled.submit({ category: row.name, enabled });
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-xl font-semibold">Categories</h1>

    <section class="space-y-3 rounded-lg border p-4">
      <h2 class="text-sm font-semibold text-gray-700">Add category</h2>
      <div class="flex gap-2">
        <FormControl v-model="newCategory" type="text" placeholder="e.g. Groceries" />
        <Button
          variant="solid"
          :disabled="!newCategory"
          :loading="categories.insert.loading"
          @click="addCategory"
        >
          Add
        </Button>
      </div>
      <p v-if="categories.insert.error" class="text-sm text-red-600">
        Could not add the category. If it already exists, restore it from the archived list.
      </p>
    </section>

    <section class="rounded-lg border p-4">
      <h2 class="mb-3 text-sm font-semibold text-gray-700">Active</h2>
      <p v-if="categories.data && !active.length" class="text-sm text-gray-500">No active categories.</p>
      <ul class="divide-y">
        <li v-for="row in active" :key="row.name" class="flex items-center justify-between py-2 text-sm">
          <span>{{ row.name }}</span>
          <Button variant="subtle" theme="red" :loading="setEnabled.loading" @click="toggle(row, 0)">
            Archive
          </Button>
        </li>
      </ul>
    </section>

    <section v-if="archived.length" class="rounded-lg border p-4">
      <h2 class="mb-3 text-sm font-semibold text-gray-700">Archived</h2>
      <ul class="divide-y">
        <li v-for="row in archived" :key="row.name" class="flex items-center justify-between py-2 text-sm">
          <span class="text-gray-500">{{ row.name }}</span>
          <Button variant="subtle" :loading="setEnabled.loading" @click="toggle(row, 1)">Restore</Button>
        </li>
      </ul>
    </section>
  </div>
</template>
