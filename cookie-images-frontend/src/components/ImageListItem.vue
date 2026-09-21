<script setup>
import { computed } from 'vue'
import { THUMB_SUFFIX } from '../config.js'

const prop = defineProps({
  image: { type: Object, required: true },
})

const emit = defineEmits(['open'])

const postAt = computed(() => {
  if (!prop.image.ctime) return ''
  const d = new Date(prop.image.ctime * 1000)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
})
</script>

<template>
  <div class="card" :data-image-id="image.id" @click="emit('open')">
    <div class="card-img-wrap">
      <img :src="image.src + THUMB_SUFFIX" :alt="image.title" loading="lazy" />
      <div class="card-overlay">
        <span class="overlay-hint">查看大图</span>
      </div>
    </div>
    <div class="card-info">
      <p class="card-title">{{ image.title }}</p>
      <div class="card-meta">
        <span class="card-author">{{ postAt }}</span>
        <div class="card-stats">
          <span>♥ {{ image.likes }}</span>
          <span>◎ {{ image.views }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.25s, box-shadow 0.25s;
  cursor: pointer;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.14);
}

.card-img-wrap {
  position: relative;
  aspect-ratio: 3 / 2;
  overflow: hidden;
  background: #f0f0f0;
}

.card-img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: top;
  transition: transform 0.4s;
}

.card:hover .card-img-wrap img {
  transform: scale(1.06);
}

.card-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.25s;
}

.card:hover .card-overlay {
  opacity: 1;
}

.overlay-hint {
  padding: 8px 20px;
  background: #fff;
  color: #333;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.card-info {
  padding: 12px 14px;
}

.card-title {
  margin: 0 0 8px;
  font-size: 14px;
  font-weight: 600;
  color: #1a1a2e;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-author {
  font-size: 12px;
  color: #888;
}

.card-stats {
  display: flex;
  gap: 10px;
  font-size: 12px;
  color: #aaa;
}
</style>
