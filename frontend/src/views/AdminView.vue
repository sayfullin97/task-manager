<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'
import { adminApi, type AdminUser, type AdminBoard, type AdminStats } from '@/api/admin'
import { Button } from '@/components/ui/button'

const router = useRouter()
const auth = useAuthStore()
const { isDark, toggle: toggleTheme } = useTheme()

const tab = ref<'users' | 'boards'>('users')
const stats = ref<AdminStats | null>(null)
const users = ref<AdminUser[]>([])
const boards = ref<AdminBoard[]>([])
const loading = ref(true)
const togglingId = ref<string | null>(null)

onMounted(async () => {
  try {
    const [s, u, b] = await Promise.all([
      adminApi.stats(),
      adminApi.users(),
      adminApi.boards(),
    ])
    stats.value = s.data
    users.value = u.data
    boards.value = b.data
  } finally {
    loading.value = false
  }
})

async function toggleAdmin(userId: string) {
  togglingId.value = userId
  try {
    const { data } = await adminApi.toggleAdmin(userId)
    const idx = users.value.findIndex(u => u.id === userId)
    if (idx !== -1) users.value[idx] = data
  } finally {
    togglingId.value = null
  }
}
</script>

<template>
  <div class="min-h-screen bg-muted flex flex-col">

    <!-- Header -->
    <header class="border-b bg-card px-6 py-3.5 flex items-center gap-4">
      <Button variant="ghost" size="sm" class="text-muted-foreground" @click="router.push('/boards')">← Назад</Button>
      <span class="text-border">|</span>
      <h1 class="font-bold text-base flex-1">Панель администратора</h1>
      <span class="text-sm text-muted-foreground">{{ auth.user?.name }}</span>
      <Button variant="outline" size="icon" @click="toggleTheme">{{ isDark ? '☀️' : '🌙' }}</Button>
    </header>

    <main class="flex-1 max-w-6xl mx-auto w-full px-6 py-6 space-y-6">

      <!-- Stats cards -->
      <div v-if="stats" class="grid grid-cols-3 sm:grid-cols-6 gap-3">
        <div v-for="[label, val] in [
          ['Пользователи', stats.users],
          ['Доски', stats.boards],
          ['Колонки', stats.columns],
          ['Карточки', stats.cards],
          ['Комментарии', stats.comments],
          ['Метки', stats.labels],
        ]" :key="label" class="bg-card border border-border rounded-xl p-4 text-center">
          <p class="text-2xl font-bold">{{ val }}</p>
          <p class="text-xs text-muted-foreground mt-0.5">{{ label }}</p>
        </div>
      </div>
      <div v-else-if="loading" class="grid grid-cols-6 gap-3">
        <div v-for="i in 6" :key="i" class="h-20 bg-card border rounded-xl animate-pulse" />
      </div>

      <!-- Tabs -->
      <div class="flex gap-1 border-b border-border">
        <button
          v-for="t in [{ key: 'users', label: 'Пользователи' }, { key: 'boards', label: 'Доски' }]"
          :key="t.key"
          class="px-4 py-2 text-sm font-medium transition-colors border-b-2 -mb-px"
          :class="tab === t.key
            ? 'border-foreground text-foreground'
            : 'border-transparent text-muted-foreground hover:text-foreground'"
          @click="tab = t.key as any"
        >{{ t.label }}</button>
      </div>

      <!-- Users table -->
      <div v-if="tab === 'users'" class="bg-card border border-border rounded-xl overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-muted border-b border-border">
            <tr>
              <th class="text-left px-4 py-3 font-medium text-muted-foreground">Имя</th>
              <th class="text-left px-4 py-3 font-medium text-muted-foreground">Email</th>
              <th class="text-left px-4 py-3 font-medium text-muted-foreground">Зарегистрирован</th>
              <th class="text-center px-4 py-3 font-medium text-muted-foreground">Досок</th>
              <th class="text-center px-4 py-3 font-medium text-muted-foreground">Роль</th>
              <th class="px-4 py-3" />
            </tr>
          </thead>
          <tbody class="divide-y divide-border">
            <tr v-if="loading">
              <td colspan="6" class="px-4 py-8 text-center text-muted-foreground">Загрузка...</td>
            </tr>
            <tr v-for="u in users" :key="u.id" class="hover:bg-muted/50 transition-colors">
              <td class="px-4 py-3 font-medium">
                <div class="flex items-center gap-2">
                  <div class="size-7 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-bold shrink-0">
                    {{ u.name[0].toUpperCase() }}
                  </div>
                  {{ u.name }}
                </div>
              </td>
              <td class="px-4 py-3 text-muted-foreground">{{ u.email }}</td>
              <td class="px-4 py-3 text-muted-foreground">{{ u.created_at }}</td>
              <td class="px-4 py-3 text-center">{{ u.board_count }}</td>
              <td class="px-4 py-3 text-center">
                <span
                  class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
                  :class="u.is_admin ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground border border-border'"
                >{{ u.is_admin ? 'Admin' : 'User' }}</span>
              </td>
              <td class="px-4 py-3 text-right">
                <Button
                  v-if="u.id !== auth.user?.id"
                  variant="outline"
                  size="xs"
                  :disabled="togglingId === u.id"
                  @click="toggleAdmin(u.id)"
                >{{ u.is_admin ? 'Снять admin' : 'Сделать admin' }}</Button>
                <span v-else class="text-xs text-muted-foreground">Это вы</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Boards table -->
      <div v-if="tab === 'boards'" class="bg-card border border-border rounded-xl overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-muted border-b border-border">
            <tr>
              <th class="text-left px-4 py-3 font-medium text-muted-foreground">Название</th>
              <th class="text-left px-4 py-3 font-medium text-muted-foreground">Описание</th>
              <th class="text-left px-4 py-3 font-medium text-muted-foreground">Владелец</th>
              <th class="text-center px-4 py-3 font-medium text-muted-foreground">Участников</th>
              <th class="text-center px-4 py-3 font-medium text-muted-foreground">Карточек</th>
              <th class="px-4 py-3" />
            </tr>
          </thead>
          <tbody class="divide-y divide-border">
            <tr v-if="loading">
              <td colspan="5" class="px-4 py-8 text-center text-muted-foreground">Загрузка...</td>
            </tr>
            <tr v-for="b in boards" :key="b.id" class="hover:bg-muted/50 transition-colors">
              <td class="px-4 py-3 font-medium">{{ b.title }}</td>
              <td class="px-4 py-3 text-muted-foreground max-w-[200px] truncate">{{ b.description || '—' }}</td>
              <td class="px-4 py-3">
                <div>
                  <p class="font-medium">{{ b.owner_name }}</p>
                  <p class="text-xs text-muted-foreground">{{ b.owner_email }}</p>
                </div>
              </td>
              <td class="px-4 py-3 text-center">{{ b.member_count }}</td>
              <td class="px-4 py-3 text-center">{{ b.card_count }}</td>
              <td class="px-4 py-3 text-right">
                <Button variant="ghost" size="xs" @click="router.push(`/boards/${b.id}`)">
                  Открыть →
                </Button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </main>
  </div>
</template>
