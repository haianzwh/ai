"""
认证模块测试 — 登录 / 注册 / 忘记密码 / 限流
"""
import pytest
import allure
import httpx

BASE = "http://localhost:3001"


@allure.feature("认证")
@allure.story("登录")
class TestLogin:

    @allure.title("正确密码登录成功")
    @pytest.mark.smoke
    def test_login_ok(self):
        """用户名密码正确 → 返回 token"""
        r = httpx.post(f"{BASE}/api/auth/login", json={
            "username": "admin", "password": "996qwerasdfzxcv!",
        })
        assert r.status_code in [200, 429], f"got {r.status_code}"
        if r.status_code == 200:
            data = r.json()
            assert data["success"] is True
            assert len(data["token"]) > 10

    @allure.title("错误密码登录失败")
    def test_login_wrong_password(self):
        r = httpx.post(f"{BASE}/api/auth/login", json={
            "username": "admin", "password": "wrongwrong",
        })
        assert r.status_code in [401, 429]

    @allure.title("空用户名返回400")
    def test_login_empty_username(self):
        r = httpx.post(f"{BASE}/api/auth/login", json={
            "username": "", "password": "x",
        })
        assert r.status_code in [400, 429]

    @allure.title("登录频率限制")
    @pytest.mark.security
    def test_login_rate_limit(self):
        """连续发 12 次 → 第 11 次应该 429"""
        for i in range(11):
            r = httpx.post(f"{BASE}/api/auth/login", json={
                "username": "admin", "password": "wrong",
            })
        r = httpx.post(f"{BASE}/api/auth/login", json={
            "username": "admin", "password": "wrong",
        })
        assert r.status_code == 429
        assert "频繁" in r.json()["message"]


@allure.feature("认证")
@allure.story("Token验证")
class TestToken:

    @allure.title("Token验证当前用户")
    @pytest.mark.smoke
    def test_me(self, admin_token):
        r = httpx.get(f"{BASE}/api/auth/me", headers={
            "Authorization": f"Bearer {admin_token}",
        })
        assert r.status_code == 200
        assert r.json()["user"]["username"] == "admin"

    @allure.title("无Token返回401")
    def test_no_token(self):
        r = httpx.get(f"{BASE}/api/auth/me")
        assert r.status_code == 401

    @allure.title("伪造Token返回401")
    def test_fake_token(self):
        r = httpx.get(f"{BASE}/api/auth/me", headers={
            "Authorization": "Bearer fake.token.here",
        })
        assert r.status_code == 401


@allure.feature("认证")
@allure.story("注册")
class TestRegister:

    @allure.title("非法用户名 → 400")
    def test_invalid_username(self):
        r = httpx.post(f"{BASE}/api/auth/register", json={
            "username": "a", "password": "pass1234", "email": "a@b.com",
        })
        assert r.status_code in [400, 429]

    @allure.title("非法密码 → 400")
    def test_invalid_password(self):
        r = httpx.post(f"{BASE}/api/auth/register", json={
            "username": "testuser99", "password": "short", "email": "a@b.com",
        })
        assert r.status_code in [400, 429]

    @allure.title("非法邮箱 → 400")
    def test_invalid_email(self):
        r = httpx.post(f"{BASE}/api/auth/register", json={
            "username": "testuser99", "password": "pass1234", "email": "notemail",
        })
        assert r.status_code in [400, 429]

    @allure.title("注册频率限制")
    @pytest.mark.security
    def test_register_rate_limit(self):
        for i in range(6):
            httpx.post(f"{BASE}/api/auth/register", json={
                "username": f"rlim{i}", "password": f"pass{i}000", "email": f"r{i}@t.com",
            })
        r = httpx.post(f"{BASE}/api/auth/register", json={
            "username": "newuser", "password": "pass1234", "email": "n@t.com",
        })
        assert r.status_code == 429


@allure.feature("认证")
@allure.story("忘记密码")
class TestForgotPassword:

    @allure.title("有效用户 → 成功")
    def test_valid(self):
        r = httpx.post(f"{BASE}/api/auth/forgot-password", json={
            "username": "admin", "email": "admin@example.com",
        })
        assert r.status_code == 200

    @allure.title("无效用户 → 404")
    def test_invalid(self):
        r = httpx.post(f"{BASE}/api/auth/forgot-password", json={
            "username": "nobody", "email": "no@no.com",
        })
        assert r.status_code in [404, 429]
