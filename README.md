# Blog Backend

基于 Django + DRF 的博客系统后端

## 技术栈

- Python 3.12+
- Django 5.0+
- Django REST Framework 3.14+
- PostgreSQL 14+
- Redis 6+
- MinIO
- Elasticsearch 7+
- Celery 5+

## 主要功能

1. 用户系统
   - 用户注册/登录
   - JWT认证
   - 用户信息管理
   - 权限管理

2. 文章系统
   - 文章CRUD
   - 分类管理
   - 标签管理
   - 评论系统
   - 全文搜索

3. 插件系统
   - 文件上传
   - 图片处理
   - 缓存管理
   - 异步任务

## 目录结构

```
backend/
├── apps/                    # 应用目录
│   ├── user/               # 用户模块
│   ├── post/              # 文章模块
│   └── plugin/            # 插件模块
├── config/                 # 配置目录
│   ├── settings/         # 配置文件
│   ├── urls.py          # URL配置
│   └── wsgi.py          # WSGI配置
├── docs/                  # 文档目录
│   ├── deployment.md    # 部署文档
│   └── testing.md       # 测试文档
├── tests/                 # 测试目录
├── utils/                 # 工具目录
├── manage.py             # 管理脚本
├── requirements.txt      # 依赖文件
└── README.md            # 项目说明
```

## 开发环境搭建

1. 克隆项目
```bash
git clone <repository_url>
cd backend
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，配置必要的环境变量
```

5. 数据库迁移
```bash
python manage.py migrate
```

6. 创建超级用户
```bash
python manage.py createsuperuser
```

7. 运行开发服务器
```bash
python manage.py runserver
```

## 测试

运行测试并生成覆盖率报告：

```bash
pytest --cov=apps --cov-report=html
```

详细的测试说明请参考 [测试文档](docs/testing.md)。

## 部署

部署相关说明请参考 [部署文档](docs/deployment.md)。

## API文档

启动开发服务器后访问：
- Swagger UI: http://localhost:8000/api/swagger/
- ReDoc: http://localhost:8000/api/redoc/

## 代码规范

- 遵循 PEP 8 规范
- 使用 Black 进行代码格式化
- 使用 isort 进行导入排序
- 使用 flake8 进行代码检查

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交代码
4. 创建 Pull Request

## 许可证

[MIT License](LICENSE) 