# 用户相关API

## 用户注册
- **接口说明**: 创建新用户账号
- **请求方式**: POST
- **接口路径**: `/api/v1/user/register`
- **请求头**:
  - Content-Type: application/json

- **请求参数**:

| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
|--------|------|----------|------|------|
| username | string | 是 | 用户名,长度4-20,只能包含字母、数字、下划线 | "test_user" |
| password | string | 是 | 密码,长度6-20,必须包含字母和数字 | "Test123456" |
| password2 | string | 是 | 确认密码,必须与密码一致 | "Test123456" |
| email | string | 是 | 邮箱,必须是有效的邮箱格式 | "test@example.com" |
| nickname | string | 否 | 昵称,长度2-20,允许为null | "测试用户" |

- **响应参数**:

| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| code | number | 是 | 状态码 |
| message | string | 是 | 状态信息 |
| data.id | number | 是 | 用户ID |
| data.username | string | 是 | 用户名 |
| data.email | string | 是 | 邮箱 |
| data.nickname | string | 否 | 昵称 |
| timestamp | string | 是 | 时间戳,格式:ISO 8601 |
| requestId | string | 是 | 请求ID |

- **响应示例**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "username": "test_user",
        "email": "test@example.com",
        "nickname": "测试用户"
    },
    "timestamp": "2024-03-20T12:00:00Z",
    "requestId": "7cb116acbcd23"
}
```

- **错误码**:
  - 400: 请求参数错误
    - 用户名长度不符合要求
    - 密码长度不符合要求
    - 密码不包含字母或数字
    - 两次密码不一致
    - 邮箱格式无效
    - 昵称长度不符合要求
  - 409: 用户名或邮箱已存在

## 用户登录
- **接口说明**: 用户登录获取访问令牌
- **请求方式**: POST
- **接口路径**: `/api/v1/user/login`
- **请求头**:
  - Content-Type: application/json
  - X-Timezone: 用户时区（可选,默认Asia/Shanghai,使用IANA时区名称,如Asia/Shanghai、America/New_York等）

- **请求参数**:

| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
|--------|------|----------|------|------|
| username | string | 是 | 用户名 | "test_user" |
| password | string | 是 | 密码 | "Test123456" |
| remember | boolean | 否 | 是否记住登录状态,为true时访问令牌有效期延长至30天,刷新令牌有效期延长至60天,默认访问令牌24小时,刷新令牌7天 | true |

- **响应参数**:

| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| code | number | 是 | 状态码 |
| message | string | 是 | 状态信息 |
| data.access | string | 是 | 访问令牌 |
| data.refresh | string | 是 | 刷新令牌 |
| data.user.id | number | 是 | 用户ID |
| data.user.username | string | 是 | 用户名 |
| data.user.email | string | 是 | 邮箱 |
| data.user.nickname | string | 否 | 昵称 |
| data.user.avatar | string | 是 | 头像URL,无头像时返回默认头像URL(/media/avatars/default.png) |
| data.user.date_joined | string | 是 | 注册时间,格式:YYYY-MM-DD HH:mm:ss,按用户时区显示 |
| data.user.last_login | string | 是 | 最后登录时间,格式:YYYY-MM-DD HH:mm:ss,按用户时区显示 |
| timestamp | string | 是 | 时间戳,格式:ISO 8601 |
| requestId | string | 是 | 请求ID |

- **响应示例**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "user": {
            "id": 1,
            "username": "test_user",
            "email": "test@example.com",
            "nickname": "测试用户",
            "avatar": "http://example.com/media/avatars/default.png",
            "date_joined": "2024-03-20 12:00:00",
            "last_login": "2024-03-20 12:00:00"
        }
    },
    "timestamp": "2024-03-20T12:00:00Z",
    "requestId": "7cb116acbcd23"
}
```

- **错误码**:
  - 401: 用户名或密码错误
  - 403: 账号已被锁定（连续5次密码错误）
  - 429: 登录尝试次数过多（1分钟内超过10次尝试）

## 获取个人信息
- **接口说明**: 获取当前登录用户的详细信息
- **请求方式**: GET
- **接口路径**: `/api/v1/user/me`
- **请求头**:
  - Authorization: Bearer {token}（必填）

- **响应参数**:

| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| code | number | 是 | 状态码 |
| message | string | 是 | 状态信息 |
| data.id | number | 是 | 用户ID |
| data.username | string | 是 | 用户名 |
| data.email | string | 是 | 邮箱 |
| data.nickname | string | 否 | 昵称 |
| data.avatar | string | 是 | 头像URL,无头像时返回默认头像URL(/media/avatars/default.png) |
| data.bio | string | 是 | 个人简介,无简介时返回空字符串 |
| data.date_joined | string | 是 | 注册时间,格式:YYYY-MM-DD HH:mm:ss |
| data.last_login | string | 是 | 最后登录时间,格式:YYYY-MM-DD HH:mm:ss |
| timestamp | string | 是 | 时间戳,格式:ISO 8601 |
| requestId | string | 是 | 请求ID |

