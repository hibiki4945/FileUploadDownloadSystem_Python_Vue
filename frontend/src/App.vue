<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <header>
    <div class="wrapper">
      <!-- ホームページへ -->
      <nav>
        <RouterLink to="/">ホームページ</RouterLink>
      </nav>
    </div>
  </header>
  <br/>
  <!-- ホームページの内容 -->
  <div>
    <RouterView />
  </div>
</template>

<style scoped>
</style>
