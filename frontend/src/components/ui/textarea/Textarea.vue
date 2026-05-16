<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { useVModel } from '@vueuse/core'
import { cn } from '@/lib/utils'

const props = defineProps<{
  class?: HTMLAttributes['class']
  defaultValue?: string | number
  modelValue?: string | number
}>()

const emits = defineEmits<{
  (e: 'update:modelValue', payload: string | number): void
}>()

const modelValue = useVModel(props, 'modelValue', emits, {
  passive: true,
  defaultValue: props.defaultValue,
})
</script>

<template>
  <textarea
    v-model="modelValue"
    data-slot="textarea"
    :class="cn('border-input focus-visible:border-ring focus-visible:ring-ring focus-visible:ring-1 aria-invalid:ring-destructive aria-invalid:border-destructive resize-none rounded-md border px-3 py-2 text-sm transition-colors focus-visible:ring-2 aria-invalid:ring-2 flex field-sizing-content min-h-20 w-full outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50', props.class)"
  />
</template>
