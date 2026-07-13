# AI Chat 接口测试报告

## 📊 测试概览

| 指标 | 数值 |
|------|------|
| 总用例数 | 42 |
| 通过 | 29 ✅ |
| 跳过 (限流) | 13 ⏭️ |
| 失败 | 0 ❌ |

## 🏗️ 测试架构

```
tests/
├── conftest.py          ← 共享 fixtures + 配置
├── pytest.ini           ← pytest 配置 + markers
├── test_auth.py         ← 认证: 登录/注册/限流/Token  (13 cases)
├── test_projects_files.py ← 项目+文件+安全       (15 cases)
├── test_chat.py          ← 聊天: 会话+消息         (5 cases)
└── test_stats_security.py ← 统计+安全完整性        (9 cases)
```

## 🏷️ 测试分层

| Marker | 说明 | 数量 |
|--------|------|------|
| `smoke` | 冒烟测试 | 5 |
| `security` | 安全测试 | 9 |
| `slow` | 慢速测试 | 1 |
| `auth` | 认证测试 | 13 |
| `project` / `file` / `chat` / `stats` | 功能模块测试 | 14 |

## 🚀 运行方式

```bash
# 全部测试
pytest tests/ -v

# 冒烟测试
pytest tests/ -v -m smoke

# 安全测试
pytest tests/ -v -m security

# 生成 Allure 报告
pytest tests/ --alluredir=reports/allure-results
allure generate reports/allure-results -o reports/allure-report
```

## 📋 测试覆盖

| 模块 | 覆盖接口 |
|------|---------|
| 认证 | login, register, forgot-password, me |
| 项目 | list, create |
| 文件 | upload, list, download, path traversal, latest |
| 聊天 | sessions CRUD, send, messages |
| 安全 | SQL注入, XSS, 路径遍历, 限流, 超大请求 |
| 统计 | ranking(daily/all), users, privacy |
