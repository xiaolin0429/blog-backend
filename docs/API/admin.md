# 管理员API文档

## 基础信息
- 基础路径：`/api/v1/user/admin`
- 认证方式：Bearer Token
- 权限要求：需要同时满足以下条件
  - 用户已认证（is_authenticated=True）
  - 用户具有管理员权限（is_staff=True）
  - 符合权限等级控制规则

## 权限等级控制规则

### 用户角色等级
1. 超级管理员（superadmin）：`is_superuser=True`
2. 管理员（admin）：`is_staff=True`
3. 普通用户（user）：普通注册用户

### 权限控制策略
1. 超级管理员
   - 可以执行所有操作
   - 是唯一可以修改用户权限的角色
   - 系统必须保留至少一个超级管理员

2. 普通管理员
   - 只能管理普通用户
   - 不能修改任何用户的权限
   - 不能操作其他管理员或超级管理员

3. 通用限制
   - 用户不能修改自己的权限
   - 用户不能删除自己的账号
   - 用户不能停用自己的账号
   - 不能停用或删除唯一的超级管理员

## 1. 用户管理

### 1.1 获取用户列表

#### 基本信息
- 请求路径: `/api/v1/user/admin/users/`
- 请求方法: `GET`
- 权限要求: 管理员及以上

#### 请求参数
| 参数名 | 类型 | 位置 | 是否必须 | 说明 | 示例 |
| --- | --- | --- | --- | --- | --- |
| search | string | query | 否 | 搜索关键词（用户名、邮箱、昵称） | "test" |
| status | string | query | 否 | 用户状态（active/inactive） | "active" |
| role | string | query | 否 | 用户角色（admin/user） | "admin" |
| page | integer | query | 否 | 页码，默认1 | 1 |
| size | integer | query | 否 | 每页数量，默认20 | 20 |
| ordering | string | query | 否 | 排序字段，前缀-表示降序 | "-date_joined" |

#### 支持的排序字段
- `id`: 用户ID
- `date_joined`: 注册时间
- `last_login`: 最后登录时间

#### 响应数据
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "total": 100,
        "page": 1,
        "size": 20,
        "items": [
            {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com",
                "nickname": "管理员",
                "status": "active",
                "role": "admin",
                "last_login": "2024-01-20T10:00:00Z",
                "date_joined": "2024-01-01T00:00:00Z"
            }
        ]
    }
}
```

### 1.2 创建用户

#### 基本信息
- 请求路径: `/api/v1/user/admin/users/`
- 请求方法: `POST`
- 权限要求: 管理员及以上
- 权限限制: 普通管理员只能创建普通用户

#### 请求参数
| 参数名 | 类型 | 位置 | 是否必须 | 说明 |
| --- | --- | --- | --- | --- |
| username | string | body | 是 | 用户名（唯一） |
| email | string | body | 是 | 邮箱（唯一） |
| password | string | body | 是 | 密码 |
| nickname | string | body | 否 | 昵称 |
| is_active | boolean | body | 否 | 是否激活 |
| is_staff | boolean | body | 否 | 是否为管理员（仅超级管理员可设置） |

#### 响应数据
```json
{
    "code": 200,
    "message": "创建用户成功",
    "data": {
        "id": 2,
        "username": "newuser",
        "email": "user@example.com",
        "nickname": "新用户",
        "status": "active",
        "role": "user",
        "last_login": null,
        "date_joined": "2024-01-20T10:00:00Z"
    }
}
```

### 1.3 获取用户详情

#### 基本信息
- 请求路径: `/api/v1/user/admin/users/{id}/`
- 请求方法: `GET`
- 权限要求: 管理员及以上

#### 路径参数
| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| id | integer | 是 | 用户ID | 1 |

#### 响应数据
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "nickname": "管理员",
        "bio": "个人简介",
        "status": "active",
        "role": "admin",
        "avatar": "/media/avatars/admin.jpg",
        "last_login": "2024-01-20T10:00:00Z",
        "date_joined": "2024-01-01T00:00:00Z",
        "is_active": true,
        "is_staff": true
    }
}
```

### 1.4 更新用户信息

#### 基本信息
- 请求路径: `/api/v1/user/admin/users/{id}/`
- 请求方法: `PUT/PATCH`
- 权限要求: 管理员及以上
- 权限限制:
  - 普通管理员只能修改普通用户信息
  - 只有超级管理员可以修改权限相关字段
  - 不能修改自己的权限
  - 用户名不可修改

#### 路径参数
| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| id | integer | 是 | 用户ID | 1 |

