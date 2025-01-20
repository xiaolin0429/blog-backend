# 标签相关API

## 获取标签列表
- **接口说明**: 获取标签列表，支持分页、排序和筛选
- **请求方式**: GET
- **接口路径**: `/api/v1/tags/`
- **请求参数**:
  - page: 页码（可选，默认1）
  - size: 每页数量（可选，默认10，最大50）
  - ordering: 排序字段（可选，支持name, created_at）
  - search: 搜索关键词（可选，搜索name）

- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "count": 0,
        "next": "string",
        "previous": "string",
        "results": [
            {
                "id": 0,
                "name": "string",
                "created_at": "string",
                "updated_at": "string"
            }
        ]
    }
}
```

## 创建标签
- **接口说明**: 创建新标签
- **请求方式**: POST
- **接口路径**: `/api/v1/tags/`
- **请求头**:
  - Authorization: Bearer {token}
- **请求参数**:
```json
{
    "name": "string"  // 标签名称（必填，2-50字符，唯一）
}
```
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 0,
        "name": "string",
        "created_at": "string",
        "updated_at": "string"
    }
}
```
- **错误码**:
  - 400: 请求参数错误（名称为空或超长）
  - 401: 未授权
  - 409: 标签名称已存在

## 批量创建标签
- **接口说明**: 批量创建多个标签
- **请求方式**: POST
- **接口路径**: `/api/v1/tags/batch/`
- **请求头**:
  - Authorization: Bearer {token}
- **请求参数**:
```json
{
    "names": ["string"]  // 标签名称列表（必填，每个名称2-50字符，唯一）
}
```
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "created": [
            {
                "id": 0,
                "name": "string",
                "created_at": "string",
                "updated_at": "string"
            }
        ],
        "existed": [
            {
                "id": 0,
                "name": "string",
                "created_at": "string",
                "updated_at": "string"
            }
        ]
    }
}
```
- **错误码**:
  - 400: 请求参数错误（名称为空或超长）
  - 401: 未授权

## 获取标签详情
- **接口说明**: 获取标签详细信息
- **请求方式**: GET
- **接口路径**: `/api/v1/tags/{id}/`
- **响应数据**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 0,
        "name": "string",
        "created_at": "string",
        "updated_at": "string"
    }
}
```

## 更新标签
- **接口说明**: 更新标签信息
- **请求方式**: PUT
- **接口路径**: `/api/v1/tags/{id}/`
- **请求头**:
  - Authorization: Bearer {token}
- **请求参数**: 同创建标签
- **响应数据**: 同创建标签
- **错误码**:
  - 400: 请求参数错误（名称为空或超长）
  - 401: 未授权
  - 403: 无权限修改此标签
  - 404: 标签不存在
  - 409: 标签名称已存在

## 删除标签
- **接口说明**: 删除标签
- **请求方式**: DELETE
- **接口路径**: `/api/v1/tags/{id}/`
- **请求头**:
  - Authorization: Bearer {token}
- **响应数据**:
```json
{
    "code": 204,
    "message": "success",
    "data": null
}
```
- **错误码**:
  - 401: 未授权
  - 403: 无权限删除此标签
  - 404: 标签不存在
  - 422: 标签下存在文章，无法删除 