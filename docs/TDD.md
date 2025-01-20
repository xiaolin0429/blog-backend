# 个人博客系统技术架构文档

## 一、系统概述

### 1. 项目简介
本博客系统采用 Python + Vue.js 技术栈，基于前后端分离架构，通过 Vue.js 提供高效的交互体验，Python 后端使用 Django 处理业务逻辑和数据存储。系统支持主题定制、文章管理、评论互动等核心功能。

### 2. 系统功能特性
- **内容管理**
  - Markdown 编辑器支持
  - 文章草稿和发布管理
  - 文章分类和标签管理
  - 文章搜索和过滤
  - 评论管理系统

- **用户体验**
  - 响应式设计，适配多端设备
  - 深色/浅色主题切换
  - 文章目录自动生成
  - 代码高亮显示
  - 图片懒加载

- **SEO 优化**
  - 自定义 Meta 信息
  - 文章永久链接优化
  - 站点地图自动生成
  - 结构化数据支持
  - 页面预渲染

- **安全特性**
  - CSRF 防护
  - XSS 防护
  - SQL 注入防护
  - 敏感信息加密
  - 访问频率限制

### 3. 系统架构图
```
┌─────────────────────────────────────────────────┐
│                   前端展示层                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  文章页面 │  │  评论模块 │  │  用户中心 │      │
│  └──────────┘  └──────────┘  └──────────┘       │
├─────────────────────────────────────────────────┤
│                   API 接口层                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ 文章接口  │  │  用户接口 │  │ 评论接口  │      │
│  └──────────┘  └──────────┘  └──────────┘       │
├─────────────────────────────────────────────────┤
│                   业务逻辑层                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ 文章服务  │  │  用户服务 │  │ 评论服务  │      │
│  └──────────┘  └──────────┘  └──────────┘       │
├─────────────────────────────────────────────────┤
│                   基础服务层                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ 数据存储  │  │ 缓存接口  │  │ 搜索服务  │      │
│  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────┘
```

## 二、技术栈选型

### 1. 后端技术栈
- **核心框架**：Django 4.x
- **API框架**：Django REST framework
- **数据库**：PostgreSQL
- **搜索引擎**：Elasticsearch
- **缓存方案**：
  - 默认：Django内置缓存框架
  - 可扩展：预留分布式缓存接口
- **文件存储**：MinIO
- **异步任务**：Celery（可选）

### 2. 前端技术栈
- **核心框架**：Vue 3
- **状态管理**：Pinia
- **路由管理**：Vue Router
- **UI框架**：Element Plus
- **HTTP客户端**：Axios
- **编辑器**：MD Editor V3

## 三、测试策略

### 1. 测试框架
- pytest：单元测试和集成测试
- pytest-django：Django测试支持
- pytest-cov：测试覆盖率
- factory-boy：测试数据生成

### 2. 测试分层
```python
# 1. 单元测试示例
@pytest.mark.unit
class TestCacheService:
    def test_cache_interface(self):
        """测试缓存接口"""
        cache = CacheBackend()
        with pytest.raises(NotImplementedError):
            cache.get("test_key")
    
    def test_local_cache(self):
        """测试本地缓存实现"""
        cache = LocalCache()
        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"
    
    def test_cache_service(self):
        """测试缓存服务"""
        service = CacheService()
        service.set_post(1, {"title": "test"})
        assert service.get_post(1) == {"title": "test"}

# 2. 集成测试示例
@pytest.mark.integration
class TestPostViews:
    def test_post_cache(self, client, post_factory):
        """测试文章缓存集成"""
        post = post_factory()
        
        # 首次请求，应该从数据库获取
        response1 = client.get(f"/api/posts/{post.id}/")
        assert response1.status_code == 200
        
        # 再次请求，应该从缓存获取
        response2 = client.get(f"/api/posts/{post.id}/")
        assert response2.status_code == 200
        assert response2.data == response1.data

# 3. 性能测试示例
@pytest.mark.benchmark
class TestCachePerformance:
    def test_cache_performance(self, benchmark):
        """测试缓存性能"""
        service = CacheService()
        
        def cache_operation():
            service.set_post(1, {"title": "test"})
            return service.get_post(1)
        
        result = benchmark(cache_operation)
        assert result == {"title": "test"}
```

### 3. 测试数据准备
```python
# 1. 工厂类定义
class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post
    
    title = factory.Sequence(lambda n: f'测试文章{n}')
    content = factory.Faker('text')
    author = factory.SubFactory(UserFactory)
    status = Post.Status.PUBLISHED

# 2. Fixture定义
@pytest.fixture
def post_with_cache(post_factory, cache_service):
    """创建带缓存的文章"""
    post = post_factory()
    cache_service.set_post(post.id, {
        'id': post.id,
        'title': post.title,
        'content': post.content
    })
    return post
```

