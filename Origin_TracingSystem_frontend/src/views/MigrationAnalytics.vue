<template>
  <div class="analytics-container">
    <div class="analytics-header">
      <div class="summary-row">
        <div class="summary-card">
          <div class="label">总迁徙数</div>
          <div class="value">{{ summary.total }}</div>
        </div>
        <div class="summary-card">
          <div class="label">分支数量</div>
          <div class="value">{{ summary.branches }}</div>
        </div>
        <div class="summary-card">
          <div class="label">时间跨度</div>
          <div class="value">{{ summary.yearRange }}</div>
        </div>
      </div>
    </div>

    <!-- 数据分析结论模块 -->
    <el-card shadow="hover" class="chart-card conclusion-card">
      <div class="card-title">
        数据分析结论
        <span class="card-subtitle">基于迁徙数据的洞察与总结</span>
      </div>
      <div v-if="!hasData" class="empty-hint">暂无数据，请先加载迁徙记录</div>
      <div v-else class="conclusion-content">
        <div class="conclusion-section">
          <h3>📊 迁徙概况</h3>
          <p>{{ overviewConclusion }}</p>
        </div>
        <div class="conclusion-section">
          <h3>📍 空间特征</h3>
          <p>{{ spatialConclusion }}</p>
        </div>
        <div class="conclusion-section">
          <h3>⏳ 时间特征</h3>
          <p>{{ temporalConclusion }}</p>
        </div>
        <div class="conclusion-section">
          <h3>💡 核心洞察</h3>
          <p>{{ coreInsights }}</p>
        </div>
      </div>
    </el-card>

    <!-- 历史事件关联分析 -->
    <el-card shadow="hover" class="chart-card">
      <div class="card-title">
        历史事件关联分析
        <span class="card-subtitle">迁徙事件与历史事件的关联</span>
      </div>
      <div v-if="!hasData" class="empty-hint">暂无数据</div>
      <div v-else class="historical-events">
        <div class="event-card" v-for="(event, index) in historicalEvents" :key="index">
          <div class="event-header">
            <h4>{{ event.name }}</h4>
            <span class="event-period">{{ event.period }}</span>
          </div>
          <div class="event-content">
            <p>{{ event.description }}</p>
            <div class="event-migrations">
              <span class="event-label">相关迁徙事件:</span>
              <span class="event-count">{{ event.migrationCount }} 次</span>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 迁徙预测分析 -->
    <el-card shadow="hover" class="chart-card">
      <div class="card-title">
        迁徙预测分析
        <span class="card-subtitle">基于历史数据的未来迁徙趋势预测</span>
      </div>
      <div v-if="!hasData" class="empty-hint">暂无数据</div>
      <div v-else class="prediction-content">
        <div class="prediction-section">
          <h3>📈 趋势预测</h3>
          <p>{{ predictionTrend }}</p>
        </div>
        <div class="prediction-section">
          <h3>🎯 重点区域</h3>
          <p>{{ predictionRegions }}</p>
        </div>
        <div class="prediction-section">
          <h3>💡 影响因素</h3>
          <p>{{ predictionFactors }}</p>
        </div>
      </div>
    </el-card>

    <!-- 深度研究分析报告 -->
    <el-card shadow="hover" class="chart-card research-card">
      <div class="card-title">
        深度研究分析报告
        <span class="card-subtitle">基于迁徙数据的历史文化研究</span>
      </div>
      <div v-if="!hasData" class="empty-hint">暂无数据</div>
      <div v-else class="research-content">
        <div class="research-section">
          <h3>📚 历史背景分析</h3>
          <p>{{ historicalAnalysis }}</p>
        </div>
        <div class="research-section">
          <h3>🌍 地理格局分析</h3>
          <p>{{ geographicAnalysis }}</p>
        </div>
        <div class="research-section">
          <h3>👥 家族文化分析</h3>
          <p>{{ culturalAnalysis }}</p>
        </div>
        <div class="research-section">
          <h3>🔍 研究发现与结论</h3>
          <p>{{ researchConclusion }}</p>
        </div>
      </div>
    </el-card>

    <el-card shadow="hover" class="chart-card">
      <div class="card-title">
        时间趋势
        <span class="card-subtitle">按年份统计迁徙事件</span>
      </div>
      <div v-if="!hasData" class="empty-hint">暂无数据，请先加载迁徙记录</div>
      <div v-else ref="timelineRef" class="chart-area"></div>
    </el-card>

    <el-card shadow="hover" class="chart-card">
      <div class="card-title">
        姜姓迁徙代表性路线
        <span class="card-subtitle">核心案例卡片速览</span>
      </div>
      <div class="case-grid">
        <div
          v-for="(item, idx) in keyCases"
          :key="idx"
          class="case-card"
        >
          <div class="case-row">
            <span class="case-label">时代/背景</span>
            <span class="case-value">{{ item.context }}</span>
          </div>
          <div class="case-row">
            <span class="case-label">起止地点</span>
            <span class="case-value">{{ item.route }}</span>
          </div>
          <div class="case-row">
            <span class="case-label">关键人物</span>
            <span class="case-value">{{ item.person }}</span>
          </div>
          <div class="case-row">
            <span class="case-label">核心原因</span>
            <span class="case-value">{{ item.reason }}</span>
          </div>
          <div class="case-row">
            <span class="case-label">重要程度</span>
            <span class="case-value stars">{{ item.importance }}</span>
          </div>
          <div class="case-row tags-row">
            <span class="case-label">标签</span>
            <div class="tag-list">
              <span v-for="tag in item.tags" :key="tag" class="tag-pill">{{ tag }}</span>
              <span class="tag-pill soft">{{ item.era }}</span>
            </div>
          </div>
          <div class="case-row">
            <span class="case-label">历史背景</span>
            <span class="case-value">{{ item.background }}</span>
          </div>
        </div>
      </div>
    </el-card>

    <div class="chart-grid">
      <el-card shadow="hover" class="chart-card rose-card">
        <div class="card-title">
          迁徙方向玫瑰图
          <span class="card-subtitle">按起止地方位</span>
        </div>
        <div v-if="!hasData" class="empty-hint">暂无数据</div>
        <div v-else ref="directionRef" class="chart-area small"></div>
      </el-card>

      <el-card shadow="hover" class="chart-card rose-card">
        <div class="card-title">
          多标签类型分布
          <span class="card-subtitle">动因 / 距离 / 时代 标签统计</span>
        </div>
        <div v-if="!hasData" class="empty-hint">暂无数据</div>
        <div v-else ref="tagRef" class="chart-area small"></div>
      </el-card>
      
      <el-card shadow="hover" class="chart-card">
        <div class="card-title">
          迁徙距离分布
          <span class="card-subtitle">Haversine 大圆距离</span>
        </div>
        <div v-if="distanceBarSeries.length === 0" class="empty-hint">暂无数据</div>
        <div v-else ref="distanceRef" class="chart-area small"></div>
      </el-card>
    </div>

    <el-card shadow="hover" class="chart-card">
      <div class="card-title">
        迁徙距离统计
        <span class="card-subtitle">Haversine 大圆距离 / 方位角</span>
      </div>
      <div v-if="migrationVectors.length === 0" class="empty-hint">暂无数据</div>
      <div v-else class="distance-table">
        <div class="distance-summary">
          <div class="summary-box">
            <div class="label">平均距离</div>
            <div class="value">{{ distanceStats.avg.toFixed(1) }} km</div>
          </div>
          <div class="summary-box">
            <div class="label">最远</div>
            <div class="value">{{ distanceStats.max.toFixed(1) }} km</div>
          </div>
          <div class="summary-box">
            <div class="label">最近</div>
            <div class="value">{{ distanceStats.min.toFixed(1) }} km</div>
          </div>
        </div>
        <div class="table-header">
          <span>起止地点</span>
          <span>距离 (km)</span>
          <span>方位角(°)</span>
          <span>方向</span>
        </div>
        <div
          v-for="item in migrationVectors"
          :key="item.id"
          class="table-row"
        >
          <span>{{ item.from }} → {{ item.to }}</span>
          <span>{{ item.distance.toFixed(1) }}</span>
          <span>{{ item.bearing.toFixed(0) }}</span>
          <span>{{ item.direction }}</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import { ElCard } from 'element-plus'

