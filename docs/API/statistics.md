# 统计数据API文档

## 基础信息
- 基础路径：`/api/v1/statistics`
- 认证方式：Bearer Token
- 权限要求：需要登录

## 1. 内容统计

### 基本信息
- 请求路径: `/api/v1/statistics/content`
- 请求方法: `GET`
- 权限要求: 需要登录

### 请求参数
| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| startDate | string | 否 | 开始日期（YYYY-MM-DD） | "2024-02-01" |
| endDate | string | 否 | 结束日期（YYYY-MM-DD） | "2024-02-08" |

### 响应数据
```typescript
interface ContentStatistics {
  posts: {
    total: number;        // 文章总数
    published: number;    // 已发布文章数
    draft: number;       // 草稿数
    private: number;     // 私密文章数
    topAuthors: Array<{  // 热门作者
      id: number;        // 作者ID
      username: string;  // 作者用户名
      postCount: number; // 文章数
      totalViews: number;// 总浏览量
    }>;
  };
  comments: {
    total: number;      // 评论总数
    approved: number;   // 已通过评论数
    pending: number;    // 待审核评论数
    spam: number;       // 垃圾评论数
  };
  categories: {
    total: number;      // 分类总数
    topCategories: Array<{  // 热门分类
      id: number;          // 分类ID
      name: string;        // 分类名称
      postCount: number;   // 文章数
      totalViews: number;  // 总浏览量
    }>;
  };
  tags: {
    total: number;      // 标签总数
    topTags: Array<{    // 热门标签
      id: number;       // 标签ID
      name: string;     // 标签名称
      postCount: number;// 文章数
      totalViews: number;// 总浏览量
    }>;
  };
}
```

### 使用示例
```typescript
// 获取最近7天的内容统计
const response = await request.get('/statistics/content');

// 获取指定日期范围的内容统计
const response = await request.get('/statistics/content', {
  params: {
    startDate: '2024-02-01',
    endDate: '2024-02-08'
  }
});
```

## 2. 访问统计

### 基本信息
- 请求路径: `/api/v1/statistics/visits`
- 请求方法: `GET`
- 权限要求: 需要登录

### 请求参数
| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| startDate | string | 否 | 开始日期（YYYY-MM-DD） | "2024-02-01" |
| endDate | string | 否 | 结束日期（YYYY-MM-DD） | "2024-02-08" |

### 响应数据
```typescript
interface VisitStatistics {
  total: {
    pv: number;        // 总页面浏览量
    uv: number;        // 总独立访客数
    ip: number;        // 总IP数
  };
  trends: Array<{      // 趋势数据
    date: string;      // 日期（YYYY-MM-DD）
    pv: number;        // 当日页面浏览量
    uv: number;        // 当日独立访客数
    ip: number;        // 当日IP数
  }>;
}
```

### 使用示例
```typescript
// 获取最近7天的访问统计
const response = await request.get('/statistics/visits');

// 获取指定日期范围的访问统计
const response = await request.get('/statistics/visits', {
  params: {
    startDate: '2024-02-01',
    endDate: '2024-02-08'
  }
});
```

## 3. 用户统计

### 基本信息
- 请求路径: `/api/v1/statistics/users`
- 请求方法: `GET`
- 权限要求: 需要登录

### 请求参数
| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| startDate | string | 否 | 开始日期（YYYY-MM-DD） | "2024-02-01" |
| endDate | string | 否 | 结束日期（YYYY-MM-DD） | "2024-02-08" |

### 响应数据
```typescript
interface UserStatistics {
  total: {
    total_users: number;   // 总用户数
    active_users: number;  // 活跃用户数
    new_users: number;     // 新增用户数
  };
  trends: Array<{         // 趋势数据
    date: string;         // 日期（YYYY-MM-DD）
    total_users: number;  // 当日总用户数
    active_users: number; // 当日活跃用户数
    new_users: number;    // 当日新增用户数
  }>;
}
```

### 使用示例
```typescript
// 获取最近7天的用户统计
const response = await request.get('/statistics/users');

// 获取指定日期范围的用户统计
const response = await request.get('/statistics/users', {
  params: {
    startDate: '2024-02-01',
    endDate: '2024-02-08'
  }
});
```

## 前端实现建议

### 1. 定义API服务
```typescript
// src/api/statistics.ts
import request from '@/utils/request'

export interface ContentStatistics { ... }
export interface VisitStatistics { ... }
export interface UserStatistics { ... }

export function getContentStatistics(params?: { startDate?: string; endDate?: string }) {
  return request.get<ContentStatistics>('/statistics/content', { params })
}

export function getVisitStatistics(params?: { startDate?: string; endDate?: string }) {
  return request.get<VisitStatistics>('/statistics/visits', { params })
}

export function getUserStatistics(params?: { startDate?: string; endDate?: string }) {
  return request.get<UserStatistics>('/statistics/users', { params })
}
```

### 2. 在组件中使用
```typescript
import { ref, onMounted } from 'vue'
import { getContentStatistics, getVisitStatistics, getUserStatistics } from '@/api/statistics'

// 定义响应式数据
const contentStats = ref<ContentStatistics>()
const visitStats = ref<VisitStatistics>()
const userStats = ref<UserStatistics>()

// 加载数据
const loadStatistics = async () => {
  try {
    const [content, visit, user] = await Promise.all([
      getContentStatistics(),
      getVisitStatistics(),
      getUserStatistics()
    ])
    contentStats.value = content
    visitStats.value = visit
    userStats.value = user
  } catch (error) {
    console.error('Failed to load statistics:', error)
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadStatistics()
})
```

### 3. 数据刷新策略
1. 定时刷新：每隔一定时间（如5分钟）自动刷新数据
2. 手动刷新：提供刷新按钮，用户可手动刷新数据
3. 条件刷新：当日期范围改变时刷新数据

### 4. 错误处理
1. 网络错误：显示网络错误提示
2. 权限错误：跳转到登录页面
3. 服务器错误：显示友好的错误提示

### 5. 缓存策略
1. 后端已实现1小时的数据缓存
2. 前端可以实现本地缓存，减少请求次数
3. 使用状态管理（如Pinia）统一管理统计数据
