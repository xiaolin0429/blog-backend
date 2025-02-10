# 备份管理 API

## 1. 备份记录管理

### 1.1 获取备份列表

**请求**

```http
GET /api/v1/backup/backups/
```

**参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认10 |
| backup_type | string | 否 | 备份类型(full/db/files/settings) |
| status | string | 否 | 备份状态(pending/running/completed/failed) |
| is_auto | boolean | 否 | 是否自动备份 |
| start_date | date | 否 | 开始日期 |
| end_date | date | 否 | 结束日期 |

**响应**

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "count": 100,
        "next": "http://example.com/api/v1/backup/backups/?page=2",
        "previous": null,
        "results": [
            {
                "id": 1,
                "name": "完整备份_20250210_235959",
                "backup_type": "full",
                "backup_type_display": "完整备份",
                "description": "每日自动备份",
                "file_path": "/path/to/backup/file.tar.gz",
                "file_size": 1024000,
                "status": "completed",
                "status_display": "已完成",
                "error_message": "",
                "is_auto": true,
                "created_at": "2025-02-10T23:59:59+08:00",
                "started_at": "2025-02-10T23:59:59+08:00",
                "completed_at": "2025-02-11T00:00:30+08:00",
                "created_by": 1,
                "created_by_name": "admin"
            }
        ]
    }
}
```

### 1.2 创建备份

**请求**

```http
POST /api/v1/backup/backups/
```

**参数**

```json
{
    "name": "手动备份_20250210_235959",
    "backup_type": "full",
    "description": "手动创建的完整备份"
}
```

**响应**

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "id": 2,
        "name": "手动备份_20250210_235959",
        "backup_type": "full",
        "backup_type_display": "完整备份",
        "description": "手动创建的完整备份",
        "file_path": "",
        "file_size": 0,
        "status": "pending",
        "status_display": "等待中",
        "error_message": "",
        "is_auto": false,
        "created_at": "2025-02-10T23:59:59+08:00",
        "started_at": null,
        "completed_at": null,
        "created_by": 1,
        "created_by_name": "admin"
    }
}
```

### 1.3 获取备份详情

**请求**

```http
GET /api/v1/backup/backups/{id}/
```

**响应**

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "id": 1,
        "name": "完整备份_20250210_235959",
        "backup_type": "full",
        "backup_type_display": "完整备份",
        "description": "每日自动备份",
        "file_path": "/path/to/backup/file.tar.gz",
        "file_size": 1024000,
        "status": "completed",
        "status_display": "已完成",
        "error_message": "",
        "is_auto": true,
        "created_at": "2025-02-10T23:59:59+08:00",
        "started_at": "2025-02-10T23:59:59+08:00",
        "completed_at": "2025-02-11T00:00:30+08:00",
        "created_by": 1,
        "created_by_name": "admin"
    }
}
```

### 1.4 删除备份

**请求**

```http
DELETE /api/v1/backup/backups/{id}/
```

**响应**

```json
{
    "code": 0,
    "message": "备份已删除"
}
```

### 1.5 恢复备份

**请求**

```http
POST /api/v1/backup/backups/{id}/restore/
```

**响应**

```json
{
    "code": 0,
    "message": "备份恢复成功"
}
```

### 1.6 下载备份文件

**请求**

```http
GET /api/v1/backup/backups/{id}/download/
```

**响应**

文件流，自动下载备份文件。

## 2. 备份配置管理

### 2.1 获取备份配置列表

**请求**

```http
GET /api/v1/backup/configs/
```

**响应**

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "count": 1,
        "next": null,
        "previous": null,
        "results": [
            {
                "id": 1,
                "enabled": true,
                "backup_type": "full",
                "backup_type_display": "完整备份",
                "frequency": "daily",
                "frequency_display": "每天",
                "retention_days": 30,
                "backup_time": "02:00:00",
                "last_backup": "2025-02-10T02:00:00+08:00",
                "next_backup": "2025-02-11T02:00:00+08:00",
                "created_at": "2025-02-10T00:00:00+08:00",
                "updated_at": "2025-02-10T02:00:00+08:00"
            }
        ]
    }
}
```

### 2.2 创建备份配置

**请求**

```http
POST /api/v1/backup/configs/
```

**参数**

```json
{
    "enabled": true,
    "backup_type": "full",
    "frequency": "daily",
    "retention_days": 30,
    "backup_time": "02:00:00"
}
```

**响应**

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "id": 2,
        "enabled": true,
        "backup_type": "full",
        "backup_type_display": "完整备份",
        "frequency": "daily",
        "frequency_display": "每天",
        "retention_days": 30,
        "backup_time": "02:00:00",
        "last_backup": null,
        "next_backup": "2025-02-11T02:00:00+08:00",
        "created_at": "2025-02-10T00:00:00+08:00",
        "updated_at": "2025-02-10T00:00:00+08:00"
    }
}
```

### 2.3 获取备份配置详情

**请求**

```http
GET /api/v1/backup/configs/{id}/
```

**响应**

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "id": 1,
        "enabled": true,
        "backup_type": "full",
        "backup_type_display": "完整备份",
        "frequency": "daily",
        "frequency_display": "每天",
        "retention_days": 30,
        "backup_time": "02:00:00",
        "last_backup": "2025-02-10T02:00:00+08:00",
        "next_backup": "2025-02-11T02:00:00+08:00",
        "created_at": "2025-02-10T00:00:00+08:00",
        "updated_at": "2025-02-10T02:00:00+08:00"
    }
}
```

### 2.4 更新备份配置

**请求**

```http
PUT /api/v1/backup/configs/{id}/
```

**参数**

```json
{
    "enabled": true,
    "backup_type": "full",
    "frequency": "daily",
    "retention_days": 30,
    "backup_time": "02:00:00"
}
```

**响应**

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "id": 1,
        "enabled": true,
        "backup_type": "full",
        "backup_type_display": "完整备份",
        "frequency": "daily",
        "frequency_display": "每天",
        "retention_days": 30,
        "backup_time": "02:00:00",
        "last_backup": "2025-02-10T02:00:00+08:00",
        "next_backup": "2025-02-11T02:00:00+08:00",
        "created_at": "2025-02-10T00:00:00+08:00",
        "updated_at": "2025-02-10T02:00:00+08:00"
    }
}
```

### 2.5 删除备份配置

**请求**

```http
DELETE /api/v1/backup/configs/{id}/
```

**响应**

```json
{
    "code": 0,
    "message": "备份配置已删除"
}
```

### 2.6 测试备份配置

**请求**

```http
POST /api/v1/backup/configs/{id}/test/
```

**响应**

```json
{
    "code": 0,
    "message": "测试备份已启动"
}
```
