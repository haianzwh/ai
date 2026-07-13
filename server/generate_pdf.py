#!/usr/bin/env python3
"""生成 AI Chat 架构文档 PDF — 使用 fpdf2 + 文泉驿中文字体"""
from fpdf import FPDF
from pathlib import Path

BASE = Path("/tmp/opencode/ai-chat/server/python_app")
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
OUTPUT = Path("/tmp/opencode/ai-chat/AI_Chat_架构文档.pdf")

def read_code(filename: str) -> list[str]:
    """读取源码并返回行列表"""
    try:
        return (BASE / filename).read_text().splitlines()
    except Exception:
        return [f"# {filename} 不存在"]


class PDF(FPDF):
    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.add_font("ZH", "", FONT_PATH)
        self.add_font("ZH", "B", FONT_PATH)  # fpdf2 自动加粗
        self.set_auto_page_break(True, 18)

    # ====== 工具方法 ======
    def divider(self):
        """章节分割线"""
        self.ln(4)
        x = self.get_x()
        w = self.w - 2 * self.l_margin
        self.set_draw_color(99, 102, 241)
        self.set_line_width(0.4)
        self.line(x, self.get_y(), x + w, self.get_y())
        self.ln(8)

    def divider_dot(self):
        """装饰性分割线"""
        self.ln(3)
        self.set_font("ZH", "", 10)
        self.set_text_color(180, 180, 190)
        self.cell(0, 6, "◆  ◆  ◆", align="C")
        self.ln(8)
        self.set_text_color(45, 52, 54)

    def section_title(self, title: str):
        """大章节标题"""
        self.set_font("ZH", "B", 22)
        self.set_text_color(25, 25, 40)
        self.ln(4)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        # 下划线装饰
        self.set_draw_color(99, 102, 241)
        self.set_line_width(0.8)
        self.line(self.l_margin, self.get_y() + 1, self.l_margin + 60, self.get_y() + 1)
        self.ln(8)

    def sub_title(self, title: str):
        """小标题"""
        self.set_font("ZH", "B", 14)
        self.set_text_color(45, 52, 54)
        self.ln(2)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def body_text(self, text: str):
        """正文"""
        self.set_font("ZH", "", 10)
        self.set_text_color(45, 52, 54)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def code_block(self, lines: list[str], max_lines: int = 0):
        """代码块 — 最多显示 max_lines 行"""
        if max_lines and len(lines) > max_lines:
            lines = lines[:max_lines] + ["... (省略后续代码)"]

        self.set_font("ZH", "", 7.5)
        self.set_fill_color(30, 30, 46)
        self.set_text_color(205, 214, 244)

        for line in lines:
            # 替换特殊字符
            display = line.replace("\t", "    ")[:95]
            self.cell(0, 4.5, "  " + display, new_x="LMARGIN", new_y="NEXT", fill=True)

        self.ln(3)
        self.set_text_color(45, 52, 54)

    def info_table(self, headers: list[str], rows: list[list[str]], col_widths: list[float] = None):
        """表格"""
        if col_widths is None:
            col_widths = [self.w - 2 * self.l_margin - 40] + [40]

        # 表头
        self.set_fill_color(99, 102, 241)
        self.set_text_color(255, 255, 255)
        self.set_font("ZH", "B", 9)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 8, h, border=1, fill=True)
        self.ln()

        # 数据行
        self.set_font("ZH", "", 8.5)
        for ri, row in enumerate(rows):
            if ri % 2 == 0:
                self.set_fill_color(248, 250, 252)
            else:
                self.set_fill_color(255, 255, 255)
            self.set_text_color(45, 52, 54)
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 7, " " + str(cell), border=1, fill=True)
            self.ln()
        self.ln(4)

    def tag(self, text: str, color: tuple = (99, 102, 241)):
        """彩色标签"""
        r, g, b = color
        self.set_font("ZH", "B", 8)
        self.set_text_color(r, g, b)
        self.cell(self.get_string_width(text) + 4, 5, text)

    # ====== 页面 ======
    def cover_page(self):
        """封面"""
        self.add_page()
        self.ln(50)
        self.set_font("ZH", "B", 16)
        self.set_text_color(120, 130, 140)
        self.cell(0, 10, "AI Chat 全栈项目", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

        self.set_font("ZH", "B", 32)
        self.set_text_color(25, 25, 40)
        self.cell(0, 16, "架构文档 & 源码详解", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(8)

        # 装饰线
        self.set_draw_color(99, 102, 241)
        self.set_line_width(0.8)
        xc = self.w / 2
        self.line(xc - 40, self.get_y() + 4, xc + 40, self.get_y() + 4)
        self.ln(18)

        self.set_font("ZH", "", 12)
        self.set_text_color(100, 100, 110)
        self.cell(0, 8, "Python FastAPI  ·  MySQL  ·  Nginx  ·  OpenCode", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)
        self.cell(0, 8, "2026年7月  ·  版本 2.0", align="C", new_x="LMARGIN", new_y="NEXT")

    def toc_page(self):
        """目录"""
        self.add_page()
        self.section_title("目  录")

        items = [
            "系统架构概览",
            "技术栈清单",
            "目录结构",
            "配置中心 — config.py",
            "数据库层 — database.py",
            "认证安全  — auth.py",
            "数据模型 — models.py",
            "认证路由 — routes_auth.py",
            "项目路由 — routes_projects.py",
            "文件下载 — routes_files.py",
            "统计排名 — routes_stats.py",
            "技能插件系统 — skills/",
            "入口文件 — main.py",
            "API 接口速查表",
            "安全特性清单",
        ]
        for i, item in enumerate(items):
            self.set_font("ZH", "", 12)
            self.set_text_color(45, 52, 54)
            num = f"{i+1:02d}"
            self.set_text_color(99, 102, 241)
            self.cell(14, 9, num)
            self.set_text_color(45, 52, 54)
            self.cell(0, 9, item, new_x="LMARGIN", new_y="NEXT")
            # 下划线点
            self.set_draw_color(220, 220, 230)
            self.line(self.l_margin + 14, self.get_y(), self.w - self.r_margin, self.get_y())
            self.ln(2)


pdf = PDF()

# ====== 封面 & 目录 ======
pdf.cover_page()
pdf.toc_page()

# ====== 1. 架构概览 ======
pdf.add_page()
pdf.section_title("01  系统架构概览")
pdf.body_text("整个系统以 Nginx 为统一入口，根据请求路径分发到不同的后端服务。")
pdf.ln(2)

pdf.set_font("ZH", "", 8.5)
arch = [
    " 用户浏览器",
    "     │",
    "     ▼",
    " ┌──────────────────────────────────┐",
    " │  Nginx (端口80)                  │",
    " │  www.zwhnb.top                   │",
    " │                                  │",
    " │  /auth/* ───────► FastAPI :3001  │",
    " │  /api/*              │           │",
    " │  /login.html         │ Python    │",
    " │  /projects.html      │ 后端      │",
    " │  /ranking.html       │           │",
    " │                      ▼           │",
    " │                  ┌─────────┐     │",
    " │                  │ MySQL   │     │",
    " │                  │ aichat  │     │",
    " │                  └─────────┘     │",
    " │                                  │",
    " │  /* ────────────► OpenCode :4096 │",
    " │                      │           │",
    " │                      ▼           │",
    " │                  DeepSeek AI     │",
    " └──────────────────────────────────┘",
]
for line in arch:
    pdf.cell(0, 4, line, new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)

pdf.set_font("ZH", "", 10)
pdf.set_text_color(45, 52, 54)
pdf.body_text("数据流说明：")
bullets = [
    "用户浏览器 → Nginx → FastAPI (3001) 处理认证和业务逻辑",
    "FastAPI → OpenCode (4096) 获取 AI 会话和 Token 统计",
    "FastAPI → MySQL 存储用户、项目归属、统计数据",
    "OpenCode → DeepSeek API 调用云端 AI 模型",
]
for b in bullets:
    pdf.cell(0, 6, "  · " + b, new_x="LMARGIN", new_y="NEXT")
pdf.divider_dot()

# ====== 2. 技术栈 ======
pdf.add_page()
pdf.section_title("02  技术栈清单")
tech_headers = ["层级", "技术", "说明"]
tech_rows = [
    ["后端框架", "FastAPI 0.139", "异步 Web 框架，自动生成 Swagger"],
    ["ASGI 服务器", "Uvicorn 0.51", "高性能异步，支持 uvloop"],
    ["数据库驱动", "aiomysql", "MySQL 异步连接池"],
    ["数据校验", "Pydantic 2", "请求/响应自动类型校验"],
    ["认证", "PyJWT + bcrypt", "JWT 令牌 + 密码哈希"],
    ["HTTP 客户端", "httpx", "异步请求 OpenCode API"],
    ["反向代理", "Nginx", "统一入口、Cookie 鉴权"],
    ["前端", "HTML/CSS/JS", "原生实现，零框架依赖"],
]
pdf.info_table(tech_headers, tech_rows, [30, 45, 85])
pdf.divider_dot()

# ====== 3. 目录结构 ======
pdf.add_page()
pdf.section_title("03  目录结构")
struct_lines = [
    "server/",
    "├── run.sh                       ← systemd 启动脚本",
    "├── .venv/                       ← Python 虚拟环境",
    "└── python_app/                  ← ★ 新版 Python 后端",
    "    ├── main.py                  ← 应用入口 & 路由注册",
    "    ├── config.py                ← 集中配置管理",
    "    ├── database.py              ← 异步数据库连接池",
    "    ├── auth.py                  ← JWT 认证 + 频率限制",
    "    ├── models.py                ← Pydantic 数据模型",
    "    ├── routes_auth.py           ← 登录/注册/忘记密码",
    "    ├── routes_projects.py       ← 项目管理 + 文件搜索",
    "    ├── routes_files.py          ← 文件下载 API",
    "    ├── routes_stats.py          ← Token 排名统计",
    "    └── skills/                  ← 技能插件系统",
    "        ├── base.py              ← 技能抽象基类",
    "        ├── registry.py          ← 技能注册表",
    "        └── hello.py             ← 示例技能",
]
pdf.set_font("ZH", "", 9)
for line in struct_lines:
    pdf.cell(0, 5.5, line, new_x="LMARGIN", new_y="NEXT")
pdf.divider_dot()

# ====== 4-13 各模块源码 ======
modules = [
    ("04", "配置中心 — config.py", "63行", "集中管理所有运行配置", read_code("config.py")),
    ("05", "数据库层 — database.py", "77行", "aiomysql 异步连接池", read_code("database.py")),
    ("06", "认证安全 — auth.py", "129行", "JWT + 频率限制 + 认证中间件", read_code("auth.py")),
    ("07", "数据模型 — models.py", "156行", "Pydantic 请求/响应校验模型", read_code("models.py")),
    ("08", "认证路由 — routes_auth.py", "116行", "登录 / 注册 / 忘记密码", read_code("routes_auth.py")),
    ("09", "项目路由 — routes_projects.py", "173行", "项目CRUD + find搜索文件", read_code("routes_projects.py")),
    ("10", "文件下载 — routes_files.py", "139行", "单文件/打包下载 + 安全白名单", read_code("routes_files.py")),
    ("11", "统计排名 — routes_stats.py", "164行", "Token排名 + 隐私遮蔽", read_code("routes_stats.py")),
]

for num, title, lines, desc, code in modules:
    pdf.add_page()
    pdf.section_title(f"{num}  {title}")
    pdf.body_text(f"{lines}  —  {desc}")
    pdf.ln(2)
    pdf.code_block(code, 45)
    pdf.divider()

# ====== 12. 技能系统 ======
pdf.add_page()
pdf.section_title("12  技能插件系统 — skills/")
pdf.body_text("技能插件是系统的可扩展机制。每个技能是一个 Python 类，继承 BaseSkill，在 on_register() 中注册路由或事件。启动时由 SkillRegistry 统一安装。")

pdf.sub_title("12.1  基类 — base.py (24行)")
pdf.body_text("定义技能的抽象接口，所有自定义技能必须继承此类。")
pdf.code_block(read_code("skills/base.py"), 20)

pdf.sub_title("12.2  注册表 — registry.py (46行)")
pdf.body_text("单例模式，管理所有技能。在 startup 事件中批量安装到 FastAPI app。")
pdf.code_block(read_code("skills/registry.py"), 25)

pdf.sub_title("12.3  示例 — hello.py (20行)")
pdf.body_text("演示如何创建一个技能：定义路由 → 注册到 app。")
pdf.code_block(read_code("skills/hello.py"), 20)

pdf.ln(3)
pdf.set_fill_color(254, 249, 195)
pdf.set_text_color(45, 52, 54)
pdf.set_font("ZH", "B", 10)
pdf.cell(0, 7, "  ★ 添加新技能只需3步：", fill=True, new_x="LMARGIN", new_y="NEXT")
pdf.set_font("ZH", "", 9)
steps = [
    "1. 在 skills/ 目录新建文件 (如 ppt_skill.py)",
    "2. 继承 BaseSkill，实现 on_register(app) 方法",
    "3. 在 main.py 的 lifespan 中注册: registry.register(MySkill())",
]
for s in steps:
    pdf.cell(0, 6, "     " + s, new_x="LMARGIN", new_y="NEXT")
pdf.divider()

# ====== 13. 入口文件 ======
pdf.add_page()
pdf.section_title("13  入口文件 — main.py")
pdf.body_text("155行  —  FastAPI 应用创建、生命周期管理、路由注册、全局错误处理。")
pdf.code_block(read_code("main.py"), 50)
pdf.divider()

# ====== 14. API 速查表 ======
pdf.add_page()
pdf.section_title("14  API 接口速查表")
api_headers = ["方法", "路径", "认证", "说明"]
api_rows = [
    ["POST", "/api/auth/login", "否", "用户登录 → 返回 JWT Token"],
    ["POST", "/api/auth/register", "否", "用户注册 → 自动校验参数"],
    ["POST", "/api/auth/forgot-password", "否", "忘记密码验证身份"],
    ["GET", "/api/auth/me", "是", "获取当前登录用户信息"],
    ["GET", "/api/projects", "是", "获取当前用户的项目列表"],
    ["POST", "/api/projects", "是", "创建新项目 (opencode 会话)"],
    ["GET", "/api/projects/{id}/files", "是", "获取项目生成文件列表"],
    ["GET", "/api/download/file?path=", "是", "下载单个文件 (路径白名单)"],
    ["GET", "/api/download/project/{id}", "是", "按项目打包下载 (tar.gz)"],
    ["GET", "/api/download/latest", "是", "打包下载最新生成文件"],
    ["GET", "/api/stats/ranking", "是", "项目 Token 消耗排名"],
    ["GET", "/api/stats/users", "是", "用户 Token 排名 (含隐私)"],
    ["GET", "/api/skills/hello", "否", "技能插件示例接口"],
]
pdf.info_table(api_headers, api_rows, [16, 58, 10, 76])
pdf.divider_dot()

# ====== 15. 安全特性 ======
pdf.add_page()
pdf.section_title("15  安全特性清单")
sec_headers = ["#", "特性", "实现方式"]
sec_rows = [
    ["1", "JWT 密钥保护", "环境变量 JWT_SECRET，随机 64 字节"],
    ["2", "路径遍历防护", "ALLOWED_DIRS 白名单校验路径"],
    ["3", "命令注入防护", "subprocess.run 参数数组传参"],
    ["4", "数据库密码保护", "环境变量 DB_PASSWORD"],
    ["5", "错误信息不泄露", "统一返回 '服务器内部错误'"],
    ["6", "频率限制", "登录 10次/分 · 注册 5次/分"],
    ["7", "密码 bcrypt 哈希", "加盐 10 rounds"],
    ["8", "请求体大小限制", "最大 100KB 防内存攻击"],
    ["9", "隐私数据遮蔽", "非管理员只能看到自己的信息"],
    ["10", "CSRF 防护", "Cookie 设置 SameSite=Lax"],
    ["11", "临时文件清理", "随机文件名 + 传输后自动删除"],
    ["12", "SQL 注入防护", "参数化查询 (%s 占位符)"],
]
pdf.info_table(sec_headers, sec_rows, [12, 38, 110])
pdf.ln(10)
pdf.divider_dot()

# 尾页
pdf.set_font("ZH", "", 10)
pdf.set_text_color(160, 160, 170)
pdf.cell(0, 8, "— End of Document —", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, "AI Chat 全栈项目 · Python FastAPI 版 · 2026", align="C", new_x="LMARGIN", new_y="NEXT")

# 输出
pdf.output(str(OUTPUT))
print(f"PDF 已生成: {OUTPUT}")
print(f"大小: {OUTPUT.stat().st_size / 1024:.0f} KB · 页数: {pdf.pages_count}")
