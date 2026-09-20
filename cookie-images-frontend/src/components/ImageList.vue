<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import ImageListItem from './ImageListItem.vue'

const props = defineProps({
  images:      { type: Array,   required: true },
  searching:   { type: Boolean, default: false }, // 搜索加载中 → 骨架屏
  loadingMore: { type: Boolean, default: false }, // 无限滚动加载中 → 底部提示
})
const emit = defineEmits(['open', 'load-more'])

// ── 虚拟列表 ──────────────────────────────────
const GAP = 20
const BUFFER_ROWS = 3
const SKELETON_COUNT = 12

const gridRef    = ref(null)
const sentinelRef = ref(null)
const scrollY    = ref(window.scrollY)
const numCols    = ref(4)
const itemHeight = ref(240)
const gridTop    = ref(0)

const rowHeight = computed(() => itemHeight.value + GAP)
const numRows   = computed(() => Math.ceil(props.images.length / numCols.value))

const firstRow  = computed(() =>
  Math.max(0, Math.floor((scrollY.value - gridTop.value) / rowHeight.value) - BUFFER_ROWS))
const lastRow   = computed(() =>
  Math.min(numRows.value - 1,
    Math.ceil((scrollY.value - gridTop.value + window.innerHeight) / rowHeight.value) + BUFFER_ROWS))

const startIdx      = computed(() => firstRow.value * numCols.value)
const endIdx        = computed(() => Math.min((lastRow.value + 1) * numCols.value, props.images.length))
const visibleImages = computed(() => props.images.slice(startIdx.value, endIdx.value))
const paddingTop    = computed(() => firstRow.value * rowHeight.value)
const paddingBottom = computed(() => Math.max(0, (numRows.value - lastRow.value - 1) * rowHeight.value))

function measure() {
  if (!gridRef.value) return
  const cols = getComputedStyle(gridRef.value).gridTemplateColumns.split(' ').length
  numCols.value = cols
  const card = gridRef.value.querySelector('.card')
  if (card) itemHeight.value = card.offsetHeight
  gridTop.value = gridRef.value.getBoundingClientRect().top + window.scrollY
}

function scrollToIdx(idx) {
  const img = props.images[idx]
  if (!img) return
  const el = document.querySelector(`[data-image-id="${img.id}"]`)
  if (el) {
    const rect = el.getBoundingClientRect()
    const y = window.scrollY + rect.top - window.innerHeight / 2 + el.offsetHeight / 2
    window.scrollTo({ top: Math.max(0, y), behavior: 'smooth' })
    return
  }
  const row = Math.floor(idx / numCols.value)
  const y = gridTop.value + row * rowHeight.value - window.innerHeight / 2 + itemHeight.value / 2
  window.scrollTo({ top: Math.max(0, y), behavior: 'smooth' })
}

defineExpose({ scrollToIdx })

function onScroll() { scrollY.value = window.scrollY }

let ro, io

onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
  nextTick(() => {
    measure()
    ro = new ResizeObserver(measure)
    ro.observe(gridRef.value)
    io = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && !props.loadingMore && !props.searching) emit('load-more')
    })
    io.observe(sentinelRef.value)
  })
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  ro?.disconnect()
  io?.disconnect()
})

watch(() => props.images.length, () => nextTick(measure))
</script>

<template>
  <main class="image-list-wrap">

    <!-- 骨架屏：搜索加载中 -->
    <div v-if="searching" class="image-grid">
      <div v-for="n in SKELETON_COUNT" :key="n" class="skeleton-card">
        <div class="skeleton-img" />
        <div class="skeleton-info">
          <div class="skeleton-line" style="width: 68%" />
          <div class="skeleton-line" style="width: 42%" />
        </div>
      </div>
    </div>

    <!-- 正常内容 -->
    <template v-else>
      <div v-if="images.length === 0" class="state-tip">暂无图片</div>
      <template v-else>
        <div
          ref="gridRef"
          class="image-grid"
          :style="{ paddingTop: paddingTop + 'px', paddingBottom: paddingBottom + 'px' }"
        >
          <ImageListItem
            v-for="(img, i) in visibleImages"
            :key="img.id"
            :image="img"
            @open="emit('open', startIdx + i)"
          />
        </div>

        <div ref="sentinelRef" class="sentinel" />
        <div v-if="loadingMore" class="loading-more">加载中...</div>
      </template>
    </template>

  </main>
</template>

<style scoped>
.image-list-wrap {
  max-width: 1400px;
  margin: 0 auto;
  padding: 28px 24px 60px;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}

/* ── 骨架屏 ── */
@keyframes shimmer {
  0%   { background-position: -200% 0; }
  100% { background-position:  200% 0; }
}

.skeleton-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.skeleton-img {
  aspect-ratio: 3 / 2;
  background: linear-gradient(90deg, #efefef 25%, #e3e3e3 50%, #efefef 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s ease-in-out infinite;
}

.skeleton-info {
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-line {
  height: 13px;
  border-radius: 4px;
  background: linear-gradient(90deg, #efefef 25%, #e3e3e3 50%, #efefef 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s ease-in-out infinite;
}

/* ── 其他 ── */
.state-tip {
  text-align: center;
  padding: 80px 0;
  color: #aaa;
  font-size: 15px;
}

.sentinel {
  height: 1px;
}

.loading-more {
  text-align: center;
  padding: 20px 0;
  color: #aaa;
  font-size: 14px;
}
</style>
