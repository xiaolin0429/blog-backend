# 文件管理API

## 基础信息
- 基础路径：`/api/v1/storage`
- 认证方式：Bearer Token
- 权限要求：需要登录

## 1. 上传文件

### 基本信息
- 请求路径: `/api/v1/storage/upload`
- 请求方法: `POST`
- 权限要求: 需要登录
- Content-Type: multipart/form-data

### 请求头
| 参数名 | 参数值 | 是否必须 | 示例 | 备注 |
| --- | --- | --- | --- | --- |
| Authorization | Bearer {access_token} | 是 | Bearer abc.def.xyz | 访问令牌 |
| Content-Type | multipart/form-data | 是 | multipart/form-data | 请求体格式 |

### 请求参数
| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| file | file | 是 | 要上传的文件 | - |
| type | string | 否 | 文件类型，默认自动识别 | "image" |
| path | string | 否 | 保存路径，默认按日期生成 | "posts/2024/01" |

### 支持的文件类型
- 图片文件：
  - 格式：jpg、jpeg、png、gif、webp、svg、tiff、bmp、ico、heic、heif
  - 大小限制：20MB
- 文档文件：
  - 格式：pdf、doc、docx、xls、xlsx、ppt、pptx、txt、md、csv、json、xml、zip、rar、7z
  - 大小限制：50MB
- 媒体文件：
  - 格式：
    - 视频：mp4、webm、avi、mov、mkv
    - 音频：mp3、wav、midi、ogg、aac、flac、wma
  - 大小限制：200MB

### 响应数据
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": "string",         // 文件唯一标识符
        "url": "string",         // 文件访问URL
        "path": "string",        // 文件存储路径（已废弃，使用id代替）
        "name": "string",        // 文件名
        "original_name": "string", // 原始文件名
        "type": "string",        // 文件类型
        "size": number,          // 文件大小(字节)
        "mime_type": "string",   // MIME类型
        "upload_time": "string"  // 上传时间
    },
    "timestamp": "string",
    "requestId": "string"
}
```

### 错误码
| 错误码 | 说明 |
| --- | --- |
| 400 | 请求参数错误 |
| 401 | 未登录或Token无效 |
| 403 | 无权限上传文件 |
| 413 | 文件大小超出限制 |
| 415 | 不支持的文件类型 |

## 2. 删除文件

### 基本信息
- 请求路径: `/api/v1/storage/files/{file_id}`
- 请求方法: `DELETE`
- 权限要求: 需要登录

### 请求头
| 参数名 | 参数值 | 是否必须 | 示例 | 备注 |
| --- | --- | --- | --- | --- |
| Authorization | Bearer {access_token} | 是 | Bearer abc.def.xyz | 访问令牌 |

### 路径参数
| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| file_id | string | 是 | 文件ID | "a1b2c3d4e5f6" |

### 响应数据
```json
{
    "code": 200,
    "message": "success",
    "data": null,
    "timestamp": "string",
    "requestId": "string"
}
```

### 错误码
| 错误码 | 说明 |
| --- | --- |
| 401 | 未登录或Token无效 |
| 403 | 无权限删除文件 |
| 404 | 文件不存在 |

## 3. 获取文件列表

### 基本信息
- 请求路径: `/api/v1/storage/files`
- 请求方法: `GET`
- 权限要求: 需要登录

### 请求头
| 参数名 | 参数值 | 是否必须 | 示例 | 备注 |
| --- | --- | --- | --- | --- |
| Authorization | Bearer {access_token} | 是 | Bearer abc.def.xyz | 访问令牌 |

### 查询参数
| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| path | string | 否 | 目录路径 | "posts/2024/01" |
| type | string | 否 | 文件类型(all/image/document/media) | "image" |
| page | integer | 否 | 页码，默认1 | 1 |
| size | integer | 否 | 每页数量，默认20，最大100 | 20 |
| order_by | string | 否 | 排序字段，前缀-表示降序 | "-upload_time" |

### 排序说明
支持的排序字段：
- `name`: 按文件名排序
- `size`: 按文件大小排序
- `upload_time`: 按上传时间排序（默认）
- `type`: 按文件类型排序
- 前缀 `-` 表示降序，如 `-upload_time`

### 响应数据
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "total": number,        // 文件总数
        "page": number,         // 当前页码
        "size": number,         // 每页数量
        "pages": number,        // 总页数
        "items": [             // 文件列表
            {
                "id": "string",         // 文件唯一标识符
                "url": "string",         // 文件访问URL
                "path": "string",        // 文件存储路径（已废弃，使用id代替）
                "name": "string",        // 文件名
                "original_name": "string", // 原始文件名
                "type": "string",        // 文件类型
                "size": number,          // 文件大小(字节)
                "mime_type": "string",   // MIME类型
                "upload_time": "string"  // 上传时间
            }
        ]
    },
    "timestamp": "string",
    "requestId": "string"
}
```

