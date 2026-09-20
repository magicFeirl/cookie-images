<script setup>
import { ref, onMounted } from 'vue'
import AppHeader from './components/AppHeader.vue'
import ImageList from './components/ImageList.vue'
import ImageLightbox from './components/ImageLightbox.vue'

const initialImages = [
  {
    id: 1, src: 'https://picsum.photos/seed/1/600/400', title: '晨曦中的山峦', author: 'Alice', likes: 312, views: 4820,
    info: `絵柄がシイティっぽいなNYN姉貴\nPixiv ID: 149802306\n投稿者(id=57754852): ニシアカ_Nishiaka\n\nNYN姉貴 | クッキー☆ | ネズミ`,
  },
  {
    id: 2, src: 'https://picsum.photos/seed/2/600/400', title: '静谧的湖面', author: 'Bob', likes: 198, views: 3100,
    info: `im11768942\nウェディングフォトRRHS\n投稿者: Rio (/user/illust/139333122)\n\nキャラクター | クッキー☆ | RRM姉貴 | HSKRHSB | 刀剣淫夢 | RRHS`,
  },
  {
    id: 3, src: 'https://picsum.photos/seed/3/600/400', title: '城市夜景', author: 'Carol', likes: 540, views: 8900,
    info: `投稿者: 午前二時デフォメト\nおねがい…♡\n\n1878604988479598834`,
  },
  { id: 4,  src: 'https://picsum.photos/seed/4/600/400',  title: '秋日落叶',  author: 'Dave',  likes: 87,  views: 1200 },
  { id: 5,  src: 'https://picsum.photos/seed/5/600/400',  title: '海边日落',  author: 'Eva',   likes: 420, views: 6300 },
  { id: 6,  src: 'https://picsum.photos/seed/6/600/400',  title: '雪山远眺',  author: 'Frank', likes: 260, views: 4100 },
  { id: 7,  src: 'https://picsum.photos/seed/7/600/400',  title: '森林小径',  author: 'Grace', likes: 155, views: 2700 },
  { id: 8,  src: 'https://picsum.photos/seed/8/600/400',  title: '沙漠之夜',  author: 'Henry', likes: 330, views: 5500 },
  { id: 9,  src: 'https://picsum.photos/seed/9/600/400',  title: '春花烂漫',  author: 'Iris',  likes: 210, views: 3800 },
  { id: 10, src: 'https://picsum.photos/seed/10/600/400', title: '港湾渔船',  author: 'Jack',  likes: 99,  views: 1500 },
  { id: 11, src: 'https://picsum.photos/seed/11/600/400', title: '高原牧场',  author: 'Kate',  likes: 178, views: 2900 },
  { id: 12, src: 'https://picsum.photos/seed/12/600/400', title: '古镇黄昏',  author: 'Leo',   likes: 450, views: 7200 },
  { id: 13, src: 'https://i1.hdslb.com/bfs/new_dyn/3185ea7829dc5bd98cfc4b4a89079647343118157.png@1052w_!web-dynamic.avif', title: 'B站测试图',  author: 'Test', likes: 0, views: 0 },
  { id: 14, src: 'https://i1.hdslb.com/bfs/new_dyn/0e794f4ab5fb2d97a619dea734bf31c4343118157.jpg@1052w_!web-dynamic.avif', title: 'B站测试图2', author: 'Test', likes: 0, views: 0 },
]

const PAGE_SIZE = 12
let nextId = 1
let nextSeed = 1
let isFirstLoad = true

const allImages = ref([])
const isSearching = ref(false)  // 搜索/初始加载中 → 骨架屏
const isLoadingMore = ref(false) // 下拉加载更多 → 底部提示

// 搜索：关闭灯箱 → 骨架屏 → 100ms 后返回结果
async function doSearch(query) {
  activeIndex.value = null
  isSearching.value = true
  allImages.value = []

  await new Promise(r => setTimeout(r, 100))

  if (isFirstLoad && !query) {
    // 首次加载：返回预置图片
    allImages.value = [...initialImages]
    nextId = initialImages.length + 1
    nextSeed = 20
    isFirstLoad = false
  } else {
    // 后续搜索：生成模拟结果（seed 按 query 字符码偏移）
    const base = query
      ? query.split('').reduce((s, c) => s + c.charCodeAt(0), 0) % 800 + 100
      : Math.floor(Math.random() * 800) + 100
    nextSeed = base
    nextId = 1
    allImages.value = Array.from({ length: PAGE_SIZE }, (_, i) => ({
      id: nextId + i,
      src: `https://picsum.photos/seed/${nextSeed + i}/600/400`,
      title: query ? `${query} · 图片 ${nextId + i}` : `图片 ${nextId + i}`,
      author: `User${nextId + i}`,
      likes: Math.floor(Math.random() * 500),
      views: Math.floor(Math.random() * 9000) + 500,
    }))
    nextId += PAGE_SIZE
    nextSeed += PAGE_SIZE
  }

  isSearching.value = false
}

// 无限滚动加载更多
async function loadMore() {
  if (isLoadingMore.value || isSearching.value) return
  isLoadingMore.value = true
  await new Promise(r => setTimeout(r, 600))
  const batch = Array.from({ length: PAGE_SIZE }, (_, i) => ({
    id: nextId + i,
    src: `https://picsum.photos/seed/${nextSeed + i}/600/400`,
    title: `图片 ${nextId + i}`,
    author: `User${nextId + i}`,
    likes: Math.floor(Math.random() * 500),
    views: Math.floor(Math.random() * 9000) + 500,
  }))
  nextId += PAGE_SIZE
  nextSeed += PAGE_SIZE
  allImages.value.push(...batch)
  isLoadingMore.value = false
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

function goHome() {
  searchQuery.value = ''
  isFirstLoad = true
  doSearch('')
}

onMounted(() => doSearch(''))
</script>

<template>
  <div class="page">
    <AppHeader
      title="饼图站"
      v-model:searchQuery="searchQuery"
      @search="onSearch"
      @home="goHome"
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
