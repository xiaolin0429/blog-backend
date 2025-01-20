# 文章相关API

## 获取文章列表
- **接口说明**: 获取文章列表，支持分页、排序和筛选。普通用户只能看到已发布的文章，管理员可以看到所有文章。
- **请求方式**: GET
- **接口路径**: `/api/v1/posts/`
- **请求头**:
  - Authorization: Bearer {token}
- **请求参数**:
  - page: 页码（可选，默认1）
  - size: 每页数量（可选，默认10，最大50）
  - ordering: 排序字段（可选，支持created_at, -created_at, updated_at, -updated_at, published_at, -published_at, views, -views, likes, -likes）
  - category: 分类ID（可选）
  - tags: 标签ID列表（可选，多个标签ID用逗号分隔）
  - status: 状态（可选，draft/published/archived，普通用户只能看到published）
  - author: 作者ID（可选）
  - search: 搜索关键词（可选，搜索title, content, excerpt）

- **响应数据**:
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
                "title": "string",
                "excerpt": "string",
                "author": 0,
                "author_username": "string",
                "category": 0,
                "category_name": "string",
                "tags": [
                    {
                        "id": 0,
                        "name": "string"
                    }
                ],
                "status": "string",
                "comments_count": 0,
                "created_at": "string",
                "updated_at": "string",
                "published_at": "string"
            }
        ]
    }
}
```

## 创建文章
- **接口说明**: 创建新文章，作者会自动设置为当前登录用户
- **请求方式**: POST
- **接口路径**: `/api/v1/posts/`
- **请求头**:
  - Authorization: Bearer {token}（必填）
  - Content-Type: application/json
- **请求参数**:
```json
{
    "title": "string",     // 标题（必填，2-200字符）
    "content": "string",   // 内容（必填）
    "excerpt": "string",   // 摘要（可选）
    "category": 0,        // 分类ID（可选，如果提供则必须是有效的分类ID）
    "tags": [0],         // 标签ID列表（可选）
    "status": "string"   // 状态（可选，默认draft，可选值：draft/published/archived）
}
```
- **响应数据**:
```json
{
    "code": 201,
    "message": "success",
    "data": {
        "id": 0,
        "title": "string",
        "content": "string",
        "excerpt": "string",
        "author": 0,
        "category": 0,
        "tags": [0],
        "status": "string",
        "created_at": "string",
        "updated_at": "string",
        "published_at": "string"
    }
}
```
- **错误码**:
  - 400: 请求参数错误（标题长度不符、必填字段缺失等）
  - 401: 未授权（未登录或token无效）
  - 404: 分类或标签不存在

## 获取文章详情
- **接口说明**: 获取文章详细信息
- **请求方式**: GET
- **接口路径**: `/api/v1/posts/{id}/`
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 0,
        "title": "string",
        "content": "string",
        "excerpt": "string",
        "author": 0,
        "author_username": "string",
        "category": {
            "id": 0,
            "name": "string",
            "description": "string"
        },
        "tags": [
            {
                "id": 0,
                "name": "string"
            }
        ],
        "status": "string",
        "comments": [
            {
                "id": 0,
                "content": "string",
                "author": {
                    "id": 0,
                    "username": "string"
                },
                "created_at": "string",
                "replies": []
            }
        ],
        "created_at": "string",
        "updated_at": "string",
        "published_at": "string"
    }
}
```

## 更新文章
- **接口说明**: 更新文章信息
- **请求方式**: PUT
- **接口路径**: `/api/v1/posts/{id}/`
- **请求头**:
  - Authorization: Bearer {token}
- **请求参数**: 同创建文章
- **响应数据**: 同创建文章

## 删除文章
- **接口说明**: 删除文章
- **请求方式**: DELETE
- **接口路径**: `/api/v1/posts/{id}/`
- **请求头**:
  - Authorization: Bearer {token}
- **响应数据**: 
```json
{
    "code": 204,
    "message": "success",
    "data": null
}
```

## 文章点赞
- **接口说明**: 给文章点赞
- **请求方式**: POST
- **接口路径**: `/api/v1/posts/{id}/like/`
- **请求头**:
  - Authorization: Bearer {token}
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "likes": 0
    }
}
```

## 文章浏览
- **接口说明**: 增加文章浏览量
- **请求方式**: POST
- **接口路径**: `/api/v1/posts/{id}/view/`
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "views": 0
    }
}
```

## 文章归档
- **接口说明**: 将文章归档
- **请求方式**: POST
- **接口路径**: `/api/v1/posts/{id}/archive/`
- **请求头**:
  - Authorization: Bearer {token}
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "status": "archived"
    }
}
```
- **错误码**:
  - 401: 未授权
  - 403: 无权限操作此文章
  - 404: 文章不存在 

## 回收站相关API

### 获取回收站文章列表
- **接口说明**: 获取已删除的文章列表（软删除的文章）。普通用户只能看到自己的文章，管理员可以看到所有文章。
- **请求方式**: GET
- **接口路径**: `/api/v1/posts/trash/`
- **请求头**:
  - Authorization: Bearer {token}（必填）
- **请求参数**:
  - page: 页码（可选，默认1）
  - size: 每页数量（可选，默认10，最大50）
  - ordering: 排序字段（可选，支持deleted_at, -deleted_at）
  - search: 搜索关键词（可选，搜索title, content, excerpt）

- **响应数据**:
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
                "title": "string",
                "excerpt": "string",
                "author": 0,
                "author_username": "string",
                "category": 0,
                "category_name": "string",
                "tags": [
                    {
                        "id": 0,
                        "name": "string"
                    }
                ],
                "deleted_at": "string"
            }
        ]
    }
}
```
- **错误码**:
  - 401: 未授权（未登录或token无效）

### 恢复回收站文章
- **接口说明**: 恢复已删除的文章。恢复后的文章状态会重置为草稿状态。普通用户只能恢复自己的文章，管理员可以恢复所有文章。
- **请求方式**: POST
- **接口路径**: `/api/v1/posts/trash/{id}/restore/`
- **请求头**:
  - Authorization: Bearer {token}（必填）
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 0,
        "title": "string",
        "status": "draft"
    }
}
```
- **错误码**:
  - 401: 未授权（未登录或token无效）
  - 404: 文章不存在或无权限操作

### 彻底删除文章
- **接口说明**: 从回收站中彻底删除文章（物理删除）。此操作不可恢复。普通用户只能删除自己的文章，管理员可以删除所有文章。
- **请求方式**: DELETE
- **接口路径**: `/api/v1/posts/trash/{id}/`
- **请求头**:
  - Authorization: Bearer {token}（必填）
- **响应数据**:
```json
{
    "code": 204,
    "message": "success",
    "data": null
}
```
- **错误码**:
  - 401: 未授权（未登录或token无效）
  - 404: 文章不存在或无权限操作

### 清空回收站
- **接口说明**: 清空回收站中的所有文章（物理删除）。此操作不可恢复。普通用户只能清空自己的文章，管理员可以清空所有文章。
- **请求方式**: DELETE
- **接口路径**: `/api/v1/posts/trash/`
- **请求头**:
  - Authorization: Bearer {token}（必填）
- **响应数据**:
```json
{
    "code": 204,
    "message": "success",
    "data": null
}
```
- **错误码**:
  - 401: 未授权（未登录或token无效） 