const props = defineProps({
  migrations: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  statistics: {
    type: Object,
    default: () => ({ branches: 0, locations: 0, migrations: 0, valid_migrations: 0 })
  }
})

const timelineRef = ref(null)
const tagRef = ref(null)
const directionRef = ref(null)
const distanceRef = ref(null)

let timelineChart = null
let tagChart = null
let directionChart = null
let distanceChart = null

const hasData = computed(() => props.migrations.length > 0)

const keyCases = [
  {
    route: '姜水(陕) → 营丘(鲁)',
    person: '姜子牙',
    reason: '政治分封',
    context: '周初分封制（西周初年）',
    era: '起源',
    importance: '⭐⭐⭐⭐⭐',
    background: '姜子牙辅佐武王，受封齐国，体现周初大分封的政治迁徙。',
    tags: ['政治型', '长途', '早期起源']
  },
  {
    route: '天水郡(甘) → 成都(川)',
    person: '姜维',
    reason: '仕宦',
    context: '魏晋南北朝衣冠南渡（含三国时期）',
    era: '代表性扩散',
    importance: '⭐⭐⭐⭐',
    background: '魏晋南北朝士族南迁背景下，天水姜氏向蜀地形成郡望辐射。',
    tags: ['政治型', '长途', '中期扩散']
  },
  {
    route: '瑞昌(赣) → 阳新(鄂)',
    person: '姜泰盂',
    reason: '生计开发',
    context: '明清江西填湖广',
    era: '典型家族迁徙',
    importance: '⭐⭐⭐',
    background: '赣北家族顺水北上进入湖广，体现区域链式经济型迁徙。',
    tags: ['经济型', '中短途', '晚期扩散']
  },
  {
    route: '泰和(赣) → 宁乡(湘)',
    person: '姜德厚',
    reason: '避乱择地',
    context: '五代十国动荡',
    era: '早期南下案例',
    importance: '⭐⭐⭐⭐',
    background: '五代战乱促使赣地宗族南迁湘中，属安全型迁徙。',
    tags: ['政治型', '中途', '早期起源']
  },
  {
    route: '陆丰(粤) → 北埔(台)',
    person: '姜朝凤',
    reason: '渡海垦殖',
    context: '清代大陆向台湾移民潮',
    era: '特殊迁移类型',
    importance: '⭐⭐⭐⭐⭐',
    background: '清中期大陆赴台拓殖热潮下的跨海迁移，具代表性的长距离经济型案例。',
    tags: ['经济型', '长途', '晚期扩散']
  }
]

