"""
项目管理 & 文件操作测试
"""
import pytest
import allure


@allure.feature("项目")
class TestProjects:

    @allure.title("获取项目列表")
    @pytest.mark.smoke
    def test_list_projects(self, client):
        r = client.get("/api/projects")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert isinstance(data["projects"], list)

    @allure.title("创建新项目")
    def test_create_project(self, client):
        r = client.post("/api/projects")
        assert r.status_code == 200
        assert r.json()["success"] is True
        assert len(r.json()["id"]) > 0

    @allure.title("未登录不能访问项目")
    def test_unauthorized(self, anon_client):
        r = anon_client.get("/api/projects")
        assert r.status_code == 401


@allure.feature("文件")
class TestFiles:

    @allure.title("上传文件成功")
    @pytest.mark.smoke
    def test_upload_text(self, client, test_text_file):
        with open(test_text_file, "rb") as f:
            r = client.post("/api/upload", files={"file": ("test.txt", f, "text/plain")})
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["filename"].endswith("test.txt")

    @allure.title("上传图片成功")
    def test_upload_image(self, client, test_image):
        with open(test_image, "rb") as f:
            r = client.post("/api/upload", files={"file": ("img.png", f, "image/png")})
        assert r.status_code == 200
        assert r.json()["success"] is True

    @allure.title("获取上传文件列表")
    def test_list_uploads(self, client):
        r = client.get("/api/uploads")
        assert r.status_code == 200
        assert "files" in r.json()

    @allure.title("下载已存在文件")
    def test_download_ok(self, client):
        r = client.get("/api/download/file", params={
            "path": "/tmp/opencode/ai-chat/login.html",
        })
        assert r.status_code == 200

    @allure.title("未登录不能下载")
    def test_download_no_auth(self, anon_client):
        r = anon_client.get("/api/download/file", params={
            "path": "/tmp/opencode/ai-chat/login.html",
        })
        assert r.status_code == 401

    @allure.title("路径遍历被阻止")
    @pytest.mark.security
    def test_path_traversal(self, client):
        """尝试读取 /etc/shadow → 403"""
        r = client.get("/api/download/file", params={
            "path": "/etc/shadow",
        })
        assert r.status_code == 403

    @allure.title("不存在的文件 → 404")
    def test_file_not_found(self, client):
        r = client.get("/api/download/file", params={
            "path": "/tmp/opencode/nonexistent_999.txt",
        })
        assert r.status_code == 404

    @allure.title("最新文件打包下载")
    def test_download_latest(self, client):
        r = client.get("/api/download/latest")
        assert r.status_code in [200, 404]  # 可能没有新文件


@allure.feature("文件")
class TestFileSecurity:

    @allure.title("尝试读取 /etc/passwd → 403")
    @pytest.mark.security
    def test_etc_passwd(self, client):
        r = client.get("/api/download/file", params={"path": "/etc/passwd"})
        assert r.status_code == 403

    @allure.title("尝试读取系统文件 → 403")
    @pytest.mark.security
    def test_ssh_key(self, client):
        r = client.get("/api/download/file", params={"path": "/root/.bashrc"})
        assert r.status_code == 403

    @allure.title("尝试路径穿越 .. → 403")
    @pytest.mark.security
    def test_dotdot(self, client):
        r = client.get("/api/download/file", params={
            "path": "/tmp/opencode/../../etc/shadow",
        })
        assert r.status_code == 403
