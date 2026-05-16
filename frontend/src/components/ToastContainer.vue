<script setup lang="ts">
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()
</script>

<template>
  <Teleport to="body">
    <div class="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 items-end">
      <Transition
        v-for="t in toast.toasts"
        :key="t.id"
        appear
        enter-from-class="opacity-0 translate-y-2"
        enter-active-class="transition duration-200"
        leave-to-class="opacity-0 translate-y-2"
        leave-active-class="transition duration-200"
      >
        <div
          class="flex items-start gap-3 px-4 py-3 rounded-lg shadow-lg text-sm max-w-sm w-full"
          :class="{
            'bg-emerald-600 text-white': t.type === 'success',
            'bg-destructive text-destructive-foreground': t.type === 'error',
            'bg-card text-foreground border border-border': t.type === 'info',
          }"
        >
          <span class="flex-1">{{ t.message }}</span>
          <button class="opacity-70 hover:opacity-100 ml-2 flex-shrink-0" @click="toast.remove(t.id)">✕</button>
        </div>
      </Transition>
    </div>
  </Teleport>
</template>
