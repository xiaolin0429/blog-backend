import os
import sys
import django

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def reset_admin():
    try:
        # 删除所有超级管理员账户
        User.objects.filter(is_superuser=True).delete()
        
        # 创建新的超级管理员
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print(f'Successfully created superuser: {admin.username}')
        print('Password: admin123')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    reset_admin() 