## 四、接口设计

### 1. 缓存接口
```python
# 1. 缓存后端接口
class CacheBackend(Protocol):
    """缓存后端协议"""
    
    def get(self, key: str) -> Any:
        """获取缓存值"""
        ...
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """设置缓存值"""
        ...
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        ...
    
    def clear(self) -> bool:
        """清空缓存"""
        ...

# 2. 本地缓存实现
class LocalCache(CacheBackend):
    """Django本地缓存实现"""
    
    def __init__(self):
        self.cache = caches['default']
    
    def get(self, key: str) -> Any:
        return self.cache.get(key)
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        return self.cache.set(key, value, timeout)
    
    def delete(self, key: str) -> bool:
        return self.cache.delete(key)
    
    def clear(self) -> bool:
        return self.cache.clear()

# 3. 缓存服务接口
class CacheService:
    """缓存服务"""
    
    def __init__(self, backend: Optional[CacheBackend] = None):
        self.backend = backend or LocalCache()
    
    def get_post(self, post_id: int) -> Optional[dict]:
        """获取文章缓存"""
        return self.backend.get(f'post:{post_id}')
    
    def set_post(self, post_id: int, data: dict, timeout: Optional[int] = None) -> bool:
        """设置文章缓存"""
        return self.backend.set(f'post:{post_id}', data, timeout)
    
    def clear_post(self, post_id: int) -> bool:
        """清除文章缓存"""
        return self.backend.delete(f'post:{post_id}')
```

### 2. 分布式功能接口
```python
# 1. 分布式锁接口
class DistributedLock(Protocol):
    """分布式锁协议"""
    
    def acquire(self, key: str, timeout: Optional[int] = None) -> bool:
        """获取锁"""
        ...
    
    def release(self, key: str) -> bool:
        """释放锁"""
        ...

# 2. 消息队列接口
class MessageQueue(Protocol):
    """消息队列协议"""
    
    def publish(self, channel: str, message: Any) -> bool:
        """发布消息"""
        ...
    
    def subscribe(self, channel: str) -> AsyncIterator[Any]:
        """订阅消息"""
        ...

# 3. 会话管理接口
class SessionManager(Protocol):
    """会话管理协议"""
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """获取会话"""
        ...
    
    def set_session(self, session_id: str, data: dict, timeout: Optional[int] = None) -> bool:
        """设置会话"""
        ...
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        ...
```

## 五、性能优化

### 1. 缓存策略
- **多级缓存**：
  1. 本地内存缓存（默认）
  2. 分布式缓存（可扩展）
  3. 数据库查询缓存

- **缓存预热**：
```python
class CacheWarmer:
    """缓存预热服务"""
    
    def __init__(self, cache_service: CacheService):
        self.cache_service = cache_service
    
    async def warm_posts(self):
        """预热文章缓存"""
        posts = await Post.objects.filter(status='published').all()
        for post in posts:
            data = PostSerializer(post).data
            await self.cache_service.set_post(post.id, data)
```

- **缓存更新策略**：
```python
class CacheInvalidator:
    """缓存失效服务"""
    
    def __init__(self, cache_service: CacheService):
        self.cache_service = cache_service
    
    def invalidate_post(self, post_id: int):
        """失效文章缓存"""
        self.cache_service.clear_post(post_id)
    
    def invalidate_related(self, post_id: int):
        """失效相关缓存"""
        self.cache_service.clear_post(post_id)
        self.cache_service.clear_post_list()
        self.cache_service.clear_category_posts()
```

### 2. 数据库优化
- 合理使用索引
- 查询优化
- 数据库连接池
- 定期维护

### 3. 代码优化
- 异步处理
- 批量操作
- 延迟加载
- 资源复用

## 六、监控告警

### 1. 性能监控
- 接口响应时间
- 缓存命中率
- 数据库性能
- 系统资源使用

### 2. 异常监控
- 错误日志
- 业务异常
- 系统异常
- 安全事件

### 3. 监控指标
```python
class MonitoringService:
    """监控服务"""
    
    def track_cache_metrics(self, operation: str, success: bool, duration: float):
        """跟踪缓存指标"""
        tags = {
            'operation': operation,
            'success': success
        }
        self.record_metric('cache_operation', duration, tags)
    
    def track_api_metrics(self, endpoint: str, method: str, status: int, duration: float):
        """跟踪API指标"""
        tags = {
            'endpoint': endpoint,
            'method': method,
            'status': status
        }
        self.record_metric('api_request', duration, tags)
```