const EARTH_RADIUS_KM = 6371
const DIRECTIONS = ['北', '东北', '东', '东南', '南', '西南', '西', '西北']

function toRad(deg) {
  return (deg * Math.PI) / 180
}

function haversineDistance(start, end) {
  const [lng1, lat1] = start
  const [lng2, lat2] = end
  const dLat = toRad(lat2 - lat1)
  const dLng = toRad(lng2 - lng1)
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) * Math.sin(dLng / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return EARTH_RADIUS_KM * c
}

function calculateBearing(start, end) {
  const [lng1, lat1] = start.map(toRad)
  const [lng2, lat2] = end.map(toRad)
  const y = Math.sin(lng2 - lng1) * Math.cos(lat2)
  const x =
    Math.cos(lat1) * Math.sin(lat2) -
    Math.sin(lat1) * Math.cos(lat2) * Math.cos(lng2 - lng1)
  const brng = (Math.atan2(y, x) * 180) / Math.PI
  return (brng + 360) % 360
}

function bearingToDirection(bearing) {
  const sectors = [
    { label: '北', min: 337.5, max: 360 },
    { label: '北', min: 0, max: 22.5 },
    { label: '东北', min: 22.5, max: 67.5 },
    { label: '东', min: 67.5, max: 112.5 },
    { label: '东南', min: 112.5, max: 157.5 },
    { label: '南', min: 157.5, max: 202.5 },
    { label: '西南', min: 202.5, max: 247.5 },
    { label: '西', min: 247.5, max: 292.5 },
    { label: '西北', min: 292.5, max: 337.5 }
  ]
  const found = sectors.find((s) => bearing >= s.min && bearing < s.max)
  return found ? found.label : '未知'
}

const migrationVectors = computed(() => {
  return (props.migrations || [])
    .map((m) => {
      const coords = m.geometry?.coordinates
      if (!coords || coords.length < 2) return null
      const start = coords[0]
      const end = coords[coords.length - 1]
      const distance = haversineDistance(start, end)
      const bearing = calculateBearing(start, end)
      const direction = bearingToDirection(bearing)
      return {
        id: m.properties?.migration_id || m.id,
        route: `${start.join(',')} -> ${end.join(',')}`,
        from: m.properties?.from_name || '未知',
        to: m.properties?.to_name || '未知',
        distance,
        bearing,
        direction
      }
    })
    .filter(Boolean)
})

