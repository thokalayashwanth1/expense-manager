<script setup>
import TelegramLink from "../components/TelegramLink.vue";
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-xl font-semibold">Telegram</h1>
    <TelegramLink />

    <section class="rounded-lg border p-4">
      <h2 class="mb-2 text-sm font-semibold text-gray-700">How to use the bot</h2>
      <ol class="list-decimal space-y-1 pl-5 text-sm text-gray-600">
        <li>Link your account with the code above.</li>
        <li>Send a voice note such as "I spent 200 on Zomato".</li>
        <li>To charge a dependent, say their name: "Kid2 spent 100 on snacks".</li>
        <li>The bot records the expense and replies with a summary and the budget or pocket money left.</li>
      </ol>
    </section>
  </div>
</template>
