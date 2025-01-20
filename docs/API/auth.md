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
        "access": "string",   // 访问令牌
        "refresh": "string",  // 刷新令牌（remember为true时返回）
        "user": {
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
}
```
- **错误码**:
  - 400: 请求参数错误
  - 401: 用户名或密码错误
  - 403: 用户已被禁用

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
        "access": "string"  // 新的访问令牌
    }
}
```
- **错误码**:
  - 400: 请求参数错误
  - 401: 刷新令牌无效或已过期

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
    "data": null
}
```
- **错误码**:
  - 401: 未授权或令牌已过期 