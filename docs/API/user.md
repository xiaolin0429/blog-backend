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
    "nickname": "string"    // 昵称（可选，2-20个字符）
}
```
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 0,
        "username": "string",
        "email": "string",
        "nickname": "string",
        "created_at": "string"
    }
}
```
- **错误码**:
  - 400: 请求参数错误
  - 409: 用户名或邮箱已存在

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
        "id": 0,
        "username": "string",
        "email": "string",
        "nickname": "string",
        "avatar": "string",
        "bio": "string",
        "created_at": "string",
        "last_login": "string"
    }
}
```
- **错误码**:
  - 401: 未授权或令牌已过期

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
    "avatar": "string",    // 头像URL（可选）
    "bio": "string"       // 个人简介（可选，最大500字符）
}
```
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 0,
        "username": "string",
        "email": "string",
        "nickname": "string",
        "avatar": "string",
        "bio": "string",
        "created_at": "string",
        "last_login": "string"
    }
}
```
- **错误码**:
  - 400: 请求参数错误
  - 401: 未授权或令牌已过期

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
    "data": null
}
```
- **错误码**:
  - 400: 请求参数错误
  - 401: 未授权或令牌已过期
  - 403: 旧密码错误 