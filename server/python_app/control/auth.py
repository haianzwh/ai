from __future__ import annotations
from ..database import execute_one, execute_write

# 各 provider 的 key 在 users 表中的列名映射
# 扩展新 provider 时在此添加
KEY_COLUMNS: dict[str, str] = {
    "deepseek": "api_key_deepseek",
    "zen": "api_key_zen",
}


async def get_user_api_keys(user_id: str) -> dict[str, str]:
    """获取用户所有已配置的 API Key"""
    u = await execute_one(
        "SELECT api_key_deepseek, api_key_zen FROM users WHERE id=%s",
        (user_id,),
    )
    keys: dict[str, str] = {}
    if u:
        for key_type, col in KEY_COLUMNS.items():
            if u.get(col):
                keys[key_type] = u[col]
    return keys


def mask_key(key: str) -> str:
    """脱敏显示 API Key"""
    if not key:
        return ""
    if len(key) <= 10:
        return key[:3] + "****"
    return key[:6] + "****" + key[-4:]


async def save_user_api_key(user_id: str, key_type: str, api_key: str) -> bool:
    """保存用户 API Key 到数据库"""
    col = KEY_COLUMNS.get(key_type)
    if not col:
        return False
    val = api_key.strip() if api_key else None
    await execute_write(
        f"UPDATE users SET {col}=%s WHERE id=%s",
        (val, user_id),
    )
    return True
