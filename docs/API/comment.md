# 评论相关API

## 获取全局评论列表
- **接口说明**: 获取所有评论列表，支持分页、排序和筛选
- **请求方式**: GET
- **接口路径**: `/api/v1/comments/`
- **请求参数**:
  - page: 页码（可选，默认1）
  - size: 每页数量（可选，默认10，最大50）
  - ordering: 排序字段（可选，支持created_at）
  - author: 作者ID（可选）
  - post: 文章ID（可选）
  - search: 搜索关键词（可选，搜索content）

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
                "content": "string",
                "author": {
                    "id": 0,
                    "username": "string"
                },
                "post": {
                    "id": 0,
                    "title": "string"
                },
                "parent": 0,
                "replies_count": 0,
                "created_at": "string",
                "updated_at": "string"
            }
        ]
    }
}
```

## 获取文章评论列表
- **接口说明**: 获取指定文章的评论列表
- **请求方式**: GET
- **接口路径**: `/api/v1/posts/{post_id}/comments/`
- **请求参数**:
  - page: 页码（可选，默认1）
  - size: 每页数量（可选，默认10，最大50）
  - ordering: 排序字段（可选，支持created_at）

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
                "content": "string",
                "author": {
                    "id": 0,
                    "username": "string"
                },
                "parent": 0,
                "replies": [
                    {
                        "id": 0,
                        "content": "string",
                        "author": {
                            "id": 0,
                            "username": "string"
                        },
                        "created_at": "string"
                    }
                ],
                "created_at": "string",
                "updated_at": "string"
            }
        ]
    }
}
```

## 创建评论
- **接口说明**: 创建新评论或回复评论
- **请求方式**: POST
- **接口路径**: `/api/v1/posts/{post_id}/comments/`
- **请求头**:
  - Authorization: Bearer {token}
- **请求参数**:
```json
{
    "content": "string",  // 评论内容（必填，2-500字符）
    "parent": 0          // 父评论ID（可选，回复评论时必填）
}
```
- **响应数据**:
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
        "parent": 0,
        "created_at": "string",
        "updated_at": "string"
    }
}
```
- **错误码**:
  - 400: 请求参数错误
  - 401: 未授权
  - 404: 文章或父评论不存在

## 获取评论详情
- **接口说明**: 获取评论详细信息
- **请求方式**: GET
- **接口路径**: `/api/v1/comments/{id}/`
- **响应数据**:
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
        "post": {
            "id": 0,
            "title": "string"
        },
        "parent": 0,
        "replies": [
            {
                "id": 0,
                "content": "string",
                "author": {
                    "id": 0,
                    "username": "string"
                },
                "created_at": "string"
            }
        ],
        "created_at": "string",
        "updated_at": "string"
    }
}
```

## 更新评论
- **接口说明**: 更新评论内容
- **请求方式**: PUT
- **接口路径**: `/api/v1/comments/{id}/`
- **请求头**:
  - Authorization: Bearer {token}
- **请求参数**:
```json
{
    "content": "string"  // 评论内容（必填，2-500字符）
}
```
- **响应数据**: 同创建评论
- **错误码**:
  - 400: 请求参数错误
  - 401: 未授权
  - 403: 无权限修改此评论
  - 404: 评论不存在

## 删除评论
- **接口说明**: 删除评论
- **请求方式**: DELETE
- **接口路径**: `/api/v1/comments/{id}/`
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
- **错误码**:
  - 401: 未授权
  - 403: 无权限删除此评论
  - 404: 评论不存在
