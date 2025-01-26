# 搜索相关API

## 高级搜索
### 基本信息
- **接口说明**: 支持多字段组合的模糊搜索，可按分类、标签、作者、日期范围过滤，支持结果高亮显示
- **请求方式**: GET
- **接口路径**: `/api/v1/search`

### 请求参数
| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
|--------|------|----------|------|------|
| keyword | string | 是 | 搜索关键词，支持模糊匹配，不区分大小写 | "Django" |
| fields | string | 否 | 搜索字段，多个字段用逗号分隔 | "title,content,excerpt" |
| category | number | 否 | 分类ID | 1 |
| tags | string | 否 | 标签ID列表，多个标签用逗号分隔 | "1,2,3" |
| author | number | 否 | 作者ID | 1 |
| date_start | string | 否 | 开始日期，YYYY-MM-DD格式 | "2024-01-01" |
| date_end | string | 否 | 结束日期，YYYY-MM-DD格式 | "2024-12-31" |
| highlight | boolean | 否 | 是否高亮显示搜索结果，默认true | true |
| page | number | 否 | 页码，默认1 | 1 |
| page_size | number | 否 | 每页数量，默认10 | 10 |

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
| next | string | 否 | 下一页URL |
| previous | string | 否 | 上一页URL |
| results | array | 是 | 搜索结果列表 |

#### results数组元素
| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| id | number | 是 | 文章ID |
| title | string | 是 | 文章标题，可能包含高亮标签 |
| excerpt | string | 是 | 文章摘要，可能包含高亮标签 |
| content | string | 是 | 文章内容，可能包含高亮标签 |
| created_at | string | 是 | 创建时间 |
| updated_at | string | 是 | 更新时间 |

##### author对象
| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| id | number | 是 | 作者ID |
| username | string | 是 | 用户名 |
| nickname | string | 否 | 昵称 |

##### category对象
| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| id | number | 是 | 分类ID |
| name | string | 是 | 分类名称 |
| level | number | 是 | 分类层级 |

##### tags数组元素
| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| id | number | 是 | 标签ID |
| name | string | 是 | 标签名称 |

### 响应示例
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "count": 0,
        "next": null,
        "previous": null,
        "results": [
            {
                "id": 1,
                "title": "Django教程",
                "excerpt": "Django是一个高级的Python Web框架",
                "content": "Django是一个由Python编写的开源Web框架",
                "author": {
                    "id": 1,
                    "username": "admin",
                    "nickname": "管理员"
                },
                "category": {
                    "id": 1,
                    "name": "Python",
                    "level": 0
                },
                "tags": [
                    {
                        "id": 1,
                        "name": "Django"
                    }
                ],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        ]
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "requestId": "xxxxx"
}
```

## 搜索建议
### 基本信息
- **接口说明**: 根据输入的关键词返回相关的文章、分类、标签建议
- **请求方式**: GET
- **接口路径**: `/api/v1/search/suggest`

### 请求参数
| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
|--------|------|----------|------|------|
| keyword | string | 是 | 搜索关键词，支持模糊匹配，不区分大小写 | "Django" |
| limit | number | 否 | 返回结果数量限制，默认10 | 10 |

### 响应参数
#### 基础字段
| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| code | number | 是 | 状态码 |
| message | string | 是 | 状态信息 |
| timestamp | string | 是 | 时间戳 |
| requestId | string | 是 | 请求ID |

#### data.suggestions数组元素（文章类型）
| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| type | string | 是 | 建议类型，固定值为"post" |
| id | number | 是 | 文章ID |
| title | string | 是 | 文章标题 |
| excerpt | string | 是 | 文章摘要 |

##### category对象
| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| id | number | 是 | 分类ID |
| name | string | 是 | 分类名称 |
| level | number | 是 | 分类层级 |

#### data.suggestions数组元素（分类类型）
| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| type | string | 是 | 建议类型，固定值为"category" |
| id | number | 是 | 分类ID |
| name | string | 是 | 分类名称 |
| level | number | 是 | 分类层级 |
| post_count | number | 是 | 文章数量 |

#### data.suggestions数组元素（标签类型）
| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| type | string | 是 | 建议类型，固定值为"tag" |
| id | number | 是 | 标签ID |
| name | string | 是 | 标签名称 |
| post_count | number | 是 | 文章数量 |

### 响应示例
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "suggestions": [
            {
                "type": "post",
                "id": 1,
                "title": "Django教程",
                "excerpt": "Django是一个高级的Python Web框架",
                "category": {
                    "id": 1,
                    "name": "Python",
                    "level": 0
                }
            },
            {
                "type": "category",
                "id": 1,
                "name": "Python",
                "level": 0,
                "post_count": 10
            },
            {
                "type": "tag",
                "id": 1,
                "name": "Django",
                "post_count": 5
            }
        ]
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "requestId": "xxxxx"
}
```

### 错误码
| 错误码 | 说明 |
|--------|------|
| 400 | 搜索关键词不能为空 |
