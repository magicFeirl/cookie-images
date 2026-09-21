<script setup>
import FilterDropdown from './FilterDropdown.vue'
import SortDropdown from './SortDropdown.vue'

defineProps({
  title: { type: String, default: '饼图站' },
  searchQuery: { type: String, default: '' },
})

defineEmits(['filter-change', 'sort-change', 'update:searchQuery', 'search', 'home'])

const filterGroups = [
  { key: 'types', label: '类型', options: ['Pixiv', 'X', 'NicoSeiga'] },
  {
    key: 'users',
    label: '搬运用户',
    options: ['银饼综合推送bot', 'クッキー_イラストBot', '时云_饼图搬运', '时云_电脑网后门'],
  },
]
</script>

<template>
  <header class="header">
    <div class="header-inner">
      <div class="logo" @click="$emit('home')">
        <img class="logo-icon" src="/favicon.ico" alt="logo" />
        <span class="logo-text">{{ title }}</span>
      </div>
      <div class="right">
        <SortDropdown storage-key="ck_sort" @change="$emit('sort-change', $event)" />
        <FilterDropdown :groups="filterGroups" storage-key="ck_filter" @change="$emit('filter-change', $event)" />
        <div class="search">
          <input type="text" placeholder="搜索图片..." :value="searchQuery"
            @input="$emit('update:searchQuery', $event.target.value)" @keydown.enter="$emit('search', searchQuery)" />
          <button v-if="searchQuery" class="clear-btn" @click="$emit('update:searchQuery', ''); $emit('search', '')"
            title="清除">✕</button>
          <button @click="$emit('search', searchQuery)">搜索</button>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.06);
}

.header-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  min-height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}

.logo:hover .logo-text {
  color: #646cff;
}

.logo-icon {
  width: 28px;
  height: 28px;
  object-fit: contain;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a2e;
  letter-spacing: 0.5px;
}

.right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
}

.search input {
  width: 220px;
  padding: 7px 0px 7px 14px;
  border: 1px solid #ddd;
  border-radius: 20px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
}

.search input:focus {
  border-color: #646cff;
}

.search button {
  padding: 7px 18px;
  background: #646cff;
  color: #fff;
  border: none;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}

.search button:hover {
  background: #535bf2;
}

.clear-btn {
  position: absolute;
  right: 72px;
  background: none;
  border: none;
  color: #ccc;
  font-size: 10px;
  cursor: pointer;
  border-radius: 50%;
  line-height: 1;
  opacity: 0.6;
  transition: opacity 0.15s, color 0.15s;
}

.clear-btn:hover {
  color: #888;
  opacity: 1;
  background: none;
}

/* 中等宽度：缩小搜索框 */
@media (max-width: 900px) {
  .search input {
    width: 140px;
  }
}

/* 窄屏：工具栏换行，搜索框撑满 */
@media (max-width: 640px) {
  .logo {
    display: none;
  }

  .header-inner {
    padding: 10px 16px;
  }

  .right {
    width: 100%;
    gap: 6px;
  }

  .search {
    flex: 1;
    min-width: 0;
  }

  .search input {
    width: 0;
    flex: 1;
    min-width: 0;
  }
}
</style>
