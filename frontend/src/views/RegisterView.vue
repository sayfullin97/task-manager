<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Card from '@/components/ui/Card.vue'

const router = useRouter()
const auth = useAuthStore()

const name = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  if (!name.value || !email.value || !password.value) return
  loading.value = true
  error.value = ''
  try {
    await auth.register(email.value, password.value, name.value)
    router.push('/boards')
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-muted/30">
    <Card class="w-full max-w-md p-8 space-y-6">
      <div class="space-y-2 text-center">
        <h1 class="text-2xl font-bold">Create account</h1>
        <p class="text-muted-foreground text-sm">Start managing your tasks today</p>
      </div>

      <form class="space-y-4" @submit.prevent="submit">
        <div class="space-y-1">
          <label class="text-sm font-medium">Name</label>
          <Input v-model="name" placeholder="Your name" />
        </div>
        <div class="space-y-1">
          <label class="text-sm font-medium">Email</label>
          <Input v-model="email" type="email" placeholder="you@example.com" />
        </div>
        <div class="space-y-1">
          <label class="text-sm font-medium">Password</label>
          <Input v-model="password" type="password" placeholder="••••••••" />
        </div>

        <p v-if="error" class="text-destructive text-sm">{{ error }}</p>

        <Button type="submit" class="w-full" :disabled="loading">
          {{ loading ? 'Creating account...' : 'Create account' }}
        </Button>
      </form>

      <p class="text-center text-sm text-muted-foreground">
        Already have an account?
        <RouterLink to="/login" class="text-primary hover:underline font-medium">Sign in</RouterLink>
      </p>
    </Card>
  </div>
</template>
