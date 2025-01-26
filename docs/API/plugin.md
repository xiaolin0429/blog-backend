# 插件管理API

## 获取插件列表

### 基本信息

- 请求路径: `/api/v1/plugins`
- 请求方法: `GET`
- 权限要求: 管理员

### 请求头

| 参数名 | 参数值 | 是否必须 | 示例 | 备注 |
| --- | --- | --- | --- | --- |
| Authorization | Bearer {access_token} | 是 | Bearer abc.def.xyz | 管理员访问令牌 |

### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "name": "plugin-name",
      "description": "Plugin description",
      "version": "1.0.0",
      "enabled": false,
      "config": {},
      "created_at": "2024-01-19T10:30:00Z",
      "updated_at": "2024-01-19T10:30:00Z"
    }
  ],
  "timestamp": "2024-01-19T10:30:00Z",
  "requestId": "string"
}
```

### 错误码

| 错误码 | 说明 |
| --- | --- |
| 401 | 未登录或Token无效 |
| 403 | 权限不足 |

## 安装插件

### 基本信息

- 请求路径: `/api/v1/plugins/install`
- 请求方法: `POST`
- 权限要求: 管理员

### 请求头

| 参数名 | 参数值 | 是否必须 | 示例 | 备注 |
| --- | --- | --- | --- | --- |
| Authorization | Bearer {access_token} | 是 | Bearer abc.def.xyz | 管理员访问令牌 |
| Content-Type | application/json | 是 | application/json | 请求体格式 |

### 请求参数

```json
{
  "name": "plugin-name",
  "description": "Plugin description",
  "version": "1.0.0"
}
```

| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| name | string | 是 | 插件名称,唯一标识 |
| description | string | 否 | 插件描述 |
| version | string | 是 | 插件版本号 |

### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "name": "plugin-name",
    "description": "Plugin description",
    "version": "1.0.0",
    "enabled": false,
    "config": {},
    "created_at": "2024-01-19T10:30:00Z",
    "updated_at": "2024-01-19T10:30:00Z"
  },
  "timestamp": "2024-01-19T10:30:00Z",
  "requestId": "string"
}
```

### 错误码

| 错误码 | 说明 |
| --- | --- |
| 400 | 安装插件失败 |
| 401 | 未登录或Token无效 |
| 403 | 权限不足 |
| 409 | 插件已存在 |

## 卸载插件

### 基本信息

- 请求路径: `/api/v1/plugins/{plugin_id}/uninstall`
- 请求方法: `DELETE`
- 权限要求: 管理员

### 请求头

| 参数名 | 参数值 | 是否必须 | 示例 | 备注 |
| --- | --- | --- | --- | --- |
| Authorization | Bearer {access_token} | 是 | Bearer abc.def.xyz | 管理员访问令牌 |

### 路径参数

| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| plugin_id | string | 是 | 插件名称 |

### 响应数据

```json
{
  "code": 200,
  "message": "插件已卸载",
  "data": null,
  "timestamp": "2024-01-19T10:30:00Z",
  "requestId": "string"
}
```

### 错误码

| 错误码 | 说明 |
| --- | --- |
| 401 | 未登录或Token无效 |
| 403 | 权限不足 |
| 404 | 插件不存在 |

## 启用插件

### 基本信息

- 请求路径: `/api/v1/plugins/{plugin_id}/enable`
- 请求方法: `POST`
- 权限要求: 管理员

### 请求头

| 参数名 | 参数值 | 是否必须 | 示例 | 备注 |
| --- | --- | --- | --- | --- |
| Authorization | Bearer {access_token} | 是 | Bearer abc.def.xyz | 管理员访问令牌 |

### 路径参数

| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| plugin_id | string | 是 | 插件名称 |

### 响应数据

```json
{
  "code": 200,
  "message": "插件已启用",
  "data": null,
  "timestamp": "2024-01-19T10:30:00Z",
  "requestId": "string"
}
```

### 错误码

| 错误码 | 说明 |
| --- | --- |
| 401 | 未登录或Token无效 |
| 403 | 权限不足 |
| 404 | 插件不存在 |

## 禁用插件

### 基本信息

- 请求路径: `/api/v1/plugins/{plugin_id}/disable`
- 请求方法: `POST`
- 权限要求: 管理员

### 请求头

| 参数名 | 参数值 | 是否必须 | 示例 | 备注 |
| --- | --- | --- | --- | --- |
| Authorization | Bearer {access_token} | 是 | Bearer abc.def.xyz | 管理员访问令牌 |

### 路径参数

| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| plugin_id | string | 是 | 插件名称 |

### 响应数据

```json
{
  "code": 200,
  "message": "插件已禁用",
  "data": null,
  "timestamp": "2024-01-19T10:30:00Z",
  "requestId": "string"
}
```

### 错误码

| 错误码 | 说明 |
| --- | --- |
| 401 | 未登录或Token无效 |
| 403 | 权限不足 |
| 404 | 插件不存在 |

## 获取插件配置

### 基本信息

- 请求路径: `/api/v1/plugins/{plugin_id}/settings`
- 请求方法: `GET`
- 权限要求: 管理员

### 请求头

| 参数名 | 参数值 | 是否必须 | 示例 | 备注 |
| --- | --- | --- | --- | --- |
| Authorization | Bearer {access_token} | 是 | Bearer abc.def.xyz | 管理员访问令牌 |

### 路径参数

| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| plugin_id | string | 是 | 插件名称 |

### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "config": {
      "key": "value"
    }
  },
  "timestamp": "2024-01-19T10:30:00Z",
  "requestId": "string"
}
```

### 错误码

| 错误码 | 说明 |
| --- | --- |
| 401 | 未登录或Token无效 |
| 403 | 权限不足 |
| 404 | 插件不存在 |

## 更新插件配置

### 基本信息

- 请求路径: `/api/v1/plugins/{plugin_id}/settings`
- 请求方法: `PUT`
- 权限要求: 管理员

### 请求头

| 参数名 | 参数值 | 是否必须 | 示例 | 备注 |
| --- | --- | --- | --- | --- |
| Authorization | Bearer {access_token} | 是 | Bearer abc.def.xyz | 管理员访问令牌 |
| Content-Type | application/json | 是 | application/json | 请求体格式 |

### 路径参数

| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| plugin_id | string | 是 | 插件名称 |

### 请求参数

```json
{
  "config": {
    "key": "value"
  }
}
```

| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| config | object | 是 | 插件配置对象 |

### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "config": {
      "key": "value"
    }
  },
  "timestamp": "2024-01-19T10:30:00Z",
  "requestId": "string"
}
```

### 错误码

| 错误码 | 说明 |
| --- | --- |
| 400 | 更新配置失败 |
| 401 | 未登录或Token无效 |
| 403 | 权限不足 |
| 404 | 插件不存在 | 