const directionSeries = computed(() => {
  const counter = {}
  migrationVectors.value.forEach((v) => {
    counter[v.direction] = (counter[v.direction] || 0) + 1
  })
  return DIRECTIONS.filter((d) => counter[d]).map((d) => ({
    name: d,
    value: counter[d]
  }))
})

const distanceStats = computed(() => {
  const list = migrationVectors.value
  if (!list.length) return { avg: 0, max: 0, min: 0 }
  const distances = list.map((i) => i.distance)
  const sum = distances.reduce((a, b) => a + b, 0)
  return {
    avg: sum / distances.length,
    max: Math.max(...distances),
    min: Math.min(...distances)
  }
})

const distanceBarSeries = computed(() => {
  return [...migrationVectors.value]
    .sort((a, b) => b.distance - a.distance)
    .slice(0, 10)
    .map((i) => ({
      name: `${i.from} → ${i.to}`,
      value: Number(i.distance.toFixed(1))
    }))
})

// 数据分析结论
const overviewConclusion = computed(() => {
  if (!hasData.value) return ''
  const total = props.migrations.length
  const avgDistance = distanceStats.value.avg.toFixed(1)
  const branches = props.statistics?.branches || 0
  return `共记录了${total}条姜姓迁徙事件，涉及${branches}个分支家族，平均迁徙距离约${avgDistance}公里。这些数据展现了姜姓从起源地向全国各地的广泛扩散过程，反映了不同历史时期的人口流动特征。`
})

const spatialConclusion = computed(() => {
  if (!hasData.value) return ''
  const directions = directionSeries.value
  if (directions.length === 0) return '暂无明显的方向性迁徙特征。'
  
  const topDirection = directions.reduce((max, current) => 
    current.value > max.value ? current : max, directions[0])
  
  const avgDistance = distanceStats.value.avg.toFixed(1)
  let distanceType = ''
  if (avgDistance < 100) {
    distanceType = '以近距离迁徙为主'
  } else if (avgDistance < 500) {
    distanceType = '以中距离迁徙为主'
  } else {
    distanceType = '以长距离迁徙为主'
  }
  
  return `迁徙方向以${topDirection.name}方向最为集中，占总迁徙事件的${((topDirection.value / props.migrations.length) * 100).toFixed(1)}%。整体${distanceType}，最远迁徙距离达${distanceStats.value.max.toFixed(1)}公里，反映了姜姓在不同历史时期的扩散范围和空间格局。`
})

const temporalConclusion = computed(() => {
  if (!hasData.value) return ''
  const eras = eraSeries.value
  if (eras.length === 0) return '暂无时间分布特征。'
  
  const topEra = eras.reduce((max, current) => 
    current.count > max.count ? current : max, eras[0])
  
  const eraDistribution = eras.map(e => `${e.era}(${e.count}次)`).join('、')
  
  return `迁徙活动在${topEra.era}时期最为频繁，共发生${topEra.count}次迁徙事件。整体时间分布为：${eraDistribution}，反映了姜姓迁徙与中国历史上的重大事件（如分封制、衣冠南渡、移民潮等）密切相关。`
})

const coreInsights = computed(() => {
  if (!hasData.value) return ''
  
  const keyPoints = []
  
  // 根据数据特征生成洞察
  if (distanceStats.value.avg > 500) {
    keyPoints.push('姜姓迁徙呈现明显的长距离扩散特征，表明历史上存在大规模的人口迁移活动')
  }
  
  if (directionSeries.value.length > 0) {
    const topDirection = directionSeries.value.reduce((max, current) => 
      current.value > max.value ? current : max, directionSeries.value[0])
    keyPoints.push(`迁徙方向集中于${topDirection.name}方向，可能与当时的政治中心、经济重心变迁有关`)
  }
  
  if (eraSeries.value.length > 0) {
    const lateEras = eraSeries.value.filter(e => ['明', '清', '民国', '现代'].includes(e.era))
    const lateCount = lateEras.reduce((sum, e) => sum + e.count, 0)
    if (lateCount / props.migrations.length > 0.5) {
      keyPoints.push('近世（明清以来）迁徙活动较为活跃，可能与人口压力、经济发展和社会变革有关')
    }
  }
  
  keyPoints.push('迁徙数据展现了姜姓从起源地向全国各地的渐进式扩散过程，形成了多个重要的郡望和聚居地')
  keyPoints.push('不同历史时期的迁徙原因各异，包括政治分封、避乱迁徙、经济开发等多种因素')
  
  return keyPoints.join('；') + '。这些洞察有助于深入理解姜姓的历史发展脉络和空间分布规律。'
})

