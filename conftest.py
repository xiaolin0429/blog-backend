import os

import allure
import pytest


# 设置Allure环境信息
@pytest.fixture(scope="session", autouse=True)
def allure_environment_info(request):
    """
    设置Allure环境信息
    """
    allure_dir = request.config.getoption("--alluredir")
    if allure_dir:
        env_file_path = os.path.join(allure_dir, "environment.properties")
        with open(env_file_path, "w") as f:
            f.write(f"Python.Version={os.environ.get('PYTHON_VERSION', '3.12.9')}\n")
            f.write("Django.Version=4.2.18\n")
            f.write("DRF.Version=3.15.2\n")
            f.write(f"OS={os.environ.get('OS', 'macOS')}\n")
            f.write("Runner=pytest\n")


# 导入测试钩子
from tests.allure_hooks import *
