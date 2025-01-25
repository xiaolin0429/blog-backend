# 博客后端系统部署文档

## 1. 环境要求

### 基础环境
- Python 3.10+ (推荐3.10.x)
- PostgreSQL 14+ (推荐14.x)
- Redis 6+ (推荐6.2.x)
- Node.js 16+ (推荐16.x LTS，用于前端构建)

### Python依赖包
核心依赖：
- Django 4.2+
- Django REST framework 3.14+
- Celery 5.3+
- psycopg2-binary 2.9+
- redis 5.0+

测试依赖：
- pytest 7.4+
- pytest-django 4.5+
- pytest-cov 4.1+
- factory-boy 3.3+
- coverage 7.3+

开发工具：
- black 23.0+
- flake8 6.0+
- mypy 1.0+
- pre-commit 3.0+

## 2. 开发环境部署

### 2.1 基础环境准备

1. 克隆项目：
```bash
git clone https://github.com/xiaolin0429/blog-backend
cd blog-backend
```

2. 创建并激活虚拟环境：
```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. 配置pip镜像（可选，提高下载速度）：
```bash
# 配置pip镜像源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 升级pip
pip install --upgrade pip
```

### 2.2 安装依赖

1. 安装项目依赖：
```bash
# 安装开发环境依赖
pip install -r requirements/dev.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装生产环境依赖
pip install -r requirements/base.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 初始化pre-commit
pre-commit install
```

2. 可选的pip镜像源：
```bash
# 清华大学镜像源
https://pypi.tuna.tsinghua.edu.cn/simple

# 阿里云镜像源
https://mirrors.aliyun.com/pypi/simple

# 华为云镜像源
https://repo.huaweicloud.com/repository/pypi/simple
```

### 2.3 环境配置

1. 创建并配置环境变量：
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，配置以下必要参数
# 1. 数据库连接信息
# 2. Redis连接信息
# 3. JWT密钥
# 4. 存储配置
```

2. 环境变量说明：
```env
# Django基础配置
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库配置
DB_NAME=blog_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# JWT配置
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_LIFETIME=24
JWT_REFRESH_TOKEN_LIFETIME=7

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your-access-key
MINIO_SECRET_KEY=your-secret-key
MINIO_BUCKET_NAME=blog-media
MINIO_SECURE=False

# Elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Rate Limiting
RATELIMIT_ENABLE=True
RATELIMIT_USE_CACHE=default

# API Documentation
SWAGGER_SETTINGS_ENABLED=True
```

### 2.4 数据库初始化

1. 创建数据库：
```bash
# PostgreSQL
createdb blog_db

# 或者使用psql
psql -U postgres
CREATE DATABASE blog_db;
```

2. 执行数据库迁移：
```bash
# 创建迁移文件
python manage.py makemigrations

# 应用迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
```

### 2.5 运行开发服务器

1. 启动开发服务器：
```bash
python manage.py runserver
```

2. 启动Celery（需要新的终端）：
```bash
# 收集静态文件
python manage.py collectstatic --noinput

# 创建媒体文件目录
mkdir -p media
# Windows
celery -A config worker -l info -P eventlet
# Linux/Mac
celery -A config worker -l info
```

3. 启动Celery Beat（可选，需要新的终端）：
```bash
celery -A config beat -l info
```

## 3. 测试

### 3.1 测试环境配置

1. 测试数据库配置（config/settings/test.py）：
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
```

2. 准备测试数据：
```bash
# 创建测试数据目录
mkdir -p tests/resources

# 复制测试资源文件
cp path/to/test/files tests/resources/
```

### 3.2 运行测试

1. 运行所有测试：
```bash
# 运行测试并生成覆盖率报告
pytest --cov=apps --cov-report=html

# 运行特定测试文件
pytest tests/apps/post/test_post_api.py

# 运行特定测试类
pytest tests/apps/post/test_post_api.py::TestPostAPI

