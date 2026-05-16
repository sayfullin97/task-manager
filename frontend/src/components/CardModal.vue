<script setup lang="ts">
import { ref, computed } from 'vue'
import { useBoardsStore } from '@/stores/boards'
import { cardsApi } from '@/api/cards'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'

const emit = defineEmits<{ close: [] }>()
const store = useBoardsStore()
const card = store.activeCard!

const title = ref(card.title)
const description = ref(card.description ?? '')
const newComment = ref('')
const savingTitle = ref(false)
const addingComment = ref(false)
const dueDate = ref(card.due_date ? card.due_date.slice(0, 10) : '')

const COVER_COLORS = [
  '#ef4444', '#f97316', '#eab308', '#22c55e',
  '#3b82f6', '#8b5cf6', '#ec4899', '#14b8a6',
]

// Sync labels/assignees/cover back to the kanban card brief
function syncBrief() {
  const col = store.currentBoard?.columns.find(c => c.id === card.column_id)
  const brief = col?.cards.find(c => c.id === card.id)
  if (!brief) return
  brief.labels = [...card.labels]
  brief.assignees = [...card.assignees]
  brief.due_date = card.due_date
  brief.cover_color = card.cover_color
}

async function saveTitle() {
  if (title.value === card.title) return
  savingTitle.value = true
  try {
    await cardsApi.update(card.id, { title: title.value })
    card.title = title.value
    const col = store.currentBoard?.columns.find(c => c.id === card.column_id)
    const brief = col?.cards.find(c => c.id === card.id)
    if (brief) brief.title = title.value
  } finally {
    savingTitle.value = false
  }
}

async function saveDescription() {
  await cardsApi.update(card.id, { description: description.value })
  card.description = description.value
}

async function saveDueDate() {
  await cardsApi.update(card.id, { due_date: dueDate.value })
  card.due_date = dueDate.value || null
  syncBrief()
}

async function setCoverColor(color: string | null) {
  await cardsApi.update(card.id, { cover_color: color ?? '' })
  card.cover_color = color
  syncBrief()
}

// Labels
const boardLabels = computed(() => store.currentBoard?.labels ?? [])
const cardLabelIds = computed(() => new Set(card.labels.map(l => l.id)))

async function toggleLabel(labelId: string) {
  if (cardLabelIds.value.has(labelId)) {
    await cardsApi.removeLabel(card.id, labelId)
    const idx = card.labels.findIndex(l => l.id === labelId)
    if (idx !== -1) card.labels.splice(idx, 1)
  } else {
    const { data } = await cardsApi.addLabel(card.id, labelId)
    card.labels = data.labels
  }
  syncBrief()
}

// Assignees
const boardMembers = computed(() => store.currentBoard?.members ?? [])
const cardAssigneeIds = computed(() => new Set(card.assignees.map(u => u.id)))

async function toggleAssignee(userId: string) {
  if (cardAssigneeIds.value.has(userId)) {
    await cardsApi.removeAssignee(card.id, userId)
    const idx = card.assignees.findIndex(u => u.id === userId)
    if (idx !== -1) card.assignees.splice(idx, 1)
  } else {
    const { data } = await cardsApi.addAssignee(card.id, userId)
    card.assignees = data.assignees
  }
  syncBrief()
}

// Comments
async function postComment() {
  if (!newComment.value.trim()) return
  addingComment.value = true
  try {
    const { data } = await cardsApi.addComment(card.id, newComment.value.trim())
    card.comments.push(data as any)
    newComment.value = ''
  } finally {
    addingComment.value = false
  }
}

async function deleteComment(commentId: string) {
  await cardsApi.deleteComment(commentId)
  const idx = card.comments.findIndex(c => c.id === commentId)
  if (idx !== -1) card.comments.splice(idx, 1)
}
</script>

