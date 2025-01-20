# 个人博客系统前端技术实现文档

## 一、架构设计

### 1.1 整体架构图
```
┌─────────────────────────────────────────────────────────┐
│                      应用层 (App)                        │
├─────────────────────────────────────────────────────────┤
│                      路由层 (Router)                     │
├─────────────────────────────────────────────────────────┤
│                      状态管理 (Vuex)                     │
├─────────────────────────────────────────────────────────┤
│                      组件层 (Components)                 │
├───────────────┬───────────────┬───────────────┬─────────┤
│    布局组件    │    业务组件    │   通用组件    │  插件组件 │
└───────────────┴───────────────┴───────────────┴─────────┘
```

### 1.2 目录结构
```
src/
├── assets/          # 静态资源
├── components/      # 组件
│   ├── layout/     # 布局组件
│   ├── common/     # 通用组件
│   ├── business/   # 业务组件
│   └── plugin/     # 插件组件
├── router/         # 路由配置
├── store/          # 状态管理
├── views/          # 页面视图
├── api/            # API 接口
├── utils/          # 工具函数
├── hooks/          # 组合式函数
├── styles/         # 样式文件
└── plugins/        # 插件系统
```

## 二、技术选型

### 2.1 核心框架
- Vue.js 3.x：采用 Composition API
- Vue Router 4.x：路由管理
- Pinia：状态管理
- Vite：构建工具

### 2.2 UI 框架
- Element Plus：桌面端组件库
- TailwindCSS：原子化 CSS 框架

### 2.3 工具库
- Axios：HTTP 请求
- Day.js：日期处理
- ECharts：图表可视化
- Markdown-it：Markdown 渲染

## 三、组件设计

### 3.1 布局组件
```vue
<!-- layouts/DefaultLayout.vue -->
<template>
  <div class="layout-default" :class="{ 'dark': isDarkMode }">
    <header-component />
    <div class="layout-content">
      <sidebar-component v-if="showSidebar" />
      <main class="main-content">
        <router-view />
      </main>
    </div>
    <footer-component />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useThemeStore } from '@/store/theme'
import HeaderComponent from './Header.vue'
import SidebarComponent from './Sidebar.vue'
import FooterComponent from './Footer.vue'

const themeStore = useThemeStore()
const isDarkMode = computed(() => themeStore.isDarkMode)
const showSidebar = computed(() => themeStore.layout.sidebar !== 'none')
</script>
```

### 3.2 业务组件

#### 文章编辑器
```vue
<!-- components/business/PostEditor.vue -->
<template>
  <div class="post-editor">
    <el-form :model="postForm" :rules="rules" ref="formRef">
      <el-form-item label="标题" prop="title">
        <el-input v-model="postForm.title" />
      </el-form-item>
      
      <el-form-item label="内容" prop="content">
        <markdown-editor
          v-model="postForm.content"
          :plugins="enabledPlugins"
          @save="handleAutoSave"
        />
      </el-form-item>
      
      <el-form-item label="分类" prop="categoryId">
        <category-selector v-model="postForm.categoryId" />
      </el-form-item>
      
      <el-form-item label="标签" prop="tags">
        <tag-selector v-model="postForm.tags" multiple />
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="handleSubmit">发布</el-button>
        <el-button @click="handleSaveDraft">存为草稿</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { usePostStore } from '@/store/post'
import { usePluginStore } from '@/store/plugin'
import type { PostForm } from '@/types'

const postStore = usePostStore()
const pluginStore = usePluginStore()

const postForm = ref<PostForm>({
  title: '',
  content: '',
  categoryId: null,
  tags: [],
  status: 'draft'
})

const rules = {
  title: [
    { required: true, message: '请输入文章标题' },
    { min: 5, message: '标题长度不能少于5个字符' }
  ],
  content: [
    { required: true, message: '请输入文章内容' }
  ],
  categoryId: [
    { required: true, message: '请选择文章分类' }
  ]
}

const enabledPlugins = computed(() => 
  pluginStore.plugins.filter(p => p.type === 'content' && p.enabled)
)

const handleAutoSave = async () => {
  await postStore.autoSave(postForm.value)
}

const handleSubmit = async () => {
  await postStore.createPost({
    ...postForm.value,
    status: 'published'
  })
}

const handleSaveDraft = async () => {
  await postStore.createPost({
    ...postForm.value,
    status: 'draft'
  })
}
</script>
```

### 3.3 通用组件

