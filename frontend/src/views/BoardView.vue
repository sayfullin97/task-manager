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
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Dialog, DialogScrollContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import CardModal from '@/components/CardModal.vue'
import LabelsManager from '@/components/LabelsManager.vue'
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

// Board title inline edit
const editingBoardTitle = ref(false)
const boardTitleDraft = ref('')
function startEditBoardTitle() {
  boardTitleDraft.value = store.currentBoard?.title ?? ''
  editingBoardTitle.value = true
}
async function saveBoardTitle() {
  editingBoardTitle.value = false
  const trimmed = boardTitleDraft.value.trim()
  if (!trimmed || trimmed === store.currentBoard?.title) return
  try {
    await store.updateBoard(boardId, trimmed, store.currentBoard?.description)
  } catch { /* toast shown by interceptor */ }
}

// Column inline rename
const editingColId = ref<string | null>(null)
const editingColTitle = ref('')
function startEditCol(colId: string, currentTitle: string) {
  editingColId.value = colId
  editingColTitle.value = currentTitle
}
async function saveColTitle() {
  const colId = editingColId.value
  const trimmed = editingColTitle.value.trim()
  editingColId.value = null
  if (!colId || !trimmed) return
  const col = store.currentBoard?.columns.find(c => c.id === colId)
  if (!col || trimmed === col.title) return
  try {
    await store.updateColumn(colId, trimmed)
  } catch { /* toast shown by interceptor */ }
}

// Search
const searchQuery = ref('')

// Column sort: 'default' | 'due_asc' | 'title_asc'
const colSort = ref<Record<string, 'default' | 'due_asc' | 'title_asc'>>({})
const SORT_CYCLE: Record<string, 'default' | 'due_asc' | 'title_asc'> = {
  default: 'due_asc',
  due_asc: 'title_asc',
  title_asc: 'default',
}
const SORT_LABEL: Record<string, string> = {
  default: '↕',
  due_asc: '📅',
  title_asc: 'A–Z',
}
function cycleSort(colId: string) {
  colSort.value[colId] = SORT_CYCLE[colSort.value[colId] ?? 'default']
}
function sortedCards(col: { id: string; cards: CardBrief[] }): CardBrief[] {
  const mode = colSort.value[col.id] ?? 'default'
  if (mode === 'default') return col.cards
  return [...col.cards].sort((a, b) => {
    if (mode === 'title_asc') return a.title.localeCompare(b.title)
    // due_asc: nulls last
    if (!a.due_date && !b.due_date) return 0
    if (!a.due_date) return 1
    if (!b.due_date) return -1
    return a.due_date < b.due_date ? -1 : 1
  })
}

// Overdue helper
const now = new Date()
function isOverdue(due: string | null) {
  return !!due && new Date(due) < now
}

// Stable sorted display per column (used as :list in draggable)
const colDisplayCards = computed(() => {
  if (!store.currentBoard) return {} as Record<string, CardBrief[]>
  const result: Record<string, CardBrief[]> = {}
  for (const col of store.currentBoard.columns) {
    result[col.id] = sortedCards(col)
  }
  return result
})

// Drag state
const isDragging = ref(false)
const dragOverColId = ref<string | null>(null)

function onCardDragStart() { isDragging.value = true }
function onCardDragEnd() {
  isDragging.value = false
  dragOverColId.value = null
}
function onColDragEnter(colId: string) {
  if (isDragging.value) dragOverColId.value = colId
}
function onColDragLeave(e: DragEvent, colId: string) {
  const el = e.currentTarget as HTMLElement
  if (!el.contains(e.relatedTarget as Node)) {
    if (dragOverColId.value === colId) dragOverColId.value = null
  }
}

