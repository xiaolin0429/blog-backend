# 用户相关API

## 用户注册
- **接口说明**: 注册新用户
- **请求方式**: POST
- **接口路径**: `/api/v1/users/`
- **请求头**:
  - Content-Type: application/json
- **请求参数**:
```json
{
    "username": "string",   // 用户名（必填，4-20个字符，只能包含字母、数字、下划线）
    "email": "string",      // 邮箱（必填，有效的邮箱格式）
    "password": "string",   // 密码（必填，6-20个字符，必须包含字母和数字）
    "password2": "string",  // 确认密码（必填，与密码相同）
    "nickname": "string",   // 昵称（可选，2-20个字符）
    "avatar": "string",     // 头像URL（可选）
    "bio": "string"        // 个人简介（可选，最大500字符）
}
```
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "username": "string",
        "email": "string",
        "nickname": "string",
        "avatar": "string",
        "bio": "string",
        "created_at": "2024-01-19T10:30:00Z"
    },
    "timestamp": "2024-01-19T10:30:00Z",
    "requestId": "string"
}
```
- **错误码**:
  - 400: 请求参数错误（参数格式错误）
  - 409: 用户名已存在（1003）或邮箱已被使用（1004）
  - 429: 注册请求过于频繁

- **注册限制**:
  - 同一IP每小时最多注册5个账号
  - 同一邮箱每天最多注册1个账号
  - 用户名不能包含敏感词

## 获取当前用户信息
- **接口说明**: 获取当前登录用户的详细信息
- **请求方式**: GET
- **接口路径**: `/api/v1/users/me/`
- **请求头**:
  - Authorization: Bearer {token}
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "username": "string",
        "email": "string",
        "nickname": "string",
        "avatar": "string",
        "bio": "string",
        "role": "string",         // 用户角色：admin/editor/user
        "status": "string",       // 账号状态：active/locked/disabled
        "email_verified": true,   // 邮箱是否已验证
        "last_login_ip": "string", // 最后登录IP
        "created_at": "2024-01-19T10:30:00Z",
        "last_login": "2024-01-19T10:30:00Z",
        "stats": {               // 用户统计信息
            "post_count": 0,     // 文章数
            "comment_count": 0,  // 评论数
            "like_count": 0      // 获赞数
        }
    },
    "timestamp": "2024-01-19T10:30:00Z",
    "requestId": "string"
}
```
- **错误码**:
  - 401: 未授权或token已失效

## 更新当前用户信息
- **接口说明**: 更新当前登录用户的信息
- **请求方式**: PUT
- **接口路径**: `/api/v1/users/me/`
- **请求头**:
  - Authorization: Bearer {token}
  - Content-Type: application/json
- **请求参数**:
```json
{
    "nickname": "string",  // 昵称（可选，2-20个字符）
    "avatar": "string",    // 头像URL（可选，必须是有效的图片URL）
    "bio": "string",      // 个人简介（可选，最大500字符）
    "email": "string"     // 新邮箱（可选，修改邮箱需要验证）
}
```
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "username": "string",
        "email": "string",
        "nickname": "string",
        "avatar": "string",
        "bio": "string",
        "email_verified": true,
        "created_at": "2024-01-19T10:30:00Z",
        "updated_at": "2024-01-19T10:30:00Z"
    },
    "timestamp": "2024-01-19T10:30:00Z",
    "requestId": "string"
}
```
- **错误码**:
  - 400: 请求参数错误
  - 401: 未授权或token已失效
  - 409: 邮箱已被使用（1004）

## 修改密码
- **接口说明**: 修改当前登录用户的密码
- **请求方式**: PUT
- **接口路径**: `/api/v1/users/me/password/`
- **请求头**:
  - Authorization: Bearer {token}
  - Content-Type: application/json
- **请求参数**:
```json
{
    "old_password": "string",  // 旧密码（必填）
    "new_password": "string",  // 新密码（必填，6-20个字符，必须包含字母和数字）
    "new_password2": "string"  // 确认新密码（必填，与新密码相同）
}
```
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
  - 400: 请求参数错误（密码格式错误）
  - 401: 未授权或token已失效
  - 403: 原密码错误（1005）

## 验证邮箱
- **接口说明**: 发送或验证邮箱验证码
- **请求方式**: POST
- **接口路径**: `/api/v1/users/me/verify-email/`
- **请求头**:
  - Authorization: Bearer {token}
  - Content-Type: application/json
- **请求参数**:
```json
{
    "email": "string",  // 邮箱地址（必填）
    "code": "string"    // 验证码（可选，不传则发送验证码）
}
```
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "email": "string",
        "verified": true,
        "expires_in": 300  // 验证码有效期（秒）
    },
    "timestamp": "2024-01-19T10:30:00Z",
    "requestId": "string"
}
```
- **错误码**:
  - 400: 请求参数错误
  - 401: 未授权或token已失效
  - 409: 邮箱已被使用
  - 429: 发送验证码过于频繁

- **验证码限制**:
  - 同一邮箱每分钟最多发送1次验证码
  - 同一邮箱每天最多发送10次验证码
  - 验证码有效期5分钟