#### 分页组件
```vue
<!-- components/common/Pagination.vue -->
<template>
  <div class="pagination-wrapper">
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :total="total"
      :page-sizes="[10, 20, 50, 100]"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  total: number
  initialPage?: number
  initialPageSize?: number
}>()

const emit = defineEmits<{
  (e: 'update:page', page: number): void
  (e: 'update:pageSize', size: number): void
}>()

const currentPage = ref(props.initialPage || 1)
const pageSize = ref(props.initialPageSize || 10)

const handleSizeChange = (size: number) => {
  emit('update:pageSize', size)
}

const handleCurrentChange = (page: number) => {
  emit('update:page', page)
}
</script>
```

### 3.4 插件组件系统

#### 插件容器
```vue
<!-- components/plugin/PluginContainer.vue -->
<template>
  <div class="plugin-container">
    <component
      v-for="plugin in activePlugins"
      :key="plugin.id"
      :is="plugin.component"
      v-bind="plugin.props"
      @event="handlePluginEvent"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { usePluginStore } from '@/store/plugin'

const props = defineProps<{
  position: 'sidebar' | 'content' | 'header' | 'footer'
}>()

const pluginStore = usePluginStore()

const activePlugins = computed(() => 
  pluginStore.getActivePluginsByPosition(props.position)
)

const handlePluginEvent = (event: any) => {
  pluginStore.handlePluginEvent(event)
}
</script>
```

## 四、状态管理

### 4.1 Store 模块设计
```typescript
// store/modules/post.ts
import { defineStore } from 'pinia'
import { PostApi } from '@/api'
import type { Post, PostForm } from '@/types'

export const usePostStore = defineStore('post', {
  state: () => ({
    posts: [] as Post[],
    currentPost: null as Post | null,
    loading: false,
    total: 0
  }),
  
  actions: {
    async fetchPosts(params: any) {
      this.loading = true
      try {
        const { data } = await PostApi.getPosts(params)
        this.posts = data.items
        this.total = data.total
      } finally {
        this.loading = false
      }
    },
    
    async createPost(form: PostForm) {
      const { data } = await PostApi.createPost(form)
      this.posts.unshift(data)
      return data
    },
    
    async updatePost(id: number, form: PostForm) {
      const { data } = await PostApi.updatePost(id, form)
      const index = this.posts.findIndex(p => p.id === id)
      if (index > -1) {
        this.posts[index] = data
      }
      return data
    }
  }
})
```

### 4.2 API 封装
```typescript
// api/post.ts
import { http } from '@/utils/http'
import type { Post, PostForm } from '@/types'

export const PostApi = {
  getPosts(params: any) {
    return http.get<Post[]>('/posts', { params })
  },
  
  getPost(id: number) {
    return http.get<Post>(`/posts/${id}`)
  },
  
  createPost(data: PostForm) {
    return http.post<Post>('/posts', data)
  },
  
  updatePost(id: number, data: PostForm) {
    return http.put<Post>(`/posts/${id}`, data)
  },
  
  deletePost(id: number) {
    return http.delete(`/posts/${id}`)
  }
}
```

## 五、主题系统

### 5.1 主题配置
```typescript
// types/theme.ts
export interface ThemeConfig {
  colors: {
    primary: string
    secondary: string
    background: string
    text: string
  }
  layout: {
    sidebar: 'left' | 'right' | 'none'
    headerFixed: boolean
    footerFixed: boolean
  }
  typography: {
    fontFamily: string
    fontSize: string
    lineHeight: string
  }
}

// store/modules/theme.ts
export const useThemeStore = defineStore('theme', {
  state: () => ({
    currentTheme: 'default',
    isDarkMode: false,
    config: {} as ThemeConfig
  }),
  
  actions: {
    async switchTheme(themeId: string) {
      const { data } = await ThemeApi.switchTheme(themeId)
      this.currentTheme = themeId
      this.config = data.config
      this.applyTheme()
    },
    
    toggleDarkMode() {
      this.isDarkMode = !this.isDarkMode
      document.documentElement.classList.toggle('dark')
    },
    
    applyTheme() {
      const { colors, typography } = this.config
      
      // 应用主题变量
      document.documentElement.style.setProperty('--primary-color', colors.primary)
      document.documentElement.style.setProperty('--font-family', typography.fontFamily)
    }
  }
})
```

## 六、插件系统

