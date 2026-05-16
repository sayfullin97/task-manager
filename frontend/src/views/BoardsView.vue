<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useBoardsStore } from '@/stores/boards'
import { useToastStore } from '@/stores/toast'
import { useTheme } from '@/composables/useTheme'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Dialog, DialogScrollContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'

const router = useRouter()
const auth = useAuthStore()
const store = useBoardsStore()
const toast = useToastStore()
const { isDark, toggle: toggleTheme } = useTheme()

const showCreate = ref(false)
const newTitle = ref('')
const creating = ref(false)
const deletingBoardId = ref<string | null>(null)

async function doDeleteBoard(boardId: string) {
  try {
    await store.deleteBoard(boardId)
    toast.success('Доска удалена')
  } catch {
    // toast shown by interceptor
  } finally {
    deletingBoardId.value = null
  }
}

onMounted(() => store.fetchBoards())

async function createBoard() {
  if (!newTitle.value.trim()) return
  creating.value = true
  try {
    const board = await store.createBoard(newTitle.value.trim())
    newTitle.value = ''
    showCreate.value = false
    toast.success('Доска создана')
    router.push(`/boards/${board.id}`)
  } finally {
    creating.value = false
  }
}

function logout() {
  auth.logout()
  router.push('/login')
}

const COLORS = ['#2563a8', '#5c3ea8', '#a83250', '#1a7a52', '#a87820', '#1a7a8e']
function boardColor(id: string) {
  return COLORS[id.charCodeAt(0) % COLORS.length]
}
</script>

<template>
  <div class="min-h-screen bg-muted/20">
    <!-- Header -->
    <header class="border-b bg-background px-6 py-4 flex items-center justify-between">
      <h1 class="text-xl font-bold">Task Manager</h1>
      <div class="flex items-center gap-3">
        <span class="text-sm text-muted-foreground">{{ auth.user?.name }}</span>
        <Button v-if="auth.user?.is_admin" variant="outline" size="sm" @click="router.push('/admin')">Admin</Button>
        <Button
          variant="outline"
          size="icon"
          :title="isDark ? 'Светлая тема' : 'Тёмная тема'"
          @click="toggleTheme"
        >{{ isDark ? '☀️' : '🌙' }}</Button>
        <Button variant="outline" size="sm" @click="logout">Logout</Button>
      </div>
    </header>

    <main class="max-w-6xl mx-auto px-6 py-8">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-2xl font-semibold">My Boards</h2>
        <Button @click="showCreate = true; newTitle = ''">+ New Board</Button>
      </div>

      <!-- Create board dialog -->
      <Dialog :open="showCreate" @update:open="showCreate = false">
        <DialogScrollContent class="max-w-sm">
          <DialogHeader>
            <DialogTitle>New Board</DialogTitle>
          </DialogHeader>
          <div class="flex flex-col gap-4 pt-2">
            <Input v-model="newTitle" placeholder="Board title" autofocus @keyup.enter="createBoard" />
            <div class="flex gap-2">
              <Button :disabled="creating" @click="createBoard">{{ creating ? 'Creating...' : 'Create' }}</Button>
              <Button variant="ghost" @click="showCreate = false; newTitle = ''">Cancel</Button>
            </div>
          </div>
        </DialogScrollContent>
      </Dialog>

      <!-- Boards grid -->
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        <!-- Skeleton loading -->
        <template v-if="store.loading">
          <div v-for="i in 6" :key="i" class="rounded-lg overflow-hidden border animate-pulse">
            <div class="h-20 bg-muted" />
            <div class="p-3 bg-card space-y-2">
              <div class="h-3.5 bg-muted rounded w-3/4" />
              <div class="h-2.5 bg-muted rounded w-1/2" />
            </div>
          </div>
        </template>

        <template v-else>
          <div
            v-for="board in store.boards"
            :key="board.id"
            class="group relative"
          >
            <RouterLink :to="`/boards/${board.id}`">
              <div class="rounded-lg overflow-hidden border hover:shadow-md transition-shadow cursor-pointer">
                <div :style="{ background: boardColor(board.id) }" class="h-20" />
                <div class="p-3 bg-card">
                  <p class="font-medium text-sm truncate">{{ board.title }}</p>
                  <p v-if="board.description" class="text-xs text-muted-foreground mt-0.5 truncate">{{ board.description }}</p>
                  <p class="text-xs text-muted-foreground mt-1 capitalize">{{ board.role }}</p>
                </div>
              </div>
            </RouterLink>

            <!-- Delete board button (owner only) -->
            <button
              v-if="board.role === 'owner'"
              class="absolute top-1.5 right-1.5 size-6 rounded flex items-center justify-center bg-black/30 text-white opacity-0 group-hover:opacity-100 transition-opacity hover:bg-black/60 text-xs leading-none"
              :title="'Удалить доску'"
              @click.prevent="deletingBoardId === board.id ? doDeleteBoard(board.id) : (deletingBoardId = board.id)"
            >✕</button>

            <!-- Confirm overlay -->
            <div
              v-if="deletingBoardId === board.id"
              class="absolute inset-0 rounded-lg bg-background/90 flex flex-col items-center justify-center gap-2 p-3"
            >
              <p class="text-xs font-medium text-center">Удалить «{{ board.title }}»?</p>
              <div class="flex gap-1.5">
                <Button size="xs" variant="destructive" @click="doDeleteBoard(board.id)">Удалить</Button>
                <Button size="xs" variant="ghost" @click="deletingBoardId = null">Отмена</Button>
              </div>
            </div>
          </div>

          <p v-if="!store.boards.length" class="col-span-full text-center text-muted-foreground py-12">
            No boards yet. Create your first one!
          </p>
        </template>
      </div>
    </main>
  </div>
</template>
