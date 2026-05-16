<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import draggable from 'vuedraggable'
import { useBoardsStore } from '@/stores/boards'
import { useToastStore } from '@/stores/toast'
import { useTheme } from '@/composables/useTheme'
import { boardsApi } from '@/api/boards'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import CardModal from '@/components/CardModal.vue'
import type { CardBrief } from '@/types'

const route = useRoute()
const router = useRouter()
const store = useBoardsStore()
const toast = useToastStore()
const { isDark, toggle: toggleTheme } = useTheme()

const boardId = route.params.id as string
const newColTitle = ref('')
const addingCol = ref(false)
const addingCardColId = ref<string | null>(null)
const newCardTitle = ref('')

// Invite member
const showInvite = ref(false)
const inviteEmail = ref('')
const inviting = ref(false)

async function inviteMember() {
  if (!inviteEmail.value.trim()) return
  inviting.value = true
  try {
    await boardsApi.addMember(boardId, inviteEmail.value.trim())
    await store.fetchBoard(boardId)
    toast.success(`${inviteEmail.value} добавлен на доску`)
    inviteEmail.value = ''
    showInvite.value = false
  } catch {
    // error toast shown by interceptor
  } finally {
    inviting.value = false
  }
}

// Filters
const showFilters = ref(false)
const selectedLabelIds = ref(new Set<string>())
const selectedMemberIds = ref(new Set<string>())
const dueDateFilter = ref<'overdue' | 'week' | 'none' | null>(null)

const hasFilters = computed(() =>
  selectedLabelIds.value.size > 0 || selectedMemberIds.value.size > 0 || dueDateFilter.value !== null
)

const matchingCardIds = computed<Set<string> | null>(() => {
  if (!hasFilters.value) return null
  const result = new Set<string>()
  for (const col of store.currentBoard?.columns ?? []) {
    for (const card of col.cards) {
      let match = true
      if (selectedLabelIds.value.size > 0) {
        const ids = new Set(card.labels.map(l => l.id))
        if (![...selectedLabelIds.value].some(id => ids.has(id))) match = false
      }
      if (match && selectedMemberIds.value.size > 0) {
        const ids = new Set(card.assignees.map(u => u.id))
        if (![...selectedMemberIds.value].some(id => ids.has(id))) match = false
      }
      if (match && dueDateFilter.value) {
        const now = new Date()
        const due = card.due_date ? new Date(card.due_date) : null
        if (dueDateFilter.value === 'overdue') match = !!due && due < now
        else if (dueDateFilter.value === 'week') match = !!due && due <= new Date(now.getTime() + 7 * 864e5)
        else if (dueDateFilter.value === 'none') match = !due
      }
      if (match) result.add(card.id)
    }
  }
  return result
})

function toggleLabelFilter(id: string) {
  const next = new Set(selectedLabelIds.value)
  next.has(id) ? next.delete(id) : next.add(id)
  selectedLabelIds.value = next
}

function toggleMemberFilter(id: string) {
  const next = new Set(selectedMemberIds.value)
  next.has(id) ? next.delete(id) : next.add(id)
  selectedMemberIds.value = next
}

