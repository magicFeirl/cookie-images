<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  label: {
    type: String,
    default: '筛选',
  },
  // 每组：{ key, label, options: string[], single?: boolean }
  // single=true 时为单选（无"全部"选项），默认选第一个
  // single=false/undefined 时为多选，含"全部"选项
  groups: {
    type: Array,
    default: () => [
      { key: 'types', label: '类型',    options: ['Pixiv', 'X', 'NicoSeiga'] },
      { key: 'users', label: '搬运用户', options: ['UserA', 'UserB', 'UserC'] },
    ],
  },
})

const emit = defineEmits(['change'])

const isOpen = ref(false)

// 初始 selected：单选取第一项（字符串），多选取 ['全部']
const selected = ref(
  Object.fromEntries(
    props.groups.map(g => [g.key, g.single ? g.options[0] : ['全部']])
  )
)

function isChecked(groupKey, value) {
  const g = props.groups.find(x => x.key === groupKey)
  return g?.single
    ? selected.value[groupKey] === value
    : selected.value[groupKey].includes(value)
}

function toggle(groupKey, value) {
  const g = props.groups.find(x => x.key === groupKey)
  if (g?.single) {
    selected.value[groupKey] = value
  } else if (value === '全部') {
    selected.value[groupKey] = ['全部']
  } else {
    const without = selected.value[groupKey].filter(v => v !== '全部')
    const idx = without.indexOf(value)
    if (idx !== -1) {
      const next = without.filter(v => v !== value)
      selected.value[groupKey] = next.length ? next : ['全部']
    } else {
      selected.value[groupKey] = [...without, value]
    }
  }
  emit('change', JSON.parse(JSON.stringify(selected.value)))
}

// 按钮徽标：非默认状态的选项数
const activeCount = computed(() =>
  props.groups.reduce((n, g) => {
    if (g.single) return n + (selected.value[g.key] !== g.options[0] ? 1 : 0)
    return n + (selected.value[g.key].includes('全部') ? 0 : selected.value[g.key].length)
  }, 0)
)

const wrapperRef = ref(null)
function onDocumentClick(e) {
  if (wrapperRef.value && !wrapperRef.value.contains(e.target)) isOpen.value = false
}
onMounted(() => document.addEventListener('click', onDocumentClick))
onUnmounted(() => document.removeEventListener('click', onDocumentClick))
</script>

<template>
  <div class="filter-wrap" ref="wrapperRef">
    <button class="filter-btn" :class="{ active: activeCount > 0 }" @click="isOpen = !isOpen">
      <span>{{ label }}</span>
      <span v-if="activeCount > 0" class="badge">{{ activeCount }}</span>
      <span class="arrow" :class="{ open: isOpen }">▾</span>
    </button>

    <Transition name="dropdown">
      <div v-if="isOpen" class="panel" @click.stop>
        <div
          v-for="(group, gi) in groups"
          :key="group.key"
          class="group"
          :class="{ 'has-divider': gi > 0 }"
        >
          <p class="group-label">{{ group.label }}</p>

          <!-- 多选专属：全部选项 -->
          <label v-if="!group.single" class="option">
            <input
              type="checkbox"
              :checked="isChecked(group.key, '全部')"
              @change="toggle(group.key, '全部')"
            />
            <span>全部</span>
          </label>

          <!-- 各选项：单选用 radio，多选用 checkbox -->
          <label v-for="opt in group.options" :key="opt" class="option">
            <input
              :type="group.single ? 'radio' : 'checkbox'"
              :name="group.single ? group.key : undefined"
              :checked="isChecked(group.key, opt)"
              @change="toggle(group.key, opt)"
            />
            <span>{{ opt }}</span>
          </label>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.filter-wrap {
  position: relative;
  flex-shrink: 0;
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 7px 14px;
  border: 1px solid #ddd;
  border-radius: 20px;
  background: #fff;
  font-size: 13px;
  cursor: pointer;
  color: #555;
  transition: border-color 0.2s, color 0.2s;
  white-space: nowrap;
}

.filter-btn.active,
.filter-btn:hover {
  border-color: #646cff;
  color: #646cff;
}

.badge {
  background: #646cff;
  color: #fff;
  border-radius: 10px;
  font-size: 11px;
  padding: 1px 6px;
  line-height: 1.4;
}

.arrow {
  font-size: 11px;
  transition: transform 0.2s;
  display: inline-block;
}

.arrow.open {
  transform: rotate(180deg);
}

.panel {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  min-width: 160px;
  z-index: 200;
  overflow: hidden;
}

.group {
  padding: 12px 16px;
}

.group.has-divider {
  border-top: 1px solid #f0f0f0;
}

.group-label {
  font-size: 11px;
  font-weight: 600;
  color: #aaa;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 0;
  cursor: pointer;
  font-size: 13px;
  color: #333;
  user-select: none;
}

.option input {
  width: 15px;
  height: 15px;
  accent-color: #646cff;
  cursor: pointer;
  flex-shrink: 0;
}

.option:hover span {
  color: #646cff;
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
