import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isAuthenticated = computed(() => !!user.value)

  function loadFromStorage() {
    const token = localStorage.getItem('access_token')
    if (!token) return false
    return true
  }

  async function fetchMe() {
    try {
      const { data } = await authApi.me()
      user.value = data
      return true
    } catch {
      return false
    }
  }

  async function login(email: string, password: string) {
    const { data } = await authApi.login(email, password)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    user.value = data.user
  }

  async function register(email: string, password: string, name: string) {
    const { data } = await authApi.register(email, password, name)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    user.value = data.user
  }

  function logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    user.value = null
  }

  return { user, isAuthenticated, loadFromStorage, fetchMe, login, register, logout }
})
