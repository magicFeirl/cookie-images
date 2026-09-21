import axios from 'axios'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://192.168.10.15:8000',
  timeout: 10000,
  // 数组参数序列化为重复 key：filter_type=pixiv&filter_type=x
  // 空数组直接省略，不发送该参数
  paramsSerializer: (params) => {
    const parts = []
    for (const [key, val] of Object.entries(params)) {
      if (val === undefined || val === null) continue
      if (Array.isArray(val)) {
        val.forEach(v => parts.push(`${key}=${encodeURIComponent(v)}`))
      } else {
        parts.push(`${key}=${encodeURIComponent(val)}`)
      }
    }
    return parts.join('&')
  },
})

// 响应拦截：校验 code，解包 data 层
http.interceptors.response.use(
  (response) => {
    const body = response.data
    if (body.code !== 0) {
      return Promise.reject(new Error(body.message ?? '请求失败'))
    }
    return body
  },
  (error) => Promise.reject(error),
)

// 后端单条记录 → 前端 image 对象列表（多图展开，无图过滤）
function normalizeImages(item) {
  // pictures 可能为 [] 或 [[]]（空嵌套），展平后过滤掉非字符串和空串
  const pics = (item.pictures ?? []).flat().filter(src => typeof src === 'string' && src)
  if (!pics.length) return []
  return pics.map((src, i) => ({
    id:     pics.length === 1 ? item.dyn_id : `${item.dyn_id}_${i}`,
    dynId:  item.dyn_id,
    src,
    title:  item.title || '',
    author: String(item.poster_uid),
    likes:  item.like  ?? 0,
    views:  item.view  ?? 0,
    ctime:  item.ctime ?? null,
    info:   item.description || undefined,
  }))
}

/**
 * 搜索图片
 * @param {Object} searchForm
 * @param {number} searchForm.pn
 * @param {number} searchForm.ps
 * @param {string}   searchForm.order       - default | random | time_asc
 * @param {string[]} searchForm.filter_type - [] = 全部；['pixiv','x'] 等组合
 * @param {number} searchForm.filter_user - -1 = 全部
 * @param {string} [query]
 * @returns {Promise<{ pn: number, ps: number, images: Array }>}
 */
export async function searchImages(searchForm, query = '') {
  const params = {
    pn:          searchForm.pn,
    ps:          searchForm.ps,
    order:       searchForm.order,
    filter_type: searchForm.filter_type,
    filter_user: searchForm.filter_user,
  }
  if (query) params.keyword = query

  const body = await http.get('/', { params })
  return {
    pn:     body.pn,
    ps:     body.ps,
    images: (body.data ?? []).flatMap(normalizeImages),
  }
}
