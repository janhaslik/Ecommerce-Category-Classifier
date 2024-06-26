<script setup lang="ts">
import classify from './views/classify.vue';
import finetune from './views/finetune.vue';
</script>

<script lang="ts">
export default {
  data() {
    return {
      page: "finetune",
      devmode: import.meta.env.VITE_DEVMODE
    }
  }
}
</script>

<template>
  <div class="nav">
    <div @click="page = 'finetune'">FineTune</div>
    <div @click="page = 'classify'">Classify</div>
  </div>

  <classify v-if="page == 'classify'" />
  <finetune v-else-if="page == 'finetune'" />

  <div v-if="devmode=='true'" class="devmode">Devmode ON</div>
  <div v-else class="devmode">Devmode OFF</div>
</template>

<style scoped>
.devmode {
  position: fixed;
  bottom: 1rem;
  right: 1rem;
}

.nav {
  user-select: none;
  display: flex;
  height: 2rem;
  box-shadow: 1px 1px black;
  padding: 0.5rem;
  gap: 1rem;
  justify-content: center;
}

.nav>* {
  padding: 5px;
  font-size: 20px;
  font-weight: bold;
  transition: 0.1s linear;
}

.nav>*:hover {
  color: goldenrod;
  transform: scale(1.1) rotate(2deg);
  cursor: pointer;
}
</style>