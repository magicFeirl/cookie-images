<script setup>
import { computed } from 'vue'

const props = defineProps({
  info: { type: String, required: true }, // 原始文本
})

const emit = defineEmits(['tag-click'])

// ─────────────────────────────────────────────
// 解析函数
// 支持三种来源格式，无法识别时返回 { source:'未知', raw }
// ─────────────────────────────────────────────
function parseInfo(text) {
  const lines = text.trim().split('\n').map(l => l.trim()).filter(Boolean)

  // ── Pixiv ──
  // 特征：含 "Pixiv ID: <数字>" 行 或 "投稿者(id=<数字>): <名>" 行
  const pixivIdLine    = lines.find(l => /^Pixiv ID:\s*\d+/.test(l))
  const pixivAuthorLine = lines.find(l => /^投稿者\(id=\d+\):/.test(l))
  if (pixivIdLine || pixivAuthorLine) {
    const pixivId = pixivIdLine?.match(/Pixiv ID:\s*(\d+)/)?.[1]
    const am      = pixivAuthorLine?.match(/^投稿者\(id=(\d+)\):\s*(.+)/)
    const tagLine = lines.find(l => l.includes(' | '))
    const used    = new Set([pixivIdLine, pixivAuthorLine, tagLine].filter(Boolean))
    return {
      source:   'Pixiv',
      title:    lines.find(l => !used.has(l)),
      pixivId,
      author:   am?.[2]?.trim(),
      authorId: am?.[1],
      tags:     tagLine?.split(' | ').map(t => t.trim()) ?? [],
    }
  }

  // ── NicoSeiga ──
  // 特征：含独立的 "im<数字>" 行
  const nicoseigaIdLine = lines.find(l => /^im\d+$/.test(l))
  if (nicoseigaIdLine) {
    const authorLine = lines.find(l => /^投稿者:\s/.test(l))
    // 格式：投稿者: Name (/user/...)
    const am         = authorLine?.match(/^投稿者:\s*(.+?)\s*\((.+)\)$/)
    const tagLine    = lines.find(l => l.includes(' | '))
    const used       = new Set([nicoseigaIdLine, authorLine, tagLine].filter(Boolean))
    return {
      source:       'NicoSeiga',
      nicoseigaId:  nicoseigaIdLine,
      title:        lines.find(l => !used.has(l)),
      author:       am?.[1]?.trim() ?? authorLine?.replace(/^投稿者:\s*/, ''),
      authorLink:   am?.[2],
      tags:         tagLine?.split(' | ').map(t => t.trim()) ?? [],
    }
  }

  // ── X ──
  // 特征：含 "投稿者: <名>"（无括号 id/link），或含 15 位以上纯数字行（post ID）
  const xAuthorLine = lines.find(l => /^投稿者:\s/.test(l) && !/\(id=/.test(l) && !/\(\/user\//.test(l))
  const postIdLine  = lines.find(l => /^\d{15,}$/.test(l))
  if (xAuthorLine || postIdLine) {
    const used    = new Set([xAuthorLine, postIdLine].filter(Boolean))
    const caption = lines.filter(l => !used.has(l)).join('\n') || undefined
    return {
      source:  'X',
      author:  xAuthorLine?.replace(/^投稿者:\s*/, ''),
      caption,
      postId:  postIdLine,
    }
  }

  // ── 未知 ──
  return { source: '未知', raw: text }
}

const parsed = computed(() => parseInfo(props.info))

// 投稿者点击的搜索词：优先用 id，无 id 用名字
const authorSearchTerm = computed(() => {
  const p = parsed.value
  if (p.source === 'Pixiv')     return p.authorId || p.author || null
  if (p.source === 'NicoSeiga') return /(\d+)$/.exec(p.authorLink ?? '')?.[1] || p.author || null
  if (p.source === 'X')         return p.author || null
  return null
})

const sourceUrl = computed(() => {
  const p = parsed.value
  if (p.source === 'Pixiv'     && p.pixivId)      return `https://www.pixiv.net/artworks/${p.pixivId}`
  if (p.source === 'NicoSeiga' && p.nicoseigaId)  return `https://seiga.nicovideo.jp/seiga/${p.nicoseigaId}`
  if (p.source === 'X'         && p.postId)        return `https://x.com/i/web/status/${p.postId}`
  return null
})

const SOURCE_CONFIG = {
  Pixiv:     { color: '#0096fa', bg: 'rgba(0,150,250,0.18)' },
  NicoSeiga: { color: '#00c483', bg: 'rgba(0,196,131,0.18)' },
  X:         { color: '#e7e7e7', bg: 'rgba(255,255,255,0.12)' },
  '未知':    { color: '#888',    bg: 'rgba(255,255,255,0.07)' },
}
</script>

<template>
  <aside class="drawer" @click.stop>
    <div class="scroll-area">

      <!-- 来源徽标 -->
      <span
        class="source-badge"
        :style="{
          color: SOURCE_CONFIG[parsed.source]?.color,
          background: SOURCE_CONFIG[parsed.source]?.bg,
        }"
      >{{ parsed.source }}</span>

      <!-- ── Pixiv ── -->
      <template v-if="parsed.source === 'Pixiv'">
        <h3 v-if="parsed.title" class="title">{{ parsed.title }}</h3>
        <div v-if="parsed.pixivId" class="field">
          <span class="field-label">Pixiv ID</span>
          <span class="field-value mono">{{ parsed.pixivId }}</span>
        </div>
        <div v-if="parsed.author" class="field">
          <span class="field-label">投稿者</span>
          <span class="field-value author-link" @click.stop="emit('tag-click', authorSearchTerm)">
            {{ parsed.author }}
            <span v-if="parsed.authorId" class="dim">(id={{ parsed.authorId }})</span>
          </span>
        </div>
      </template>

      <!-- ── NicoSeiga ── -->
      <template v-else-if="parsed.source === 'NicoSeiga'">
        <div v-if="parsed.nicoseigaId" class="field">
          <span class="field-label">作品 ID</span>
          <span class="field-value mono">{{ parsed.nicoseigaId }}</span>
        </div>
        <h3 v-if="parsed.title" class="title">{{ parsed.title }}</h3>
        <div v-if="parsed.author" class="field">
          <span class="field-label">投稿者</span>
          <span class="field-value author-link" @click.stop="emit('tag-click', authorSearchTerm)">
            {{ parsed.author }}
            <span v-if="parsed.authorLink" class="dim">{{ parsed.authorLink }}</span>
          </span>
        </div>
      </template>

      <!-- ── X ── -->
      <template v-else-if="parsed.source === 'X'">
        <div v-if="parsed.author" class="field">
          <span class="field-label">投稿者</span>
          <span class="field-value author-link" @click.stop="emit('tag-click', authorSearchTerm)">{{ parsed.author }}</span>
        </div>
        <p v-if="parsed.caption" class="caption">{{ parsed.caption }}</p>
        <div v-if="parsed.postId" class="field">
          <span class="field-label">Post ID</span>
          <span class="field-value mono">{{ parsed.postId }}</span>
        </div>
      </template>

      <!-- ── 未知：原样显示 ── -->
      <template v-else>
        <p class="raw-text">{{ parsed.raw }}</p>
      </template>

      <!-- 标签（Pixiv / NicoSeiga 通用） -->
      <div v-if="parsed.tags?.length" class="tags-wrap">
        <span class="field-label">标签</span>
        <div class="tags">
          <span
            v-for="tag in parsed.tags"
            :key="tag"
            class="tag"
            @click.stop="emit('tag-click', tag)"
          >{{ tag }}</span>
        </div>
      </div>

      <!-- 来源链接 -->
      <a
        v-if="sourceUrl"
        :href="sourceUrl"
        target="_blank"
        rel="noopener noreferrer"
        class="source-link"
        @click.stop
      >前往来源 ↗</a>

    </div>
  </aside>
</template>

<style scoped>
.drawer {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 280px;
  background: rgba(14, 14, 22, 0.96);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  z-index: 10;
}

.scroll-area {
  flex: 1;
  overflow-y: auto;
  padding: 72px 20px 32px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.source-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.5px;
  align-self: flex-start;
}

.title {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  line-height: 1.5;
  margin: 0;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.field-label {
  font-size: 10px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.3);
  text-transform: uppercase;
  letter-spacing: 0.6px;
}

.field-value {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.5;
  word-break: break-all;
}

.field-value.mono {
  font-family: ui-monospace, monospace;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.dim {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.35);
  margin-left: 4px;
}

.caption {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
}

.raw-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.65);
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}

.tags-wrap {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  padding: 3px 10px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.65);
}

.tag {
  cursor: pointer;
}

.tag:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

.author-link {
  cursor: pointer;
}

.author-link:hover {
  color: #fff;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.source-link {
  display: inline-block;
  margin-top: 4px;
  padding: 7px 16px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.55);
  text-decoration: none;
  transition: border-color 0.2s, color 0.2s;
  align-self: flex-start;
}

.source-link:hover {
  border-color: rgba(255, 255, 255, 0.4);
  color: #fff;
}
</style>
