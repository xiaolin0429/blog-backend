# 回收站API

## 获取回收站文章列表
- **接口说明**: 获取已删除的文章列表（软删除的文章）。普通用户只能看到自己的文章，管理员可以看到所有文章。
- **请求方式**: GET
- **接口路径**: `/api/v1/trash/posts`
- **请求头**:
  - Authorization: Bearer {token}（必填）

- **请求参数**:

| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
|--------|------|----------|------|------|
| page | number | 否 | 页码,默认1 | 1 |
| size | number | 否 | 每页数量,默认10,最大50 | 10 |
| ordering | string | 否 | 排序字段,支持deleted_at, -deleted_at | -deleted_at |
| search | string | 否 | 搜索关键词,搜索title, content, excerpt | 测试 |

- **响应参数**:

| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| code | number | 是 | 状态码 |
| message | string | 是 | 状态信息 |
| data.total | number | 是 | 总数 |
| data.page | number | 是 | 当前页码 |
| data.size | number | 是 | 每页数量 |
| data.pages | number | 是 | 总页数 |
| data.items[].id | number | 是 | 文章ID |
| data.items[].title | string | 是 | 文章标题 |
| data.items[].excerpt | string | 否 | 文章摘要 |
| data.items[].author.id | number | 是 | 作者ID |
| data.items[].author.username | string | 是 | 用户名 |
| data.items[].author.nickname | string | 否 | 昵称 |
| data.items[].category.id | number | 是 | 分类ID |
| data.items[].category.name | string | 是 | 分类名称 |
| data.items[].tags[].id | number | 是 | 标签ID |
| data.items[].tags[].name | string | 是 | 标签名称 |
| data.items[].deleted_at | string | 是 | 删除时间 |
| timestamp | string | 是 | 时间戳 |
| requestId | string | 是 | 请求ID |

- **响应示例**:
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
                "title": "测试文章",
                "excerpt": "这是一篇测试文章",
                "author": {
                    "id": 1,
                    "username": "test",
                    "nickname": "测试用户"
                },
                "category": {
                    "id": 1,
                    "name": "测试分类"
                },
                "tags": [
                    {
                        "id": 1,
                        "name": "测试标签"
                    }
                ],
                "deleted_at": "2024-03-20T12:00:00Z"
            }
        ]
    },
    "timestamp": "2024-03-20T12:00:00Z",
    "requestId": "7cb116acbcd23"
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

- **响应参数**:

| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| code | number | 是 | 状态码 |
| message | string | 是 | 状态信息 |
| data.id | number | 是 | 文章ID |
| data.title | string | 是 | 文章标题 |
| data.status | string | 是 | 文章状态 |
| timestamp | string | 是 | 时间戳 |
| requestId | string | 是 | 请求ID |

- **响应示例**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "title": "测试文章",
        "status": "draft"
    },
    "timestamp": "2024-03-20T12:00:00Z",
    "requestId": "7cb116acbcd23"
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

- **响应参数**:

| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| code | number | 是 | 状态码 |
| message | string | 是 | 状态信息 |
| data | null | 是 | 响应数据 |
| timestamp | string | 是 | 时间戳 |
| requestId | string | 是 | 请求ID |

- **响应示例**:
```json
{
    "code": 204,
    "message": "success",
    "data": null,
    "timestamp": "2024-03-20T12:00:00Z",
    "requestId": "7cb116acbcd23"
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

- **响应参数**:

| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| code | number | 是 | 状态码 |
| message | string | 是 | 状态信息 |
| data.deleted_count | number | 是 | 删除的文章数量 |
| timestamp | string | 是 | 时间戳 |
| requestId | string | 是 | 请求ID |

- **响应示例**:
```json
{
    "code": 204,
    "message": "success",
    "data": {
        "deleted_count": 10
    },
    "timestamp": "2024-03-20T12:00:00Z",
    "requestId": "7cb116acbcd23"
}
```
- **错误码**:
  - 401: 未授权（未登录或token无效）
  - 400: 清空失败
