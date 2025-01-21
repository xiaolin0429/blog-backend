# 博客后端系统部署文档

## 1. 环境要求

- Python 3.12+
- PostgreSQL 14+
- Redis 6+
- MinIO
- Elasticsearch 7+
- Node.js 18+ (用于pre-commit hooks)

## 2. 安装依赖

```bash
# 克隆项目
git clone https://github.com/xiaolin0429/blog-backend
cd blog-backend

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 配置pip镜像源（提高下载速度和稳定性）
# Windows
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
# Linux/Mac
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 升级pip
pip install --upgrade pip

# 安装开发环境依赖
pip install -r requirements/dev.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装生产环境依赖
pip install -r requirements/base.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 初始化pre-commit
pre-commit install
```

可选的pip镜像源：
```bash
# 清华大学镜像源
https://pypi.tuna.tsinghua.edu.cn/simple

# 阿里云镜像源
https://mirrors.aliyun.com/pypi/simple

# 华为云镜像源
https://repo.huaweicloud.com/repository/pypi/simple

# 腾讯云镜像源
https://mirrors.cloud.tencent.com/pypi/simple

# 豆瓣镜像源
https://pypi.douban.com/simple
```

## 3. 环境配置

在项目根目录创建 `.env` 文件，配置以下环境变量：

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=blog_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# JWT
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

## 4. 安全检查

在部署前，执行以下安全检查：

```bash
# 检查依赖包安全性
safety check

# 执行Python代码安全检查
bandit -r .

# 运行代码风格检查
flake8 .
black . --check
mypy .

# 运行测试套件
pytest --cov
```

## 5. 数据库迁移

```bash
# 创建数据库迁移
python manage.py makemigrations

# 应用数据库迁移
python manage.py migrate

# 检查迁移状态
python manage.py showmigrations
```

## 6. 创建超级用户

```bash
python manage.py createsuperuser
```

## 7. 静态文件和媒体文件配置

```bash
# 收集静态文件
python manage.py collectstatic --noinput

# 创建媒体文件目录
mkdir -p media
# Windows
icacls media /grant Users:(OI)(CI)F
# Linux/Mac
chmod 755 media

# 确保MinIO bucket存在
python manage.py check_storage
```

## 8. 启动服务

### 开发环境

```bash
# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 启动开发服务器（默认端口8000）
python manage.py runserver

# 启动Celery Worker（确保Redis已启动）
# Windows
celery -A config worker -l info -P eventlet
# Linux/Mac
celery -A config worker -l info

# 启动Celery Beat（定时任务）
celery -A config beat -l info

# 启动文档服务（可选，默认端口8001）
cd docs
mkdocs serve -a 0.0.0.0:8001
```

### 生产环境

1. 使用 Gunicorn 作为 WSGI 服务器：

```bash
# 启动Gunicorn
.venv/bin/gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class=gevent \
    --timeout 60 \
    --access-logfile logs/gunicorn-access.log \
    --error-logfile logs/gunicorn-error.log \
    --pid logs/gunicorn.pid \
    --daemon
```

2. 使用 Supervisor 管理进程：

> 配置文件路径：`supervisor/blog.conf`

```ini
[program:blog-backend]
command=%(ENV_VIRTUAL_ENV)s/bin/gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --worker-class=gevent --timeout 60
directory=%(here)s
user=%(ENV_USER)s
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=logs/gunicorn.log
stderr_logfile=logs/gunicorn-error.log
environment=DJANGO_SETTINGS_MODULE="config.settings.production"

[program:blog-celery]
command=%(ENV_VIRTUAL_ENV)s/bin/celery -A config worker -l info
directory=%(here)s
user=%(ENV_USER)s
numprocs=1
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=logs/celery.log
stderr_logfile=logs/celery-error.log
environment=DJANGO_SETTINGS_MODULE="config.settings.production"

[program:blog-celerybeat]
command=%(ENV_VIRTUAL_ENV)s/bin/celery -A config beat -l info
directory=%(here)s
user=%(ENV_USER)s
numprocs=1
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=logs/celerybeat.log
stderr_logfile=logs/celerybeat-error.log
environment=DJANGO_SETTINGS_MODULE="config.settings.production"

[group:blog-backend]
programs=blog-backend,blog-celery,blog-celerybeat
priority=999
```

3. Supervisor 管理命令：

```bash
# 创建日志目录
mkdir -p logs
# Windows
icacls logs /grant Users:(OI)(CI)F
# Linux/Mac
chmod -R 755 logs

# 启动supervisor
supervisord -c supervisor/blog.conf

# 重新加载配置
supervisorctl -c supervisor/blog.conf reread
supervisorctl -c supervisor/blog.conf update

# 启动所有服务
supervisorctl -c supervisor/blog.conf start blog-backend:*

# 停止所有服务
supervisorctl -c supervisor/blog.conf stop blog-backend:*

# 重启所有服务
supervisorctl -c supervisor/blog.conf restart blog-backend:*

# 查看服务状态
supervisorctl -c supervisor/blog.conf status blog-backend:*
```

## 9. 安全配置

1. 生产环境配置检查：
```bash
# 运行Django安全检查
python manage.py check --deploy

# 检查文件权限
# Windows
icacls .env /inheritance:r /grant:r "%USERNAME%":F
icacls static /grant Users:(OI)(CI)R
icacls media /grant Users:(OI)(CI)R
# Linux/Mac
chmod 600 .env
chmod -R 755 static
chmod -R 755 media
```

2. 安全最佳实践：
   - 使用强密码策略
   - 启用请求频率限制
   - 配置CORS白名单
   - 启用CSRF保护
   - 配置对象级权限
   - 启用审计日志
   - 定期更新依赖包

3. 备份策略：
```bash
# 数据库备份
pg_dump blog_db > backup/db_$(date +%Y%m%d).sql

# 媒体文件备份
# Windows
xcopy /E /I media backup\media
# Linux/Mac
rsync -av media/ backup/media/

# 设置定时备份
# Windows：使用任务计划程序
# Linux/Mac：使用crontab
0 2 * * * /path/to/backup_script.sh
```

## 10. 监控和维护

1. 系统监控：
```bash
# 检查服务状态
supervisorctl -c supervisor/blog.conf status

# 检查日志
# Windows
type logs\*.log
# Linux/Mac
tail -f logs/*.log

# 检查系统资源
# Windows：任务管理器
# Linux/Mac：htop
```

2. 应用监控：
```bash
# 检查API响应时间
curl -w "%{time_total}\n" -s http://localhost:8000/health-check

# 检查数据库连接
python manage.py dbshell

# 检查缓存状态
python manage.py shell
>>> from django.core.cache import cache
>>> cache.get_stats()
```

3. 定期维护：
```bash
# 清理会话数据
python manage.py clearsessions

# 清理缓存
python manage.py clearcache

# 优化数据库
python manage.py cleanup_unused_media

# 更新依赖
pip install -r requirements/base.txt --upgrade
```

4. 文档维护：
```bash
# 构建文档
cd docs
mkdocs build

# 部署文档（如果使用GitHub Pages）
mkdocs gh-deploy
``` 