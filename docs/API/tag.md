# 标签相关API

## 获取标签列表
### 基本信息
- **接口说明**: 获取所有标签列表，支持搜索和排序
- **请求方式**: GET
- **接口路径**: `/api/v1/tags`

### 请求参数
| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
|--------|------|----------|------|------|
| search | string | 否 | 搜索关键词，搜索标签名称 | "Django" |
| ordering | string | 否 | 排序字段，支持id、name、post_count，降序在字段前加- | "-post_count" |
| page | number | 否 | 页码，默认1 | 1 |
| size | number | 否 | 每页数量，默认10，最大100 | 10 |

### 响应参数
#### 基础字段
| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| code | number | 是 | 状态码 |
| message | string | 是 | 状态信息 |
| timestamp | string | 是 | 时间戳 |
| requestId | string | 是 | 请求ID |

#### data字段
| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| count | number | 是 | 总数 |
| results | array | 是 | 标签列表 |

#### results数组元素
| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| id | number | 是 | 标签ID |
| name | string | 是 | 标签名称 |
| description | string | 否 | 标签描述 |
| post_count | number | 是 | 文章数量 |
| created_at | string | 是 | 创建时间 |
| updated_at | string | 是 | 更新时间 |

### 响应示例
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "count": 2,
        "results": [
            {
                "id": 1,
                "name": "Python",
                "description": "Python编程语言",
                "post_count": 10,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": 2,
                "name": "Django",
                "description": "Django Web框架",
                "post_count": 5,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        ]
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "requestId": "xxxxx"
}
```

## 创建标签
### 基本信息
- **接口说明**: 创建新标签
- **请求方式**: POST
- **接口路径**: `/api/v1/tags`
- **权限要求**: 需要登录

### 请求头
| 参数名 | 是否必须 | 说明 |
|--------|----------|------|
| Authorization | 是 | Bearer {token} |
| Content-Type | 是 | application/json |

### 请求参数
| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
|--------|------|----------|------|------|
| name | string | 是 | 标签名称，长度2-50字符 | "Python" |
| description | string | 否 | 标签描述 | "Python编程语言" |

### 响应参数
同标签列表中的单个标签对象

### 错误码
| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误（标签名称为空/长度不符合要求） |
| 401 | 未登录 |
| 409 | 标签名称已存在 |

### 响应示例
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "name": "Python",
        "description": "Python编程语言",
        "post_count": 0,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "requestId": "xxxxx"
}
```

## 批量创建标签
### 基本信息
- **接口说明**: 批量创建多个标签
- **请求方式**: POST
- **接口路径**: `/api/v1/tags/batch`
- **权限要求**: 需要登录

### 请求头
| 参数名 | 是否必须 | 说明 |
|--------|----------|------|
| Authorization | 是 | Bearer {token} |
| Content-Type | 是 | application/json |

### 请求参数
| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
|--------|------|----------|------|------|
| 数组项 | array | 是 | 标签列表，每项包含name和description | 见示例 |

### 响应参数
| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| success | number | 是 | 成功创建数量 |
| failed | number | 是 | 失败数量 |
| items | array | 是 | 创建结果列表 |

#### items数组元素
| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| name | string | 是 | 标签名称 |
| success | boolean | 是 | 是否成功 |
| message | string | 否 | 失败原因 |
| id | number | 否 | 标签ID（成功时返回） |
| post_count | number | 否 | 文章数量（成功时返回） |

### 请求示例
```json
[
    {
        "name": "Python",
        "description": "Python编程语言"
    },
    {
        "name": "Django",
        "description": "Django Web框架"
    }
]
```

