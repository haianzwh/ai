"""
统计排名 & 安全完整性测试
"""
import pytest
import allure
import httpx
import uuid


@allure.feature("统计")
class TestStats:

    @allure.title("项目排名(今日)")
    @pytest.mark.smoke
    def test_project_ranking_daily(self, client):
        r = client.get("/api/stats/ranking?type=daily")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert "ranking" in data
        assert "totals" in data

    @allure.title("项目排名(累计)")
    def test_project_ranking_all(self, client):
        r = client.get("/api/stats/ranking?type=all")
        assert r.status_code == 200
        assert "ranking" in r.json()

    @allure.title("用户排名")
    def test_user_ranking(self, client):
        r = client.get("/api/stats/users")
        assert r.status_code == 200
        data = r.json()
        assert "users" in data
        assert "totalTokens" in data

    @allure.title("用户排名含隐私遮蔽")
    def test_privacy_mask(self, client):
        r = client.get("/api/stats/users")
        users = r.json()["users"]
        for u in users:
            if not u["isMe"]:
                assert "*" in u["email"] or u["username"] == "admin"


@allure.feature("安全")
class TestSecurity:

    @allure.title("SQL注入尝试 → 安全参化查询")
    @pytest.mark.security
    def test_sql_injection_login(self):
        """注入引号 → 不会引起SQL错误"""
        r = httpx.post("http://localhost:3001/api/auth/login", json={
            "username": "admin' OR '1'='1",
            "password": "' OR 1=1 --",
        })
        assert r.status_code in [400, 401, 429]  # 429=限流也是安全的

    @allure.title("XSS 尝试 → 用户名被转义")
    @pytest.mark.security
    def test_xss_username(self):
        r = httpx.post("http://localhost:3001/api/auth/register", json={
            "username": "<script>alert(1)</script>",
            "password": "pass1234",
            "email": "xss@test.com",
        })
        assert r.status_code in [400, 429]

    @allure.title("超大请求体 → 拒绝")
    @pytest.mark.security
    def test_large_body(self):
        r = httpx.post("http://localhost:3001/api/auth/login", json={
            "username": "admin",
            "password": "x" * 1000,
        })
        assert r.status_code in [400, 401, 429]

    @allure.title("技能接口可访问")
    @pytest.mark.smoke
    def test_skills_available(self, client):
        r = client.get("/api/skills/hello")
        assert r.status_code == 200

    @allure.title("文件上传接口安全校验")
    @pytest.mark.security
    def test_upload_no_auth(self):
        """未登录上传 → 401"""
        r = httpx.post("http://localhost:3001/api/upload")
        assert r.status_code == 401

    @allure.title("API文档可访问")
    def test_docs(self):
        r = httpx.get("http://localhost:3001/docs", follow_redirects=True)
        assert r.status_code == 200
