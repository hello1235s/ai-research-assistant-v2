"""
AI智能科研辅助助手 - 数据库模型定义 (SQLAlchemy)
使用SQLite，零额外依赖，开箱即用
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime,
    ForeignKey, Float, Boolean, JSON, event
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import config
import os

# 创建引擎前确保目录存在
_db_dir = os.path.dirname(config.DATABASE_PATH)
if _db_dir and not os.path.exists(_db_dir):
    os.makedirs(_db_dir, exist_ok=True)

# 创建引擎和基础类
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 20},  # SQLite多线程支持 + 锁定超时
    echo=False  # 生产环境关闭SQL输出
)

Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    """获取数据库会话"""
    try:
        db = SessionLocal()
        return db
    except Exception:
        db.close()
        raise


# ========== 1. 用户表 ==========
class User(Base):
    """用户账户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)  # bcrypt哈希
    api_key_encrypted = Column(Text, nullable=True)  # AES加密后的个人API Key
    default_model = Column(String(30), default="kimi-k2.5")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime, nullable=True)

    # 关联关系
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    paper_projects = relationship("PaperProject", back_populates="user", cascade="all, delete-orphan")
    code_snippets = relationship("CodeSnippet", back_populates="user", cascade="all, delete-orphan")
    analysis_reports = relationship("AnalysisReport", back_populates="user", cascade="all, delete-orphan")
    api_logs = relationship("ApiUsageLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


# ========== 2. 对话会话表 ==========
class Conversation(Base):
    """AI对话会话表"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), default="新对话")
    model = Column(String(30), default="kimi-k2.5")
    system_prompt = Column(Text, nullable=True)
    is_pinned = Column(Boolean, default=False)  # 置顶标记
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关联关系
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.timestamp")

    def __repr__(self):
        return f"<Conversation(id={self.id}, title='{self.title}')>"


# ========== 3. 消息表 ==========
class Message(Base):
    """对话消息记录表"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' / 'assistant' / 'system'
    content = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=True)  # 估算token数
    latency_ms = Column(Integer, nullable=True)  # 响应延迟(毫秒)
    timestamp = Column(DateTime, default=datetime.now)

    # 关联关系
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}')>"


# ========== 4. 论文项目表 ==========
class PaperProject(Base):
    """论文写作项目表"""
    __tablename__ = "paper_projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(300), nullable=False)
    paper_type = Column(String(50), default="本科课程论文")  # 课程论文/毕业设计/学术论文等
    topic = Column(String(300), nullable=True)
    status = Column(String(20), default="进行中")  # 进行中/已完成/已归档
    content = Column(Text, nullable=True)  # 论文内容JSON（各章节）
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关联关系
    user = relationship("User", back_populates="paper_projects")

    def __repr__(self):
        return f"<PaperProject(id={self.id}, title='{self.title[:30]}...')>"


# ========== 5. 代码片段表 ==========
class CodeSnippet(Base):
    """代码片段收藏表"""
    __tablename__ = "code_snippets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    language = Column(String(30), default="python")
    code = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(String(300), nullable=True)  # 逗号分隔的标签
    source = Column(String(200), nullable=True)  # 来源（如AI生成/手动添加）
    created_at = Column(DateTime, default=datetime.now)

    # 关联关系
    user = relationship("User", back_populates="code_snippets")

    def __repr__(self):
        return f"<CodeSnippet(id={self.id}, title='{self.title}')>"


# ========== 6. 数据分析报告表 ==========
class AnalysisReport(Base):
    """数据分析报告归档表"""
    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(200), nullable=False)  # 原始文件名
    file_size = Column(Integer, nullable=True)  # 文件大小(字节)
    row_count = Column(Integer, nullable=True)  # 数据行数
    column_count = Column(Integer, nullable=True)  # 数据列数
    report_content = Column(Text, nullable=True)  # AI生成的分析报告文本
    stats_summary = Column(Text, nullable=True)  # 统计摘要JSON
    chart_paths = Column(Text, nullable=True)  # 图表文件路径（逗号分隔）
    created_at = Column(DateTime, default=datetime.now)

    # 关联关系
    user = relationship("User", back_populates="analysis_reports")

    def __repr__(self):
        return f"<AnalysisReport(id={self.id}, filename='{self.filename}')>"


# ========== 7. API调用日志表 ==========
class ApiUsageLog(Base):
    """API调用用量日志表"""
    __tablename__ = "api_usage_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    endpoint = Column(String(100), nullable=False)  # 调用的端点
    model = Column(String(30), nullable=False)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    latency_ms = Column(Integer, nullable=True)  # 响应延迟
    status = Column(String(20), default="success")  # success/error
    error_msg = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.now)

    # 关联关系
    user = relationship("User", back_populates="api_logs")

    def __repr__(self):
        return f"<ApiUsageLog(id={self.id}, model='{self.model}', status='{self.status}')>"


# ========== 8. 知识库条目表 ==========
class KnowledgeEntry(Base):
    """知识库结构化条目表（支持RAG）"""
    __tablename__ = "knowledge_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False, index=True)  # python_basics / ml / uav 等
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)  # 纯文本内容
    source_file = Column(String(100), nullable=False)  # 来源Markdown文件
    section_path = Column(String(300), nullable=True)  # 章节路径（如 "1.2.3"）
    keywords = Column(String(500), nullable=True)  # 关键词（逗号分隔）
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<KnowledgeEntry(id={self.id}, category='{self.category}', title='{self.title[:30]}...')>"


# ========== 数据库创建函数 ==========
def create_all_tables():
    """创建所有数据表"""
    Base.metadata.create_all(bind=engine)


def drop_all_tables():
    """删除所有数据表（危险操作！）"""
    Base.metadata.drop_all(bind=engine)
