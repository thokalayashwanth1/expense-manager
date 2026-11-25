<script setup>
import { computed } from "vue";

const props = defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  hint: { type: String, default: "" },
  alert: { type: Boolean, default: false },
  icon: { type: String, default: "" },
  tone: { type: String, default: "gray" },
  progress: { type: Number, default: null }, // 0-100, shows a bar when given
  loading: { type: Boolean, default: false },
});

// Full class names so Tailwind keeps them.
const tiles = {
  gray: "bg-gray-100",
  blue: "bg-blue-50",
  green: "bg-green-50",
  red: "bg-red-50",
  purple: "bg-purple-50",
  orange: "bg-orange-50",
};

const barColor = computed(() =>
  props.progress >= 100 ? "bg-red-500" : props.progress >= 80 ? "bg-orange-500" : "bg-green-500",
);
</script>

<template>
  <div class="rounded-xl border bg-white p-4 shadow-sm transition-shadow hover:shadow-md">
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0">
        <p class="text-xs font-medium uppercase tracking-wide text-gray-500">{{ label }}</p>
        <div v-if="loading" class="mt-2 h-7 w-28 animate-pulse rounded bg-gray-100"></div>
        <p
          v-else
          class="mt-1 truncate text-2xl font-semibold tabular-nums"
          :class="alert ? 'text-red-600' : 'text-gray-900'"
        >
          {{ value }}
        </p>
      </div>
      <span
        v-if="icon"
        class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-lg"
        :class="tiles[tone] || tiles.gray"
      >
        {{ icon }}
      </span>
    </div>

    <div v-if="progress !== null && !loading" class="mt-3 h-1.5 overflow-hidden rounded-full bg-gray-100">
      <div class="h-1.5 rounded-full transition-all" :class="barColor" :style="{ width: `${Math.min(progress, 100)}%` }" />
    </div>
    <p v-if="hint" class="mt-2 text-xs text-gray-500">{{ hint }}</p>
  </div>
</template>
