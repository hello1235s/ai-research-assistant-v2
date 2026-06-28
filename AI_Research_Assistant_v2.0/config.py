"""
AI智能科研辅助助手 - 全局配置
方案A+：SQLite专业级改造 | 大学课程作业版
"""

import os

# ========== 应用基础配置 ==========
APP_TITLE = "AI智能科研辅助助手"
APP_ICON = "🔬"
APP_VERSION = "v2.0"

# 开发者信息
DEVELOPER = "张驰"
STUDENT_ID = "202530463528"
CLASS_NAME = "AI与低空技术3班"
COLLEGE = "自动化科学与工程学院"

# ========== 数据库配置 ==========
# SQLite数据库文件路径（自动创建）
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "research_assistant.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# ========== Kimi API 配置 ==========
# 默认API配置（全局兜底）
DEFAULT_API_KEY = "sk-iW9mCrmYz7XcFbzMR0VLlkDLLRHewSpJfTqog3yIHv7DpM3Q"
DEFAULT_MODEL = "kimi-k2.5"
KIMI_BASE_URL = "https://api.moonshot.cn/v1"

# 可用模型列表
AVAILABLE_MODELS = ["kimi-k2.5", "kimi-k2-thinking", "kimi-latest"]

# ========== 安全加密配置 ==========
# AES加密密钥（用于加密用户API Key）
# 注意：生产环境应通过环境变量设置，这里使用固定值方便课程演示
AES_KEY = b"ResearchAssistant2025AESKey!!!"  # 32字节密钥
AES_IV = b"InitVector2025!"  # 16字节IV

# bcrypt密码哈希强度（4-31，越大越慢越安全）
BCRYPT_ROUNDS = 10

# ========== 知识库配置 ==========
KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge_base")

# ========== 数据目录配置 ==========
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ========== 分页配置 ==========
CHAT_HISTORY_PER_PAGE = 20  # 对话历史每页显示条数
REPORT_HISTORY_PER_PAGE = 10  # 报告历史每页显示条数

# ========== 功能开关 ==========
ENABLE_STREAMING = True  # 启用流式输出
ENABLE_KNOWLEDGE_RAG = True  # 启用知识库RAG增强
ENABLE_USAGE_TRACKING = True  # 启用API用量追踪

# ========== 默认System Prompt ==========
DEFAULT_SYSTEM_PROMPT = (
    "你是一名专业的科研助手，擅长编程、数据分析和学术写作。"
    "请用中文回答，回答要准确、清晰、有条理。如果涉及代码，请提供完整的可运行代码。"
)

CHAT_SYSTEM_PROMPT = (
    "你是一名专业的科研助手，擅长回答编程、数学、物理、工程、数据分析、机器学习等领域的问题。"
    "回答要准确、清晰、有条理。如果涉及代码，请提供完整的可运行代码。"
)

CODE_SYSTEM_PROMPT = (
    "你是一名Python编程专家，擅长根据需求生成高质量、可运行的代码。请用中文回答，并生成完整的Python代码。"
)

ANALYSIS_SYSTEM_PROMPT = (
    "你是一名数据分析专家，擅长从数据中提取洞察并给出专业分析建议。请用中文回答。"
)

PAPER_SYSTEM_PROMPT = (
    "你是一名学术论文写作专家，擅长撰写高质量的中英文学术摘要和论文内容。请用中文回答。"
)
