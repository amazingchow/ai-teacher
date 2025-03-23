<template>
  <div class="min-h-screen bg-gray-50">
    <router-view></router-view>
    <Toast />
  </div>
</template>

<script setup>
import Toast from 'primevue/toast'
</script>