# 认证相关API

## 用户登录
- **接口说明**: 用户登录获取访问令牌
- **请求方式**: POST
- **接口路径**: `/api/v1/auth/login/`
- **请求头**:
  - Content-Type: application/json
  - X-Timezone: string (可选，用户时区，默认为Asia/Shanghai)
- **请求参数**:
```json
{
    "username": "string",
    "password": "string",
    "remember": false
}
```
- **请求参数说明**:

| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| username | string | 是 | 用户名（4-20个字符） |
| password | string | 是 | 密码（6-20个字符） |
| remember | boolean | 否 | 是否记住登录（默认false） |

- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "access": "string",
        "refresh": "string",
        "user": {
            "id": 1,
            "username": "string",
            "email": "string",
            "nickname": "string",
            "avatar": "string",
            "bio": "string",
            "date_joined": "2024-01-19 10:30:00",
            "last_login": "2024-01-19 10:30:00"
        }
    },
    "timestamp": "2024-01-19T10:30:00.000Z",
    "requestId": "string"
}
```
- **响应数据说明**:

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| access | string | 访问令牌（有效期24小时） |
| refresh | string | 刷新令牌（remember为true时返回，有效期7天） |
| user.id | number | 用户ID |
| user.username | string | 用户名 |
| user.email | string | 邮箱 |
| user.nickname | string | 昵称 |
| user.avatar | string | 头像URL |
| user.bio | string | 个人简介 |
| user.date_joined | string | 注册时间（用户时区） |
| user.last_login | string | 最后登录时间（用户时区） |

- **错误码**:
  - 400: 请求参数错误（用户名或密码格式错误）
  - 401: 用户名或密码错误
  - 403: 账号已被锁定
  - 429: 登录尝试次数过多，请稍后再试

- **登录限制**:
  - 同一IP每分钟最多尝试10次登录
  - 同一用户名每分钟最多尝试5次登录
  - 连续5次登录失败后，账号将被锁定30分钟

## 刷新Token
- **接口说明**: 使用刷新令牌获取新的访问令牌
- **请求方式**: POST
- **接口路径**: `/api/v1/auth/refresh/`
- **请求头**:
  - Content-Type: application/json
- **请求参数**:
```json
{
    "refresh": "string"
}
```
- **请求参数说明**:

| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| refresh | string | 是 | 刷新令牌 |

- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "access": "string",
        "expires_in": 86400
    },
    "timestamp": "2024-01-19T10:30:00.000Z",
    "requestId": "string"
}
```
- **响应数据说明**:

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| access | string | 新的访问令牌（有效期24小时） |
| expires_in | number | 过期时间（秒） |

- **错误码**:
  - 400: 请求参数错误（refresh token格式错误）
  - 401: 刷新令牌无效或已过期

## 用户登出
- **接口说明**: 用户登出，使当前令牌失效
- **请求方式**: POST
- **接口路径**: `/api/v1/auth/logout/`
- **请求头**:
  - Authorization: Bearer {token}
  - Content-Type: application/json
- **请求参数**:
```json
{
    "refresh": "string"
}
```
- **请求参数说明**:

| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| refresh | string | 是 | 刷新令牌 |

- **响应数据**:
```json
{
    "code": 200,
    "message": "登出成功",
    "data": null,
    "timestamp": "2024-01-19T10:30:00.000Z",
    "requestId": "string"
}
```
- **错误码**:
  - 400: 令牌无效或已过期
  - 401: 未授权

## 检查Token状态
- **接口说明**: 检查当前token的有效性和过期时间
- **请求方式**: GET
- **接口路径**: `/api/v1/auth/check/`
- **请求头**:
  - Authorization: Bearer {token}
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "active": true,
        "expires_at": "2024-01-20T10:30:00Z",
        "expires_in": 86400
    },
    "timestamp": "2024-01-19T10:30:00.000Z",
    "requestId": "string"
}
```
- **响应数据说明**:

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| active | boolean | token是否有效 |
| expires_at | string | 过期时间 |
| expires_in | number | 剩余有效期（秒） |

- **错误码**:
  - 401: Token已过期或无效
