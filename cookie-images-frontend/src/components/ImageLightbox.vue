<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import ImageInfoDrawer from './ImageInfoDrawer.vue'
import { FULL_SUFFIX } from '../config.js'

const props = defineProps({
  images: { type: Array, default: () => [] },
  modelValue: { type: Number, default: null }, // 当前下标，null = 关闭
})

const emit = defineEmits(['update:modelValue', 'image-loaded', 'tag-click'])

const zoomed = ref(false)
const drawerOpen = ref(false)

const isOpen = computed(() => props.modelValue !== null && props.modelValue !== undefined)
const activeImage = computed(() => isOpen.value ? props.images[props.modelValue] : null)
const hasInfo = computed(() => !!activeImage.value?.info)

// 切换图片时重置缩放
watch(() => props.modelValue, () => {
  zoomed.value = false
})

// 锁定/恢复 body 滚动条
watch(isOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : ''
}, { immediate: true })

onUnmounted(() => { document.body.style.overflow = '' })

function close() { emit('update:modelValue', null) }

function onBackdropClick() {
  if (drawerOpen.value) drawerOpen.value = false
  else close()
}
function prev() { if (props.modelValue > 0) emit('update:modelValue', props.modelValue - 1) }
function next() { if (props.modelValue < props.images.length - 1) emit('update:modelValue', props.modelValue + 1) }

// 键盘
function onKeydown(e) {
  if (!isOpen.value) return
  if (e.key === 'Escape') { if (drawerOpen.value) drawerOpen.value = false; else close() }
  if (e.key === 'ArrowLeft') prev()
  if (e.key === 'ArrowRight') next()
}

// 滚轮切换（节流防止连跳）
let wheelLocked = false
function onWheel(e) {
  if (wheelLocked) return
  const delta = Math.abs(e.deltaY) >= Math.abs(e.deltaX) ? e.deltaY : e.deltaX
  if (delta > 0) next()
  else if (delta < 0) prev()
  wheelLocked = true
  setTimeout(() => { wheelLocked = false }, 350)
}

// 触摸滑动
let touchStartX = 0
function onTouchStart(e) { touchStartX = e.touches[0].clientX }
function onTouchEnd(e) {
  const dx = e.changedTouches[0].clientX - touchStartX
  if (Math.abs(dx) < 50) return
  if (dx > 0) prev()
  else next()
}

onMounted(() => document.addEventListener('keydown', onKeydown))
onUnmounted(() => document.removeEventListener('keydown', onKeydown))
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="isOpen"
        class="backdrop"
        @click="onBackdropClick"
        @wheel.prevent="onWheel"
        @touchstart.passive="onTouchStart"
        @touchend.passive="onTouchEnd"
      >
        <!-- 关闭按钮（右上） -->
        <button class="corner-btn close-btn" @click="close">✕</button>

        <!-- 信息抽屉开关（左上，仅有 info 时显示） -->
        <button
          v-if="hasInfo"
          class="corner-btn info-btn"
          :class="{ active: drawerOpen }"
          @click.stop="drawerOpen = !drawerOpen"
          title="图片信息"
        >!</button>

        <!-- 信息抽屉 -->
        <Transition name="drawer-slide">
          <ImageInfoDrawer
            v-if="drawerOpen && hasInfo"
            :info="activeImage.info"
            :dyn-id="activeImage.dynId"
            :src="activeImage.src + FULL_SUFFIX"
            @tag-click="emit('tag-click', $event)"
          />
        </Transition>

        <!-- 图片 -->
        <div class="img-wrap">
          <img
            :src="activeImage.src + FULL_SUFFIX"
            :alt="activeImage.title"
            :class="{ zoomed }"
            @click.stop="zoomed = !zoomed"
            @load="emit('image-loaded', modelValue)"
          />
        </div>

        <!-- 底部信息 -->
        <div class="footer" @click.stop>
          <p class="footer-title">{{ activeImage.title }}</p>
          <p class="footer-counter">{{ modelValue + 1 }} / {{ images.length }}</p>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.backdrop {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.88);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: auto;
  padding: 60px 20px 24px;
}

/* 左上 / 右上角按钮公共样式 */
.corner-btn {
  position: fixed;
  top: 18px;
  z-index: 1001;
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s;
  line-height: 1;
}

.corner-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.close-btn { right: 24px; }

.info-btn  { left: 24px; }

.info-btn.active {
  background: rgba(100, 108, 255, 0.6);
}

/* 图片 */
.img-wrap {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  width: 100%;
}

.img-wrap img {
  max-width: 90vw;
  max-height: 80vh;
  width: auto;
  height: auto;
  object-fit: contain;
  border-radius: 6px;
  cursor: zoom-in;
  transform: scale(1);
  transform-origin: center center;
  transition: transform 0.3s ease, opacity 0.25s ease;
  user-select: none;
}

.img-wrap img.zoomed {
  transform: scale(1.5);
  cursor: zoom-out;
}


/* 底部 */
.footer {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding-top: 16px;
}

.footer-title   { color: #fff; font-size: 15px; font-weight: 600; }
.footer-author  { color: rgba(255,255,255,0.5); font-size: 13px; }
.footer-counter { margin-top: 4px; color: rgba(255,255,255,0.4); font-size: 12px; letter-spacing: 1px; }

/* 抽屉滑入动画 */
.drawer-slide-enter-active,
.drawer-slide-leave-active {
  transition: transform 0.28s ease;
}

.drawer-slide-enter-from,
.drawer-slide-leave-to {
  transform: translateX(-100%);
}

/* 灯箱淡入淡出 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
