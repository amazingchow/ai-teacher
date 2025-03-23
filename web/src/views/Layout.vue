<template>
  <div class="flex h-screen">
    <!-- Sidebar -->
    <div class="w-64 bg-white shadow-lg">
      <div class="p-4 bg-blue-600">
        <h1 class="text-white text-xl font-bold">AI Teacher</h1>
      </div>
      <nav class="mt-4">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="flex items-center px-4 py-2 text-gray-700 hover:bg-blue-50"
          :class="{ 'bg-blue-50 text-blue-600': isActive(item.path) }"
        >
          <i :class="item.icon" class="mr-2"></i>
          {{ item.name }}
        </router-link>
      </nav>
    </div>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Header -->
      <header class="bg-white shadow-sm">
        <div class="px-4 py-3">
          <h2 class="text-lg font-semibold text-gray-800">
            {{ currentRouteName }}
          </h2>
        </div>
      </header>

      <!-- Page Content -->
      <main class="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 p-6">
        <router-view></router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const menuItems = [
  { name: '学生管理', path: '/students', icon: 'pi pi-users' },
  { name: '题库管理', path: '/questions', icon: 'pi pi-book' },
  { name: '课本背诵', path: '/recite', icon: 'pi pi-microphone' }
]

const currentRouteName = computed(() => {
  const currentRoute = menuItems.find(item => item.path === route.path)
  return currentRoute ? currentRoute.name : ''
})

const isActive = (path) => route.path === path
</script>