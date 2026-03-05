# API 设计规范

## RESTful API 设计原则

### URL 设计

- 使用名词，不使用动词
- 使用复数形式
- 使用小写字母和连字符
- 嵌套资源不超过 2 层

### HTTP 方法

- `GET`: 获取资源
- `POST`: 创建资源
- `PUT`: 更新资源（完整替换）
- `PATCH`: 部分更新资源
- `DELETE`: 删除资源

### 状态码

- `200 OK`: 成功
- `201 Created`: 创建成功
- `400 Bad Request`: 请求错误
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器错误

## API 版本管理

- 使用 URL 路径版本：`/api/v1/...`
- 向后兼容，不破坏现有 API
- 新版本通过新路径提供

## 响应格式

### 成功响应

```json
{
  "data": {...},
  "meta": {
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

### 错误响应

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "请求参数无效",
    "details": {...}
  }
}
```

## 分页

- 使用 `page` 和 `page_size` 参数
- 默认 `page_size` 为 20
- 最大 `page_size` 为 100

## 过滤和排序

- 使用查询参数：`?filter=status:completed&sort=created_at:desc`
- 支持多个过滤条件
- 支持多字段排序
