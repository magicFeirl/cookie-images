<script setup>
import { ref, reactive, onMounted } from 'vue'
import AppHeader from './components/AppHeader.vue'
import ImageList from './components/ImageList.vue'
import ImageLightbox from './components/ImageLightbox.vue'
import { searchImages } from './http/index.js'

// 查询参数表单
const searchForm = reactive({
  pn:          1,       // 页码
  ps:          20,      // 每页数量
  order:       'default',  // default | random | time_asc（对应 SortDropdown 第一项）
  filter_type: ['all'],    // ['all'] = 全部；['pixiv','x'] 等组合（对应 FilterDropdown）
  filter_user: [],         // [] = 全部；[343118157, ...] = 特定用户 UID 列表
})

// sort dropdown 选项 → order 字段映射
const ORDER_MAP = {
  '默认（时间正序）': 'default',
  '随机排序':        'random',
  '时间倒序':        'time_asc',
}

// filter dropdown type 选项 → filter_type 字段映射
const TYPE_MAP = { Pixiv: 'pixiv', X: 'x', NicoSeiga: 'nico' }

// filter dropdown user 选项 → UID 映射
const USER_MAP = {
  '银饼综合推送bot':     343118157,
  'クッキー_イラストBot': 495374011,
  '时云_饼图搬运':       161770294,
  '时云_电脑网后门':     407529244,
}

// 从 localStorage 恢复 sort/filter，与 FilterDropdown 保持同步
function applyStoredFilters() {
  try {
    const sort = JSON.parse(localStorage.getItem('ck_sort') ?? 'null')
    if (sort?.sort) searchForm.order = ORDER_MAP[sort.sort] ?? searchForm.order
  } catch {}
  try {
    const filter = JSON.parse(localStorage.getItem('ck_filter') ?? 'null')
    if (filter) {
      const types = filter.types ?? []
      searchForm.filter_type = types.includes('全部') || !types.length
        ? ['all']
        : types.map(t => TYPE_MAP[t] ?? t)

      const users = filter.users ?? []
      searchForm.filter_user = users.includes('全部') || !users.length
        ? []
        : users.map(u => USER_MAP[u]).filter(Boolean)
    }
  } catch {}
}
applyStoredFilters()

let initialized = false   // onMounted 完成前不因 filter 变化重复触发搜索
let filterTimer = null

const allImages = ref([])
const isSearching = ref(false)   // 搜索/初始加载中 → 骨架屏
const isLoadingMore = ref(false) // 下拉加载更多 → 底部提示
let currentQuery = ''
let hasMore = true

// 搜索：关闭灯箱 → 骨架屏 → 请求 API
async function doSearch(query) {
  activeIndex.value = null
  isSearching.value = true
  allImages.value = []
  searchForm.pn = 1
  currentQuery = query
  hasMore = true

  try {
    const result = await searchImages(searchForm, query)
    allImages.value = result.images
    if (result.images.length < searchForm.ps) hasMore = false
    window.scrollTo({ top: 0, behavior: 'instant' })
  } finally {
    isSearching.value = false
  }
}

// 无限滚动加载更多
async function loadMore() {
  if (isLoadingMore.value || isSearching.value || !hasMore) return
  isLoadingMore.value = true
  searchForm.pn++

  try {
    const result = await searchImages(searchForm, currentQuery)
    allImages.value.push(...result.images)
    if (result.images.length < searchForm.ps) hasMore = false
  } finally {
    isLoadingMore.value = false
  }
}

const activeIndex = ref(null)
const imageListRef = ref(null)
const searchQuery = ref('')

function onImageLoaded(idx) {
  imageListRef.value?.scrollToIdx(idx)
}

function onSearch(query) {
  searchQuery.value = query
  doSearch(query)
}

function onTagClick(tag) {
  searchQuery.value = tag
  doSearch(tag)
}

function onSortChange(selected) {
  searchForm.order = ORDER_MAP[selected['sort']] ?? 'default'
  if (initialized) doSearch(currentQuery)
}

function onFilterChange(selected) {
  const types = selected['types'] ?? []
  searchForm.filter_type = types.includes('全部') || !types.length
    ? ['all']
    : types.map(t => TYPE_MAP[t] ?? t)

  const users = selected['users'] ?? []
  searchForm.filter_user = users.includes('全部') || !users.length
    ? []
    : users.map(u => USER_MAP[u]).filter(Boolean)

  if (!initialized) return
  clearTimeout(filterTimer)
  filterTimer = setTimeout(() => doSearch(currentQuery), 400)
}

function goHome() {
  searchQuery.value = ''
  doSearch('')
}

onMounted(async () => {
  try {
    await doSearch('')
  } finally {
    initialized = true
  }
})
</script>

<template>
  <div class="page">
    <AppHeader
      title="饼图站"
      v-model:searchQuery="searchQuery"
      @search="onSearch"
      @home="goHome"
      @sort-change="onSortChange"
      @filter-change="onFilterChange"
    />
    <ImageList
      ref="imageListRef"
      :images="allImages"
      :searching="isSearching"
      :loading-more="isLoadingMore"
      @open="activeIndex = $event"
      @load-more="loadMore"
    />
    <ImageLightbox
      :images="allImages"
      v-model="activeIndex"
      @image-loaded="onImageLoaded"
      @tag-click="onTagClick"
    />
  </div>
</template>

<style>
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #f5f5f7;
  color: #1a1a2e;
}

.page {
  min-height: 100vh;
}
</style>
