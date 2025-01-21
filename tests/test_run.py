import os
import sys
import subprocess
import webbrowser
from datetime import datetime
import allure
import pytest

def run_tests():
    """运行所有测试用例并生成报告"""
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 设置输出目录
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    allure_results = os.path.join(project_root, 'allure-results')
    coverage_dir = os.path.join(project_root, 'htmlcov')
    
    # 确保目录存在
    os.makedirs(allure_results, exist_ok=True)
    os.makedirs(coverage_dir, exist_ok=True)

    # 设置测试参数
    pytest_args = [
        '--alluredir', allure_results,
        '--clean-alluredir',
        '-v',
        '--cov=apps',
        '--cov-report=html',
        '--cov-report=term-missing',
        '--cov-branch',
        '--no-cov-on-fail',
        '--tb=short',
        '--strict-markers',
        '--strict-config',
        '-p', 'no:warnings',
        'tests'
    ]

    print("开始运行测试用例...")
    
    try:
        # 运行测试用例
        exit_code = pytest.main(pytest_args)
        
        if exit_code != 0:
            print("测试运行失败！")
            sys.exit(exit_code)
            
        print("\n测试完成！")
        
        # 打开覆盖率报告
        coverage_report = os.path.join(coverage_dir, 'index.html')
        if os.path.exists(coverage_report):
            print("\n正在浏览器中打开覆盖率报告...")
            webbrowser.open(f'file://{coverage_report}')
            
        # 打开 Allure 结果目录
        if os.path.exists(allure_results):
            print(f"\nAllure 测试结果已生成：{allure_results}")
            print("\n您可以使用以下命令查看报告：")
            print(f"allure serve {allure_results}")
            
    except Exception as e:
        print(f"发生错误：{e}")
        sys.exit(1)

if __name__ == '__main__':
    # 添加环境变量
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')
    
    # 运行测试
    run_tests() 