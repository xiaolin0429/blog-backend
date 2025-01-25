#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库初始化脚本
自动检测系统环境，初始化PostgreSQL数据库
"""

import getpass
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import psutil
import psycopg2


class DatabaseInitializer:
    def __init__(self):
        self.system = platform.system().lower()
        self.pg_data_dir = None
        self.pg_bin_dir = None
        self.db_name = "blog_db"
        self.db_user = "blog_user"
        self.db_password = None
        self.init_sql_path = Path(__file__).parent.parent / "docs" / "database_init.sql"

    def get_postgres_path_from_user(self):
        """从用户获取PostgreSQL安装路径"""
        print("\n未能自动检测到PostgreSQL安装位置。")
        print("请手动输入PostgreSQL安装路径。")

        if self.system == "windows":
            print("示例: C:\\Program Files\\PostgreSQL\\14")
            while True:
                path = input("\n请输入PostgreSQL安装目录: ").strip()
                if not path:
                    continue

                bin_dir = os.path.join(path, "bin")
                data_dir = os.path.join(path, "data")

                if not os.path.exists(bin_dir):
                    print(f"错误: 未找到bin目录: {bin_dir}")
                    retry = input("是否重试? (y/n): ").lower()
                    if retry != "y":
                        return False
                    continue

                if not os.path.exists(data_dir):
                    print(f"错误: 未找到data目录: {data_dir}")
                    data_dir = input("请输入data目录的完整路径: ").strip()
                    if not os.path.exists(data_dir):
                        print(f"错误: 无效的data目录: {data_dir}")
                        retry = input("是否重试? (y/n): ").lower()
                        if retry != "y":
                            return False
                        continue

                # 验证是否为有效的PostgreSQL安装
                psql_path = os.path.join(bin_dir, "psql.exe")
                if not os.path.exists(psql_path):
                    print(f"错误: 未找到psql.exe: {psql_path}")
                    retry = input("是否重试? (y/n): ").lower()
                    if retry != "y":
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
                    os.path.join(path, "bin"),
                    path,  # 有时bin文件直接在主目录下
                    os.path.join(path, "pgsql/bin"),
                ]

                bin_dir = None
                for dir in possible_bin_dirs:
                    if os.path.exists(os.path.join(dir, "psql")):
                        bin_dir = dir
                        break

                if not bin_dir:
                    print("错误: 在以下位置均未找到psql执行文件:")
                    for dir in possible_bin_dirs:
                        print("  - {dir}".format(dir=dir))
                    retry = input("是否重试? (y/n): ").lower()
                    if retry != "y":
                        return False
                    continue

                # 对于Linux/Mac，尝试从pg_ctl获取data目录
                try:
                    pg_ctl = os.path.join(bin_dir, "pg_ctl")
                    result = subprocess.check_output([pg_ctl, "status"]).decode()
                    for line in result.split("\n"):
                        if "Data directory" in line:
                            data_dir = line.split(":")[1].strip()
                            break
                    else:
                        data_dir = input("请输入data目录的完整路径: ").strip()
                except:
                    data_dir = input("请输入data目录的完整路径: ").strip()

                if not os.path.exists(data_dir):
                    print(f"错误: 无效的data目录: {data_dir}")
                    retry = input("是否重试? (y/n): ").lower()
                    if retry != "y":
                        return False
                    continue

                self.pg_bin_dir = bin_dir
                self.pg_data_dir = data_dir
                return True

        return False

    def detect_postgres(self):
        """检测 PostgreSQL 安装"""
        print("正在检测 PostgreSQL 安装...")

        # 检查环境变量中的 PostgreSQL 路径
        pg_path = os.environ.get("PGBIN")
        if pg_path:
            print("在环境变量中找到 PostgreSQL: {path}".format(path=pg_path))
            self.pg_bin_dir = pg_path
            return True

        # 在默认位置查找
        default_paths = [
            "/usr/local/pgsql/bin",
            "/usr/local/bin",
            "/usr/bin",
            "C:\\Program Files\\PostgreSQL\\14\\bin",
            "C:\\Program Files\\PostgreSQL\\15\\bin",
            "C:\\Program Files\\PostgreSQL\\16\\bin",
        ]

        for path in default_paths:
            if os.path.exists(path):
                print("在默认位置找到 PostgreSQL: {path}".format(path=path))
                self.pg_bin_dir = path
                return True

        print("未找到 PostgreSQL 安装")
        return False

    def validate_postgres_installation(self):
        """验证PostgreSQL安装的有效性"""
        try:
            # 检查必要的可执行文件
            required_executables = ["psql", "pg_ctl", "pg_dump", "createdb"]
            missing_executables = []

            for exe in required_executables:
                exe_path = os.path.join(self.pg_bin_dir, exe)
                if self.system == "windows":
                    exe_path += ".exe"
                if not os.path.exists(exe_path):
                    missing_executables.append(exe)

            if missing_executables:
                print("错误: 以下PostgreSQL组件未找到:")
                for exe in missing_executables:
                    print(f"  - {exe}")
                return False

            # 验证data目录的权限
            try:
                test_file = os.path.join(self.pg_data_dir, ".test_write")
                with open(test_file, "w") as f:
                    f.write("test")
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
        """检查 PostgreSQL 服务状态"""
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password="postgres",
                host="localhost",
                port="5432",
            )
            conn.close()
            print("PostgreSQL 服务正在运行")
            return True
        except psycopg2.Error:
            print("PostgreSQL 服务未运行")
            return False

    def start_postgres(self):
        """启动PostgreSQL服务"""
        if self.check_postgres_status():
            print("PostgreSQL服务已在运行")
            return

        print("正在启动PostgreSQL服务...")
        try:
            if self.system == "windows":
                subprocess.check_call(
                    [
                        os.path.join(self.pg_bin_dir, "pg_ctl.exe"),
                        "start",
                        "-D",
                        self.pg_data_dir,
                        "-w",
                    ]
                )
            else:
                subprocess.check_call(["pg_ctl", "start", "-D", self.pg_data_dir, "-w"])
            time.sleep(5)  # 等待服务完全启动
            print("PostgreSQL服务已启动")
        except subprocess.CalledProcessError as e:
            print(f"启动PostgreSQL服务失败: {e}")
            sys.exit(1)

    def check_admin_privileges(self):
        """检查是否具有管理员权限"""
        try:
            if self.system == "windows":
                import ctypes

                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except:
            return False

    def check_dependencies(self):
        """检查必要的Python依赖"""
        required_packages = {
            "psycopg2-binary": "2.9.9",  # PostgreSQL适配器
            "pathlib": "1.0.1",  # 路径处理
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
                if pkg_resources.parse_version(
                    current_version
                ) < pkg_resources.parse_version(min_version):
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
        """检查 PostgreSQL 版本"""
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password="postgres",
                host="localhost",
            )
            cur = conn.cursor()
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            cur.close()
            conn.close()

            print("PostgreSQL 版本: {version}".format(version=version))
            return True
        except psycopg2.Error as e:
            print("检查版本失败: {error}".format(error=str(e)))
            return False

    def check_port_availability(self):
        """检查 PostgreSQL 默认端口 (5432) 是否可用"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(("127.0.0.1", 5432))
            sock.close()

            if result == 0:
                print("端口 5432 已被占用")
                return False
            print("端口 5432 可用")
            return True
        except Exception as e:
            print("检查端口时出错: {error}".format(error=str(e)))
            return False

    def check_disk_space(self):
        """检查磁盘空间是否足够"""
        try:
            # 获取当前目录所在磁盘的可用空间（以GB为单位）
            if platform.system() == "Windows":
                free_space = psutil.disk_usage(os.getcwd()).free / (1024 * 1024 * 1024)
            else:
                stat = os.statvfs(os.getcwd())
                free_space = (stat.f_bavail * stat.f_frsize) / (1024 * 1024 * 1024)

            print("可用磁盘空间: {space:.2f} GB".format(space=free_space))

            if free_space < 1:  # 如果可用空间小于1GB
                print("警告: 磁盘空间不足")
                return False
            return True
        except Exception as e:
            print("检查磁盘空间时出错: {error}".format(error=str(e)))
            return False

    def backup_existing_database(self, admin_user, admin_password):
        """备份现有数据库"""
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user=admin_user,
                password=admin_password,
                host="localhost",
            )
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.db_name,))
            if cur.fetchone():
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                backup_name = "{db}_{time}.backup".format(
                    db=self.db_name, time=timestamp
                )
                print("正在备份数据库到: {backup}".format(backup=backup_name))
                # 这里添加备份逻辑
            cur.close()
            conn.close()
        except psycopg2.Error as e:
            print("备份失败: {error}".format(error=str(e)))
            sys.exit(1)

    def get_admin_credentials(self):
        """获取PostgreSQL管理员凭据"""
        print("\n需要PostgreSQL管理员权限来创建数据库和用户。")

        while True:
            admin_user = input("请输入管理员用户名 (默认: postgres): ").strip() or "postgres"
            admin_password = getpass.getpass("请输入管理员密码: ")

            if not admin_password:
                print("错误: 密码不能为空")
                continue

            # 验证凭据
            try:
                check_cmd = [
                    os.path.join(self.pg_bin_dir, "psql")
                    if self.system == "windows"
                    else "psql",
                    "-U",
                    admin_user,
                    "-d",
                    "postgres",
                    "-c",
                    "SELECT 1",
                ]

                env = os.environ.copy()
                env["PGPASSWORD"] = admin_password

                subprocess.check_output(check_cmd, env=env)
                return admin_user, admin_password
            except subprocess.CalledProcessError:
                print("错误: 无效的管理员凭据")
                retry = input("是否重试? (y/n): ").lower()
                if retry != "y":
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
                dbname="postgres",
                user=admin_user,
                password=admin_password,
                host="localhost",
            )
            conn.autocommit = True
            cur = conn.cursor()

            # 检查数据库是否存在
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.db_name,))
            if not cur.fetchone():
                # 验证数据库名是否只包含允许的字符
                if not re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", self.db_name):
                    raise ValueError("数据库名只能包含字母、数字和下划线，且必须以字母或下划线开头")

                # 创建数据库
                create_db_sql = """
                CREATE DATABASE %(db_name)s
                    WITH
                    OWNER = %(owner)s
                    ENCODING = 'UTF8'
                    LC_COLLATE = 'Chinese_China.UTF8'
                    LC_CTYPE = 'Chinese_China.UTF8'
                    TABLESPACE = pg_default
                    CONNECTION LIMIT = -1;
                """
                cur.execute(
                    create_db_sql, {"db_name": self.db_name, "owner": admin_user}
                )
                print("数据库 {name} 创建成功".format(name=self.db_name))
            else:
                print("数据库 {name} 已存在".format(name=self.db_name))

            # 检查用户是否存在
            cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (self.db_user,))
            if not cur.fetchone():
                # 验证用户名是否只包含允许的字符
                if not re.match("^[a-zA-Z_][a-zA-Z0-9_]*$", self.db_user):
                    raise ValueError("用户名只能包含字母、数字和下划线，且必须以字母或下划线开头")

                # 创建用户和设置权限的 SQL 语句
                create_user_sql = """
                CREATE USER %(user)s WITH PASSWORD %(password)s;
                """
                alter_role_sql = """
                ALTER ROLE %(user)s SET client_encoding TO 'utf8';
                ALTER ROLE %(user)s SET default_transaction_isolation TO 'read committed';
                ALTER ROLE %(user)s SET timezone TO 'Asia/Shanghai';
                """
                grant_privileges_sql = """
                GRANT ALL PRIVILEGES ON DATABASE %(db_name)s TO %(user)s;
                """

                # 执行 SQL 语句
                cur.execute(
                    create_user_sql,
                    {"user": self.db_user, "password": self.db_password},
                )
                cur.execute(alter_role_sql, {"user": self.db_user})
                cur.execute(
                    grant_privileges_sql,
                    {"db_name": self.db_name, "user": self.db_user},
                )

                print("用户 {user} 创建成功".format(user=self.db_user))
            else:
                print("用户 {user} 已存在".format(user=self.db_user))

            cur.close()
            conn.close()

            # 连接到新数据库执行初始化脚本
            conn = psycopg2.connect(
                dbname=self.db_name,
                user=admin_user,
                password=admin_password,
                host="localhost",
            )
            conn.autocommit = True
            cur = conn.cursor()

            # 读取并执行初始化SQL脚本
            with open(self.init_sql_path, "r", encoding="utf-8") as f:
                sql_script = f.read()
                # 移除创建数据库和用户的语句
                sql_script = sql_script[sql_script.find("-- 创建扩展") :]
                cur.execute(sql_script)

            cur.close()
            conn.close()
            print("\n数据库初始化完成！")

        except psycopg2.Error as e:
            print("数据库操作失败: {error}".format(error=str(e)))
            sys.exit(1)
        except Exception as e:
            print("发生未知错误: {error}".format(error=str(e)))
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

        print("PostgreSQL已找到并验证:")
        print("  - 执行文件目录: {dir}".format(dir=self.pg_bin_dir))
        print("  - 数据目录: {dir}".format(dir=self.pg_data_dir))

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
            print("\n数据库连接信息:")
            print("  - 数据库名: {name}".format(name=self.db_name))
            print("  - 用户名: {user}".format(user=self.db_user))
            print("  - 密码: {stars}".format(stars="*" * len(self.db_password)))
            print("  - 主机: localhost")
            print("  - 端口: 5432")
        except Exception as e:
            print("创建数据库失败: {error}".format(error=str(e)))
            print("正在回滚更改...")
            # 这里可以添加回滚逻辑
            sys.exit(1)


if __name__ == "__main__":
    try:
        initializer = DatabaseInitializer()
        initializer.run()
    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n发生错误: {e}")
        sys.exit(1)