- **响应示例**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "username": "test_user",
        "email": "test@example.com",
        "nickname": "测试用户",
        "avatar": "http://example.com/media/avatars/default.png",
        "bio": "这是我的个人简介",
        "date_joined": "2024-03-20 12:00:00",
        "last_login": "2024-03-20 12:00:00"
    },
    "timestamp": "2024-03-20T12:00:00Z",
    "requestId": "7cb116acbcd23"
}
```

- **错误码**:
  - 401: 未授权（未登录或token无效）

## 更新个人信息
- **接口说明**: 更新当前用户的个人信息
- **请求方式**: PATCH
- **接口路径**: `/api/v1/user/me`
- **请求头**:
  - Authorization: Bearer {token}（必填）
  - Content-Type: multipart/form-data

- **请求参数**:

| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
|--------|------|----------|------|------|
| nickname | string | 否 | 昵称,长度2-20,允许为null | "新昵称" |
| avatar | file | 否 | 头像文件,支持jpg/png/gif,大小不超过2MB,分辨率不超过1024x1024,允许为null | - |
| bio | string | 否 | 个人简介,长度不超过500,允许为null | "这是新的个人简介" |

- **响应参数**:

| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| code | number | 是 | 状态码 |
| message | string | 是 | 状态信息 |
| data.id | number | 是 | 用户ID |
| data.username | string | 是 | 用户名 |
| data.email | string | 是 | 邮箱 |
| data.nickname | string | 否 | 昵称 |
| data.avatar | string | 是 | 头像URL |
| data.bio | string | 是 | 个人简介 |
| timestamp | string | 是 | 时间戳,格式:ISO 8601 |
| requestId | string | 是 | 请求ID |

- **响应示例**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "username": "test_user",
        "email": "test@example.com",
        "nickname": "新昵称",
        "avatar": "http://example.com/media/avatars/1.png",
        "bio": "这是新的个人简介"
    },
    "timestamp": "2024-03-20T12:00:00Z",
    "requestId": "7cb116acbcd23"
}
```

- **错误码**:
  - 400: 请求参数错误
    - 昵称长度不符合要求
    - 头像文件格式不支持
    - 头像文件大小超过限制
    - 头像分辨率超过限制
    - 个人简介长度超过限制
  - 401: 未授权（未登录或token无效）

## 修改密码
- **接口说明**: 修改当前用户的登录密码
- **请求方式**: PUT
- **接口路径**: `/api/v1/user/me/password`
- **请求头**:
  - Authorization: Bearer {token}（必填）
  - Content-Type: application/json

- **请求参数**:

| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
|--------|------|----------|------|------|
| old_password | string | 是 | 当前密码 | "Test123456" |
| new_password | string | 是 | 新密码,长度8-30,必须包含字母和数字 | "NewTest123456" |
| confirm_password | string | 是 | 确认新密码,必须与新密码一致 | "NewTest123456" |

- **响应参数**:

| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| code | number | 是 | 状态码 |
| message | string | 是 | 状态信息 |
| data | null | 是 | 响应数据 |
| timestamp | string | 是 | 时间戳,格式:ISO 8601 |
| requestId | string | 是 | 请求ID |

- **响应示例**:
```json
{
    "code": 200,
    "message": "密码修改成功",
    "data": null,
    "timestamp": "2024-03-20T12:00:00Z",
    "requestId": "7cb116acbcd23"
}
```

- **错误码**:
  - 400: 请求参数错误
    - 旧密码不正确
    - 新密码长度不符合要求（8-30个字符）
    - 新密码必须包含字母和数字
    - 新密码与旧密码相同
    - 确认密码与新密码不一致
  - 401: 未授权（未登录或token无效）

## 用户登出
- **接口说明**: 注销当前用户的登录状态,使当前token失效并加入黑名单
- **请求方式**: POST
- **接口路径**: `/api/v1/user/logout`
- **请求头**:
  - Authorization: Bearer {token}（必填）
  - Content-Type: application/json

- **请求参数**:

| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
|--------|------|----------|------|------|
| refresh | string | 是 | 刷新令牌,将被加入黑名单 | "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." |

- **响应参数**:

| 参数名 | 类型 | 是否必返回 | 说明 |
|--------|------|------------|------|
| code | number | 是 | 状态码 |
| message | string | 是 | 状态信息 |
| data | null | 是 | 响应数据 |
| timestamp | string | 是 | 时间戳,格式:ISO 8601 |
| requestId | string | 是 | 请求ID |

- **响应示例**:
```json
{
    "code": 200,
    "message": "登出成功",
    "data": null,
    "timestamp": "2024-03-20T12:00:00Z",
    "requestId": "7cb116acbcd23"
}
```

- **错误码**:
  - 400: 令牌无效或已过期
  - 401: 未授权（未登录或token无效）
