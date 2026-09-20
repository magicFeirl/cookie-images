<script setup>
import FilterDropdown from './FilterDropdown.vue'

const emit = defineEmits(['change'])

const sortGroups = [
  {
    key: 'sort',
    label: '排序方式',
    options: ['默认（时间正序）', '随机排序', '时间倒序'],
    single: true,
  },
]
</script>

<template>
  <FilterDropdown label="排序" :groups="sortGroups" @change="emit('change', $event)" />
</template>
