<script setup lang="ts">
import type { Model } from '../api/opencode'

defineProps<{
  models: Model[]
  currentModel: string
  isLoading: boolean
}>()

const emit = defineEmits<{
  'model-change': [modelId: string]
  settings: []
  compact: []
  interrupt: []
}>()
</script>

<template>
  <header class="top-bar">
    <div class="top-bar-left">
      <select
        class="model-select"
        :value="currentModel"
        @change="emit('model-change', ($event.target as HTMLSelectElement).value)"
      >
        <option v-for="model in models" :key="model.id" :value="model.id">
          {{ model.name || model.id }}
        </option>
      </select>
    </div>

    <div class="top-bar-right">
      <button
        v-if="isLoading"
        class="action-btn interrupt-btn"
        @click="emit('interrupt')"
        title="停止生成"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="6" y="6" width="12" height="12" rx="2" />
        </svg>
      </button>

      <button class="action-btn" @click="emit('compact')" title="压缩上下文">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 14h6v6M4 20l6-6M20 10h-6V4M20 4l-6 6" />
        </svg>
      </button>

      <button class="action-btn" @click="emit('settings')" title="设置">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3" />
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
        </svg>
      </button>
    </div>
  </header>
</template>

<style scoped>
.top-bar {
  height: 56px;
  background: #fff;
  border-bottom: 1px solid #e5e5e5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.top-bar-left {
  display: flex;
  align-items: center;
}

.model-select {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  background: #fff;
  cursor: pointer;
  outline: none;
  transition: border-color 0.2s;
}

.model-select:hover {
  border-color: #ccc;
}

.model-select:focus {
  border-color: #4a9eff;
}

.top-bar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #f0f0f0;
  color: #333;
}

.action-btn svg {
  width: 18px;
  height: 18px;
}

.interrupt-btn {
  background: #fff0f0;
  color: #ff4444;
}

.interrupt-btn:hover {
  background: #ffe0e0;
  color: #cc0000;
}
</style>
