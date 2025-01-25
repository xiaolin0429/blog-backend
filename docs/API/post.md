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

## 自动保存文章
- **接口说明**: 自动保存文章内容。每10秒最多保存一次，每2分钟强制保存一次。
- **请求方式**: POST
- **接口路径**: `/api/v1/posts/{id}/auto-save/`
- **请求头**:
  - Authorization: Bearer {token}（必填）
  - Content-Type: application/json
- **请求参数**:
```json
{
    "title": "string",     // 文章标题
    "content": "string",   // 文章内容
    "excerpt": "string",   // 文章摘要（可选）
    "category": 0,        // 分类ID（可选）
    "tags": [0],         // 标签ID列表（可选）
    "force_save": false  // 是否强制保存（可选，距离上次保存超过2分钟时可用）
}
```
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "version": 1,                              // 当前版本号
        "next_save_time": "2024-01-25T12:00:10Z"  // 下次允许保存的时间
    }
}
```
- **错误码**:
  - 400: 请求参数错误
  - 401: 未授权（未登录或token无效）
  - 403: 无权限（非文章作者）
  - 404: 文章不存在
  - 429: 请求过于频繁（需等待10秒）
  - 500: 数据库错误

## 获取自动保存内容
- **接口说明**: 获取文章最近一次自动保存的内容。如果没有自动保存内容，则返回当前内容。
- **请求方式**: GET
- **接口路径**: `/api/v1/posts/{id}/auto-save/`
- **请求头**:
  - Authorization: Bearer {token}（必填）
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "title": "string",                        // 文章标题
        "content": "string",                      // 文章内容
        "excerpt": "string",                      // 文章摘要
        "category": 0,                           // 分类ID
        "tags": [0],                            // 标签ID列表
        "version": 1,                           // 版本号
        "auto_save_time": "2024-01-25T12:00:00Z" // 自动保存时间
    }
}
```
- **错误码**:
  - 401: 未授权（未登录或token无效）
  - 403: 无权限（非文章作者）
  - 404: 文章不存在
