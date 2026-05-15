<script setup lang="ts">
import { ref } from 'vue'
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

async function saveTitle() {
  if (title.value === card.title) return
  savingTitle.value = true
  try {
    await cardsApi.update(card.id, { title: title.value })
    card.title = title.value
  } finally {
    savingTitle.value = false
  }
}

async function saveDescription() {
  await cardsApi.update(card.id, { description: description.value })
  card.description = description.value
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

        <!-- Labels -->
        <div v-if="card.labels?.length" class="flex flex-wrap gap-1.5">
          <span
            v-for="label in card.labels"
            :key="label.id"
            :style="{ background: label.color }"
            class="text-xs text-white px-2 py-0.5 rounded-full"
          >{{ label.name }}</span>
        </div>

        <!-- Assignees -->
        <div v-if="card.assignees?.length">
          <p class="text-xs font-semibold text-muted-foreground uppercase mb-2">Members</p>
          <div class="flex gap-2 flex-wrap">
            <div
              v-for="user in card.assignees"
              :key="user.id"
              class="flex items-center gap-1.5 bg-muted rounded-full px-2.5 py-1"
            >
              <div class="w-5 h-5 rounded-full bg-primary text-[10px] text-primary-foreground flex items-center justify-center">
                {{ user.name[0].toUpperCase() }}
              </div>
              <span class="text-xs">{{ user.name }}</span>
            </div>
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
