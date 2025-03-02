import allure
import pytest


def pytest_collection_modifyitems(items):
    """
    为测试用例添加Allure类别标记
    """
    for item in items:
        # 检查测试项是否有标记
        for marker in item.iter_markers():
            if marker.name in [
                "user",
                "post",
                "comment",
                "category",
                "tag",
                "plugin",
                "backup",
                "core",
                "overview",
            ]:
                # 根据标记名称设置不同的类别
                if marker.name == "user":
                    item.add_marker(allure.label("epic", "用户管理"))
                elif marker.name == "post":
                    item.add_marker(allure.label("epic", "文章管理"))
                elif marker.name == "comment":
                    item.add_marker(allure.label("epic", "评论管理"))
                elif marker.name == "category":
                    item.add_marker(allure.label("epic", "分类管理"))
                elif marker.name == "tag":
                    item.add_marker(allure.label("epic", "标签管理"))
                elif marker.name == "plugin":
                    item.add_marker(allure.label("epic", "插件管理"))
                elif marker.name == "backup":
                    item.add_marker(allure.label("epic", "备份管理"))
                elif marker.name == "core":
                    item.add_marker(allure.label("epic", "核心功能"))
                elif marker.name == "overview":
                    item.add_marker(allure.label("epic", "系统概览"))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    为测试报告添加Allure类别信息
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        # 检查测试项是否有标记
        for marker in item.iter_markers():
            if marker.name in [
                "user",
                "post",
                "comment",
                "category",
                "tag",
                "plugin",
                "backup",
                "core",
                "overview",
            ]:
                # 添加测试类别信息到报告
                if marker.name == "user":
                    report.test_metadata = {"类别": "用户管理"}
                elif marker.name == "post":
                    report.test_metadata = {"类别": "文章管理"}
                elif marker.name == "comment":
                    report.test_metadata = {"类别": "评论管理"}
                elif marker.name == "category":
                    report.test_metadata = {"类别": "分类管理"}
                elif marker.name == "tag":
                    report.test_metadata = {"类别": "标签管理"}
                elif marker.name == "plugin":
                    report.test_metadata = {"类别": "插件管理"}
                elif marker.name == "backup":
                    report.test_metadata = {"类别": "备份管理"}
                elif marker.name == "core":
                    report.test_metadata = {"类别": "核心功能"}
                elif marker.name == "overview":
                    report.test_metadata = {"类别": "系统概览"}
