"""
聊天功能测试 — 会话管理 + 消息收发
"""
import pytest
import allure


@allure.feature("聊天")
class TestChatSessions:

    @allure.title("创建聊天会话")
    @pytest.mark.smoke
    def test_create(self, client):
        r = client.post("/api/chat/sessions")
        assert r.status_code == 200
        assert r.json()["success"] is True

    @allure.title("列出会话")
    def test_list(self, client):
        r = client.get("/api/chat/sessions")
        assert r.status_code == 200
        assert isinstance(r.json()["sessions"], list)

    @allure.title("删除会话")
    def test_delete(self, client, chat_session_id):
        r = client.delete(f"/api/chat/sessions/{chat_session_id}")
        assert r.status_code == 200


@allure.feature("聊天")
class TestChatMessages:

    @allure.title("发送消息并获取流式回复")
    @pytest.mark.slow
    def test_send_streaming(self, client, chat_session_id):
        r = client.post(
            f"/api/chat/sessions/{chat_session_id}/send?content=hi",
            timeout=60,
        )
        # 流式返回可能是 SSE 格式
        assert r.status_code == 200

    @allure.title("获取消息历史")
    def test_get_messages(self, client, chat_session_id):
        r = client.get(f"/api/chat/sessions/{chat_session_id}/messages")
        assert r.status_code == 200
        assert isinstance(r.json()["messages"], list)
