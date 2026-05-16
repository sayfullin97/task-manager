<script setup lang="ts">
import { ref, computed } from 'vue'
import { useBoardsStore } from '@/stores/boards'
import { cardsApi } from '@/api/cards'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Separator } from '@/components/ui/separator'
import {
  Dialog, DialogScrollContent, DialogHeader, DialogTitle,
} from '@/components/ui/dialog'

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
  '#a83232', '#a86432', '#8a7820', '#1a7a52',
  '#2563a8', '#5c3ea8', '#a83278', '#1a7a8e',
]

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

const boardLabels = computed(() => store.currentBoard?.labels ?? [])
const cardLabelIds = computed(() => new Set(card.labels.map(l => l.id)))

async function toggleLabel(labelId: string) {
  if (cardLabelIds.value.has(labelId)) {
    await cardsApi.removeLabel(card.id, labelId)
    card.labels.splice(card.labels.findIndex(l => l.id === labelId), 1)
  } else {
    const { data } = await cardsApi.addLabel(card.id, labelId)
    card.labels = data.labels
  }
  syncBrief()
}

const boardMembers = computed(() => store.currentBoard?.members ?? [])
const cardAssigneeIds = computed(() => new Set(card.assignees.map(u => u.id)))

async function toggleAssignee(userId: string) {
  if (cardAssigneeIds.value.has(userId)) {
    await cardsApi.removeAssignee(card.id, userId)
    card.assignees.splice(card.assignees.findIndex(u => u.id === userId), 1)
  } else {
    const { data } = await cardsApi.addAssignee(card.id, userId)
    card.assignees = data.assignees
  }
  syncBrief()
}

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
  card.comments.splice(card.comments.findIndex(c => c.id === commentId), 1)
}
</script>

<template>
  <Dialog :open="true" @update:open="emit('close')">
    <DialogScrollContent class="max-w-2xl p-0 gap-0 overflow-hidden">
      <!-- Cover -->
      <div v-if="card.cover_color" :style="{ background: card.cover_color }" class="h-28 w-full" />

      <div class="p-6 flex flex-col gap-5 max-h-[80vh] overflow-y-auto">
        <!-- Title -->
        <DialogHeader>
          <DialogTitle as="div">
            <input
              v-model="title"
              class="w-full text-lg font-semibold bg-transparent outline-none border-b border-transparent focus:border-border rounded-sm px-0 transition-colors"
              @blur="saveTitle"
              @keyup.enter="($event.target as HTMLInputElement).blur()"
            />
          </DialogTitle>
        </DialogHeader>

        <!-- Due date -->
        <div class="flex flex-col gap-1.5">
          <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Due date</p>
          <input
            type="date"
            v-model="dueDate"
            class="w-fit text-sm border border-border rounded-md px-2.5 py-1.5 outline-none focus:ring-2 focus:ring-ring transition-colors"
            @change="saveDueDate"
          />
        </div>

        <Separator />

        <!-- Labels -->
        <div v-if="boardLabels.length" class="flex flex-col gap-2">
          <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Labels</p>
          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="label in boardLabels"
              :key="label.id"
              :style="{ background: label.color }"
              class="inline-flex items-center rounded-full px-2.5 py-0.5 text-[10px] font-medium text-white transition-all border-2"
              :class="cardLabelIds.has(label.id) ? 'border-foreground/50 scale-105' : 'border-transparent opacity-40 hover:opacity-80'"
              @click="toggleLabel(label.id)"
            >{{ label.name }}</button>
          </div>
        </div>

        <!-- Members -->
        <div v-if="boardMembers.length" class="flex flex-col gap-2">
          <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Members</p>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="member in boardMembers"
              :key="member.user.id"
              class="flex items-center gap-2 rounded-full border px-2 py-1 transition-colors"
              :class="cardAssigneeIds.has(member.user.id)
                ? 'border-foreground bg-muted text-foreground'
                : 'border-border bg-transparent text-muted-foreground hover:text-foreground hover:bg-muted'"
              @click="toggleAssignee(member.user.id)"
            >
              <Avatar data-size="sm">
                <AvatarFallback class="text-[10px]">{{ member.user.name[0].toUpperCase() }}</AvatarFallback>
              </Avatar>
              <span class="text-xs font-medium">{{ member.user.name }}</span>
            </button>
          </div>
        </div>

        <!-- Cover -->
        <div class="flex flex-col gap-2">
          <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Cover</p>
          <div class="flex gap-2">
            <button
              v-for="color in COVER_COLORS"
              :key="color"
              :style="{ background: color }"
              class="w-7 h-7 rounded-md border-2 transition-all hover:scale-110"
              :class="card.cover_color === color ? 'border-foreground scale-110' : 'border-transparent'"
              @click="setCoverColor(card.cover_color === color ? null : color)"
            />
            <Button v-if="card.cover_color" variant="outline" size="sm" @click="setCoverColor(null)">Remove</Button>
          </div>
        </div>

        <Separator />

        <!-- Description -->
        <div class="flex flex-col gap-2">
          <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Description</p>
          <Textarea
            v-model="description"
            placeholder="Add a description..."
            class="min-h-[80px] resize-none"
            @blur="saveDescription"
          />
        </div>

        <Separator />

        <!-- Comments -->
        <div class="flex flex-col gap-3">
          <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Comments</p>

          <div class="flex flex-col gap-3">
            <div v-for="comment in card.comments" :key="comment.id" class="flex gap-2.5">
              <Avatar data-size="sm">
                <AvatarFallback class="text-[10px]">{{ comment.user.name[0].toUpperCase() }}</AvatarFallback>
              </Avatar>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <span class="text-xs font-medium">{{ comment.user.name }}</span>
                  <span class="text-[10px] text-muted-foreground">{{ new Date(comment.created_at).toLocaleString() }}</span>
                </div>
                <p class="text-xs mt-0.5 text-foreground">{{ comment.text }}</p>
              </div>
              <Button variant="ghost" size="icon-sm" class="text-muted-foreground hover:text-destructive flex-shrink-0" @click="deleteComment(comment.id)">✕</Button>
            </div>
          </div>

          <div class="flex gap-2">
            <Input v-model="newComment" placeholder="Write a comment..." class="flex-1" @keyup.enter="postComment" />
            <Button size="sm" :disabled="addingComment" @click="postComment">Post</Button>
          </div>
        </div>
      </div>
    </DialogScrollContent>
  </Dialog>
</template>
