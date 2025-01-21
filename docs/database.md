# 数据库部署文档

## 1. 数据库环境要求

- PostgreSQL 14+
- Redis 6+ (用于缓存和Celery)
- Elasticsearch 7+ (用于全文搜索)

## 2. PostgreSQL安装和配置

### 2.1 安装PostgreSQL

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# CentOS/RHEL
sudo dnf install postgresql-server postgresql-contrib
sudo postgresql-setup --initdb

# Windows
# 从 https://www.postgresql.org/download/windows/ 下载安装包
```

### 2.2 基础配置

1. 创建数据库和用户：
```sql
-- 登录PostgreSQL
psql -U postgres

-- 创建数据库
CREATE DATABASE blog_db;

-- 创建用户并设置密码
CREATE USER blog_user WITH PASSWORD 'your-secure-password';

-- 授权
GRANT ALL PRIVILEGES ON DATABASE blog_db TO blog_user;
```

2. 配置数据库连接（`postgresql.conf`）：
```conf
# 监听地址
listen_addresses = '*'          # 生产环境建议设置具体IP
max_connections = 100          # 根据需求调整
shared_buffers = 256MB         # 建议为系统内存的1/4
work_mem = 4MB                 # 根据查询复杂度调整
maintenance_work_mem = 64MB    # 维护操作使用的内存
effective_cache_size = 768MB   # 建议为系统内存的1/2
```

3. 配置访问控制（`pg_hba.conf`）：
```conf
# IPv4 local connections:
host    blog_db         blog_user        127.0.0.1/32            md5
host    blog_db         blog_user        your-server-ip/32       md5
```

### 2.3 性能优化

1. 内存配置：
```conf
effective_io_concurrency = 200         # SSD磁盘建议值
random_page_cost = 1.1                 # SSD磁盘建议值
default_statistics_target = 100        # 统计信息采样数
```

2. 并发配置：
```conf
max_worker_processes = 8               # CPU核心数
max_parallel_workers_per_gather = 4    # 并行查询工作进程数
max_parallel_workers = 8               # 最大并行工作进程数
```

3. WAL配置：
```conf
wal_level = replica                    # WAL级别
max_wal_size = 1GB                    # 最大WAL文件大小
min_wal_size = 80MB                   # 最小WAL文件大小
```

## 3. Redis配置

### 3.1 安装Redis

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install redis-server

# CentOS/RHEL
sudo dnf install redis

# Windows
# 从 https://github.com/microsoftarchive/redis/releases 下载安装包
```

### 3.2 基础配置

编辑 `redis.conf`：
```conf
bind 127.0.0.1            # 监听地址
port 6379                 # 端口
daemonize yes            # 守护进程模式
databases 16             # 数据库数量
maxmemory 256mb         # 最大内存使用
maxmemory-policy allkeys-lru  # 内存策略
```

### 3.3 持久化配置

```conf
# RDB配置
save 900 1              # 900秒内有1个改动就保存
save 300 10             # 300秒内有10个改动就保存
save 60 10000          # 60秒内有10000个改动就保存

# AOF配置
appendonly yes
appendfsync everysec
```

## 4. 数据库备份策略

### 4.1 PostgreSQL备份

1. 创建备份脚本 `backup_db.sh`：
```bash
#!/bin/bash
BACKUP_DIR="/path/to/backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="blog_db"
DB_USER="blog_user"

# 创建备份
pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/db_backup_$TIMESTAMP.sql

# 压缩备份
gzip $BACKUP_DIR/db_backup_$TIMESTAMP.sql

# 删除7天前的备份
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete
```

2. 设置定时任务：
```bash
# 编辑crontab
crontab -e

# 添加每日备份任务（每天凌晨2点执行）
0 2 * * * /path/to/backup_db.sh
```

### 4.2 Redis备份

1. 配置Redis自动保存：
```conf
save 900 1
save 300 10
save 60 10000
dir /path/to/redis/backup
dbfilename dump.rdb
```

2. 创建备份脚本 `backup_redis.sh`：
```bash
#!/bin/bash
BACKUP_DIR="/path/to/backup/redis"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 创建BGSAVE
redis-cli BGSAVE

# 等待保存完成
sleep 10

# 复制并压缩备份
cp /path/to/redis/backup/dump.rdb $BACKUP_DIR/redis_backup_$TIMESTAMP.rdb
gzip $BACKUP_DIR/redis_backup_$TIMESTAMP.rdb

# 删除7天前的备份
find $BACKUP_DIR -name "redis_backup_*.rdb.gz" -mtime +7 -delete
```

## 5. 数据库监控

### 5.1 PostgreSQL监控

1. 查看数据库状态：
```sql
-- 数据库大小
SELECT pg_size_pretty(pg_database_size('blog_db'));

-- 表大小
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- 活动连接
SELECT * FROM pg_stat_activity;
```

2. 性能监控：
```sql
-- 慢查询
SELECT * FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- 索引使用情况
SELECT * FROM pg_stat_user_indexes;
```

### 5.2 Redis监控

1. 基础监控命令：
```bash
# 查看Redis信息
redis-cli info

# 监控命令执行
redis-cli monitor

# 内存使用情况
redis-cli info memory
```

## 6. 故障恢复

### 6.1 PostgreSQL恢复

1. 从备份恢复：
```bash
# 恢复数据库
gunzip -c backup_file.sql.gz | psql -U blog_user blog_db

# 或使用pg_restore
pg_restore -U blog_user -d blog_db backup_file.dump
```

### 6.2 Redis恢复

1. 从RDB文件恢复：
```bash
# 停止Redis
sudo service redis stop

# 复制备份文件
cp redis_backup.rdb /path/to/redis/dump.rdb

# 启动Redis
sudo service redis start
```

## 7. 安全建议

1. 访问控制：
   - 使用强密码
   - 限制IP访问
   - 使用SSL连接

2. 数据加密：
   - 配置SSL/TLS
   - 加密敏感数据

3. 审计：
   - 启用数据库审计日志
   - 监控异常访问

4. 权限管理：
   - 最小权限原则
   - 定期审查权限

## 8. 维护计划

1. 日常维护：
   - 监控数据库状态
   - 检查备份是否成功
   - 清理过期日志

2. 周期维护：
   - 更新统计信息
   - 整理表空间
   - 检查索引使用情况

3. 定期优化：
   - 分析慢查询
   - 优化数据库配置
   - 更新数据库版本 