### 错误码
| 错误码 | 说明 |
| --- | --- |
| 400 | 请求参数错误 |
| 401 | 未登录或Token无效 |
| 403 | 无权限查看文件列表 |

## 4. 重命名文件

### 基本信息
- 请求路径: `/api/v1/storage/files/{file_id}/rename`
- 请求方法: `PUT`
- 权限要求: 需要登录
- Content-Type: application/json

### 请求头
| 参数名 | 参数值 | 是否必须 | 示例 | 备注 |
| --- | --- | --- | --- | --- |
| Authorization | Bearer {access_token} | 是 | Bearer abc.def.xyz | 访问令牌 |
| Content-Type | application/json | 是 | application/json | 请求体格式 |

### 路径参数
| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| file_id | string | 是 | 文件ID | "a1b2c3d4e5f6" |

### 请求体
```json
{
    "new_name": "string"  // 新文件名（不包含路径和扩展名）
}
```

### 请求参数说明
- new_name:
  - 不能为空
  - 不能包含路径分隔符（/ 或 \）
  - 仅包含文件名，不包含路径和扩展名
  - 文件扩展名将保持原文件的扩展名不变

### 响应数据
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": "string",         // 文件唯一标识符
        "url": "string",         // 文件访问URL
        "path": "string",        // 文件存储路径（已废弃，使用id代替）
        "name": "string",        // 文件名
        "original_name": "string", // 原始文件名
        "type": "string",        // 文件类型
        "size": number,          // 文件大小(字节)
        "mime_type": "string",   // MIME类型
        "upload_time": "string"  // 上传时间
    },
    "timestamp": "string",
    "requestId": "string"
}
```

### 错误码
| 错误码 | 说明 |
| --- | --- |
| 400 | 请求参数错误 |
| 401 | 未登录或Token无效 |
| 403 | 无权限修改文件 |
| 404 | 文件不存在 |
| 409 | 新文件名已存在 |
| 500 | 服务器错误 |

### 错误响应示例
```json
{
    "code": 400,
    "message": "新文件名不能包含路径分隔符"
}
```
```json
{
    "code": 409,
    "message": "新文件名已存在"
}
```
```json
{
    "code": 404,
    "message": "文件不存在"
}
```

### 注意事项
1. 重命名操作会保持原有的目录结构不变，只修改文件名部分
2. 文件扩展名会保持不变，不需要在新文件名中指定扩展名
3. 操作是原子的，如果重命名过程中出现错误会自动回滚
4. 重命名后的文件会保持原有的文件类型、大小等属性不变
5. URL 中的文件路径需要进行 URL 编码

### 字段说明
| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| id | string | 文件唯一标识符，用于文件的删除、重命名等操作 |
| url | string | 文件访问URL，用于下载或预览文件 |
| path | string | 文件存储路径（已废弃，请使用id字段） |
| name | string | 文件名 |
| original_name | string | 原始文件名 |
| type | string | 文件类型(image/document/media) |
| size | number | 文件大小(字节) |
| mime_type | string | MIME类型 |
| upload_time | string | 上传时间(ISO 8601格式) |

### 注意事项
1. `id` 字段是文件的唯一标识符，用于文件的删除、重命名等操作
2. `path` 字段已废弃，为了向后兼容暂时保留，新代码请使用 `id` 字段
3. 所有时间字段均使用 ISO 8601 格式，包含时区信息
