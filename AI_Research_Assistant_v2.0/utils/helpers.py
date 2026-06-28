"""
AI智能科研辅助助手 - 通用工具函数
"""

from datetime import datetime


def estimate_tokens(text: str) -> int:
    """
    估算文本的token数（中文按字，英文按词）
    这是粗略估计，实际值取决于tokenizer
    """
    if not text:
        return 0
    # 中文字符数
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    # 英文单词数（按空格分割）
    non_chinese = ''.join(c if not ('\u4e00' <= c <= '\u9fff') else ' ' for c in text)
    english_words = len(non_chinese.split())
    # 粗略估算：1中文字 ≈ 1.5token，1英文词 ≈ 1.3token
    return int(chinese_chars * 1.5 + english_words * 1.3)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M") -> str:
    """
    格式化日期时间
    """
    if not dt:
        return ""
    return dt.strftime(format_str)


def format_relative_time(dt: datetime) -> str:
    """
    返回相对时间描述（如"3分钟前"）
    """
    if not dt:
        return ""

    now = datetime.now()
    diff = now - dt

    if diff.days > 365:
        return f"{diff.days // 365}年前"
    elif diff.days > 30:
        return f"{diff.days // 30}个月前"
    elif diff.days > 0:
        return f"{diff.days}天前"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600}小时前"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60}分钟前"
    else:
        return "刚刚"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本到指定长度
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小（自动选择单位）
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def safe_json_loads(json_str: str, default=None):
    """
    安全的JSON解析
    """
    import json
    try:
        return json.loads(json_str) if json_str else default
    except Exception:
        return default
