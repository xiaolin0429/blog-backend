# 评论相关API

## 获取全局评论列表

### 基本信息
- **接口说明**: 获取所有评论列表，支持分页、排序和筛选
- **请求方式**: GET
- **接口路径**: `/api/v1/comments`
- **权限要求**: 无

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| page | number | 否 | 页码,默认1 |
| size | number | 否 | 每页数量,默认10,最大50 |
| ordering | string | 否 | 排序字段,支持created_at和reply_count,前缀-表示降序 |
| keyword | string | 否 | 关键词搜索,搜索评论内容和作者用户名 |
| post | number | 否 | 按文章ID筛选 |
| author | number | 否 | 按作者ID筛选 |
| start_date | string | 否 | 开始日期,格式:YYYY-MM-DD |
| end_date | string | 否 | 结束日期,格式:YYYY-MM-DD |

### 响应数据
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "count": 0,
    "next": "string",
    "previous": "string",
    "results": [
      {
        "id": 0,
        "content": "string",
        "author": {
          "id": 0,
          "username": "string"
        },
        "post": {
          "id": 0,
          "title": "string"
        },
        "parent": null,
        "reply_count": 0,
        "created_at": "2024-01-19T10:30:00Z",
        "updated_at": "2024-01-19T10:30:00Z"
      }
    ]
  },
  "timestamp": "2024-01-19T10:30:00Z",
  "requestId": "string"
}
```

## 获取文章评论列表

### 基本信息
- **接口说明**: 获取指定文章的评论列表,包含评论的回复
- **请求方式**: GET
- **接口路径**: `/api/v1/posts/{post_id}/comments`
- **权限要求**: 无

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| post_id | number | 是 | 文章ID |
| page | number | 否 | 页码,默认1 |
| size | number | 否 | 每页数量,默认10,最大50 |

### 响应数据
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 0,
      "content": "string",
      "author": {
        "id": 0,
        "username": "string"
      },
      "parent": null,
      "replies": [
        {
          "id": 0,
          "content": "string",
          "author": {
            "id": 0,
            "username": "string"
          },
          "created_at": "2024-01-19T10:30:00Z",
          "updated_at": "2024-01-19T10:30:00Z"
        }
      ],
      "reply_count": 0,
      "created_at": "2024-01-19T10:30:00Z",
      "updated_at": "2024-01-19T10:30:00Z"
    }
  ],
  "timestamp": "2024-01-19T10:30:00Z",
  "requestId": "string"
}
```

### 错误码
| 错误码 | 说明 |
|--------|------|
| 404 | 文章不存在 |

## 创建评论

### 基本信息
- **接口说明**: 为指定文章创建新评论
- **请求方式**: POST  
- **接口路径**: `/api/v1/posts/{post_id}/comments`
- **权限要求**: 需要登录

### 请求头
| 参数名 | 必填 | 说明 |
|--------|------|------|
| Authorization | 是 | Bearer {access_token} |
| Content-Type | 是 | application/json |

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| post_id | number | 是 | 文章ID |
| content | string | 是 | 评论内容 |
| parent | number | 否 | 父评论ID,用于回复评论 |

### 响应数据
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 0,
    "content": "string",
    "author": {
      "id": 0,
      "username": "string"
    },
    "parent": null,
    "created_at": "2024-01-19T10:30:00Z",
    "updated_at": "2024-01-19T10:30:00Z"
  },
  "timestamp": "2024-01-19T10:30:00Z",
  "requestId": "string"
}
```

### 错误码
| 错误码 | 说明 |
|--------|------|
| 400 | 评论内容不能为空 |
| 400 | 不支持嵌套回复 |
| 400 | 不能跨文章回复评论 |
| 400 | 父评论不存在 |
| 401 | 未登录用户无法评论 |
| 404 | 文章不存在 |

## 获取评论详情

### 基本信息
- **接口说明**: 获取指定评论的详细信息
- **请求方式**: GET
- **接口路径**: `/api/v1/comments/{id}`
- **权限要求**: 无

### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | number | 是 | 评论ID |

### 响应数据
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 0,
    "content": "string",
    "author": {
      "id": 0,
      "username": "string"
    },
    "parent": null,
    "replies": [
      {
        "id": 0,
        "content": "string",
        "author": {
          "id": 0,
          "username": "string"
        },
        "created_at": "2024-01-19T10:30:00Z",
        "updated_at": "2024-01-19T10:30:00Z"
      }
    ],
    "reply_count": 0,
    "created_at": "2024-01-19T10:30:00Z",
    "updated_at": "2024-01-19T10:30:00Z"
  },
  "timestamp": "2024-01-19T10:30:00Z",
  "requestId": "string"
}
```

### 错误码
| 错误码 | 说明 |
|--------|------|
| 404 | 评论不存在 |

## 更新评论

### 基本信息
- **接口说明**: 更新指定评论的内容
- **请求方式**: PUT
- **接口路径**: `/api/v1/comments/{id}`
- **权限要求**: 需要登录且只能修改自己的评论

### 请求头
| 参数名 | 必填 | 说明 |
|--------|------|------|
| Authorization | 是 | Bearer {access_token} |
| Content-Type | 是 | application/json |

### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | number | 是 | 评论ID |
| content | string | 是 | 评论内容 |

### 响应数据
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 0,
    "content": "string",
    "author": {
      "id": 0,
      "username": "string"
    },
    "parent": null,
    "created_at": "2024-01-19T10:30:00Z",
    "updated_at": "2024-01-19T10:30:00Z"
  },
  "timestamp": "2024-01-19T10:30:00Z",
  "requestId": "string"
}
```

### 错误码
| 错误码 | 说明 |
|--------|------|
| 401 | 未登录用户无法修改评论 |
| 403 | 无权修改他人的评论 |
| 404 | 评论不存在 |

## 删除评论

### 基本信息
- **接口说明**: 删除指定评论
- **请求方式**: DELETE
- **接口路径**: `/api/v1/comments/{id}`
- **权限要求**: 需要登录且只能删除自己的评论

### 请求头
| 参数名 | 必填 | 说明 |
|--------|------|------|
| Authorization | 是 | Bearer {access_token} |

### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | number | 是 | 评论ID |

### 响应数据
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null,
  "timestamp": "2024-01-19T10:30:00Z",
  "requestId": "string"
}
```

### 错误码
| 错误码 | 说明 |
|--------|------|
| 401 | 未登录用户无法删除评论 |
| 403 | 无权删除他人的评论 |
| 404 | 评论不存在 |