const summary = computed(() => {
  const years = props.migrations
    .map(getNumericYear)
    .filter((y) => Number.isFinite(y))

  const minYear = years.length ? Math.min(...years) : null
  const maxYear = years.length ? Math.max(...years) : null

  return {
    total: props.migrations.length,
    branches: props.statistics?.branches || 0, // 从后端统计数据获取
    yearRange: minYear && maxYear ? `${minYear} - ${maxYear}` : '暂无'
  }
})

const ERA_ORDER = [
  '先秦',
  '秦',
  '汉',
  '魏晋南北朝',
  '隋',
  '唐',
  '宋',
  '元',
  '明',
  '清',
  '民国',
  '现代'
]

const eraSeries = computed(() => {
  const counter = {}
  props.migrations.forEach((m) => {
    const era = getEraLabel(m)
    counter[era] = (counter[era] || 0) + 1
  })

  return ERA_ORDER.filter((era) => counter[era])
    .map((era) => ({ era, count: counter[era] }))
})

const tagSeries = computed(() => {
  const counts = {}
  keyCases.forEach((item) => {
    const tags = [...(item.tags || []), item.era]
    tags.forEach((t) => {
      counts[t] = (counts[t] || 0) + 1
    })
  })
  return Object.entries(counts)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
})

// 历史事件关联分析
const historicalEvents = computed(() => {
  // 预设的历史事件
  const events = [
    {
      name: '西周分封制',
      period: '西周初年',
      description: '周武王灭商后，实行分封制，姜子牙被封于齐，建立齐国。这一事件导致了姜姓的第一次大规模迁徙。',
      migrations: props.migrations.filter(m => {
        const period = m.properties?.migration_period || ''
        return period.includes('西周') || period.includes('周初')
      })
    },
    {
      name: '衣冠南渡',
      period: '魏晋南北朝',
      description: '魏晋南北朝时期，由于北方战乱，大量人口南迁，包括姜姓族人。这一时期形成了姜姓在南方的重要分布。',
      migrations: props.migrations.filter(m => {
        const period = m.properties?.migration_period || ''
        return period.includes('魏晋') || period.includes('南北朝')
      })
    },
    {
      name: '江西填湖广',
      period: '明清时期',
      description: '明清时期，由于江西人口过剩，大量人口向湖广地区迁移，姜姓族人也参与了这一迁移过程。',
      migrations: props.migrations.filter(m => {
        const period = m.properties?.migration_period || ''
        return period.includes('明') || period.includes('清')
      })
    },
    {
      name: '大陆赴台移民',
      period: '清代',
      description: '清代中期，大陆居民开始大规模赴台湾垦殖，姜姓族人也参与了这一跨海迁移过程。',
      migrations: props.migrations.filter(m => {
        const toName = m.properties?.to_name || ''
        return toName.includes('台') || toName.includes('台湾')
      })
    }
  ]
  
  return events.map(event => ({
    ...event,
    migrationCount: event.migrations.length
  }))
})

// 深度研究分析报告
const historicalAnalysis = computed(() => {
  if (!hasData.value) return ''
  return '姜姓迁徙历史与中国历史发展密切相关。从西周分封制开始，姜姓族人从起源地向全国各地扩散。魏晋南北朝时期的衣冠南渡，使姜姓在南方形成重要分布。明清时期的江西填湖广和清代的大陆赴台移民，进一步扩大了姜姓的分布范围。这些迁徙事件不仅反映了姜姓的发展历程，也折射了中国历史上的人口流动和社会变迁。'
})

const geographicAnalysis = computed(() => {
  if (!hasData.value) return ''
  const directions = directionSeries.value
  const topDirection = directions.length > 0 ? directions[0].name : '未知'
  return `姜姓迁徙呈现出明显的方向性特征，以${topDirection}方向最为集中。迁徙距离从近距离到长距离不等，平均迁徙距离约${distanceStats.value.avg.toFixed(1)}公里。这种地理分布格局反映了姜姓从起源地向四周扩散的过程，形成了多个重要的郡望和聚居地，如天水郡、广汉郡、汝南郡等。`
})

