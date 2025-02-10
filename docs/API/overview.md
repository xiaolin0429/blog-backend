# 系统概览 API

## 1. 获取系统概览信息

获取系统的整体概览信息，包括系统信息、内容统计、存储统计和最近活动。

**请求**

```http
GET /api/v1/overview/
```

**响应**

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "system_info": {
            "version": "1.0.0",
            "status": "running",
            "uptime": 86400,
            "system_load": {
                "cpu": 45.6,
                "memory": 32.1,
                "disk": 68.9
            },
            "timestamp": 1644451200.0
        },
        "content_stats": {
            "total_users": 100,
            "active_users": 50,
            "total_posts": 200,
            "published_posts": 180,
            "total_comments": 500,
            "recent_comments": 50,
            "timestamp": 1644451200.0
        },
        "storage_stats": {
            "total_files": 1000,
            "total_size": 1073741824,
            "backup_count": 10,
            "last_backup": {
                "id": 1,
                "name": "自动备份 2024-02-10",
                "created_at": "2024-02-10T10:00:00Z",
                "status": "completed",
                "status_display": "已完成"
            },
            "timestamp": 1644451200.0
        },
        "recent_activities": {
            "recent_posts": [
                {
                    "id": 1,
                    "title": "示例文章",
                    "author": "admin",
                    "created_at": "2024-02-10T10:00:00Z",
                    "status": "published",
                    "status_display": "已发布"
                }
            ],
            "recent_backups": [
                {
                    "id": 1,
                    "name": "自动备份 2024-02-10",
                    "created_at": "2024-02-10T10:00:00Z",
                    "status": "completed",
                    "status_display": "已完成"
                }
            ],
            "timestamp": 1644451200.0
        }
    }
}
```

## 2. 获取系统信息

获取系统基本信息。

**请求**

```http
GET /api/v1/overview/system/
```

**响应**

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "version": "1.0.0",
        "start_time": 1644451200.0,
        "python_version": "3.12.0",
        "cpu_usage": {
            "percent": 45.6,
            "cores": 8,
            "physical_cores": 4
        },
        "memory_usage": {
            "percent": 32.1,
            "total": 17179869184,
            "available": 8589934592,
            "used": 8589934592
        },
        "disk_usage": {
            "percent": 68.9,
            "total": 1099511627776,
            "used": 757573918208,
            "free": 341937709568
        },
        "timestamp": 1644451200.0
    }
}
```

## 3. 获取内容统计

获取系统内容统计信息。

**请求**

```http
GET /api/v1/overview/content/
```

**响应**

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "total_users": 100,
        "active_users": 50,
        "total_posts": 200,
        "published_posts": 180,
        "total_comments": 500,
        "recent_comments": 50,
        "timestamp": 1644451200.0
    }
}
```

## 4. 获取存储统计

获取系统存储使用统计信息。

**请求**

```http
GET /api/v1/overview/storage/
```

**响应**

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "total_files": 1000,
        "total_size": 1073741824,
        "backup_count": 10,
        "last_backup": {
            "id": 1,
            "name": "自动备份 2024-02-10",
            "created_at": "2024-02-10T10:00:00Z",
            "status": "completed",
            "status_display": "已完成"
        },
        "timestamp": 1644451200.0
    }
}
```

## 字段说明

### 系统信息
- `version`: 系统版本号
- `status`: 系统状态（running: 运行中，unknown: 未知）
- `uptime`: 系统运行时间（秒）
- `system_load`: 系统负载情况
  - `cpu`: CPU使用率（0-100%）
  - `memory`: 内存使用率（0-100%）
  - `disk`: 磁盘使用率（0-100%）
- `timestamp`: 数据获取时间（Unix时间戳）

### 内容统计
- `total_users`: 总用户数
- `active_users`: 活跃用户数（最近7天有登录）
- `total_posts`: 总文章数
- `published_posts`: 已发布文章数
- `total_comments`: 总评论数
- `recent_comments`: 最近评论数（最近7天）
- `timestamp`: 数据获取时间（Unix时间戳）

### 存储统计
- `total_files`: 总文件数
- `total_size`: 总存储大小（字节）
- `backup_count`: 备份数量
- `last_backup`: 最近一次备份信息
  - `id`: 备份ID
  - `name`: 备份名称
  - `created_at`: 创建时间
  - `status`: 备份状态
  - `status_display`: 备份状态显示文本
- `timestamp`: 数据获取时间（Unix时间戳）

### 最近活动
- `recent_posts`: 最近文章列表（最多5条）
  - `id`: 文章ID
  - `title`: 文章标题
  - `author`: 作者用户名
  - `created_at`: 创建时间
  - `status`: 文章状态
  - `status_display`: 状态显示文本
- `recent_backups`: 最近备份列表（最多5条）
  - `id`: 备份ID
  - `name`: 备份名称
  - `created_at`: 创建时间
  - `status`: 备份状态
  - `status_display`: 状态显示文本
- `timestamp`: 数据获取时间（Unix时间戳）

## 注意事项

1. 所有接口都需要管理员权限
2. 所有数据都包含 `timestamp` 字段，表示数据的获取时间
3. 系统信息为实时数据，建议前端定期刷新（推荐间隔：5秒）
4. 存储大小单位为字节
5. 时间戳格式为Unix时间戳（秒）
6. 如果获取系统信息失败，会返回基本版本信息和状态信息
7. 所有百分比数据都已标准化到0-100范围内
