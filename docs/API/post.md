# 文章相关API

## 获取文章列表

### 基本信息

- 请求路径: `/api/v1/posts`
- 请求方法: `GET`
- 权限要求: 无

### 查询参数

| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| page | integer | 否 | 页码，默认1 | 1 |
| size | integer | 否 | 每页数量，默认20，最大100 | 20 |
| ordering | string | 否 | 排序字段，默认-created_at，前缀-表示降序 | -created_at |
| category | integer | 否 | 按分类ID过滤 | 1 |
| tags | array | 否 | 按标签ID过滤，多个用逗号分隔 | 1,2,3 |
| author | integer | 否 | 按作者ID过滤 | 1 |
| status | string | 否 | 文章状态，默认published | published |

### 响应数据
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "total": 0,
        "page": 0,
        "size": 0,
        "pages": 0,
        "items": [
            {
                "id": 0,
                "title": "string",
                "excerpt": "string",
                "author": {
                    "id": 0,
                    "username": "string",
                    "nickname": "string"
                },
                "category": {
                    "id": 0,
                    "name": "string",
                    "level": 0
                },
                "tags": [
                    {
                        "id": 0,
                        "name": "string"
                    }
                ],
                "status": "string",
                "views": 0,
                "likes": 0,
                "comments": 0,
                "created_at": "string",
                "updated_at": "string"
            }
        ]
    },
    "timestamp": "string",
    "requestId": "string"
}
```

### 错误码

| 错误码 | 说明 |
| --- | --- |
| 400 | 请求参数错误 |

## 获取文章详情

### 基本信息

- 请求路径: `/api/v1/posts/{id}`
- 请求方法: `GET`
- 权限要求: 无

### 路径参数

| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| id | integer | 是 | 文章ID |

### 响应数据
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 0,
        "title": "string",
        "content": "string",
        "excerpt": "string",
        "author": {
            "id": 0,
            "username": "string",
            "nickname": "string"
        },
        "category": {
            "id": 0,
            "name": "string",
            "level": 0
        },
        "tags": [
            {
                "id": 0,
                "name": "string"
            }
        ],
        "status": "string",
        "views": 0,
        "likes": 0,
        "comments": 0,
        "created_at": "string",
        "updated_at": "string"
    },
    "timestamp": "string",
    "requestId": "string"
}
```

### 错误码

| 错误码 | 说明 |
| --- | --- |
| 404 | 文章不存在 |

## 创建文章

### 基本信息

- 请求路径: `/api/v1/posts`
- 请求方法: `POST`
- 权限要求: 需要登录

### 请求头

| 参数名 | 参数值 | 是否必须 | 示例 | 备注 |
| --- | --- | --- | --- | --- |
| Authorization | Bearer {access_token} | 是 | Bearer abc.def.xyz | 访问令牌 |
| Content-Type | application/json | 是 | application/json | 请求体格式 |

### 请求参数

| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| title | string | 是 | 文章标题，长度2-100 | "示例文章" |
| content | string | 是 | 文章内容，最大长度50000 | "这是文章内容" |
| excerpt | string | 否 | 文章摘要，最大长度500 | "这是摘要" |
| category_id | integer | 是 | 分类ID | 1 |
| tag_ids | array | 否 | 标签ID列表 | [1, 2] |
| status | string | 否 | 文章状态，默认draft | "draft" |

### 响应数据
```json
{
    "code": 201,
    "message": "success",
    "data": {
        "id": 0,
        "title": "string",
        "excerpt": "string",
        "category": {
            "id": 0,
            "name": "string",
            "level": 0
        },
        "tags": [
            {
                "id": 0,
                "name": "string"
            }
        ],
        "status": "string",
        "created_at": "string"
    },
    "timestamp": "string",
    "requestId": "string"
}
```

### 错误码

| 错误码 | 说明 |
| --- | --- |
| 400 | 请求参数错误 |
| 401 | 未登录或Token无效 |
| 409 | 分类或标签不存在 |

## 更新文章

### 基本信息

- 请求路径: `/api/v1/posts/{id}`
- 请求方法: `PUT`
- 权限要求: 需要登录且只能更新自己的文章

### 请求头

| 参数名 | 参数值 | 是否必须 | 示例 | 备注 |
| --- | --- | --- | --- | --- |
| Authorization | Bearer {access_token} | 是 | Bearer abc.def.xyz | 访问令牌 |
| Content-Type | application/json | 是 | application/json | 请求体格式 |

### 路径参数

| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| id | integer | 是 | 文章ID |

### 请求参数

| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| title | string | 否 | 文章标题，长度2-100 | "示例文章" |
| content | string | 否 | 文章内容，最大长度50000 | "这是文章内容" |
| excerpt | string | 否 | 文章摘要，最大长度500 | "这是摘要" |
| category_id | integer | 否 | 分类ID | 1 |
| tag_ids | array | 否 | 标签ID列表 | [1, 2] |
| status | string | 否 | 文章状态 | "published" |

### 响应数据
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 0,
        "title": "string",
        "excerpt": "string",
        "category": {
            "id": 0,
            "name": "string",
            "level": 0
        },
        "tags": [
            {
                "id": 0,
                "name": "string"
            }
        ],
        "status": "string",
        "updated_at": "string"
    },
    "timestamp": "string",
    "requestId": "string"
}
```

### 错误码

| 错误码 | 说明 |
| --- | --- |
| 400 | 请求参数错误 |
| 401 | 未登录或Token无效 |
| 403 | 无权限修改 |
| 404 | 文章不存在 |
| 409 | 分类或标签不存在 |

## 删除文章

### 基本信息

- 请求路径: `/api/v1/posts/{id}`
- 请求方法: `DELETE`
- 权限要求: 需要登录且只能删除自己的文章

### 请求头

| 参数名 | 参数值 | 是否必须 | 示例 | 备注 |
| --- | --- | --- | --- | --- |
| Authorization | Bearer {access_token} | 是 | Bearer abc.def.xyz | 访问令牌 |

### 路径参数

| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| id | integer | 是 | 文章ID |

### 响应数据
```json
{
    "code": 204,
    "message": "success",
    "data": null,
    "timestamp": "string",
    "requestId": "string"
}
```

### 错误码

| 错误码 | 说明 |
| --- | --- |
| 401 | 未登录或Token无效 |
| 403 | 无权限删除 |
| 404 | 文章不存在 |

## 自动保存文章

### 基本信息

- 请求路径: `/api/v1/posts/{id}/auto-save`
- 请求方法: `PUT`
- 权限要求: 需要登录且只能保存自己的文章

### 请求头

| 参数名 | 参数值 | 是否必须 | 示例 | 备注 |
| --- | --- | --- | --- | --- |
| Authorization | Bearer {access_token} | 是 | Bearer abc.def.xyz | 访问令牌 |
| Content-Type | application/json | 是 | application/json | 请求体格式 |

### 路径参数

| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| id | integer | 是 | 文章ID |

### 请求参数

| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| title | string | 是 | 文章标题，长度2-100 | "示例文章" |
| content | string | 是 | 文章内容，最大长度50000 | "这是文章内容" |
| category_id | integer | 是 | 分类ID | 1 |
| tag_ids | array | 否 | 标签ID列表 | [1, 2] |

### 响应数据
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 0,
        "title": "string",
        "content": "string",
        "category": {
            "id": 0,
            "name": "string",
            "level": 0
        },
        "tags": [
            {
                "id": 0,
                "name": "string"
            }
        ],
        "auto_saved_at": "string",
        "next_save_time": "string"
    },
    "timestamp": "string",
    "requestId": "string"
}
```

### 错误码

| 错误码 | 说明 |
| --- | --- |
| 400 | 请求参数错误 |
| 401 | 未登录或Token无效 |
| 403 | 无权限保存 |
| 404 | 文章不存在 |
| 409 | 分类或标签不存在 |

## 获取自动保存内容

### 基本信息

- 请求路径: `/api/v1/posts/{id}/auto-save`
- 请求方法: `GET`
- 权限要求: 需要登录且只能获取自己的文章

### 请求头

| 参数名 | 参数值 | 是否必须 | 示例 | 备注 |
| --- | --- | --- | --- | --- |
| Authorization | Bearer {access_token} | 是 | Bearer abc.def.xyz | 访问令牌 |

### 路径参数

| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| id | integer | 是 | 文章ID |

### 响应数据
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 0,
        "title": "string",
        "content": "string",
        "category": {
            "id": 0,
            "name": "string",
            "level": 0
        },
        "tags": [
            {
                "id": 0,
                "name": "string"
            }
        ],
        "auto_saved_at": "string"
    },
    "timestamp": "string",
    "requestId": "string"
}
```

### 错误码

| 错误码 | 说明 |
| --- | --- |
| 401 | 未登录或Token无效 |
| 403 | 无权限访问 |
| 404 | 文章不存在 |
