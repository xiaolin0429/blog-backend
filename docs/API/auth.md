# 认证相关API

## 用户登录
- **接口说明**: 用户登录获取访问令牌
- **请求方式**: POST
- **接口路径**: `/api/v1/auth/login/`
- **请求头**:
  - Content-Type: application/json
- **请求参数**:
```json
{
    "username": "string",  // 用户名（必填，4-20个字符）
    "password": "string",  // 密码（必填，6-20个字符）
    "remember": false      // 是否记住登录（可选，默认false）
}
```
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "access": "string",   // 访问令牌（有效期24小时）
        "refresh": "string",  // 刷新令牌（remember为true时返回，有效期7天）
        "user": {
            "id": 1,
            "username": "string",
            "email": "string",
            "nickname": "string",
            "avatar": "string",
            "bio": "string",
            "created_at": "2024-01-19T10:30:00Z",
            "last_login": "2024-01-19T10:30:00Z"
        }
    },
    "timestamp": "2024-01-19T10:30:00Z",
    "requestId": "string"
}
```
- **错误码**:
  - 400: 请求参数错误（用户名或密码格式错误）
  - 401: 用户名或密码错误（1001）
  - 403: 账号已被锁定（1002）
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
    "refresh": "string"  // 刷新令牌（必填）
}
```
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "access": "string",  // 新的访问令牌（有效期24小时）
        "expires_in": 86400  // 过期时间（秒）
    },
    "timestamp": "2024-01-19T10:30:00Z",
    "requestId": "string"
}
```
- **错误码**:
  - 400: 请求参数错误（refresh token格式错误）
  - 401: Token已过期（1006）或无效（1007）

## 用户登出
- **接口说明**: 用户登出，使当前令牌失效
- **请求方式**: POST
- **接口路径**: `/api/v1/auth/logout/`
- **请求头**:
  - Authorization: Bearer {token}
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": null,
    "timestamp": "2024-01-19T10:30:00Z",
    "requestId": "string"
}
```
- **错误码**:
  - 401: 未授权或token已失效

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
        "active": true,           // token是否有效
        "expires_at": "2024-01-20T10:30:00Z",  // 过期时间
        "expires_in": 86400       // 剩余有效期（秒）
    },
    "timestamp": "2024-01-19T10:30:00Z",
    "requestId": "string"
}
```
- **错误码**:
  - 401: Token已过期或无效