### 响应示例
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "success": 2,
        "failed": 0,
        "items": [
            {
                "name": "Python",
                "success": true,
                "id": 1,
                "post_count": 0
            },
            {
                "name": "Django",
                "success": true,
                "id": 2,
                "post_count": 0
            }
        ]
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "requestId": "xxxxx"
}
```

## 获取标签详情
### 基本信息
- **接口说明**: 获取标签详细信息，包含最近的文章列表
- **请求方式**: GET
- **接口路径**: `/api/v1/tags/{id}`

### 路径参数
| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
|--------|------|----------|------|------|
| id | number | 是 | 标签ID | 1 |

### 响应参数
除了标签基本信息外，还包含：

| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| posts | array | 是 | 最近的文章列表（最多10篇） |

#### posts数组元素
| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| id | number | 是 | 文章ID |
| title | string | 是 | 文章标题 |
| created_at | string | 是 | 创建时间 |

### 响应示例
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "name": "Python",
        "description": "Python编程语言",
        "post_count": 2,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "posts": [
            {
                "id": 1,
                "title": "Python入门教程",
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": 2,
                "title": "Python进阶教程",
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "requestId": "xxxxx"
}
```

## 更新标签
### 基本信息
- **接口说明**: 更新标签信息
- **请求方式**: PUT
- **接口路径**: `/api/v1/tags/{id}`
- **权限要求**: 需要登录

### 请求头
| 参数名 | 是否必须 | 说明 |
|--------|----------|------|
| Authorization | 是 | Bearer {token} |
| Content-Type | 是 | application/json |

### 路径参数
| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
|--------|------|----------|------|------|
| id | number | 是 | 标签ID | 1 |

### 请求参数
| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
|--------|------|----------|------|------|
| name | string | 是 | 标签名称，长度2-50字符 | "Python" |
| description | string | 否 | 标签描述 | "Python编程语言" |

### 错误码
| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未登录 |
| 404 | 标签不存在 |
| 409 | 标签名称已存在 |

### 响应示例
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "name": "Python",
        "description": "Python编程语言",
        "post_count": 2,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "requestId": "xxxxx"
}
```

## 删除标签
### 基本信息
- **接口说明**: 删除指定标签，如果标签下存在文章则无法删除
- **请求方式**: DELETE
- **接口路径**: `/api/v1/tags/{id}`
- **权限要求**: 需要登录

### 请求头
| 参数名 | 是否必须 | 说明 |
|--------|----------|------|
| Authorization | 是 | Bearer {token} |

### 路径参数
| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
|--------|------|----------|------|------|
| id | number | 是 | 标签ID | 1 |

### 错误码
| 错误码 | 说明 |
|--------|------|
| 401 | 未登录 |
| 404 | 标签不存在 |
| 409 | 标签下存在文章，不能删除 |

### 响应示例
```json
{
    "code": 200,
    "message": "删除成功",
    "data": null,
    "timestamp": "2024-01-01T00:00:00Z",
    "requestId": "xxxxx"
}
```

## 获取标签统计
### 基本信息
- **接口说明**: 获取标签使用统计信息
- **请求方式**: GET
- **接口路径**: `/api/v1/tags/stats`

### 响应参数
| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| total | number | 是 | 标签总数 |
| total_used | number | 是 | 已使用标签数 |
| most_used | array | 是 | 使用最多的标签（前10个） |
| recently_created | array | 是 | 最近创建的标签（前10个） |
| recently_used | array | 是 | 最近使用的标签（前10个） |

#### most_used数组元素
| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| id | number | 是 | 标签ID |
| name | string | 是 | 标签名称 |
| post_count | number | 是 | 文章数量 |

#### recently_created数组元素
| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| id | number | 是 | 标签ID |
| name | string | 是 | 标签名称 |
| created_at | string | 是 | 创建时间 |

#### recently_used数组元素
| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| id | number | 是 | 标签ID |
| name | string | 是 | 标签名称 |
| last_used_at | string | 是 | 最后使用时间 |

### 响应示例
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "total": 10,
        "total_used": 5,
        "most_used": [
            {
                "id": 1,
                "name": "Python",
                "post_count": 10
            }
        ],
        "recently_created": [
            {
                "id": 2,
                "name": "Django",
                "created_at": "2024-01-01T00:00:00Z"
            }
        ],
        "recently_used": [
            {
                "id": 1,
                "name": "Python",
                "last_used_at": "2024-01-01T00:00:00Z"
            }
        ]
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "requestId": "xxxxx"
}
```
