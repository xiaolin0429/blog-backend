# 测试文档

## 1. 测试环境配置

> 注意：所有命令均在项目根目录 `/backend` 下执行

### 1.1 安装测试依赖

```bash
# 进入项目根目录
cd /path/to/backend

# 安装测试依赖
pip install pytest
pip install pytest-django
pip install pytest-cov
pip install pytest-faker
```

### 1.2 配置测试设置

在项目根目录 `/backend/pytest.ini` 文件中配置：

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.test
python_files = tests.py test_*.py *_tests.py
addopts = --cov=apps --cov-report=html
```

## 2. 测试目录结构

```
backend/                   # 项目根目录
├── tests/
│   ├── conftest.py              # 测试配置和通用fixture
│   ├── apps/
│   │   ├── user/               # 用户模块测试
│   │   │   ├── models/        # 模型测试
│   │   │   ├── serializers/   # 序列化器测试
│   │   │   └── views/        # 视图测试
│   │   ├── post/              # 文章模块测试
│   │   │   ├── models/
│   │   │   ├── serializers/
│   │   │   └── views/
│   │   └── plugin/            # 插件模块测试
│   │       ├── models/
│   │       ├── serializers/
│   │       └── views/
│   └── utils/                  # 工具函数测试
```

## 3. 测试用例编写规范

### 3.1 命名规范

- 测试文件：`test_*.py`
- 测试类：`Test*`
- 测试方法：`test_*`

### 3.2 测试类型

1. 单元测试
   - 模型测试
   - 序列化器测试
   - 工具函数测试

2. 集成测试
   - 视图测试
   - API测试

### 3.3 测试用例编写原则

1. 每个测试用例只测试一个功能点
2. 测试用例之间相互独立
3. 使用合适的断言方法
4. 包含正常和异常情况的测试
5. 使用有意义的测试数据

### 3.4 测试用例示例

> 测试文件路径：`/backend/tests/apps/user/models/test_user.py`

```python
@pytest.mark.django_db
class TestUserModel:
    """用户模型测试"""

    def test_create_user(self, user_data):
        """测试创建用户"""
        user = User.objects.create_user(**user_data)
        assert user.username == user_data['username']
        assert user.email == user_data['email']
        assert user.check_password(user_data['password'])

    def test_user_str(self, test_user):
        """测试用户字符串表示"""
        assert str(test_user) == test_user.username
```

## 4. 运行测试

> 所有测试命令均在项目根目录 `/backend` 下执行

### 4.1 运行所有测试

```bash
# 进入项目根目录
cd /path/to/backend

# 运行所有测试
pytest
```

### 4.2 运行特定模块测试

```bash
# 运行用户模块测试
pytest tests/apps/user/

# 运行特定测试文件
pytest tests/apps/user/models/test_user.py

# 运行特定测试类
pytest tests/apps/user/models/test_user.py::TestUserModel

# 运行特定测试方法
pytest tests/apps/user/models/test_user.py::TestUserModel::test_create_user
```

### 4.3 生成测试覆盖率报告

```bash
# 生成HTML格式的覆盖率报告
pytest --cov=apps --cov-report=html

# 报告将生成在 /backend/htmlcov/ 目录下
```

## 5. 测试数据准备

### 5.1 Fixtures

在项目根目录 `/backend/tests/conftest.py` 中定义通用的 fixtures：

```python
@pytest.fixture
def api_client():
    """返回API测试客户端"""
    return APIClient()

@pytest.fixture
def user_data():
    """返回测试用户数据"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test123456'
    }

@pytest.fixture
def test_user(user_data):
    """创建并返回测试用户"""
    return User.objects.create_user(**user_data)

@pytest.fixture
def authenticated_client(api_client, test_user):
    """返回已认证的API测试客户端"""
    api_client.force_authenticate(user=test_user)
    return api_client
```

### 5.2 Factory Boy

在项目根目录 `/backend/tests/factories.py` 中定义测试数据工厂：

```python
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password')
```

## 6. 测试覆盖率要求

1. 模型测试覆盖率 ≥ 90%
2. 序列化器测试覆盖率 ≥ 90%
3. 视图测试覆盖率 ≥ 85%
4. 工具函数测试覆盖率 ≥ 90%
5. 总体测试覆盖率 ≥ 85%

## 7. 持续集成

### 7.1 GitHub Actions 配置

> 配置文件路径：`/backend/.github/workflows/tests.yml`

```yaml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run tests
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
      run: |
        pytest --cov=apps --cov-report=xml
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v2
```

## 8. 测试报告

### 8.1 HTML 报告

运行测试后在项目根目录 `/backend/htmlcov/index.html` 查看详细的覆盖率报告。

### 8.2 控制台报告

```bash
# 在项目根目录下执行
pytest -v
```

### 8.3 JUnit XML 报告

```bash
# 在项目根目录下执行，报告将生成在 /backend/report.xml
pytest --junitxml=report.xml
```