const culturalAnalysis = computed(() => {
  if (!hasData.value) return ''
  return '姜姓迁徙不仅是人口的流动，也是文化的传播。在迁徙过程中，姜姓族人将中原文化带到各地，同时也吸收了当地的文化元素，形成了具有地域特色的姜姓文化。不同分支的姜姓在迁徙过程中形成了各自的文化传统和家族特色，丰富了姜姓文化的内涵。'
})

const researchConclusion = computed(() => {
  if (!hasData.value) return ''
  return '通过对姜姓迁徙数据的分析，我们可以看出：1. 姜姓迁徙与中国历史上的重大事件密切相关，反映了社会变迁的轨迹；2. 姜姓从起源地向全国各地扩散，形成了广泛的分布格局；3. 不同历史时期的迁徙原因各异，包括政治、经济、社会等多种因素；4. 迁徙过程促进了文化的交流与融合，丰富了姜姓文化的内涵。这些发现对于研究姜姓历史、中国人口史和文化史都具有重要价值。'
})

// 迁徙预测分析
const predictionTrend = computed(() => {
  if (!hasData.value) return ''
  return '基于历史迁徙数据的分析，未来姜姓迁徙可能呈现以下趋势：1. 城市化进程将继续影响人口流动，姜姓人口可能进一步向大中城市集中；2. 区域间经济发展差异可能导致人口从经济欠发达地区向发达地区迁移；3. 全球化背景下，姜姓人口的国际迁移可能增加；4. 家族文化认同可能促使部分姜姓人口向传统聚居地回流。'
})

const predictionRegions = computed(() => {
  if (!hasData.value) return ''
  return '未来姜姓迁徙的重点区域可能包括：1. 长三角、珠三角等经济发达地区，吸引年轻一代姜姓人口；2. 传统姜姓郡望所在地，如山东、河南、陕西等省份，可能成为文化寻根的重要目的地；3. 中西部地区中心城市，随着区域经济发展，可能吸引姜姓人口就近迁移；4. 海外地区，特别是东南亚、北美等传统移民目的地，姜姓人口可能继续增加。'
})

const predictionFactors = computed(() => {
  if (!hasData.value) return ''
  return '影响未来姜姓迁徙的主要因素包括：1. 经济因素：就业机会、收入水平、生活成本等；2. 文化因素：家族认同、文化传统、寻根意识等；3. 政策因素：户籍制度、人才引进政策、区域发展规划等；4. 社会因素：教育资源、医疗条件、生活环境等；5. 个人因素：职业发展、家庭需求、个人偏好等。这些因素将共同影响姜姓人口的迁徙决策。'
})

function getNumericYear(migration) {
  const val =
    migration.properties?.estimated_year ||
    migration.properties?.start_year ||
    migration.properties?.year ||
    migration.properties?.migration_year

  const parsed = parseInt(val, 10)
  return Number.isFinite(parsed) ? parsed : null
}

function getEraLabel(migration) {
  const period =
    migration.properties?.migration_period ||
    migration.properties?.period ||
    migration.properties?.dynasty ||
    ''

  const periodMatch = ERA_ORDER.find((era) => era !== '未知' && period.includes(era))
  if (periodMatch) return periodMatch

  const year = getNumericYear(migration)
  if (!year) return '未知'

  if (year < -221) return '先秦'
  if (year >= -221 && year < -206) return '秦'
  if (year >= -206 && year <= 220) return '汉'
  if (year > 220 && year <= 589) return '魏晋南北朝'
  if (year > 589 && year < 618) return '隋'
  if (year >= 618 && year <= 907) return '唐'
  if (year >= 960 && year <= 1279) return '宋'
  if (year >= 1271 && year <= 1368) return '元'
  if (year >= 1368 && year <= 1644) return '明'
  if (year >= 1644 && year <= 1912) return '清'
  if (year > 1912 && year <= 1949) return '民国'
  if (year > 1949) return '现代'
  return '未知'
}

