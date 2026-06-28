"""
AI智能科研辅助助手 - 输入验证模块
统一处理所有用户输入的校验
"""

import re


def validate_username(username: str) -> tuple:
    """
    验证用户名
    返回: (是否有效, 错误信息)
    """
    if not username:
        return False, "用户名不能为空"
    if len(username) < 3:
        return False, "用户名至少3个字符"
    if len(username) > 20:
        return False, "用户名最多20个字符"
    if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fff]+$', username):
        return False, "用户名只能包含字母、数字、下划线和中文"
    return True, ""


def validate_password(password: str) -> tuple:
    """
    验证密码强度
    返回: (是否有效, 错误信息)
    """
    if not password:
        return False, "密码不能为空"
    if len(password) < 6:
        return False, "密码至少6个字符"
    if len(password) > 50:
        return False, "密码最多50个字符"
    return True, ""


def validate_api_key(api_key: str) -> tuple:
    """
    验证API Key格式
    返回: (是否有效, 错误信息)
    """
    if not api_key:
        return False, "API Key不能为空"
    if not api_key.startswith("sk-"):
        return False, "API Key格式不正确，应以 'sk-' 开头"
    if len(api_key) < 20:
        return False, "API Key长度过短"
    return True, ""


def sanitize_input(text: str, max_length: int = 5000) -> str:
    """
    清理用户输入（防止XSS和注入）
    """
    if not text:
        return ""
    # 截断过长文本
    text = text[:max_length]
    # 移除危险的HTML标签
    text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<iframe.*?>.*?</iframe>', '', text, flags=re.DOTALL | re.IGNORECASE)
    return text


def validate_conversation_title(title: str) -> str:
    """
    清理对话标题
    """
    title = title.strip()
    if not title:
        return "新对话"
    # 移除换行符
    title = title.replace('\n', ' ').replace('\r', '')
    # 截断
    if len(title) > 50:
        title = title[:47] + "..."
    return title
