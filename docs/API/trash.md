# 回收站API

## 获取回收站文章列表
- **接口说明**: 获取已删除的文章列表（软删除的文章）。普通用户只能看到自己的文章，管理员可以看到所有文章。
- **请求方式**: GET
- **接口路径**: `/api/v1/trash/posts`
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
        "total": number,      // 总数（必返回）
        "page": number,       // 当前页码（必返回）
        "size": number,       // 每页数量（必返回）
        "pages": number,      // 总页数（必返回）
        "items": [           // 文章列表（必返回）
            {
                "id": number,           // 文章ID（必返回）
                "title": "string",      // 文章标题（必返回）
                "excerpt": "string",    // 文章摘要（可能为null）
                "author": {            // 作者信息（必返回）
                    "id": number,       // 作者ID（必返回）
                    "username": "string", // 用户名（必返回）
                    "nickname": "string"  // 昵称（可能为null）
                },
                "category": {          // 分类信息（必返回）
                    "id": number,       // 分类ID（必返回）
                    "name": "string"    // 分类名称（必返回）
                },
                "tags": [             // 标签列表（必返回）
                    {
                        "id": number,   // 标签ID（必返回）
                        "name": "string" // 标签名称（必返回）
                    }
                ],
                "deleted_at": "string" // 删除时间（必返回）
            }
        ]
    },
    "timestamp": "string", // 时间戳（必返回）
    "requestId": "string"  // 请求ID（必返回）
}
```
- **错误码**:
  - 401: 未授权（未登录或token无效）

## 恢复回收站文章
- **接口说明**: 恢复已删除的文章。恢复后的文章状态会重置为草稿状态。普通用户只能恢复自己的文章，管理员可以恢复所有文章。
- **请求方式**: POST
- **接口路径**: `/api/v1/trash/posts/{id}/restore`
- **请求头**:
  - Authorization: Bearer {token}（必填）
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": number,         // 文章ID（必返回）
        "title": "string",    // 文章标题（必返回）
        "status": "draft"     // 文章状态（必返回）
    },
    "timestamp": "string", // 时间戳（必返回）
    "requestId": "string"  // 请求ID（必返回）
}
```
- **错误码**:
  - 401: 未授权（未登录或token无效）
  - 404: 文章不存在或无权限操作

## 彻底删除文章
- **接口说明**: 从回收站中彻底删除文章（物理删除）。此操作不可恢复。普通用户只能删除自己的文章，管理员可以删除所有文章。
- **请求方式**: DELETE
- **接口路径**: `/api/v1/trash/posts/{id}`
- **请求头**:
  - Authorization: Bearer {token}（必填）
- **响应数据**:
```json
{
    "code": 204,
    "message": "success",
    "data": null,
    "timestamp": "string", // 时间戳（必返回）
    "requestId": "string"  // 请求ID（必返回）
}
```
- **错误码**:
  - 401: 未授权（未登录或token无效）
  - 404: 文章不存在或无权限操作

## 清空回收站
- **接口说明**: 清空回收站中的所有文章（物理删除）。此操作不可恢复。普通用户只能清空自己的文章，管理员可以清空所有文章。
- **请求方式**: DELETE
- **接口路径**: `/api/v1/trash/posts/empty`
- **请求头**:
  - Authorization: Bearer {token}（必填）
- **响应数据**:
```json
{
    "code": 204,
    "message": "success",
    "data": {
        "deleted_count": number  // 删除的文章数量
    },
    "timestamp": "string", // 时间戳（必返回）
    "requestId": "string"  // 请求ID（必返回）
}
```
- **错误码**:
  - 401: 未授权（未登录或token无效）
  - 400: 清空失败
