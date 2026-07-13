"""
=============================================================================
  AI Chat 后端配置模块
  所有运行配置集中管理，便于后期添加快捷修改
=============================================================================
"""
import os
from pathlib import Path

# 获取环境变量，未设置则使用默认值（生产环境必须设置关键变量）
JWT_SECRET: str = os.getenv("JWT_SECRET", "")
JWT_EXPIRE_HOURS: int = 48  # Token 过期时间（小时）

# MySQL 连接配置（强制使用环境变量以保证安全）
DB_CONFIG: dict = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "db": os.getenv("DB_NAME", "aichat"),
    "charset": "utf8mb4",
    "minsize": 2,   # 连接池最小连接数
    "maxsize": 10,  # 连接池最大连接数
}

# OpenCode 服务地址（用于获取会话和创建项目）
OPENCODE_BASE_URL: str = os.getenv("OPENCODE_URL", "http://localhost:4096")

# 文件管理配置
MAX_FILES: int = 100                        # 每个项目最多保留文件数
FILE_DIR: Path = Path("/tmp/opencode/generated_files")  # 生成文件存储目录
FILE_DIR.mkdir(parents=True, exist_ok=True)  # 确保目录存在

# 文件下载白名单（只有这些目录下的文件允许被下载）
ALLOWED_DIRS: list[Path] = [
    Path("/tmp/opencode/generated_files"),
    Path("/tmp/opencode"),
    Path("/home/ubuntu"),
]

# 文件搜索目录（生成文件的来源目录）
SEARCH_DIRS: list[str] = ["/tmp/opencode", "/home/ubuntu"]

# 文件搜索排除规则（防止源代码文件被收录）
FIND_EXCLUDES: list[str] = [
    "*/node_modules/*", "*/.git/*", "*/ai-chat/*", "*/.cache/*",
    "*/.npm/*", "*/server/*", "*/src/*", "*.js", "*.ts", "*.vue",
    "*.json", "*.css", "*.lock", "*.log", "*.toml", "*.cfg", ".*",
]
# 基准时间文件：只收录比此文件更新的文件
NEWER_REF: str = "/tmp/opencode/ai-chat"

# 频率限制配置
RATE_LIMITS: dict[str, tuple[int, int]] = {
    "login":   (10, 60),   # 登录: 每分钟最多10次
    "register": (5, 60),   # 注册: 每分钟最多5次
    "forgot":   (5, 60),   # 忘记密码: 每分钟最多5次
}

# 在线状态判定：最后活跃时间在此阈值内的用户视为在线（毫秒）
ONLINE_THRESHOLD_MS: int = 30 * 60 * 1000  # 30分钟

# 管理员用户名（可看到所有人的真实信息）
ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
