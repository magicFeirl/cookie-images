<script setup>
import { computed } from 'vue'

const props = defineProps({
  info:  { type: String, required: true },
  dynId: { type: [String, Number], default: null },
  src:   { type: String, default: '' },
})

const emit = defineEmits(['tag-click'])

// ─────────────────────────────────────────────
// 解析函数
// 支持三种来源格式，无法识别时返回 { source:'未知', raw }
// ─────────────────────────────────────────────
function parseInfo(text) {
  let normalized = text.trim()

  // Pixiv 单行：标题 Pixiv ID: \d+ 投稿者(id=\d+): Name  TAG1 | TAG2
  if (!normalized.includes('\n') && /Pixiv ID:\s*\d+|投稿者\(id=\d+\):/.test(normalized)) {
    normalized = normalized
      .replace(/\s+(Pixiv ID:)/, '\n$1')               // Pixiv ID 前换行
      .replace(/\s+(投稿者\(id=)/, '\n$1')              // 投稿者 前换行
      .replace(/(投稿者\(id=\d+\):\s*\S+)\s{2,}/, '$1\n') // 作者后多空格 → 标签行换行
  }

  // NicoSeiga 旧单行：im\d+ 标题 投稿者: Name (/user/...) TAG1 | TAG2
  if (!normalized.includes('\n') && /^im\d+/.test(normalized)) {
    normalized = normalized
      .replace(/(im\d+)\s+/, '$1\n')          // ID 后换行
      .replace(/\s+(投稿者:\s*)/, '\n$1')      // 投稿者 前换行
      .replace(/\)\s+(?=\S)/, ')\n')           // 作者括号后换行（标签行）
  }

  // X 旧单行：twitter/x URL + 投稿者: name | id caption + 投稿时间
  if (!normalized.includes('\n') && /https?:\/\/(twitter\.com|x\.com|t\.co)\//.test(normalized)) {
    normalized = normalized
      .replace(/(https?:\/\/\S+)\s+/, '$1\n')                        // URL 后换行
      .replace(/\s+(投稿时间)/, '\n$1')                               // 投稿时间 前换行
      .replace(/(投稿者:\s*[^|\n]+?)\s*\|\s*(\d{10,})/, '$1\n$2')   // author | id 拆行
      .replace(/(\d{15,})\s+(\S)/, '$1\n$2')                         // id 后换行（caption）
  }

  // 通用：投稿者行内含 原推：URL，拆分为两行
  normalized = normalized.replace(/(投稿者:[^\n]*?)\s{1,}(原推[:：])/g, '$1\n$2')

  const lines = normalized.split('\n').map(l => l.trim()).filter(Boolean)

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
  // 特征：含 "im<数字>" 开头的行（ID 后可跟标题）
  const nicoseigaIdLine = lines.find(l => /^im\d+/.test(l))
  if (nicoseigaIdLine) {
    const idMatch      = nicoseigaIdLine.match(/^(im\d+)\s*(.*)$/)
    const nicoseigaId  = idMatch[1]
    const titleFromId  = idMatch[2]?.trim() || undefined

    const authorLine = lines.find(l => /^投稿者:\s/.test(l))
    // 格式1：投稿者: Name (/user/...)  格式2：投稿者: Name (user/...)
    const am = authorLine?.match(/^投稿者:\s*(.+?)\s*\(\/?(.+)\)$/)

    // 标签格式1：TAG1 | TAG2
    const tagPipeLine = lines.find(l => l.includes(' | '))
    // 标签格式2：<TAG🔒] 或 <TAG]（每行一个）
    const bracketTagLines = lines.filter(l => /^<.+🔒?\]$/.test(l))

    // 参考链接：文字列→URL
    const refLinkLine = lines.find(l => /→https?:\/\//.test(l))
    const externalUrl = refLinkLine?.match(/→(https?:\/\/\S+)/)?.[1]

    // 时间行（跳过，不作为标题）
    const timeLine = lines.find(l => /^投稿时间/.test(l))

    const used = new Set([
      nicoseigaIdLine, authorLine, tagPipeLine, refLinkLine, timeLine,
      ...bracketTagLines,
    ].filter(Boolean))

    let tags = []
    if (tagPipeLine) {
      tags = tagPipeLine.split(' | ').map(t => t.trim())
    } else if (bracketTagLines.length) {
      tags = bracketTagLines.map(l => l.match(/^<(.+?)🔒?\]$/)?.[1]?.trim()).filter(Boolean)
    }

    return {
      source:       'NicoSeiga',
      nicoseigaId,
      title:        titleFromId ?? lines.find(l => !used.has(l)),
      author:       am?.[1]?.trim() ?? authorLine?.replace(/^投稿者:\s*/, ''),
      authorLink:   am?.[2],
      externalUrl,
      tags,
    }
  }

  // ── X ──
  // 特征：含 "投稿者: <名>"（无括号 user/link），或含 15 位以上纯数字行，或含 Twitter/X/t.co URL
  // 排除 NicoSeiga 的作者行格式 (user/...) / (/user/...)；允许 (id=Twitter用户ID)
  const xAuthorLine    = lines.find(l => /^投稿者:\s/.test(l) && !/\(\/?user\//.test(l))
  const postIdLine     = lines.find(l => /^\d{15,}$/.test(l))
  const directUrlLine  = lines.find(l => /^https?:\/\/(twitter\.com|x\.com)\/\S+\/status\/\d+/.test(l))
  const tcoUrlLine     = lines.find(l => /^https?:\/\/t\.co\/\S+/.test(l))
  const gensuiLine     = lines.find(l => /原推[:：]/.test(l))
  const gensuiUrl      = gensuiLine?.match(/原推[:：]\s*(https?:\/\/\S+)/)?.[1]
  const xTimeLine      = lines.find(l => /^投稿时间/.test(l))

  if (xAuthorLine || postIdLine || directUrlLine || tcoUrlLine || gensuiLine) {
    // 来源 URL：直接链接 > 原推链接 > t.co 缩短链接
    const twitterUrl = directUrlLine ?? gensuiUrl ?? (tcoUrlLine ? tcoUrlLine : null)
    // post ID：独立 ID 行 > 直接链接 > 原推链接
    const postId = postIdLine
      ?? directUrlLine?.match(/\/status\/(\d+)/)?.[1]
      ?? gensuiUrl?.match(/\/status\/(\d+)/)?.[1]

    const used = new Set([xAuthorLine, postIdLine, directUrlLine, tcoUrlLine, gensuiLine, xTimeLine].filter(Boolean))
    const caption = lines.filter(l => !used.has(l)).join('\n') || undefined

    // 去除作者名末尾的 Twitter 用户 ID：因幡瞳 (id=840578110621863937) → 因幡瞳
    const authorRaw = xAuthorLine?.replace(/^投稿者:\s*/, '') ?? ''
    const author = authorRaw.replace(/\s*\(id=\d+\)\s*$/, '').trim() || undefined

    return {
      source: 'X',
      author,
      caption,
      postId,
      twitterUrl,
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
  if (p.source === 'X')                            return p.twitterUrl ?? null
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
        <a
          v-if="parsed.externalUrl"
          :href="parsed.externalUrl"
          target="_blank"
          rel="noopener noreferrer"
          class="source-link"
          @click.stop
        >参考来源 ↗</a>
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

      <!-- B 站动态链接 -->
      <a
        v-if="dynId"
        :href="`https://www.bilibili.com/opus/${dynId}`"
        target="_blank"
        rel="noopener noreferrer"
        class="source-link bili-link"
        @click.stop
      >B 站动态 ↗</a>

      <!-- 下载（跳转原图） -->
      <a
        v-if="src"
        :href="src"
        target="_blank"
        rel="noopener noreferrer"
        class="source-link"
        @click.stop
      >下载原图 ↗</a>

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

.bili-link {
  border-color: rgba(0, 161, 214, 0.3);
  color: rgba(0, 161, 214, 0.7);
}

.bili-link:hover {
  border-color: #00a1d6;
  color: #00a1d6;
}
</style>