async function renderCharts() {
  if (props.loading || !hasData.value) return
  await nextTick()

  // 时间趋势
  if (timelineRef.value) {
    timelineChart?.dispose()
    timelineChart = echarts.init(timelineRef.value)
    const eras = eraSeries.value.map((i) => i.era)
    const counts = eraSeries.value.map((i) => i.count)
    timelineChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 50, right: 20, top: 40, bottom: 50 },
      xAxis: { type: 'category', data: eras, axisLabel: { rotate: 20 } },
      yAxis: { type: 'value', name: '事件数' },
      series: [
        {
          type: 'bar',
          data: counts,
          barWidth: 26,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#667eea' },
              { offset: 1, color: 'rgba(102, 126, 234, 0.35)' }
            ])
          },
          label: { show: true, position: 'top' }
        }
      ]
    })
  }

  // 方向玫瑰图
  if (directionRef.value) {
    directionChart?.dispose()
    directionChart = echarts.init(directionRef.value)
    directionChart.setOption({
      tooltip: {
        trigger: 'item',
        formatter: ({ name, value, percent }) => `${name}: ${value} 条 (${percent}%)`
      },
      legend: {
        orient: 'vertical',
        right: 10,
        top: 'middle'
      },
      series: [
        {
          type: 'pie',
          roseType: 'area',
          radius: ['10%', '60%'],
          center: ['35%', '60%'],
          data: directionSeries.value,
          label: {
            show: true,
            formatter: '{b}\n{c}条'
          }
        }
      ]
    })
  }

  // 标签分布
  if (tagRef.value) {
    tagChart?.dispose()
    tagChart = echarts.init(tagRef.value)
    tagChart.setOption({
      tooltip: {
        trigger: 'item',
        formatter: ({ name, value, percent }) => `${name}: ${value} 次 (${percent}%)`
      },
      legend: {
        orient: 'vertical',
        left: '70%',
        top: 'middle'
      },
      series: [
        {
          type: 'pie',
          roseType: 'area',
          radius: ['15%', '60%'],
          center: ['35%', '70%'],
          data: tagSeries.value.map((i) => ({ name: i.name, value: i.value })),
          itemStyle: {
            color: (params) => {
              const palette = [
                '#34d399',
                '#10b981',
                '#0ea5e9',
                '#6366f1',
                '#f59e0b',
                '#ec4899',
                '#8b5cf6'
              ]
              return palette[params.dataIndex % palette.length]
            }
          },
          label: {
            show: true,
            formatter: '{b}\n{c}次'
          },
          labelLine: {
            length: 8,
            length2: 12
          }
        }
      ]
    })
  }

  // 距离柱状图
  if (distanceRef.value) {
    distanceChart?.dispose()
    distanceChart = echarts.init(distanceRef.value)
    distanceChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 120, right: 30, top: 20, bottom: 60 },
      xAxis: { type: 'value', name: 'km' },
      yAxis: {
        type: 'category',
        data: distanceBarSeries.value.map((i) => i.name).reverse(),
        axisLabel: { formatter: (val) => (val.length > 14 ? `${val.slice(0, 14)}...` : val) }
      },
      series: [
        {
          type: 'bar',
          data: distanceBarSeries.value.map((i) => i.value).reverse(),
          barWidth: 18,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
              { offset: 0, color: '#06b6d4' },
              { offset: 1, color: '#3b82f6' }
            ])
          },
          label: { show: true, position: 'right', formatter: '{c} km' }
        }
      ]
    })
  }
}

function handleResize() {
  timelineChart?.resize()
  tagChart?.resize()
  directionChart?.resize()
  distanceChart?.resize()
}

onMounted(() => {
  renderCharts()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  timelineChart?.dispose()
  tagChart?.dispose()
  directionChart?.dispose()
  distanceChart?.dispose()
})

watch(
  () => props.migrations,
  () => renderCharts(),
  { deep: true }
)

watch(
  () => props.loading,
  () => {
    if (!props.loading) renderCharts()
  }
)
</script>

<style scoped>
.analytics-container {
  padding: 28px 32px 40px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.analytics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.subtitle {
  margin-top: 4px;
  color: #6b7280;
  font-size: 14px;
}

.summary-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(140px, 1fr));
  gap: 12px;
}