#### 请求参数
| 参数名 | 类型 | 位置 | 是否必须 | 说明 |
| --- | --- | --- | --- | --- |
| email | string | body | 否 | 邮箱（唯一） |
| nickname | string | body | 否 | 昵称 |
| bio | string | body | 否 | 个人简介 |
| is_active | boolean | body | 否 | 是否激活（需要权限） |
| is_staff | boolean | body | 否 | 是否为管理员（仅超级管理员可设置） |
| is_superuser | boolean | body | 否 | 是否为超级管理员（仅超级管理员可设置） |
| avatar | file | body | 否 | 头像文件 |

#### 响应数据
```json
{
    "code": 200,
    "message": "更新用户信息成功",
    "data": {
        "id": 1,
        "username": "admin",
        "email": "new@example.com",
        "nickname": "新昵称",
        "bio": "新简介",
        "status": "active",
        "role": "user",
        "avatar": null,
        "last_login": "2024-01-20T10:00:00Z",
        "date_joined": "2024-01-01T00:00:00Z",
        "is_active": true,
        "is_staff": false
    }
}
```

### 1.5 删除用户

#### 基本信息
- 请求路径: `/api/v1/user/admin/users/{id}/`
- 请求方法: `DELETE`
- 权限要求: 管理员及以上
- 权限限制:
  - 普通管理员只能删除普通用户
  - 不能删除自己的账号
  - 不能删除唯一的超级管理员
  - 实际执行软删除（设置is_active=False）

#### 路径参数
| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| id | integer | 是 | 用户ID | 1 |

#### 响应数据
```json
{
    "code": 200,
    "message": "删除用户成功"
}
```

### 1.6 激活用户

#### 基本信息
- 请求路径: `/api/v1/user/admin/users/{id}/activate/`
- 请求方法: `POST`
- 权限要求: 管理员及以上
- 权限限制: 普通管理员只能激活普通用户

#### 路径参数
| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| id | integer | 是 | 用户ID | 1 |

#### 响应数据
```json
{
    "code": 200,
    "message": "激活用户成功"
}
```

### 1.7 禁用用户

#### 基本信息
- 请求路径: `/api/v1/user/admin/users/{id}/deactivate/`
- 请求方法: `POST`
- 权限要求: 管理员及以上
- 权限限制:
  - 普通管理员只能停用普通用户
  - 不能停用自己的账号
  - 不能停用唯一的超级管理员

#### 路径参数
| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| id | integer | 是 | 用户ID | 1 |

#### 响应数据
```json
{
    "code": 200,
    "message": "禁用用户成功"
}
```

### 1.8 设置管理员权限

#### 基本信息
- 请求路径: `/api/v1/user/admin/users/{id}/set_admin/`
- 请求方法: `POST`
- 权限要求: 管理员及以上

#### 路径参数
| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| id | integer | 是 | 用户ID | 1 |

#### 响应数据
```json
{
    "code": 200,
    "message": "设置管理员权限成功"
}
```

### 1.9 移除管理员权限

#### 基本信息
- 请求路径: `/api/v1/user/admin/users/{id}/remove_admin/`
- 请求方法: `POST`
- 权限要求: 管理员及以上

#### 路径参数
| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| id | integer | 是 | 用户ID | 1 |

#### 响应数据
```json
{
    "code": 200,
    "message": "移除管理员权限成功"
}
```

### 1.10 重置用户密码

#### 基本信息
- 请求路径: `/api/v1/user/admin/users/{id}/reset_password/`
- 请求方法: `POST`
- 权限要求: 管理员及以上
- 权限限制: 普通管理员只能重置普通用户密码

#### 路径参数
| 参数名 | 类型 | 是否必须 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| id | integer | 是 | 用户ID | 1 |

#### 请求参数
```json
{
    "new_password": "newpass123"  // 新密码（必填，6-20字符）
}
```

#### 响应数据
```json
{
    "code": 200,
    "message": "重置密码成功"
}
```

## 错误码说明

| 错误码 | 说明 |
| --- | --- |
| 400 | 请求参数错误 |
| 401 | 未授权或Token无效 |
| 403 | 无权限执行此操作 |
| 404 | 用户不存在 |
| 409 | 用户名或邮箱已存在 |
| 500 | 服务器内部错误 |

## 注意事项

1. 所有请求都需要在请求头中携带有效的管理员Token：
```
Authorization: Bearer {access_token}
```

2. 用户状态说明：
- `active`: 正常状态
- `inactive`: 禁用状态

3. 用户角色说明：
- `superadmin`: 超级管理员
- `admin`: 普通管理员
- `user`: 普通用户

4. 删除用户采用软删除方式，只是将用户状态设置为禁用。

5. 创建或更新用户时的字段限制：
- `username`: 4-20个字符，只能包含字母、数字、下划线
- `email`: 有效的邮箱格式
- `password`: 6-20个字符，必须包含字母和数字
- `nickname`: 2-20个字符
- `bio`: 最大500个字符
