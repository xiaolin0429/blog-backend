#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库初始化脚本
自动检测系统环境，初始化PostgreSQL数据库
"""

import os
import sys
import platform
import subprocess
import psycopg2
from pathlib import Path
import time
import getpass
import re
from datetime import datetime
import shutil

class DatabaseInitializer:
    def __init__(self):
        self.system = platform.system().lower()
        self.pg_data_dir = None
        self.pg_bin_dir = None
        self.db_name = 'blog_db'
        self.db_user = 'blog_user'
        self.db_password = None
        self.init_sql_path = Path(__file__).parent.parent / 'docs' / 'database_init.sql'

    def get_postgres_path_from_user(self):
        """从用户获取PostgreSQL安装路径"""
        print("\n未能自动检测到PostgreSQL安装位置。")
        print("请手动输入PostgreSQL安装路径。")
        
        if self.system == 'windows':
            print("示例: C:\\Program Files\\PostgreSQL\\14")
            while True:
                path = input("\n请输入PostgreSQL安装目录: ").strip()
                if not path:
                    continue
                    
                bin_dir = os.path.join(path, 'bin')
                data_dir = os.path.join(path, 'data')
                
                if not os.path.exists(bin_dir):
                    print(f"错误: 未找到bin目录: {bin_dir}")
                    retry = input("是否重试? (y/n): ").lower()
                    if retry != 'y':
                        return False
                    continue
                    
                if not os.path.exists(data_dir):
                    print(f"错误: 未找到data目录: {data_dir}")
                    data_dir = input("请输入data目录的完整路径: ").strip()
                    if not os.path.exists(data_dir):
                        print(f"错误: 无效的data目录: {data_dir}")
                        retry = input("是否重试? (y/n): ").lower()
                        if retry != 'y':
                            return False
                        continue
                
                # 验证是否为有效的PostgreSQL安装
                psql_path = os.path.join(bin_dir, 'psql.exe')
                if not os.path.exists(psql_path):
                    print(f"错误: 未找到psql.exe: {psql_path}")
                    retry = input("是否重试? (y/n): ").lower()
                    if retry != 'y':
                        return False
                    continue
                
                self.pg_bin_dir = bin_dir
                self.pg_data_dir = data_dir
                return True
        else:
            print("示例: /usr/local/pgsql 或 /usr/lib/postgresql/14")
            while True:
                path = input("\n请输入PostgreSQL安装目录: ").strip()
                if not path:
                    continue
                    
                # 在Linux/Mac上，尝试多个可能的bin目录位置
                possible_bin_dirs = [
                    os.path.join(path, 'bin'),
                    path,  # 有时bin文件直接在主目录下
                    os.path.join(path, 'pgsql/bin')
                ]
                
                bin_dir = None
                for dir in possible_bin_dirs:
                    if os.path.exists(os.path.join(dir, 'psql')):
                        bin_dir = dir
                        break
                
                if not bin_dir:
                    print(f"错误: 在以下位置均未找到psql执行文件:")
                    for dir in possible_bin_dirs:
                        print(f"  - {dir}")
                    retry = input("是否重试? (y/n): ").lower()
                    if retry != 'y':
                        return False
                    continue
                
                # 对于Linux/Mac，尝试从pg_ctl获取data目录
                try:
                    pg_ctl = os.path.join(bin_dir, 'pg_ctl')
                    result = subprocess.check_output([pg_ctl, 'status']).decode()
                    for line in result.split('\n'):
                        if 'Data directory' in line:
                            data_dir = line.split(':')[1].strip()
                            break
                    else:
                        data_dir = input("请输入data目录的完整路径: ").strip()
                except:
                    data_dir = input("请输入data目录的完整路径: ").strip()
                
                if not os.path.exists(data_dir):
                    print(f"错误: 无效的data目录: {data_dir}")
                    retry = input("是否重试? (y/n): ").lower()
                    if retry != 'y':
                        return False
                    continue
                
                self.pg_bin_dir = bin_dir
                self.pg_data_dir = data_dir
                return True
            
        return False

    def detect_postgres(self):
        """检测PostgreSQL安装位置"""
        print("正在检测PostgreSQL安装...")
        
        if self.system == 'windows':
            # 检查常见的PostgreSQL安装路径
            possible_paths = [
                r'C:\Program Files\PostgreSQL',
                r'C:\Program Files (x86)\PostgreSQL',
            ]
            for base_path in possible_paths:
                if os.path.exists(base_path):
                    versions = [d for d in os.listdir(base_path) if d[0].isdigit()]
                    if versions:
                        latest_version = sorted(versions)[-1]
                        self.pg_bin_dir = os.path.join(base_path, latest_version, 'bin')
                        self.pg_data_dir = os.path.join(base_path, latest_version, 'data')
                        return True
        else:
            # Linux/Mac系统通常已添加到PATH
            try:
                pg_ctl = subprocess.check_output(['which', 'pg_ctl']).decode().strip()
                self.pg_bin_dir = os.path.dirname(pg_ctl)
                # 尝试获取数据目录
                result = subprocess.check_output([pg_ctl, 'status']).decode()
                for line in result.split('\n'):
                    if 'Data directory' in line:
                        self.pg_data_dir = line.split(':')[1].strip()
                        return True
            except subprocess.CalledProcessError:
                pass
        
        # 如果自动检测失败，尝试从用户获取路径
        return self.get_postgres_path_from_user()

    def validate_postgres_installation(self):
        """验证PostgreSQL安装的有效性"""
        try:
            # 检查必要的可执行文件
            required_executables = ['psql', 'pg_ctl', 'pg_dump', 'createdb']
            missing_executables = []
            
            for exe in required_executables:
                exe_path = os.path.join(self.pg_bin_dir, exe)
                if self.system == 'windows':
                    exe_path += '.exe'
                if not os.path.exists(exe_path):
                    missing_executables.append(exe)
            
            if missing_executables:
                print("错误: 以下PostgreSQL组件未找到:")
                for exe in missing_executables:
                    print(f"  - {exe}")
                return False
            
            # 验证data目录的权限
            try:
                test_file = os.path.join(self.pg_data_dir, '.test_write')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except (IOError, OSError):
                print(f"错误: 无法写入data目录: {self.pg_data_dir}")
                print("请确保有足够的权限")
                return False
            
            return True
        except Exception as e:
            print(f"验证PostgreSQL安装时出错: {e}")
            return False

    def check_postgres_status(self):
        """检查PostgreSQL服务状态"""
        print("检查PostgreSQL服务状态...")
        
        try:
            if self.system == 'windows':
                status = subprocess.check_output([
                    os.path.join(self.pg_bin_dir, 'pg_ctl.exe'),
                    'status',
                    '-D',
                    self.pg_data_dir
                ], stderr=subprocess.STDOUT).decode()
            else:
                status = subprocess.check_output([
                    'pg_ctl',
                    'status',
                    '-D',
                    self.pg_data_dir
                ], stderr=subprocess.STDOUT).decode()
            return 'server is running' in status.lower()
        except subprocess.CalledProcessError:
            return False

    def start_postgres(self):
        """启动PostgreSQL服务"""
        if self.check_postgres_status():
            print("PostgreSQL服务已在运行")
            return
            
        print("正在启动PostgreSQL服务...")
        try:
            if self.system == 'windows':
                subprocess.check_call([
                    os.path.join(self.pg_bin_dir, 'pg_ctl.exe'),
                    'start',
                    '-D',
                    self.pg_data_dir,
                    '-w'
                ])
            else:
                subprocess.check_call([
                    'pg_ctl',
                    'start',
                    '-D',
                    self.pg_data_dir,
                    '-w'
                ])
            time.sleep(5)  # 等待服务完全启动
            print("PostgreSQL服务已启动")
        except subprocess.CalledProcessError as e:
            print(f"启动PostgreSQL服务失败: {e}")
            sys.exit(1)

    def check_admin_privileges(self):
        """检查是否具有管理员权限"""
        try:
            if self.system == 'windows':
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except:
            return False

    def check_dependencies(self):
        """检查必要的Python依赖"""
        required_packages = {
            'psycopg2-binary': '2.9.9',  # PostgreSQL适配器
            'pathlib': '1.0.1',          # 路径处理
        }
        
        print("检查Python依赖...")
        missing_packages = []
        
        import pkg_resources
        installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
        
        for package, min_version in required_packages.items():
            if package not in installed_packages:
                missing_packages.append(f"{package}>={min_version}")
            else:
                current_version = installed_packages[package]
                if pkg_resources.parse_version(current_version) < pkg_resources.parse_version(min_version):
                    missing_packages.append(f"{package}>={min_version}")
        
        if missing_packages:
            print("错误: 缺少必要的Python依赖:")
            for package in missing_packages:
                print(f"  - {package}")
            print("\n请使用以下命令安装依赖:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
        
        return True

    def check_postgres_version(self):
        """检查PostgreSQL版本"""
        try:
            if self.system == 'windows':
                version_output = subprocess.check_output([
                    os.path.join(self.pg_bin_dir, 'psql.exe'),
                    '--version'
                ]).decode()
            else:
                version_output = subprocess.check_output([
                    'psql',
                    '--version'
                ]).decode()
            
            # 从输出中提取版本号
            version_match = re.search(r'(\d+\.?\d*)', version_output)
            if version_match:
                version = float(version_match.group(1))
                if version < 14.0:
                    print(f"错误: PostgreSQL版本过低 (当前: {version}, 需要: >= 14.0)")
                    return False
                print(f"PostgreSQL版本: {version}")
                return True
            return False
        except Exception as e:
            print(f"检查PostgreSQL版本时出错: {e}")
            return False

    def check_port_availability(self):
        """检查PostgreSQL默认端口(5432)是否可用"""
        import socket
        
        print("检查端口5432状态...")
        
        # 检查PostgreSQL服务状态
        is_running = self.check_postgres_status()
        if is_running:
            print("PostgreSQL服务已在运行")
            return True
        
        # 只有在PostgreSQL服务未运行时才检查端口
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('127.0.0.1', 5432))
            sock.close()
            return True
        except socket.error:
            if is_running:
                # 如果服务在运行，端口被占用是正常的
                return True
            print("错误: 端口5432被其他程序占用")
            print("请确保没有其他应用程序正在使用此端口")
            return False

    def check_disk_space(self):
        """检查磁盘空间是否充足"""
        import shutil
        
        print("检查磁盘空间...")
        
        # 建议的最小空闲空间（1GB）
        MIN_FREE_SPACE = 1024 * 1024 * 1024
        
        try:
            # 获取数据目录所在磁盘的可用空间
            free_space = shutil.disk_usage(self.pg_data_dir).free
            
            if free_space < MIN_FREE_SPACE:
                print(f"错误: 磁盘空间不足")
                print(f"当前可用: {free_space / (1024*1024*1024):.2f} GB")
                print(f"建议最小: 1.00 GB")
                return False
            
            print(f"可用磁盘空间: {free_space / (1024*1024*1024):.2f} GB")
            return True
        except Exception as e:
            print(f"检查磁盘空间时出错: {e}")
            return False

    def backup_existing_database(self, admin_user, admin_password):
        """如果数据库已存在，创建备份"""
        try:
            # 检查数据库是否存在
            check_cmd = [
                os.path.join(self.pg_bin_dir, 'psql') if self.system == 'windows' else 'psql',
                '-U', admin_user,
                '-d', 'postgres',
                '-t', '-c', f"SELECT 1 FROM pg_database WHERE datname = '{self.db_name}'"
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = admin_password
            
            result = subprocess.check_output(check_cmd, env=env).decode().strip()
            
            if result == '1':
                print(f"\n检测到已存在的数据库 {self.db_name}，创建备份...")
                
                # 创建备份目录
                backup_dir = Path('backups')
                backup_dir.mkdir(exist_ok=True)
                
                # 生成备份文件名
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_file = backup_dir / f"{self.db_name}_{timestamp}.sql"
                
                # 执行备份
                dump_cmd = [
                    os.path.join(self.pg_bin_dir, 'pg_dump') if self.system == 'windows' else 'pg_dump',
                    '-U', admin_user,
                    '-d', self.db_name,
                    '-f', str(backup_file)
                ]
                
                subprocess.run(dump_cmd, env=env, check=True)
                print(f"备份已创建: {backup_file}")
                
                return True
        except Exception as e:
            print(f"创建备份时出错: {e}")
            return False
        
        return True

    def get_admin_credentials(self):
        """获取PostgreSQL管理员凭据"""
        print("\n需要PostgreSQL管理员权限来创建数据库和用户。")
        
        while True:
            admin_user = input("请输入管理员用户名 (默认: postgres): ").strip() or 'postgres'
            admin_password = getpass.getpass("请输入管理员密码: ")
            
            if not admin_password:
                print("错误: 密码不能为空")
                continue
            
            # 验证凭据
            try:
                check_cmd = [
                    os.path.join(self.pg_bin_dir, 'psql') if self.system == 'windows' else 'psql',
                    '-U', admin_user,
                    '-d', 'postgres',
                    '-c', 'SELECT 1'
                ]
                
                env = os.environ.copy()
                env['PGPASSWORD'] = admin_password
                
                subprocess.check_output(check_cmd, env=env)
                return admin_user, admin_password
            except subprocess.CalledProcessError:
                print("错误: 无效的管理员凭据")
                retry = input("是否重试? (y/n): ").lower()
                if retry != 'y':
                    sys.exit(1)
                continue

    def get_blog_credentials(self):
        """获取博客数据库用户密码"""
        while True:
            password = getpass.getpass("\n请输入要设置的数据库密码: ")
            if not password:
                print("错误: 密码不能为空")
                continue
            
            confirm = getpass.getpass("请再次输入密码: ")
            if password != confirm:
                print("错误: 两次输入的密码不匹配")
                continue
            
            return password

    def create_database(self, admin_user, admin_password):
        """创建数据库和用户"""
        print("\n正在创建数据库和用户...")
        
        try:
            # 连接到默认数据库
            conn = psycopg2.connect(
                dbname='postgres',
                user=admin_user,
                password=admin_password,
                host='localhost'
            )
            conn.autocommit = True
            cur = conn.cursor()

            # 检查数据库是否存在
            cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{self.db_name}'")
            if not cur.fetchone():
                # 创建数据库
                cur.execute(f"""
                CREATE DATABASE {self.db_name}
                    WITH 
                    OWNER = {admin_user}
                    ENCODING = 'UTF8'
                    LC_COLLATE = 'Chinese_China.UTF8'
                    LC_CTYPE = 'Chinese_China.UTF8'
                    TABLESPACE = pg_default
                    CONNECTION LIMIT = -1;
                """)
                print(f"数据库 {self.db_name} 创建成功")
            else:
                print(f"数据库 {self.db_name} 已存在")

            # 检查用户是否存在
            cur.execute(f"SELECT 1 FROM pg_roles WHERE rolname = '{self.db_user}'")
            if not cur.fetchone():
                # 创建用户
                cur.execute(f"""
                CREATE USER {self.db_user} WITH PASSWORD '{self.db_password}';
                ALTER ROLE {self.db_user} SET client_encoding TO 'utf8';
                ALTER ROLE {self.db_user} SET default_transaction_isolation TO 'read committed';
                ALTER ROLE {self.db_user} SET timezone TO 'Asia/Shanghai';
                GRANT ALL PRIVILEGES ON DATABASE {self.db_name} TO {self.db_user};
                """)
                print(f"用户 {self.db_user} 创建成功")
            else:
                print(f"用户 {self.db_user} 已存在")

            cur.close()
            conn.close()

            # 连接到新数据库执行初始化脚本
            conn = psycopg2.connect(
                dbname=self.db_name,
                user=admin_user,
                password=admin_password,
                host='localhost'
            )
            conn.autocommit = True
            cur = conn.cursor()

            # 读取并执行初始化SQL脚本
            with open(self.init_sql_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
                # 移除创建数据库和用户的语句
                sql_script = sql_script[sql_script.find('-- 创建扩展'):]
                cur.execute(sql_script)

            cur.close()
            conn.close()
            print("\n数据库初始化完成！")
            
        except psycopg2.Error as e:
            print(f"数据库操作失败: {e}")
            sys.exit(1)

    def run(self):
        """运行初始化流程"""
        print("=== 博客系统数据库初始化工具 ===\n")
        
        # 前置检查
        if not self.check_admin_privileges():
            print("错误: 需要管理员权限")
            sys.exit(1)
        
        if not self.check_dependencies():
            sys.exit(1)
        
        if not self.detect_postgres():
            print("未能找到有效的PostgreSQL安装")
            sys.exit(1)
        
        if not self.validate_postgres_installation():
            print("PostgreSQL安装验证失败")
            sys.exit(1)
        
        print(f"PostgreSQL已找到并验证:")
        print(f"  - 执行文件目录: {self.pg_bin_dir}")
        print(f"  - 数据目录: {self.pg_data_dir}")
        
        if not self.check_postgres_version():
            sys.exit(1)
        
        # 检查端口和服务状态
        port_status = self.check_port_availability()
        if not port_status and not self.check_postgres_status():
            # 只有当端口被占用且PostgreSQL服务未运行时才退出
            sys.exit(1)
        
        if not self.check_disk_space():
            sys.exit(1)
        
        self.start_postgres()
        
        admin_user, admin_password = self.get_admin_credentials()
        
        # 如果数据库存在，先创建备份
        self.backup_existing_database(admin_user, admin_password)
        
        self.db_password = self.get_blog_credentials()
        
        try:
            self.create_database(admin_user, admin_password)
            print("\n数据库初始化成功完成！")
            print(f"\n数据库连接信息:")
            print(f"  - 数据库名: {self.db_name}")
            print(f"  - 用户名: {self.db_user}")
            print(f"  - 密码: {'*' * len(self.db_password)}")
            print(f"  - 主机: localhost")
            print(f"  - 端口: 5432")
        except Exception as e:
            print(f"创建数据库失败: {e}")
            print("正在回滚更改...")
            # 这里可以添加回滚逻辑
            sys.exit(1)

if __name__ == '__main__':
    try:
        initializer = DatabaseInitializer()
        initializer.run()
    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n发生错误: {e}")
        sys.exit(1) 