<template>
  <div class="fixed inset-0 bg-black/50 flex items-start justify-center pt-16 z-50 px-4" @click.self="emit('close')">
    <div class="bg-card rounded-xl shadow-xl w-full max-w-2xl max-h-[80vh] overflow-y-auto">
      <!-- Cover -->
      <div v-if="card.cover_color" :style="{ background: card.cover_color }" class="h-32 rounded-t-xl" />

      <div class="p-6 space-y-6">
        <!-- Title -->
        <div class="flex items-start gap-3">
          <div class="flex-1">
            <input
              v-model="title"
              class="w-full text-xl font-bold bg-transparent border-none outline-none focus:bg-muted/50 rounded px-1 -mx-1"
              @blur="saveTitle"
              @keyup.enter="saveTitle"
            />
          </div>
          <button class="text-muted-foreground hover:text-foreground mt-1" @click="emit('close')">✕</button>
        </div>

        <!-- Meta row: due date -->
        <div class="flex flex-wrap gap-4">
          <div>
            <p class="text-xs font-semibold text-muted-foreground uppercase mb-1">Due date</p>
            <input
              type="date"
              v-model="dueDate"
              class="text-sm bg-muted/50 border border-input rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-ring"
              @change="saveDueDate"
            />
          </div>
        </div>

        <!-- Labels selector -->
        <div v-if="boardLabels.length">
          <p class="text-xs font-semibold text-muted-foreground uppercase mb-2">Labels</p>
          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="label in boardLabels"
              :key="label.id"
              :style="{ background: label.color, opacity: cardLabelIds.has(label.id) ? 1 : 0.35 }"
              class="text-xs text-white px-2.5 py-1 rounded-full transition-opacity hover:opacity-100 border-2"
              :class="cardLabelIds.has(label.id) ? 'border-white/40' : 'border-transparent'"
              @click="toggleLabel(label.id)"
            >{{ label.name }}</button>
          </div>
        </div>

        <!-- Assignees selector -->
        <div v-if="boardMembers.length">
          <p class="text-xs font-semibold text-muted-foreground uppercase mb-2">Members</p>
          <div class="flex gap-2 flex-wrap">
            <button
              v-for="member in boardMembers"
              :key="member.user.id"
              class="flex items-center gap-1.5 rounded-full px-2.5 py-1 border-2 transition-colors"
              :class="cardAssigneeIds.has(member.user.id)
                ? 'bg-primary/10 border-primary'
                : 'bg-muted border-transparent hover:border-muted-foreground/30'"
              @click="toggleAssignee(member.user.id)"
            >
              <div class="w-5 h-5 rounded-full bg-primary text-[10px] text-primary-foreground flex items-center justify-center">
                {{ member.user.name[0].toUpperCase() }}
              </div>
              <span class="text-xs">{{ member.user.name }}</span>
            </button>
          </div>
        </div>

        <!-- Cover color -->
        <div>
          <p class="text-xs font-semibold text-muted-foreground uppercase mb-2">Cover</p>
          <div class="flex gap-2">
            <button
              v-for="color in COVER_COLORS"
              :key="color"
              :style="{ background: color }"
              class="w-7 h-7 rounded-md border-2 transition-transform hover:scale-110"
              :class="card.cover_color === color ? 'border-foreground scale-110' : 'border-transparent'"
              @click="setCoverColor(card.cover_color === color ? null : color)"
            />
          </div>
        </div>

        <!-- Description -->
        <div>
          <p class="text-xs font-semibold text-muted-foreground uppercase mb-2">Description</p>
          <textarea
            v-model="description"
            rows="4"
            placeholder="Add a description..."
            class="w-full text-sm bg-muted/50 border border-input rounded-md px-3 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-ring"
            @blur="saveDescription"
          />
        </div>

        <!-- Comments -->
        <div>
          <p class="text-xs font-semibold text-muted-foreground uppercase mb-3">Comments</p>

          <div class="space-y-3 mb-4">
            <div v-for="comment in card.comments" :key="comment.id" class="flex gap-2.5">
              <div class="w-7 h-7 rounded-full bg-primary text-xs text-primary-foreground flex items-center justify-center flex-shrink-0">
                {{ comment.user.name[0].toUpperCase() }}
              </div>
              <div class="flex-1">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-medium">{{ comment.user.name }}</span>
                  <span class="text-xs text-muted-foreground">{{ new Date(comment.created_at).toLocaleString() }}</span>
                </div>
                <p class="text-sm mt-0.5">{{ comment.text }}</p>
              </div>
              <button class="text-muted-foreground hover:text-destructive text-xs self-start mt-1" @click="deleteComment(comment.id)">✕</button>
            </div>
          </div>

          <div class="flex gap-2">
            <Input v-model="newComment" placeholder="Write a comment..." class="flex-1" @keyup.enter="postComment" />
            <Button size="sm" :disabled="addingComment" @click="postComment">Post</Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
