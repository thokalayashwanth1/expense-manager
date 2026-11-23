<script setup>
import { computed, onUnmounted, ref, watch } from "vue";
import { Button, createResource } from "frappe-ui";
import { createAction } from "../api";

const code = ref("");
const secondsLeft = ref(0);
let timer;

const status = createResource({ url: "expense_manager.api.get_telegram_status", auto: true });

const stopCountdown = () => {
  clearInterval(timer);
  secondsLeft.value = 0;
  code.value = "";
};

const generate = createAction({
  url: "expense_manager.api.generate_link_code",
  onSuccess: (data) => {
    clearInterval(timer);
    code.value = data.code;
    secondsLeft.value = data.expires_in;
    timer = setInterval(() => {
      secondsLeft.value -= 1;
      if (secondsLeft.value % 3 === 0) status.reload();
      if (secondsLeft.value <= 0) stopCountdown();
    }, 1000);
  },
});

const unlink = createAction({
  success: "Telegram unlinked",
  url: "expense_manager.api.unlink_telegram",
  onSuccess: () => status.reload(),
});

watch(
  () => status.data?.linked,
  (linked) => linked && stopCountdown(),
);
onUnmounted(() => clearInterval(timer));

const countdown = computed(
  () => `${Math.floor(secondsLeft.value / 60)}:${String(secondsLeft.value % 60).padStart(2, "0")}`,
);
const deepLink = computed(() => `https://t.me/${status.data?.bot}?start=${code.value}`);
</script>

<template>
  <section class="space-y-3 rounded-lg border p-4">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-sm font-semibold text-gray-700">Telegram account</h2>
        <p v-if="status.data" class="mt-1 text-sm" :class="status.data.linked ? 'text-green-700' : 'text-gray-600'">
          {{ status.data.linked ? "Your Telegram account is linked." : "No Telegram account is linked." }}
        </p>
      </div>
      <Button v-if="status.data?.linked" variant="subtle" theme="red" :loading="unlink.loading" @click="unlink.submit()">
        Unlink
      </Button>
    </div>

    <Button v-if="!status.data?.linked && !code" variant="solid" :loading="generate.loading" @click="generate.submit()">
      Generate link code
    </Button>

    <div v-if="code" class="space-y-3 rounded-md bg-gray-50 p-4">
      <p class="text-sm text-gray-600">Send this to <span class="font-medium">@{{ status.data?.bot }}</span> on Telegram:</p>
      <p class="font-mono text-3xl font-semibold tracking-widest">/link {{ code }}</p>
      <p class="text-sm text-gray-600">Expires in {{ countdown }}. It works once.</p>
      <div class="flex gap-2">
        <a :href="deepLink" target="_blank" rel="noopener">
          <Button variant="solid">Open in Telegram</Button>
        </a>
        <Button variant="subtle" :loading="generate.loading" @click="generate.submit()">New code</Button>
      </div>
    </div>
  </section>
</template>
