# 分类相关API

## 分类管理API

### 获取分类列表

#### 基本信息
- 请求路径: `/api/v1/categories`
- 请求方法: `GET`
- 权限要求: 无

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| parent | number | 否 | 父分类ID,不传则获取顶级分类 |
| search | string | 否 | 搜索关键词,支持分类名称模糊搜索 |
| ordering | string | 否 | 排序字段,支持 order、name、created_at,默认按 order、id 升序排序 |

#### 响应数据
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "name": "分类1",
      "description": "分类1的描述",
      "parent": null,
      "level": 0,
      "order": 1,
      "children": [
        {
          "id": 2,
          "name": "子分类1",
          "description": "子分类1的描述", 
          "parent": 1,
          "level": 1,
          "order": 1,
          "children": []
        }
      ],
      "created_at": "2024-01-19T10:30:00Z",
      "updated_at": "2024-01-19T10:30:00Z"
    }
  ],
  "timestamp": "2024-01-19T10:30:00Z",
  "requestId": "string"
}
```

#### 说明
1. 分类支持无限层级嵌套,每个分类都有一个 level 字段表示其层级(0表示顶级分类,1表示二级分类,以此类推)
2. 默认按 order 字段升序排序,order 相同时按 id 升序排序
3. 不传 parent 参数时只返回顶级分类,子分类通过 children 字段返回

### 创建分类

#### 基本信息
- 请求路径: `/api/v1/categories`
- 请求方法: `POST`
- 权限要求: 需要管理员权限

#### 请求头
| 参数名 | 必填 | 说明 |
|-------|------|------|
| Authorization | 是 | Bearer {access_token} |
| Content-Type | 是 | application/json |

#### 请求参数
```json
{
  "name": "分类名称",
  "description": "分类描述",
  "parent": 1,
  "order": 1
}
```

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| name | string | 是 | 分类名称,2-50个字符 |
| description | string | 否 | 分类描述 |
| parent | number | 否 | 父分类ID |
| order | number | 否 | 排序值,默认为0 |

#### 响应数据
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "分类名称",
    "description": "分类描述",
    "parent": 1,
    "level": 1,
    "order": 1,
    "children": [],
    "created_at": "2024-01-19T10:30:00Z",
    "updated_at": "2024-01-19T10:30:00Z"
  },
  "timestamp": "2024-01-19T10:30:00Z",
  "requestId": "string"
}
```

#### 错误码
| 错误码 | 说明 |
|-------|------|
| 400 | 参数错误,如名称长度不符合要求 |
| 401 | 未登录 |
| 403 | 权限不足 |
| 404 | 父分类不存在 |
| 409 | 分类名称已存在 |

### 快速创建分类

#### 基本信息
- 请求路径: `/api/v1/categories/quick-create`
- 请求方法: `POST`
- 权限要求: 需要登录

#### 请求头
| 参数名 | 必填 | 说明 |
|-------|------|------|
| Authorization | 是 | Bearer {access_token} |
| Content-Type | 是 | application/json |

#### 请求参数
```json
{
  "name": "分类名称",
  "parent": 1
}
```

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| name | string | 是 | 分类名称,2-50个字符 |
| parent | number | 否 | 父分类ID |

#### 响应数据
```json
{
  "code": 200,
  "message": "success", 
  "data": {
    "id": 1,
    "name": "分类名称",
    "parent": 1,
    "parent_name": "父分类名称",
    "created_at": "2024-01-19T10:30:00Z"
  },
  "timestamp": "2024-01-19T10:30:00Z",
  "requestId": "string"
}
```

#### 错误码
| 错误码 | 说明 |
|-------|------|
| 400 | 参数错误,如名称为空或长度不符合要求 |
| 401 | 未登录 |
| 404 | 父分类不存在 |
| 409 | 分类名称已存在 |

### 获取分类详情

#### 基本信息
- 请求路径: `/api/v1/categories/{id}`
- 请求方法: `GET`
- 权限要求: 需要登录

#### 请求头
| 参数名 | 必填 | 说明 |
|-------|------|------|
| Authorization | 是 | Bearer {access_token} |

#### 响应数据
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "分类名称",
    "description": "分类描述",
    "parent": 1,
    "level": 1,
    "order": 1,
    "children": [],
    "created_at": "2024-01-19T10:30:00Z",
    "updated_at": "2024-01-19T10:30:00Z"
  },
  "timestamp": "2024-01-19T10:30:00Z",
  "requestId": "string"
}
```

#### 错误码
| 错误码 | 说明 |
|-------|------|
| 401 | 未登录 |
| 404 | 分类不存在 |

### 更新分类

#### 基本信息
- 请求路径: `/api/v1/categories/{id}`
- 请求方法: `PUT`
- 权限要求: 需要管理员权限

#### 请求头
| 参数名 | 必填 | 说明 |
|-------|------|------|
| Authorization | 是 | Bearer {access_token} |
| Content-Type | 是 | application/json |

#### 请求参数
```json
{
  "name": "分类名称",
  "description": "分类描述",
  "parent": 1,
  "order": 1
}
```

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| name | string | 否 | 分类名称,2-50个字符 |
| description | string | 否 | 分类描述 |
| parent | number | 否 | 父分类ID |
| order | number | 否 | 排序值 |

#### 响应数据
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "分类名称",
    "description": "分类描述",
    "parent": 1,
    "level": 1,
    "order": 1,
    "children": [],
    "created_at": "2024-01-19T10:30:00Z",
    "updated_at": "2024-01-19T10:30:00Z"
  },
  "timestamp": "2024-01-19T10:30:00Z",
  "requestId": "string"
}
```

#### 错误码
| 错误码 | 说明 |
|-------|------|
| 401 | 未登录 |
| 403 | 权限不足 |
| 404 | 分类不存在 |
| 422 | 更新失败,如名称已存在 |

### 删除分类

#### 基本信息
- 请求路径: `/api/v1/categories/{id}`
- 请求方法: `DELETE`
- 权限要求: 需要管理员权限

#### 请求头
| 参数名 | 必填 | 说明 |
|-------|------|------|
| Authorization | 是 | Bearer {access_token} |

#### 响应数据
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null,
  "timestamp": "2024-01-19T10:30:00Z",
  "requestId": "string"
}
```

#### 错误码
| 错误码 | 说明 |
|-------|------|
| 401 | 未登录 |
| 403 | 权限不足 |
| 404 | 分类不存在 |
| 422 | 删除失败,如存在子分类或关联文章 |