### 6.1 插件注册机制
```typescript
// plugins/index.ts
import type { Plugin } from '@/types'

export class PluginManager {
  private plugins: Map<string, Plugin> = new Map()
  
  register(plugin: Plugin) {
    if (this.plugins.has(plugin.id)) {
      throw new Error(`Plugin ${plugin.id} already exists`)
    }
    
    this.validatePlugin(plugin)
    this.plugins.set(plugin.id, plugin)
  }
  
  unregister(pluginId: string) {
    this.plugins.delete(pluginId)
  }
  
  getPlugin(pluginId: string) {
    return this.plugins.get(pluginId)
  }
  
  private validatePlugin(plugin: Plugin) {
    // 验证插件格式和必要属性
    const required = ['id', 'name', 'version', 'install']
    for (const field of required) {
      if (!(field in plugin)) {
        throw new Error(`Plugin ${plugin.id} is missing required field: ${field}`)
      }
    }
  }
}
```

### 6.2 插件示例
```typescript
// plugins/markdown-extension.ts
import type { Plugin } from '@/types'

export const MarkdownExtensionPlugin: Plugin = {
  id: 'markdown-extension',
  name: 'Markdown Extension',
  version: '1.0.0',
  description: 'Enhanced Markdown support',
  
  install(app) {
    app.component('markdown-preview', {
      props: {
        content: String
      },
      setup(props) {
        // 插件逻辑实现
      }
    })
  },
  
  uninstall(app) {
    app.unmount('markdown-preview')
  }
}
```

## 七、性能优化

### 7.1 代码分割
```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/posts',
      component: () => import('@/views/post/PostList.vue')
    },
    {
      path: '/posts/:id',
      component: () => import('@/views/post/PostDetail.vue')
    }
  ]
})
```

### 7.2 资源优化
```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig({
  plugins: [
    vue(),
    visualizer({
      open: true,
      gzipSize: true
    })
  ],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'element-plus': ['element-plus'],
          'editor': ['@toast-ui/editor'],
          'echarts': ['echarts']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  }
})
```

## 八、安全措施

### 8.1 XSS 防护
```typescript
// utils/sanitize.ts
import DOMPurify from 'dompurify'

export const sanitizeHtml = (html: string): string => {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
    ALLOWED_ATTR: ['href', 'target', 'rel']
  })
}
```

### 8.2 CSRF 防护
```typescript
// utils/http.ts
import axios from 'axios'

export const http = axios.create({
  baseURL: '/api/v1',
  headers: {
    'X-Requested-With': 'XMLHttpRequest'
  },
  withCredentials: true
})

http.interceptors.request.use(config => {
  const token = localStorage.getItem('csrf_token')
  if (token) {
    config.headers['X-CSRF-TOKEN'] = token
  }
  return config
})
```

## 九、监控系统

### 9.1 性能监控
```typescript
// utils/monitor.ts
export class PerformanceMonitor {
  private metrics: any = {}
  
  trackPageLoad() {
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
    
    this.metrics.pageLoad = {
      dnsLookup: navigation.domainLookupEnd - navigation.domainLookupStart,
      tcpConnection: navigation.connectEnd - navigation.connectStart,
      serverResponse: navigation.responseEnd - navigation.requestStart,
      domParse: navigation.domComplete - navigation.responseEnd,
      domReady: navigation.domContentLoadedEventEnd - navigation.navigationStart
    }
  }
  
  trackResourceLoad() {
    const resources = performance.getEntriesByType('resource')
    
    this.metrics.resources = resources.map(resource => ({
      name: resource.name,
      type: resource.initiatorType,
      duration: resource.duration,
      size: resource.transferSize
    }))
  }
  
  report() {
    // 上报性能数据
    return http.post('/statistics/performance', this.metrics)
  }
}
```

### 9.2 错误监控
```typescript
// utils/error-handler.ts
export class ErrorHandler {
  private errors: any[] = []
  
  setup() {
    window.addEventListener('error', this.handleError.bind(this))
    window.addEventListener('unhandledrejection', this.handlePromiseError.bind(this))
  }
  
  private handleError(event: ErrorEvent) {
    this.errors.push({
      type: 'error',
      message: event.message,
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
      stack: event.error?.stack,
      timestamp: new Date().toISOString()
    })
    
    this.report()
  }
  
  private handlePromiseError(event: PromiseRejectionEvent) {
    this.errors.push({
      type: 'unhandledrejection',
      message: event.reason?.message || String(event.reason),
      stack: event.reason?.stack,
      timestamp: new Date().toISOString()
    })
    
    this.report()
  }
  
  private report() {
    if (this.errors.length > 0) {
      http.post('/statistics/errors', this.errors)
      this.errors = []
    }
  }
}
```
``` 