"""
=============================================================================
  Pydantic 数据模型
  定义所有 API 请求参数和返回数据的类型结构
  FastAPI 会自动根据这些模型校验数据、生成 API 文档
=============================================================================
"""
from __future__ import annotations
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
import re


# ---------- 认证相关模型 ----------

class LoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., min_length=1, max_length=50, examples=["admin"])
    password: str = Field(..., min_length=1, max_length=100, examples=["your_password"])

class RegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., max_length=200)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if len(v) < 3 or len(v) > 20:
            raise ValueError("用户名3-20位")
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError("用户名只能包含字母、数字和下划线")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("密码至少8位")
        if not re.search(r'[a-zA-Z]', v) or not re.search(r'[0-9]', v):
            raise ValueError("密码必须包含字母和数字")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', v):
            raise ValueError("邮箱格式不正确")
        return v

class ForgotPasswordRequest(BaseModel):
    """忘记密码请求"""
    username: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., min_length=1, max_length=200)

class UserInfo(BaseModel):
    """用户信息（返回给客户端）"""
    id: int
    username: str
    email: str

class LoginResponse(BaseModel):
    """登录成功返回"""
    success: bool = True
    token: str
    user: UserInfo


# ---------- 项目相关模型 ----------

class ProjectItem(BaseModel):
    """单个项目信息"""
    id: str
    title: str
    dir: str = ""
    updated: str = ""
    tokens: int = 0

class FileItem(BaseModel):
    """单个文件信息"""
    name: str
    path: str
    size: int
    mtime: str

class ProjectListResponse(BaseModel):
    """项目列表返回"""
    success: bool = True
    projects: list[ProjectItem] = []
    username: str = ""

class ProjectCreateResponse(BaseModel):
    """创建项目返回"""
    success: bool = True
    id: str = ""
    title: str = ""

class FileListResponse(BaseModel):
    """文件列表返回"""
    success: bool = True
    files: list[FileItem] = []


# ---------- 统计排名模型 ----------

class ProjectRankItem(BaseModel):
    """项目排名单项"""
    name: str
    input: int = 0
    output: int = 0
    reasoning: int = 0
    total: int = 0
    sessions: int = 0
    dir: str = ""

class RankingTotals(BaseModel):
    """排名汇总统计"""
    input: int = 0
    output: int = 0
    reasoning: int = 0
    total: int = 0
    sessions: int = 0

class RankingResponse(BaseModel):
    """项目排名返回"""
    success: bool = True
    ranking: list[ProjectRankItem] = []
    totals: RankingTotals = Field(default_factory=RankingTotals)

class UserRankItem(BaseModel):
    """用户排名单项"""
    id: int
    username: str
    email: str
    totalTokens: int = 0
    isMe: bool = False
    isOnline: bool = False
    lastLogin: str = ""

class UserRankingResponse(BaseModel):
    """用户排名返回"""
    success: bool = True
    users: list[UserRankItem] = []
    totalSessions: int = 0
    totalTokens: int = 0
    currentUser: str = ""


# ---------- 通用错误返回 ----------

class ErrorResponse(BaseModel):
    """通用错误"""
    success: bool = False
    message: str = ""
    error: str = ""  # 兼容旧版返回格式
