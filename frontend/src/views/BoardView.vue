<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import draggable from 'vuedraggable'
import { useBoardsStore } from '@/stores/boards'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import CardModal from '@/components/CardModal.vue'
import type { CardBrief } from '@/types'

const route = useRoute()
const router = useRouter()
const store = useBoardsStore()

const boardId = route.params.id as string
const newColTitle = ref('')
const addingCol = ref(false)
const addingCardColId = ref<string | null>(null)
const newCardTitle = ref('')

onMounted(() => store.fetchBoard(boardId))

async function addColumn() {
  if (!newColTitle.value.trim()) return
  await store.createColumn(boardId, newColTitle.value.trim())
  newColTitle.value = ''
  addingCol.value = false
}

async function addCard(columnId: string) {
  if (!newCardTitle.value.trim()) return
  await store.createCard(columnId, newCardTitle.value.trim())
  newCardTitle.value = ''
  addingCardColId.value = null
}

function startAddCard(columnId: string) {
  addingCardColId.value = columnId
  newCardTitle.value = ''
}

async function onCardDrop(columnId: string, event: any) {
  const { added, moved } = event
  const item: CardBrief = added?.element ?? moved?.element
  if (!item) return

  const col = store.currentBoard?.columns.find(c => c.id === columnId)
  if (!col) return

  const idx = col.cards.findIndex(c => c.id === item.id)
  const prev = col.cards[idx - 1]?.position ?? 0
  const next = col.cards[idx + 1]?.position ?? (col.cards[idx]?.position ?? 1000) + 1000
  const position = Math.round((prev + next) / 2)

  const fromColumnId = added ? item.column_id : columnId
  await store.moveCard(item.id, fromColumnId, columnId, position)
}
</script>

<template>
  <div class="min-h-screen flex flex-col bg-blue-600">
    <!-- Header -->
    <header class="px-4 py-3 flex items-center gap-4 bg-black/20">
      <button class="text-white/80 hover:text-white text-sm" @click="router.push('/boards')">← Boards</button>
      <h1 class="text-white font-bold text-lg">{{ store.currentBoard?.title }}</h1>
    </header>

    <!-- Board columns -->
    <div class="flex-1 flex items-start gap-3 p-4 overflow-x-auto">
      <draggable
        v-if="store.currentBoard"
        :list="store.currentBoard.columns"
        item-key="id"
        handle=".col-handle"
        ghost-class="opacity-40"
        class="flex items-start gap-3"
        @end="store.updateColumnPositions()"
      >
        <template #item="{ element: col }">
        <div
          class="flex-shrink-0 w-72 bg-muted rounded-xl flex flex-col max-h-[calc(100vh-8rem)]"
        >
          <!-- Column header -->
          <div class="px-3 pt-3 pb-2 font-semibold text-sm flex items-center justify-between">
            <span class="col-handle cursor-grab active:cursor-grabbing flex-1">{{ col.title }}</span>
            <button class="text-muted-foreground hover:text-destructive text-xs ml-2" @click="store.deleteColumn(col.id)">✕</button>
          </div>

          <!-- Cards -->
          <div class="flex-1 overflow-y-auto px-2 pb-2">
            <draggable
              :list="col.cards"
              group="cards"
              item-key="id"
              ghost-class="opacity-40"
              class="space-y-2 min-h-[4px]"
              @change="(e: any) => onCardDrop(col.id, e)"
            >
              <template #item="{ element: card }">
                <div
                  class="bg-card rounded-lg shadow-sm cursor-pointer hover:shadow-md transition-shadow overflow-hidden"
                  @click="store.openCard(card.id)"
                >
                  <div v-if="card.cover_color" :style="{ background: card.cover_color }" class="h-8" />
                  <div class="p-2.5">
                    <p class="text-sm font-medium">{{ card.title }}</p>
                    <div class="flex flex-wrap gap-1 mt-1.5" v-if="card.labels?.length">
                      <span
                        v-for="label in card.labels"
                        :key="label.id"
                        :style="{ background: label.color }"
                        class="text-[10px] text-white px-1.5 py-0.5 rounded-full"
                      >{{ label.name }}</span>
                    </div>
                    <div class="flex items-center justify-between mt-1.5">
                      <span v-if="card.due_date" class="text-xs text-muted-foreground">
                        📅 {{ new Date(card.due_date).toLocaleDateString() }}
                      </span>
                      <div class="flex -space-x-1 ml-auto">
                        <div
                          v-for="user in card.assignees?.slice(0, 3)"
                          :key="user.id"
                          class="w-5 h-5 rounded-full bg-primary text-[10px] text-primary-foreground flex items-center justify-center border border-card"
                        >{{ user.name[0].toUpperCase() }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </template>
            </draggable>
          </div>

          <!-- Add card -->
          <div class="px-2 pb-2">
            <div v-if="addingCardColId === col.id" class="space-y-1.5">
              <Input
                v-model="newCardTitle"
                placeholder="Card title..."
                class="text-sm h-8"
                autofocus
                @keyup.enter="addCard(col.id)"
                @keyup.esc="addingCardColId = null"
              />
              <div class="flex gap-1">
                <Button size="sm" class="h-7 text-xs" @click="addCard(col.id)">Add</Button>
                <Button size="sm" variant="ghost" class="h-7 text-xs" @click="addingCardColId = null">Cancel</Button>
              </div>
            </div>
            <button
              v-else
              class="w-full text-left text-sm text-muted-foreground hover:text-foreground hover:bg-black/5 px-1 py-1 rounded"
              @click="startAddCard(col.id)"
            >+ Add a card</button>
          </div>
        </div>
        </template>
      </draggable>

      <!-- Add column -->
      <div class="flex-shrink-0 w-72">
        <div v-if="addingCol" class="bg-muted rounded-xl p-2 space-y-2">
          <Input
            v-model="newColTitle"
            placeholder="Column title..."
            autofocus
            @keyup.enter="addColumn"
            @keyup.esc="addingCol = false"
          />
          <div class="flex gap-2">
            <Button size="sm" @click="addColumn">Add</Button>
            <Button size="sm" variant="ghost" @click="addingCol = false">Cancel</Button>
          </div>
        </div>
        <button
          v-else
          class="w-full text-left text-white/80 hover:text-white hover:bg-black/10 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors"
          @click="addingCol = true"
        >+ Add column</button>
      </div>
    </div>

    <!-- Card modal -->
    <CardModal v-if="store.activeCard" @close="store.closeCard()" />
  </div>
</template>