# 运行特定测试方法
pytest tests/apps/post/test_post_api.py::TestPostAPI::test_create_post
```

2. 查看测试覆盖率报告：
```bash
# 报告位置：htmlcov/index.html
# Windows
start htmlcov/index.html
# Linux
xdg-open htmlcov/index.html
# Mac
open htmlcov/index.html
```

## 4. 生产环境部署

### 4.1 系统准备

1. 安装系统依赖：
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3-dev postgresql postgresql-contrib redis-server supervisor nginx

# CentOS/RHEL
sudo yum update
sudo yum install -y python3-devel postgresql postgresql-server redis supervisor nginx
```

2. 创建项目目录：
```bash
sudo mkdir -p /var/www/blog-backend
sudo chown -R $USER:$USER /var/www/blog-backend
```

### 4.2 安装应用

1. 克隆代码：
```bash
cd /var/www/blog-backend
git clone https://github.com/xiaolin0429/blog-backend .
```

2. 创建虚拟环境：
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/production.txt
```

3. 配置环境变量：
```bash
# 创建并编辑生产环境配置
cp .env.example .env.prod
vim .env.prod
```

### 4.3 配置服务

1. Gunicorn配置（gunicorn.conf.py）：
```python
bind = '127.0.0.1:8000'
workers = 4
worker_class = 'gevent'
timeout = 60
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
```

2. Supervisor配置（/etc/supervisor/conf.d/blog.conf）：
```ini
[program:blog-backend]
command=/var/www/blog-backend/.venv/bin/gunicorn config.wsgi:application -c gunicorn.conf.py
directory=/var/www/blog-backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/blog-backend/gunicorn.log
stderr_logfile=/var/log/blog-backend/gunicorn-error.log

[program:blog-celery]
command=/var/www/blog-backend/.venv/bin/celery -A config worker -l info
directory=/var/www/blog-backend
user=www-data
numprocs=1
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/blog-backend/celery.log
stderr_logfile=/var/log/blog-backend/celery-error.log
```

3. Nginx配置（/etc/nginx/sites-available/blog-backend）：
```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /var/www/blog-backend/static/;
    }

    location /media/ {
        alias /var/www/blog-backend/media/;
    }
}
```

### 4.4 启动服务

1. 初始化数据：
```bash
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
```

2. 启动服务：
```bash
# 启动Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all

# 启动Nginx
sudo systemctl start nginx
```

### 4.5 监控和维护

1. 查看日志：
```bash
# 应用日志
tail -f /var/log/blog-backend/gunicorn.log

# Celery日志
tail -f /var/log/blog-backend/celery.log

# Nginx日志
tail -f /var/log/nginx/access.log
```

2. 备份数据：
```bash
# 数据库备份
pg_dump blog_db > backup/db_$(date +%Y%m%d).sql

# 媒体文件备份
rsync -av media/ backup/media/
```

3. 更新应用：
```bash
# 拉取最新代码
git pull

# 更新依赖
pip install -r requirements/production.txt

# 迁移数据库
python manage.py migrate

# 重启服务
sudo supervisorctl restart all
```

## 5. 安全建议

### 5.1 系统安全

1. 文件权限：
```bash
# 设置敏感文件权限
chmod 600 .env.prod
chmod -R 755 static media
```

2. 防火墙配置：
```bash
# Ubuntu/Debian
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 5.2 应用安全

1. 安全检查：
```bash
# Django安全检查
python manage.py check --deploy

# 依赖包安全检查
safety check
```

2. 定期更新：
```bash
# 更新系统包
sudo apt update && sudo apt upgrade

# 更新Python包
pip install -r requirements/production.txt --upgrade
```

### 5.3 监控告警

1. 设置监控：
```bash
# 检查服务状态
curl -f http://localhost/health-check

# 检查数据库连接
python manage.py dbshell

# 检查Redis连接
redis-cli ping
```

2. 配置告警：
- 设置服务监控告警
- 配置磁盘空间告警
- 配置CPU/内存使用率告警
- 配置错误日志告警