// Invite member
const showLabels = ref(false)
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
  const q = searchQuery.value.trim().toLowerCase()
  if (!hasFilters.value && !q) return null
  const result = new Set<string>()
  for (const col of store.currentBoard?.columns ?? []) {
    for (const card of col.cards) {
      let match = true
      if (q && !card.title.toLowerCase().includes(q)) match = false
      if (match && selectedLabelIds.value.size > 0) {
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
      <Button variant="ghost" size="sm" class="gap-1 text-muted-foreground" @click="router.push('/boards')">← Boards</Button>
      <span class="text-border">|</span>

      <!-- Board title — click to edit -->
      <input
        v-if="editingBoardTitle"
        v-model="boardTitleDraft"
        class="font-semibold bg-transparent border-b border-ring outline-none flex-1 min-w-0 truncate"
        autofocus
        @blur="saveBoardTitle"
        @keyup.enter="saveBoardTitle"
        @keyup.esc="editingBoardTitle = false"
      />
      <h1
        v-else
        class="font-semibold flex-1 truncate cursor-pointer hover:text-muted-foreground transition-colors"
        :title="'Нажмите, чтобы переименовать'"
        @click="startEditBoardTitle"
      >{{ store.currentBoard?.title }}</h1>

      <div class="flex items-center gap-1.5">
        <!-- Members avatars -->
        <div class="flex -space-x-1.5 mr-1">
          <Avatar
            v-for="m in store.currentBoard?.members.slice(0, 4)"
            :key="m.user.id"
            size="sm"
            :title="m.user.name"
            class="border-2 border-card"
          >
            <AvatarFallback class="text-[10px] bg-primary text-primary-foreground">{{ m.user.name[0].toUpperCase() }}</AvatarFallback>
          </Avatar>
        </div>

        <!-- Search -->
        <Input
          v-model="searchQuery"
          placeholder="Поиск карточек..."
          class="h-8 w-40 text-xs"
        />

        <Button variant="outline" size="sm" @click="showLabels = true">Метки</Button>

        <Button
          variant="outline"
          size="sm"
          :class="showFilters ? 'bg-muted' : ''"
          @click="showFilters = !showFilters"
        >Фильтр{{ hasFilters ? ' ●' : '' }}</Button>

        <Button
          variant="ghost"
          size="icon"
          :title="isDark ? 'Светлая тема' : 'Тёмная тема'"
          @click="toggleTheme"
        >{{ isDark ? '☀️' : '🌙' }}</Button>

        <Button size="sm" @click="showInvite = true">+ Invite</Button>
      </div>
    </header>

    <!-- Filter bar -->
    <div v-if="showFilters && store.currentBoard" class="px-4 py-2 bg-muted border-b border-border flex flex-wrap items-center gap-4">
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
          class="transition-all"
          :class="selectedMemberIds.has(m.user.id) ? 'scale-110' : 'opacity-50 hover:opacity-100'"
          @click="toggleMemberFilter(m.user.id)"
        >
          <Avatar size="sm" :class="selectedMemberIds.has(m.user.id) ? 'ring-2 ring-foreground' : ''">
            <AvatarFallback class="text-[10px] bg-primary text-primary-foreground">{{ m.user.name[0].toUpperCase() }}</AvatarFallback>
          </Avatar>
        </button>
      </div>

      <div class="flex items-center gap-1.5 flex-wrap">
        <span class="text-xs font-medium text-muted-foreground">Дедлайн:</span>
        <Button
          v-for="opt in [{ v: 'overdue', l: 'Просрочено' }, { v: 'week', l: 'На неделе' }, { v: 'none', l: 'Без даты' }]"
          :key="opt.v"
          :variant="dueDateFilter === opt.v ? 'default' : 'outline'"
          size="xs"
          @click="dueDateFilter = dueDateFilter === opt.v ? null : opt.v as any"
        >{{ opt.l }}</Button>
      </div>

      <Button v-if="hasFilters" variant="ghost" size="xs" class="ml-auto text-muted-foreground" @click="clearFilters">
        Сбросить
      </Button>
    </div>

    <!-- Invite modal -->
    <Dialog :open="showInvite" @update:open="showInvite = false">
      <DialogScrollContent class="max-w-sm">
        <DialogHeader>
          <DialogTitle>Пригласить участника</DialogTitle>
        </DialogHeader>
        <div class="flex flex-col gap-4 pt-2">
          <Input v-model="inviteEmail" placeholder="email@example.com" type="email" autofocus @keyup.enter="inviteMember" />
          <div class="flex gap-2">
            <Button :disabled="inviting" @click="inviteMember">{{ inviting ? 'Добавляю...' : 'Добавить' }}</Button>
            <Button variant="ghost" @click="showInvite = false">Отмена</Button>
          </div>
        </div>
      </DialogScrollContent>
    </Dialog>

    <!-- Board columns -->
    <div class="flex-1 flex items-start gap-3 p-4 overflow-x-auto bg-muted">

      <!-- Skeleton while loading -->
      <template v-if="store.boardLoading">
        <div v-for="i in 3" :key="i" class="flex-shrink-0 w-72 bg-card border border-border rounded-xl p-3 space-y-2 animate-pulse">
          <div class="h-4 bg-muted rounded w-2/3 mb-3" />
          <div v-for="j in (i === 1 ? 3 : i === 2 ? 2 : 4)" :key="j" class="bg-muted rounded-lg p-3 space-y-2">
            <div class="h-3 bg-background rounded w-full" />
            <div class="h-3 bg-background rounded w-3/4" />
          </div>
        </div>
      </template>

      <draggable
        v-else-if="store.currentBoard"
        :list="store.currentBoard.columns"
        item-key="id"
        handle=".col-drag-handle"
        :animation="150"
        ghost-class="opacity-40"
        class="flex items-start gap-3"
        @end="store.updateColumnPositions()"
      >
        <template #item="{ element: col }">
        <div
          class="flex-shrink-0 w-72 bg-card border rounded-xl flex flex-col max-h-[calc(100vh-7rem)] transition-colors duration-150"
          :class="dragOverColId === col.id
            ? 'border-ring ring-2 ring-ring'
            : isDragging
              ? 'border-border'
              : 'border-border'"
          @dragenter="onColDragEnter(col.id)"
          @dragleave="onColDragLeave($event, col.id)"
        >

          <!-- Column header -->
          <div class="px-3 pt-3 pb-2 flex items-center gap-1">
            <input
              v-if="editingColId === col.id"
              v-model="editingColTitle"
              class="font-semibold text-sm bg-transparent border-b border-ring outline-none flex-1 min-w-0"
              autofocus
              @blur="saveColTitle"
              @keyup.enter="saveColTitle"
              @keyup.esc="editingColId = null"
              @click.stop
            />
            <span
              v-else
              class="col-drag-handle font-semibold text-sm flex-1 cursor-grab active:cursor-grabbing select-none truncate"
              :title="'Двойной клик — переименовать'"
              @dblclick.stop="startEditCol(col.id, col.title)"
            >{{ col.title }}</span>

            <!-- Card count -->
            <span class="text-xs text-muted-foreground shrink-0">{{ col.cards.length }}</span>

            <!-- Sort toggle -->
            <Button
              variant="ghost"
              size="icon-sm"
              class="shrink-0 text-muted-foreground text-xs"
              :class="(colSort[col.id] ?? 'default') !== 'default' ? 'text-foreground' : ''"
              :title="'Сортировка'"
              @click.stop="cycleSort(col.id)"
            >{{ SORT_LABEL[colSort[col.id] ?? 'default'] }}</Button>

            <Button
              variant="ghost"
              size="icon-sm"
              class="shrink-0 text-muted-foreground hover:text-destructive"
              @click.stop="store.deleteColumn(col.id)"
            >✕</Button>
          </div>

          <!-- Cards -->
          <div class="flex-1 overflow-y-auto px-2 pb-2">
            <draggable
              :list="colDisplayCards[col.id] ?? col.cards"
              group="cards"
              item-key="id"
              :animation="150"
              ghost-class="card-drag-ghost"
              chosen-class="card-drag-chosen"
              class="space-y-2 min-h-[4px]"
              @start="onCardDragStart"
              @end="onCardDragEnd"
              @change="(e: any) => onCardDrop(col.id, e)"
            >
              <template #item="{ element: card }">
                <div
                  class="bg-background border rounded-lg cursor-pointer hover:shadow-sm transition-all overflow-hidden"
                  :class="[
                    matchingCardIds && !matchingCardIds.has(card.id) ? 'opacity-25' : '',
                    isOverdue(card.due_date) ? 'border-destructive/50' : 'border-border',
                  ]"
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
                      <span v-if="card.due_date" class="text-xs" :class="isOverdue(card.due_date) ? 'text-destructive font-medium' : 'text-muted-foreground'">
                        📅 {{ new Date(card.due_date).toLocaleDateString() }}
                      </span>
                      <div class="flex -space-x-1 ml-auto">
                        <Avatar
                          v-for="user in card.assignees?.slice(0, 3)"
                          :key="user.id"
                          size="sm"
                          class="!size-5 border border-card"
                        >
                          <AvatarFallback class="text-[10px] bg-primary text-primary-foreground">{{ user.name[0].toUpperCase() }}</AvatarFallback>
                        </Avatar>
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
                autofocus
                @keyup.enter="addCard(col.id)"
                @keyup.esc="addingCardColId = null"
              />
              <div class="flex gap-1">
                <Button size="sm" @click="addCard(col.id)">Add</Button>
                <Button size="sm" variant="ghost" @click="addingCardColId = null">Cancel</Button>
              </div>
            </div>
            <Button
              v-else
              variant="ghost"
              class="w-full justify-start text-muted-foreground hover:text-foreground text-xs"
              @click="startAddCard(col.id)"
            >+ Add a card</Button>
          </div>
        </div>
        </template>
      </draggable>

      <!-- Add column (only when not loading) -->
      <div v-if="!store.boardLoading" class="flex-shrink-0 w-72">
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
        <Button
          v-else
          variant="outline"
          class="w-full justify-start border-dashed text-muted-foreground hover:text-foreground rounded-xl py-5"
          @click="addingCol = true"
        >+ Add column</Button>
      </div>
    </div>

    <!-- Labels manager -->
    <LabelsManager v-if="showLabels" @close="showLabels = false" />

    <!-- Card modal -->
    <CardModal v-if="store.activeCard" @close="store.closeCard()" />
  </div>
</template>
