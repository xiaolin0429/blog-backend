# 统计API文档

## 基础信息
- 基础路径：`/api/v1/statistics`
- 认证方式：Bearer Token
- 权限要求：需要管理员权限（is_staff=True）
- 请求头：
  ```
  Authorization: Bearer {access_token}
  ```

## 1. 用户统计

### 1.1 获取用户统计数据

#### 基本信息
- 请求路径: `/api/v1/statistics/users`
- 请求方法: `GET`
- 权限要求: 需要管理员权限

#### 响应数据
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "total": {
            "total_users": 1,        // 总用户数
            "active_users": 1,       // 今日活跃用户数
            "new_users": 0           // 今日新增用户数
        },
        "trends": [
            {
                "date": "2025-02-09",
                "total_users": 1,
                "active_users": 1,
                "new_users": 0
            }
        ]
    },
    "timestamp": "2025-02-09T13:02:31.478599+00:00",
    "requestId": "d985c5a8-9109-4827-903b-7005848ae89d"
}
```

#### 字段说明
| 字段 | 类型 | 说明 |
| --- | --- | --- |
| total_users | integer | 系统中的总用户数（活跃用户） |
| active_users | integer | 今日活跃用户数（24小时内有登录记录） |
| new_users | integer | 今日新增用户数 |
| trends | array | 趋势数据数组 |
| trends[].date | string | 日期（YYYY-MM-DD格式） |
| trends[].total_users | integer | 该日期的总用户数 |
| trends[].active_users | integer | 该日期的活跃用户数 |
| trends[].new_users | integer | 该日期的新增用户数 |

## 2. 访问统计

### 2.1 获取访问统计数据

#### 基本信息
- 请求路径: `/api/v1/statistics/visits`
- 请求方法: `GET`
- 权限要求: 需要管理员权限

#### 请求参数
| 参数名 | 类型 | 位置 | 是否必须 | 说明 | 示例 |
| --- | --- | --- | --- | --- | --- |
| startDate | string | query | 否 | 开始日期（YYYY-MM-DD） | "2025-02-01" |
| endDate | string | query | 否 | 结束日期（YYYY-MM-DD） | "2025-02-09" |

#### 响应数据
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "total": {
            "pv": 1000,    // 总页面浏览量
            "uv": 500,     // 总独立访客数
            "ip": 300      // 总IP数
        },
        "trends": [
            {
                "date": "2025-02-09",
                "pv": 100,
                "uv": 50,
                "ip": 30
            }
        ]
    }
}
```

## 3. 内容统计

### 3.1 获取内容统计数据

#### 基本信息
- 请求路径: `/api/v1/statistics/content`
- 请求方法: `GET`
- 权限要求: 需要管理员权限

#### 请求参数
| 参数名 | 类型 | 位置 | 是否必须 | 说明 | 示例 |
| --- | --- | --- | --- | --- | --- |
| startDate | string | query | 否 | 开始日期（YYYY-MM-DD） | "2025-02-01" |
| endDate | string | query | 否 | 结束日期（YYYY-MM-DD） | "2025-02-09" |

#### 响应数据
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "posts": {
            "total": 100,
            "published": 80,
            "draft": 15,
            "private": 5,
            "topAuthors": [
                {
                    "id": 1,
                    "username": "admin",
                    "postCount": 50
                }
            ]
        },
        "comments": {
            "total": 500,
            "approved": 450,
            "pending": 30,
            "spam": 20
        },
        "categories": {
            "total": 10,
            "topCategories": [
                {
                    "id": 1,
                    "name": "技术",
                    "postCount": 30
                }
            ]
        },
        "tags": {
            "total": 50,
            "topTags": [
                {
                    "id": 1,
                    "name": "Python",
                    "postCount": 20
                }
            ]
        }
    }
}
```

## 统计数据更新机制

1. 用户统计数据：
   - 每天凌晨自动更新（通过Celery定时任务）
   - 每次请求时实时更新
   - 统计维度包括：总用户数、活跃用户数、新增用户数

2. 访问统计数据：
   - 实时记录
   - 支持按日期范围查询
   - 统计维度包括：PV、UV、IP数

3. 内容统计数据：
   - 实时统计
   - 支持按日期范围查询
   - 统计维度包括：文章、评论、分类、标签

## 错误码说明

| 错误码 | 说明 |
| --- | --- |
| 200 | 成功 |
| 401 | 未授权（未登录或Token无效） |
| 403 | 权限不足（非管理员用户） |
| 500 | 服务器内部错误 |

## 注意事项

1. 所有统计接口都需要管理员权限
2. 请求时必须在请求头中携带有效的管理员Token
3. 日期范围查询默认返回最近7天的数据
4. 统计数据可能存在一定的延迟（1-2分钟）
5. 活跃用户的统计基于最后登录时间
