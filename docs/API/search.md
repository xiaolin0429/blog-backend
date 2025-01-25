# 搜索 API

## 高级搜索

### 基本信息

**Path:** `/api/v1/search/`

**Method:** `GET`

**Description:** 支持多字段组合的模糊搜索，可按分类、标签、作者、日期范围过滤，支持结果高亮显示。搜索是不区分大小写的模糊匹配，例如搜索"python"可以匹配到"Python教程"、"深入Python编程"等内容。

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| keyword | string | 是 | 搜索关键词（支持模糊匹配，不区分大小写） |
| fields | string | 否 | 搜索字段，多个字段用逗号分隔（可选值：title,content,excerpt），默认全部 |
| category | integer | 否 | 分类ID |
| tags | string | 否 | 标签ID列表，多个标签用逗号分隔 |
| author | integer | 否 | 作者ID |
| date_start | string | 否 | 开始日期（YYYY-MM-DD） |
| date_end | string | 否 | 结束日期（YYYY-MM-DD） |
| highlight | boolean | 否 | 是否高亮显示搜索结果，默认true |
| page | integer | 否 | 页码，默认1 |
| page_size | integer | 否 | 每页数量，默认10 |

### 响应结果

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "count": 1,
        "next": "http://example.com/api/v1/search/?page=2",
        "previous": null,
        "results": [
            {
                "id": 1,
                "title": "Python<span class=\"search-highlight\">教程</span>",
                "excerpt": "这是一篇Python教程...",
                "content": "这是一篇详细的Python教程...",
                "author": {
                    "id": 1,
                    "username": "admin"
                },
                "category": {
                    "id": 1,
                    "name": "编程"
                },
                "tags": [
                    {
                        "id": 1,
                        "name": "Python"
                    }
                ],
                "created_at": "2024-01-24T10:00:00Z",
                "updated_at": "2024-01-24T10:00:00Z"
            }
        ]
    }
}
```

### 错误码

| 错误码 | 说明 |
|--------|------|
| 400 | 搜索关键词不能为空 |
| 400 | 无效的日期格式 |

## 搜索建议

### 基本信息

**Path:** `/api/v1/search/suggest/`

**Method:** `GET`

**Description:** 根据输入的关键词返回相关的文章、分类、标签建议。使用模糊匹配算法，可以匹配标题、分类名、标签名中包含关键词的内容，并按相关度排序。

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| keyword | string | 是 | 搜索关键词（支持模糊匹配，不区分大小写） |
| limit | integer | 否 | 返回结果数量限制，默认10 |

### 响应结果

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "suggestions": [
            {
                "type": "post",
                "id": 1,
                "title": "Python教程",
                "excerpt": "这是一篇Python教程..."
            },
            {
                "type": "category",
                "id": 1,
                "title": "Python编程",
                "excerpt": "Python相关的教程和文章"
            },
            {
                "type": "tag",
                "id": 1,
                "title": "Python",
                "excerpt": "Python编程语言相关"
            }
        ]
    }
}
```

### 错误码

| 错误码 | 说明 |
|--------|------|
| 400 | 搜索关键词不能为空 |