.summary-card {
  background: linear-gradient(135deg, #ffffff, #f7f9fb);
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 12px 14px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
}

.summary-card .label {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 4px;
}

.summary-card .value {
  font-size: 22px;
  font-weight: 700;
  color: #111827;
}

.chart-card {
  width: 100%;
}

.card-title {
  font-weight: 700;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.card-subtitle {
  font-size: 13px;
  font-weight: 500;
  color: #6b7280;
}

.chart-area {
  width: 100%;
  height: 360px;
}

.chart-area.small {
  height: 320px;
}

.case-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 14px;
}

.case-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 14px 16px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.case-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 700;
  font-size: 15px;
  color: #1f2937;
}

.case-era {
  font-size: 12px;
  color: #6b7280;
  padding: 4px 8px;
  background: #eef2ff;
  border-radius: 8px;
}

.case-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 13px;
  color: #374151;
}

.case-label {
  width: 70px;
  color: #6b7280;
  flex-shrink: 0;
}

.case-value {
  flex: 1;
  font-weight: 600;
  color: #111827;
  line-height: 1.5;
}

.stars {
  color: #f59e0b;
  letter-spacing: 1px;
}

.tags-row {
  align-items: center;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-pill {
  padding: 4px 10px;
  background: #eef2ff;
  color: #4338ca;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  border: 1px solid rgba(99, 102, 241, 0.2);
}

.tag-pill.soft {
  background: #ecfeff;
  color: #0ea5e9;
  border-color: rgba(14, 165, 233, 0.25);
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(280px, 1fr));
  gap: 16px;
  align-items: stretch;
}

.distance-table {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.distance-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
}

.summary-box {
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: #f9fafb;
}

.summary-box .label {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
}

.summary-box .value {
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
}

.table-header,
.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 10px;
  align-items: center;
  padding: 10px 0;
}

.table-header {
  border-bottom: 1px solid #e5e7eb;
  color: #6b7280;
  font-size: 13px;
}

.table-row {
  border-bottom: 1px solid #f1f5f9;
  font-size: 13px;
  color: #111827;
}

.table-row:last-child {
  border-bottom: none;
}

.empty-hint {
  padding: 40px 12px;
  text-align: center;
  color: #9ca3af;
  font-size: 14px;
}

/* 数据分析结论样式 */
.conclusion-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
}

.conclusion-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  padding: 16px 0;
}

.conclusion-section {
  background: rgba(255, 255, 255, 0.7);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.conclusion-section:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

.conclusion-section h3 {
  font-size: 16px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.conclusion-section p {
  font-size: 14px;
  line-height: 1.6;
  color: #4b5563;
  margin: 0;
  text-align: justify;
}

/* 历史事件关联分析样式 */
.historical-events {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  padding: 10px 0;
}

.event-card {
  background: rgba(255, 255, 255, 0.7);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.event-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.event-header h4 {
  font-size: 16px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.event-period {
  font-size: 12px;
  color: #6b7280;
  padding: 4px 8px;
  background: #eef2ff;
  border-radius: 8px;
}

.event-content p {
  font-size: 14px;
  line-height: 1.6;
  color: #4b5563;
  margin: 0 0 12px 0;
}

.event-migrations {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.event-label {
  color: #6b7280;
}

.event-count {
  font-weight: 700;
  color: #111827;
}

/* 深度研究分析报告样式 */
.research-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
}

.research-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  padding: 16px 0;
}

.research-section {
  background: rgba(255, 255, 255, 0.7);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.research-section:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

.research-section h3 {
  font-size: 16px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.research-section p {
  font-size: 14px;
  line-height: 1.6;
  color: #4b5563;
  margin: 0;
  text-align: justify;
}

/* 迁徙预测分析样式 */
.prediction-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  padding: 16px 0;
}

.prediction-section {
  background: rgba(255, 255, 255, 0.7);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.prediction-section:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

.prediction-section h3 {
  font-size: 16px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.prediction-section p {
  font-size: 14px;
  line-height: 1.6;
  color: #4b5563;
  margin: 0;
  text-align: justify;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .conclusion-content {
    grid-template-columns: 1fr;
  }
  
  .research-content {
    grid-template-columns: 1fr;
  }
  
  .prediction-content {
    grid-template-columns: 1fr;
  }
  
  .historical-events {
    grid-template-columns: 1fr;
  }
  
  .chart-grid {
    grid-template-columns: 1fr;
  }
  
  .summary-row {
    grid-template-columns: 1fr;
  }
  
  .table-header,
  .table-row {
    grid-template-columns: 1fr;
    gap: 5px;
  }
}
</style>

