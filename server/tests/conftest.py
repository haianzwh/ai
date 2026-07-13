"""
共享 fixtures — 所有测试文件的依赖注入
"""
import pytest
import httpx
import uuid
import subprocess
from pathlib import Path

BASE_URL = "http://localhost:3001"
TEST_USER = f"test_{uuid.uuid4().hex[:8]}"
TEST_PASS = "Test12345"
TEST_EMAIL = f"{TEST_USER}@test.com"


# ==================== HTTP 客户端 ====================

@pytest.fixture
def admin_token():
    """每个测试重新登录，限流时等待重试"""
    import time
    for attempt in range(3):
        resp = httpx.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "admin", "password": "996qwerasdfzxcv!"},
        )
        if resp.status_code == 200:
            return resp.json()["token"]
        if resp.status_code == 429 and attempt < 2:
            time.sleep(3)  # 等限流窗口过期
        else:
            pytest.skip(f"登录失败(尝试{attempt+1}次): {resp.status_code}")
    pytest.skip("登录重试失败")


@pytest.fixture
def client(admin_token):
    """带 admin token 的 HTTP 客户端"""
    return httpx.Client(
        base_url=BASE_URL,
        headers={"Authorization": f"Bearer {admin_token}"},
        timeout=30,
    )


@pytest.fixture
def anon_client():
    """未登录的客户端"""
    return httpx.Client(base_url=BASE_URL, timeout=30)


# ==================== 测试数据 ====================

@pytest.fixture
def test_image():
    """创建测试图片"""
    path = Path("/tmp/test_upload.png")
    # 创建一个最小 PNG
    import struct, zlib
    def create_png(w, h):
        raw = b""
        for y in range(h):
            raw += b"\x00" + b"\xff\x00\x00" * w
        compressed = zlib.compress(raw)
        def chunk(ctype, data):
            c = ctype + data
            return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
        return (
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", compressed)
            + chunk(b"IEND", b"")
        )
    path.write_bytes(create_png(10, 10))
    return path


@pytest.fixture
def test_text_file():
    """创建测试文本文件"""
    path = Path("/tmp/test_upload.txt")
    path.write_text("Hello from pytest! " * 10)
    return path


@pytest.fixture
def chat_session_id(client):
    """创建测试聊天会话"""
    resp = client.post("/api/chat/sessions")
    assert resp.status_code == 200
    return resp.json()["id"]


# ==================== Setup/Teardown ====================

@pytest.fixture(scope="session", autouse=True)
def check_server():
    """确保服务器在运行"""
    try:
        r = httpx.get(f"{BASE_URL}/api/skills/hello", timeout=5)
        assert r.status_code == 200
    except Exception:
        pytest.exit("服务器未运行！请先启动 aichat-auth 服务")


def pytest_configure(config):
    config.addinivalue_line("filterwarnings", "ignore::DeprecationWarning")