function clearFilters() {
  selectedLabelIds.value = new Set()
  selectedMemberIds.value = new Set()
  dueDateFilter.value = null
}

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
  <div class="min-h-screen flex flex-col bg-background">

    <!-- Header -->
    <header class="px-4 py-2.5 flex items-center gap-3 bg-card border-b border-border">
      <button
        class="text-muted-foreground hover:text-foreground text-sm transition-colors flex items-center gap-1"
        @click="router.push('/boards')"
      >← Boards</button>
      <span class="text-border">|</span>
      <h1 class="font-semibold flex-1 truncate">{{ store.currentBoard?.title }}</h1>

      <div class="flex items-center gap-1.5">
        <!-- Members avatars -->
        <div class="flex -space-x-1.5 mr-1">
          <div
            v-for="m in store.currentBoard?.members.slice(0, 4)"
            :key="m.user.id"
            :title="m.user.name"
            class="w-7 h-7 rounded-full bg-primary text-primary-foreground text-xs flex items-center justify-center border-2 border-card font-medium"
          >{{ m.user.name[0].toUpperCase() }}</div>
        </div>

        <button
          class="text-sm px-2.5 py-1 rounded-md border border-border text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
          :class="showFilters ? 'bg-muted text-foreground' : ''"
          @click="showFilters = !showFilters"
        >Фильтр{{ hasFilters ? ' ●' : '' }}</button>

        <button
          class="w-8 h-8 rounded-md flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
          :title="isDark ? 'Светлая тема' : 'Тёмная тема'"
          @click="toggleTheme"
        >{{ isDark ? '☀️' : '🌙' }}</button>

        <button
          class="text-sm px-2.5 py-1 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
          @click="showInvite = true"
        >+ Invite</button>
      </div>
    </header>

    <!-- Filter bar -->
    <div v-if="showFilters && store.currentBoard" class="px-4 py-2 bg-muted/50 border-b border-border flex flex-wrap items-center gap-4">
      <div v-if="store.currentBoard.labels.length" class="flex items-center gap-1.5 flex-wrap">
        <span class="text-xs font-medium text-muted-foreground">Метки:</span>
        <button
          v-for="label in store.currentBoard.labels"
          :key="label.id"
          :style="{ background: label.color }"
          class="text-xs text-white px-2 py-0.5 rounded-full border-2 transition-all"
          :class="selectedLabelIds.has(label.id) ? 'border-foreground scale-105' : 'border-transparent opacity-50 hover:opacity-100'"
          @click="toggleLabelFilter(label.id)"
        >{{ label.name }}</button>
      </div>

      <div v-if="store.currentBoard.members.length" class="flex items-center gap-1.5 flex-wrap">
        <span class="text-xs font-medium text-muted-foreground">Участники:</span>
        <button
          v-for="m in store.currentBoard.members"
          :key="m.user.id"
          :title="m.user.name"
          class="w-6 h-6 rounded-full text-[10px] font-medium flex items-center justify-center border-2 transition-all bg-primary text-primary-foreground"
          :class="selectedMemberIds.has(m.user.id) ? 'border-foreground scale-110' : 'border-transparent opacity-50 hover:opacity-100'"
          @click="toggleMemberFilter(m.user.id)"
        >{{ m.user.name[0].toUpperCase() }}</button>
      </div>

      <div class="flex items-center gap-1.5 flex-wrap">
        <span class="text-xs font-medium text-muted-foreground">Дедлайн:</span>
        <button
          v-for="opt in [{ v: 'overdue', l: 'Просрочено' }, { v: 'week', l: 'На неделе' }, { v: 'none', l: 'Без даты' }]"
          :key="opt.v"
          class="text-xs px-2 py-0.5 rounded-full border border-border transition-colors"
          :class="dueDateFilter === opt.v ? 'bg-primary text-primary-foreground border-primary' : 'text-muted-foreground hover:text-foreground hover:bg-muted'"
          @click="dueDateFilter = dueDateFilter === opt.v ? null : opt.v as any"
        >{{ opt.l }}</button>
      </div>

      <button v-if="hasFilters" class="text-xs text-muted-foreground hover:text-foreground underline ml-auto" @click="clearFilters">
        Сбросить
      </button>
    </div>

    <!-- Invite modal -->
    <div v-if="showInvite" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4" @click.self="showInvite = false">
      <div class="bg-card border border-border rounded-xl shadow-xl p-6 w-full max-w-sm space-y-4">
        <h2 class="font-semibold text-lg">Пригласить участника</h2>
        <Input v-model="inviteEmail" placeholder="email@example.com" type="email" autofocus @keyup.enter="inviteMember" />
        <div class="flex gap-2">
          <Button :disabled="inviting" @click="inviteMember">{{ inviting ? 'Добавляю...' : 'Добавить' }}</Button>
          <Button variant="ghost" @click="showInvite = false">Отмена</Button>
        </div>
      </div>
    </div>

    <!-- Board columns -->
    <div class="flex-1 flex items-start gap-3 p-4 overflow-x-auto bg-muted/30">
      <draggable
        v-if="store.currentBoard"
        :list="store.currentBoard.columns"
        item-key="id"
        handle=".col-drag-handle"
        :animation="150"
        ghost-class="opacity-40"
        class="flex items-start gap-3"
        @end="store.updateColumnPositions()"
      >
        <template #item="{ element: col }">
        <div class="flex-shrink-0 w-72 bg-card border border-border rounded-xl flex flex-col max-h-[calc(100vh-7rem)]">

          <!-- Column header -->
          <div class="col-drag-handle px-3 pt-3 pb-2 flex items-center justify-between cursor-grab active:cursor-grabbing select-none">
            <span class="font-semibold text-sm flex-1">{{ col.title }}</span>
            <button
              class="text-muted-foreground hover:text-destructive text-xs ml-2 cursor-pointer transition-colors"
              @click.stop="store.deleteColumn(col.id)"
            >✕</button>
          </div>

          <!-- Cards -->
          <div class="flex-1 overflow-y-auto px-2 pb-2">
            <draggable
              :list="col.cards"
              group="cards"
              item-key="id"
              :animation="150"
              ghost-class="opacity-40"
              class="space-y-2 min-h-[4px]"
              @change="(e: any) => onCardDrop(col.id, e)"
            >
              <template #item="{ element: card }">
                <div
                  class="bg-background border border-border rounded-lg cursor-pointer hover:border-primary/50 hover:shadow-sm transition-all overflow-hidden"
                  :class="matchingCardIds && !matchingCardIds.has(card.id) ? 'opacity-25' : ''"
                  @click="store.openCard(card.id)"
                >
                  <div v-if="card.cover_color" :style="{ background: card.cover_color }" class="h-8" />
                  <div class="p-2.5">
                    <p class="text-sm font-medium">{{ card.title }}</p>
                    <div v-if="card.labels?.length" class="flex flex-wrap gap-1 mt-1.5">
                      <span
                        v-for="label in card.labels"
                        :key="label.id"
                        :style="{ background: label.color }"
                        class="text-[10px] text-white px-1.5 py-0.5 rounded-full font-medium"
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
                          class="w-5 h-5 rounded-full bg-primary text-[10px] text-primary-foreground flex items-center justify-center border border-card font-medium"
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
              class="w-full text-left text-sm text-muted-foreground hover:text-foreground hover:bg-muted/50 px-2 py-1.5 rounded-md transition-colors"
              @click="startAddCard(col.id)"
            >+ Add a card</button>
          </div>
        </div>
        </template>
      </draggable>

      <!-- Add column -->
      <div class="flex-shrink-0 w-72">
        <div v-if="addingCol" class="bg-card border border-border rounded-xl p-3 space-y-2">
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
          class="w-full text-left text-muted-foreground hover:text-foreground hover:bg-card/80 border border-dashed border-border hover:border-primary/30 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors"
          @click="addingCol = true"
        >+ Add column</button>
      </div>
    </div>

    <!-- Card modal -->
    <CardModal v-if="store.activeCard" @close="store.closeCard()" />
  </div>
</template>
