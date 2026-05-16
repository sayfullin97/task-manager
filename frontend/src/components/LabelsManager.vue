<script setup lang="ts">
import { ref, computed } from 'vue'
import { useBoardsStore } from '@/stores/boards'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Dialog, DialogScrollContent, DialogHeader, DialogTitle,
} from '@/components/ui/dialog'

const emit = defineEmits<{ close: [] }>()
const store = useBoardsStore()

const COLORS = [
  '#e05c5c', '#e0885c', '#c9a830', '#4a9e6e',
  '#4a7ec7', '#7c5cbf', '#bf5c9e', '#5cb8bf',
  '#7a5c3a', '#3a6b5c', '#3a4e7a', '#7a3a4e',
]

const editingId = ref<string | null>(null)
const editName = ref('')
const editColor = ref('')

const newName = ref('')
const newColor = ref(COLORS[0])
const adding = ref(false)
const saving = ref(false)

const boardId = computed(() => store.currentBoard!.id)
const labels = computed(() => store.currentBoard?.labels ?? [])

function startEdit(label: { id: string; name: string; color: string }) {
  editingId.value = label.id
  editName.value = label.name
  editColor.value = label.color
}

function cancelEdit() {
  editingId.value = null
}

async function saveEdit() {
  if (!editName.value.trim() || !editingId.value) return
  saving.value = true
  try {
    await store.updateBoardLabel(editingId.value, editName.value.trim(), editColor.value)
    editingId.value = null
  } finally {
    saving.value = false
  }
}

async function deleteLabel(labelId: string) {
  await store.deleteBoardLabel(labelId)
  if (editingId.value === labelId) editingId.value = null
}

async function addLabel() {
  if (!newName.value.trim()) return
  adding.value = true
  try {
    await store.createBoardLabel(boardId.value, newName.value.trim(), newColor.value)
    newName.value = ''
    newColor.value = COLORS[0]
  } finally {
    adding.value = false
  }
}
</script>

<template>
  <Dialog :open="true" @update:open="emit('close')">
    <DialogScrollContent class="max-w-md">
      <DialogHeader>
        <DialogTitle>Метки</DialogTitle>
      </DialogHeader>

      <div class="flex flex-col gap-3 pt-2">

        <!-- Existing labels -->
        <div v-if="labels.length" class="flex flex-col gap-1.5">
          <div
            v-for="label in labels"
            :key="label.id"
            class="rounded-lg border border-border overflow-hidden"
          >
            <!-- Edit mode -->
            <div v-if="editingId === label.id" class="p-2.5 flex flex-col gap-2">
              <div class="flex gap-2">
                <div
                  class="w-8 h-8 shrink-0 rounded-md border-2 border-border"
                  :style="{ background: editColor }"
                />
                <Input v-model="editName" class="flex-1" @keyup.enter="saveEdit" @keyup.esc="cancelEdit" />
              </div>
              <div class="flex flex-wrap gap-1">
                <button
                  v-for="c in COLORS"
                  :key="c"
                  :style="{ background: c }"
                  class="w-6 h-6 rounded-md border-2 transition-all hover:scale-110"
                  :class="editColor === c ? 'border-foreground scale-110' : 'border-transparent'"
                  @click="editColor = c"
                />
              </div>
              <div class="flex gap-2">
                <Button size="sm" :disabled="saving" @click="saveEdit">Сохранить</Button>
                <Button size="sm" variant="ghost" @click="cancelEdit">Отмена</Button>
              </div>
            </div>

            <!-- View mode -->
            <div v-else class="px-3 py-2 flex items-center gap-3">
              <div class="w-5 h-5 shrink-0 rounded" :style="{ background: label.color }" />
              <span class="flex-1 text-sm font-medium truncate">{{ label.name }}</span>
              <div class="flex gap-1 shrink-0">
                <Button variant="ghost" size="icon-sm" class="text-muted-foreground" @click="startEdit(label)">✎</Button>
                <Button variant="ghost" size="icon-sm" class="text-muted-foreground hover:text-destructive" @click="deleteLabel(label.id)">✕</Button>
              </div>
            </div>
          </div>
        </div>

        <p v-else class="text-sm text-muted-foreground text-center py-4">Нет меток. Создайте первую.</p>

        <!-- Add new label -->
        <div class="border border-border rounded-lg p-3 flex flex-col gap-2 bg-muted">
          <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Новая метка</p>
          <div class="flex gap-2">
            <div
              class="w-9 h-9 shrink-0 rounded-md border border-border"
              :style="{ background: newColor }"
            />
            <Input v-model="newName" placeholder="Название метки" @keyup.enter="addLabel" />
          </div>
          <div class="flex flex-wrap gap-1">
            <button
              v-for="c in COLORS"
              :key="c"
              :style="{ background: c }"
              class="w-6 h-6 rounded-md border-2 transition-all hover:scale-110"
              :class="newColor === c ? 'border-foreground scale-110' : 'border-transparent'"
              @click="newColor = c"
            />
          </div>
          <Button size="sm" :disabled="adding || !newName.trim()" @click="addLabel">
            {{ adding ? 'Создаю...' : '+ Добавить метку' }}
          </Button>
        </div>

      </div>
    </DialogScrollContent>
  </Dialog>
</template>
