<script setup>
import FilterDropdown from './FilterDropdown.vue'
import SortDropdown from './SortDropdown.vue'

defineProps({
  title: { type: String, default: '饼图站' },
  searchQuery: { type: String, default: '' },
})

defineEmits(['filter-change', 'sort-change', 'update:searchQuery', 'search', 'home'])
</script>

<template>
  <header class="header">
    <div class="header-inner">
      <div class="logo" @click="$emit('home')">
        <span class="logo-icon">◈</span>
        <span class="logo-text">{{ title }}</span>
      </div>
      <div class="right">
        <SortDropdown @change="$emit('sort-change', $event)" />
        <FilterDropdown @change="$emit('filter-change', $event)" />
        <div class="search">
          <input
            type="text"
            placeholder="搜索图片..."
            :value="searchQuery"
            @input="$emit('update:searchQuery', $event.target.value)"
            @keydown.enter="$emit('search', searchQuery)"
          />
          <button
            v-if="searchQuery"
            class="clear-btn"
            @click="$emit('update:searchQuery', ''); $emit('search', '')"
            title="清除"
          >✕</button>
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
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
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
  font-size: 22px;
  color: #646cff;
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
  padding: 7px 32px 7px 14px;
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
  right: 90px;
  background: none;
  border: none;
  color: #aaa;
  font-size: 12px;
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 50%;
  line-height: 1;
  transition: color 0.15s;
}

.clear-btn:hover {
  color: #555;
  background: none;
}
</style>
