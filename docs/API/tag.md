# 标签相关API

## 获取标签列表
- **接口说明**: 获取标签列表，支持分页、排序和筛选
- **请求方式**: GET
- **接口路径**: `/api/v1/tags/`
- **请求参数**:
  - page: 页码（可选，默认1）
  - size: 每页数量（可选，默认10，最大50）
  - ordering: 排序字段（可选，支持name, -name, created_at, -created_at, post_count, -post_count）
  - search: 搜索关键词（可选，搜索name和description）

- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "total": 100,
        "page": 1,
        "size": 10,
        "pages": 10,
        "items": [
            {
                "id": 1,
                "name": "string",
                "description": "string",
                "post_count": 0,
                "created_at": "2024-01-19T10:30:00Z",
                "updated_at": "2024-01-19T10:30:00Z"
            }
        ]
    },
    "timestamp": "2024-01-19T10:30:00Z",
    "requestId": "string"
}
```

## 创建标签
- **接口说明**: 创建新标签
- **请求方式**: POST
- **接口路径**: `/api/v1/tags/`
- **请求头**:
  - Authorization: Bearer {token}
- **请求参数**:
```json
{
    "name": "string",        // 标签名称（必填，2-50字符，唯一）
    "description": "string"  // 标签描述（可选，最大200字符）
}
```
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "name": "string",
        "description": "string",
        "post_count": 0,
        "created_at": "2024-01-19T10:30:00Z",
        "updated_at": "2024-01-19T10:30:00Z"
    },
    "timestamp": "2024-01-19T10:30:00Z",
    "requestId": "string"
}
```
- **错误码**:
  - 400: 请求参数错误（名称为空或超长）
  - 401: 未授权
  - 409: 标签名称已存在

## 批量创建标签
- **接口说明**: 批量创建多个标签
- **请求方式**: POST
- **接口路径**: `/api/v1/tags/batch/`
- **请求头**:
  - Authorization: Bearer {token}
- **请求参数**:
```json
{
    "tags": [
        {
            "name": "string",        // 标签名称（必填，2-50字符，唯一）
            "description": "string"  // 标签描述（可选，最大200字符）
        }
    ]
}
```
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "success": 2,      // 成功创建数量
        "failed": 1,       // 失败数量
        "items": [         // 创建结果列表
            {
                "name": "string",    // 标签名称
                "success": true,     // 是否成功
                "message": "string", // 失败原因（失败时返回）
                "data": {           // 创建成功的标签信息（成功时返回）
                    "id": 1,
                    "name": "string",
                    "description": "string",
                    "post_count": 0,
                    "created_at": "2024-01-19T10:30:00Z",
                    "updated_at": "2024-01-19T10:30:00Z"
                }
            }
        ]
    },
    "timestamp": "2024-01-19T10:30:00Z",
    "requestId": "string"
}
```
- **错误码**:
  - 400: 请求参数错误
  - 401: 未授权

## 获取标签详情
- **接口说明**: 获取标签详细信息
- **请求方式**: GET
- **接口路径**: `/api/v1/tags/{id}/`
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "name": "string",
        "description": "string",
        "post_count": 0,
        "posts": [         // 最近的文章列表（最多10篇）
            {
                "id": 1,
                "title": "string",
                "created_at": "2024-01-19T10:30:00Z"
            }
        ],
        "created_at": "2024-01-19T10:30:00Z",
        "updated_at": "2024-01-19T10:30:00Z"
    },
    "timestamp": "2024-01-19T10:30:00Z",
    "requestId": "string"
}
```

## 更新标签
- **接口说明**: 更新标签信息
- **请求方式**: PUT
- **接口路径**: `/api/v1/tags/{id}/`
- **请求头**:
  - Authorization: Bearer {token}
- **请求参数**:
```json
{
    "name": "string",        // 标签名称（必填，2-50字符，唯一）
    "description": "string"  // 标签描述（可选，最大200字符）
}
```
- **响应数据**: 同创建标签
- **错误码**:
  - 400: 请求参数错误
  - 401: 未授权
  - 403: 无权限修改此标签
  - 404: 标签不存在
  - 409: 标签名称已存在

## 删除标签
- **接口说明**: 删除标签
- **请求方式**: DELETE
- **接口路径**: `/api/v1/tags/{id}/`
- **请求头**:
  - Authorization: Bearer {token}
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": null,
    "timestamp": "2024-01-19T10:30:00Z",
    "requestId": "string"
}
```
- **错误码**:
  - 401: 未授权
  - 403: 无权限删除此标签
  - 404: 标签不存在
  - 409: 标签下存在文章，不能删除

## 获取标签统计
- **接口说明**: 获取标签使用统计信息
- **请求方式**: GET
- **接口路径**: `/api/v1/tags/stats/`
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "total": 100,           // 标签总数
        "total_used": 80,       // 已使用标签数
        "most_used": [          // 使用最多的标签（前10个）
            {
                "id": 1,
                "name": "string",
                "post_count": 50
            }
        ],
        "recently_created": [    // 最近创建的标签（前10个）
            {
                "id": 1,
                "name": "string",
                "created_at": "2024-01-19T10:30:00Z"
            }
        ],
        "recently_used": [       // 最近使用的标签（前10个）
            {
                "id": 1,
                "name": "string",
                "last_used_at": "2024-01-19T10:30:00Z"
            }
        ]
    },
    "timestamp": "2024-01-19T10:30:00Z",
    "requestId": "string"
}
```
