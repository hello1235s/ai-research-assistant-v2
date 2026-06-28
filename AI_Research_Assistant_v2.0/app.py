"""
AI智能科研辅助助手 v2.0 - 主入口文件
基于Kimi大模型 + Streamlit + SQLite 的智能科研辅助平台

升级亮点：
- SQLite数据库存储（对话历史、用户系统、代码收藏、报告归档）
- 用户注册/登录/登出（bcrypt密码加密）
- API Key安全存储（AES加密）
- 知识库结构化检索（5大领域Markdown导入数据库）
- 模块化架构（职责分离，代码清晰）
- ChatGPT风格深色主题 + 丝滑交互动画

开发者：张驰 | 学号：202530463528 | AI与低空技术3班
"""

import streamlit as st
import os
import sys

# 确保模块路径正确
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入配置
import config

# 导入模块
from modules.auth import (
    init_auth_state, is_logged_in, show_login_page, show_register_page,
    show_sidebar_auth, logout_user, get_current_username
)
from modules.chat import show_chat_page, show_conversation_sidebar
from modules.code_assist import show_code_assist_page
from modules.data_analysis import show_data_analysis_page
from modules.paper_writing import show_paper_writing_page
from modules.knowledge_base import show_knowledge_base_page
from modules.usage_stats import show_usage_stats_page
from database.models import create_all_tables


# ========== 全局CSS样式 (ChatGPT Pro级深色主题) ==========
CUSTOM_CSS = """
<style>
    /* ========== CSS变量系统 ========== */
    :root {
        --bg-primary: #343541;
        --bg-secondary: #444654;
        --bg-sidebar: #202123;
        --bg-card: #40414f;
        --bg-card-hover: #4d4d5f;
        --bg-input: #40414f;
        --bg-hover: rgba(255,255,255,0.05);
        --bg-active: rgba(25,195,125,0.1);
        --accent-primary: #19c37d;
        --accent-primary-hover: #15a66a;
        --accent-primary-glow: rgba(25,195,125,0.3);
        --accent-blue: #3b82f6;
        --accent-blue-glow: rgba(59,130,246,0.3);
        --accent-orange: #f59e0b;
        --accent-red: #ef4444;
        --text-primary: #ececf1;
        --text-secondary: #c5c5d2;
        --text-muted: #8e8ea0;
        --text-inverse: #ffffff;
        --border-color: #4d4d4f;
        --border-color-hover: #565869;
        --border-radius-sm: 8px;
        --border-radius-md: 12px;
        --border-radius-lg: 16px;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.2);
        --shadow-md: 0 4px 16px rgba(0,0,0,0.3);
        --shadow-lg: 0 8px 32px rgba(0,0,0,0.4);
        --shadow-glow: 0 0 20px var(--accent-primary-glow);
        --transition-fast: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
        --transition-base: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        --transition-slow: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* ========== 全局基础重置 ========== */
    .stApp {
        background: var(--bg-primary) !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif !important;
    }
    .stApp, .stApp p, .stApp div, .stApp span, .stApp label,
    .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown div,
    .stTextInput label, .stTextArea label, .stSelectbox label,
    .stFileUploader label, .stNumberInput label, .stSlider label,
    .stRadio label, .stCheckbox label {
        color: var(--text-primary) !important;
    }

    /* ========== 标题区域 ========== */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: var(--text-inverse);
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, #ffffff 0%, #c5c5d2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .subtitle {
        font-size: 1.15rem;
        color: var(--text-muted);
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 400;
        letter-spacing: 0.3px;
    }

    /* ========== 信息卡片系统 ========== */
    .info-box, .success-box, .warning-box, .feature-card {
        padding: 24px 28px;
        border-radius: var(--border-radius-lg);
        margin: 16px 0;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        transition: var(--transition-base);
        position: relative;
        overflow: hidden;
    }
    .info-box::before, .success-box::before, .warning-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(255,255,255,0.03) 0%, transparent 50%);
        pointer-events: none;
    }
    .info-box {
        border-left: 4px solid var(--accent-blue);
    }
    .success-box {
        border-left: 4px solid var(--accent-primary);
    }
    .warning-box {
        border-left: 4px solid var(--accent-orange);
    }
    .info-box:hover, .success-box:hover, .warning-box:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-md);
        border-color: var(--border-color-hover);
    }
    .info-box:hover {
        border-color: var(--accent-blue);
        box-shadow: 0 8px 24px var(--accent-blue-glow);
    }
    .success-box:hover {
        border-color: var(--accent-primary);
        box-shadow: 0 8px 24px var(--accent-primary-glow);
    }
    .feature-card {
        text-align: center;
        padding: 32px 24px;
    }
    .feature-card:hover {
        transform: translateY(-6px);
        box-shadow: var(--shadow-lg);
        border-color: var(--accent-primary);
    }
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 16px;
        display: block;
    }
    .feature-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-inverse);
        margin-bottom: 8px;
    }
    .feature-desc {
        font-size: 0.9rem;
        color: var(--text-muted);
        line-height: 1.5;
    }

    /* ========== Tab 标签系统 ========== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        padding: 6px;
        background: rgba(64,65,79,0.6);
        border-radius: var(--border-radius-md);
        border: 1px solid var(--border-color);
        backdrop-filter: blur(10px);
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        white-space: pre-wrap;
        background: transparent;
        border-radius: var(--border-radius-sm);
        padding: 8px 20px;
        font-weight: 500;
        transition: var(--transition-base);
        color: var(--text-muted);
        border: 2px solid transparent;
        letter-spacing: 0.2px;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--bg-hover);
        color: var(--text-primary);
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: var(--accent-primary);
        color: #ffffff;
        box-shadow: 0 2px 12px var(--accent-primary-glow);
        font-weight: 600;
    }

    /* ========== 侧边栏美化 ========== */
    [data-testid="stSidebar"] {
        background: var(--bg-sidebar) !important;
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label {
        color: var(--text-primary) !important;
    }
    [data-testid="stSidebar"] .stInfo {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: var(--border-radius-md) !important;
        color: var(--text-primary) !important;
    }

    /* ========== 按钮系统 ========== */
    .stButton > button {
        border-radius: var(--border-radius-md) !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: var(--transition-base) !important;
        border: none !important;
        background: var(--accent-primary) !important;
        color: #ffffff !important;
        position: relative;
        overflow: hidden;
        letter-spacing: 0.3px;
    }
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        background: rgba(255,255,255,0.15);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        transition: width 0.5s ease, height 0.5s ease;
    }
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }
    .stButton > button:hover {
        background: var(--accent-primary-hover) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px var(--accent-primary-glow) !important;
    }
    .stButton > button:active {
        transform: translateY(0) scale(0.98) !important;
    }

    /* ========== 输入框系统 ========== */
    .stTextInput > div > div,
    .stTextArea > div > div,
    .stSelectbox > div > div {
        border-radius: var(--border-radius-md) !important;
        border: 1.5px solid var(--border-color) !important;
        background: var(--bg-input) !important;
        color: var(--text-primary) !important;
        transition: var(--transition-base) !important;
    }
    .stTextInput > div > div:focus-within,
    .stTextArea > div > div:focus-within,
    .stSelectbox > div > div:focus-within {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 3px var(--accent-primary-glow), var(--shadow-sm) !important;
        transform: translateY(-1px) !important;
    }
    .stTextInput input, .stTextArea textarea {
        color: var(--text-primary) !important;
        font-size: 0.95rem !important;
    }
    .stTextArea textarea {
        line-height: 1.6 !important;
    }

    /* 文件上传器 */
    .stFileUploader > div > div {
        background: var(--bg-card) !important;
        border: 2px dashed var(--border-color) !important;
        border-radius: var(--border-radius-lg) !important;
        color: var(--text-secondary) !important;
        transition: var(--transition-base) !important;
        padding: 24px !important;
    }
    .stFileUploader > div > div:hover {
        border-color: var(--accent-primary) !important;
        background: var(--bg-active) !important;
    }

    /* ========== 页脚 ========== */
    .footer-text {
        text-align: center;
        color: var(--text-muted);
        font-size: 0.85rem;
        padding: 2rem 0;
        border-top: 1px solid var(--border-color);
        margin-top: 3rem;
    }

    /* ========== 分割线 ========== */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        margin: 2.5rem 0;
    }

    /* ========== 表格系统 ========== */
    table {
        border-radius: var(--border-radius-lg) !important;
        overflow: hidden !important;
        border: 1px solid var(--border-color) !important;
        box-shadow: var(--shadow-sm);
    }
    th {
        background: linear-gradient(180deg, #2a2b36, #202123) !important;
        color: var(--text-inverse) !important;
        font-weight: 600 !important;
        padding: 14px 16px !important;
        border-bottom: 2px solid var(--border-color) !important;
    }
    td {
        padding: 12px 16px !important;
        border-bottom: 1px solid rgba(77,77,79,0.5) !important;
        color: var(--text-primary) !important;
        transition: background 0.15s ease;
    }
    tr:hover td {
        background: rgba(255,255,255,0.03) !important;
    }
    tr:nth-child(even) td {
        background: rgba(255,255,255,0.015) !important;
    }

    /* ========== 聊天消息 ========== */
    .stChatMessage {
        border-radius: var(--border-radius-lg) !important;
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        margin: 8px 0 !important;
        transition: var(--transition-base) !important;
    }
    .stChatMessage:hover {
        border-color: var(--border-color-hover) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    .stChatMessage [data-testid="stChatMessageContent"] {
        color: var(--text-primary) !important;
        line-height: 1.7 !important;
    }

    /* ========== 聊天输入框 ========== */
    .stChatInputContainer {
        border-radius: var(--border-radius-lg) !important;
        border: 1.5px solid var(--border-color) !important;
        background: var(--bg-card) !important;
        box-shadow: var(--shadow-md) !important;
    }
    .stChatInputContainer:focus-within {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 3px var(--accent-primary-glow), var(--shadow-md) !important;
    }

    /* ========== 折叠面板 ========== */
    .stExpander > div > div:first-child {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--border-radius-md) !important;
        transition: var(--transition-fast) !important;
    }
    .stExpander > div > div:first-child:hover {
        background: var(--bg-card-hover) !important;
        border-color: var(--border-color-hover) !important;
    }
    .stExpander [data-testid="stExpanderDetails"] {
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-top: none !important;
        border-radius: 0 0 var(--border-radius-md) var(--border-radius-md) !important;
    }

    /* ========== 选择框 ========== */
    .stSelectbox [data-baseweb="select"] {
        transition: var(--transition-fast) !important;
    }
    div[role="listbox"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--border-radius-md) !important;
        box-shadow: var(--shadow-lg) !important;
    }
    div[role="option"] {
        color: var(--text-primary) !important;
        transition: background 0.15s ease;
    }
    div[role="option"]:hover {
        background: var(--bg-hover) !important;
    }

    /* ========== 滚动条美化 ========== */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }

    /* ========== 动画关键帧 ========== */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes scaleIn {
        from { opacity: 0; transform: scale(0.92); }
        to { opacity: 1; transform: scale(1); }
    }
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 0 0 rgba(25,195,125,0); }
        50% { box-shadow: 0 0 24px 4px rgba(25,195,125,0.25); }
    }
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    @keyframes typeCursor {
        0%, 100% { opacity: 1; }
        50% { opacity: 0; }
    }
    @keyframes borderGlow {
        0%, 100% { border-color: var(--border-color); }
        50% { border-color: var(--accent-primary); }
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* ========== 动画应用类 ========== */
    .anim-fade-in {
        animation: fadeIn 0.8s ease-out forwards;
        opacity: 0;
    }
    .anim-fade-in-up {
        animation: fadeInUp 0.7s cubic-bezier(0.22, 1, 0.36, 1) forwards;
        opacity: 0;
    }
    .anim-scale-in {
        animation: scaleIn 0.5s cubic-bezier(0.22, 1, 0.36, 1) forwards;
        opacity: 0;
    }
    .anim-slide-right {
        animation: slideInRight 0.6s cubic-bezier(0.22, 1, 0.36, 1) forwards;
        opacity: 0;
    }
    .anim-float {
        animation: float 4s ease-in-out infinite;
    }
    .anim-pulse-glow {
        animation: pulseGlow 3s ease-in-out infinite;
    }
    .anim-border-glow {
        animation: borderGlow 3s ease-in-out infinite;
    }

    .anim-delay-1 { animation-delay: 0.1s; }
    .anim-delay-2 { animation-delay: 0.2s; }
    .anim-delay-3 { animation-delay: 0.3s; }
    .anim-delay-4 { animation-delay: 0.4s; }
    .anim-delay-5 { animation-delay: 0.5s; }
    .anim-delay-6 { animation-delay: 0.6s; }
    .anim-delay-7 { animation-delay: 0.7s; }
    .anim-delay-8 { animation-delay: 0.8s; }

    /* ========== 认证页面 ========== */
    .auth-page {
        max-width: 440px;
        margin: 3rem auto;
        padding: 2.5rem;
        background: linear-gradient(145deg, #40414f, #3a3b47);
        border-radius: var(--border-radius-lg);
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
    }
    .auth-page::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(25,195,125,0.03) 0%, transparent 70%);
        pointer-events: none;
    }
    .auth-title {
        text-align: center;
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--text-inverse);
        margin-bottom: 2rem;
        letter-spacing: -0.3px;
    }
    .auth-subtitle {
        text-align: center;
        font-size: 0.9rem;
        color: var(--text-muted);
        margin-bottom: 1.5rem;
    }
    .auth-divider {
        display: flex;
        align-items: center;
        margin: 1.5rem 0;
        color: var(--text-muted);
        font-size: 0.85rem;
    }
    .auth-divider::before,
    .auth-divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
    }
    .auth-divider span {
        padding: 0 12px;
    }

    /* ========== 用户卡片 ========== */
    .user-card {
        background: linear-gradient(135deg, #40414f, #3c3d4a);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius-lg);
        padding: 18px;
        margin: 12px 0;
        transition: var(--transition-base);
    }
    .user-card:hover {
        border-color: var(--accent-primary);
        box-shadow: 0 4px 16px rgba(25,195,125,0.15);
    }

    /* ========== 统计卡片 ========== */
    .stat-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius-md);
        padding: 20px;
        text-align: center;
        transition: var(--transition-base);
    }
    .stat-card:hover {
        transform: translateY(-4px);
        border-color: var(--accent-blue);
        box-shadow: 0 8px 24px var(--accent-blue-glow);
    }
    .stat-number {
        font-size: 2rem;
        font-weight: 800;
        color: var(--accent-primary);
        display: block;
    }
    .stat-label {
        font-size: 0.85rem;
        color: var(--text-muted);
        margin-top: 4px;
    }

    /* ========== 快捷按钮网格 ========== */
    .quick-btn-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin: 16px 0;
    }
    .quick-btn {
        background: var(--bg-card);
        border: 1.5px solid var(--border-color);
        border-radius: var(--border-radius-md);
        padding: 14px 16px;
        text-align: center;
        cursor: pointer;
        transition: var(--transition-base);
        color: var(--text-secondary);
        font-size: 0.9rem;
    }
    .quick-btn:hover {
        background: var(--bg-active);
        border-color: var(--accent-primary);
        color: var(--text-primary);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px var(--accent-primary-glow);
    }

    /* ========== 代码块美化 ========== */
    .stCode {
        border-radius: var(--border-radius-md) !important;
        border: 1px solid var(--border-color) !important;
    }

    /* ========== 加载动画 ========== */
    .stSpinner > div {
        border-width: 3px !important;
        border-color: var(--accent-primary) !important;
        border-top-color: transparent !important;
    }

    /* ========== 信息/警告/错误框 ========== */
    .stAlert {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--border-radius-md) !important;
        color: var(--text-primary) !important;
    }
    .stAlert [data-testid="stAlertContent"] {
        color: var(--text-primary) !important;
    }

    /* ========== 进度条 ========== */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--accent-primary), #10b981) !important;
        border-radius: 4px !important;
    }

    /* ========== 滑块 ========== */
    .stSlider > div > div > div {
        background: var(--accent-primary) !important;
    }

    /* ========== 单选/复选框 ========== */
    .stRadio > div > div > label,
    .stCheckbox > div > div > div {
        color: var(--text-primary) !important;
    }

    /* ========== Metric组件 ========== */
    [data-testid="stMetric"] {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius-md);
        padding: 16px;
        transition: var(--transition-base);
    }
    [data-testid="stMetric"]:hover {
        border-color: var(--accent-blue);
    }
    [data-testid="stMetric"] > div:first-child {
        color: var(--text-muted) !important;
        font-size: 0.85rem !important;
    }
    [data-testid="stMetric"] > div:last-child {
        color: var(--text-inverse) !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }

    /* ========== 全局页面加载淡入 ========== */
    .stApp > div:first-child {
        animation: fadeIn 0.5s ease-out;
    }

    /* ========== 响应式调整 ========== */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        .quick-btn-grid {
            grid-template-columns: 1fr;
        }
        .auth-page {
            margin: 1rem;
            padding: 1.5rem;
        }
    }

    /* ========== 隐藏Streamlit默认元素 ========== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ========== 自定义光标效果 ========== */
    .typing-cursor::after {
        content: '|';
        color: var(--accent-primary);
        animation: typeCursor 1s ease-in-out infinite;
        margin-left: 2px;
    }

    /* ========== 渐变边框效果 ========== */
    .gradient-border {
        position: relative;
        border-radius: var(--border-radius-lg);
        background: var(--bg-card);
        z-index: 1;
    }
    .gradient-border::before {
        content: '';
        position: absolute;
        inset: -1px;
        border-radius: calc(var(--border-radius-lg) + 1px);
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-blue), var(--accent-primary));
        background-size: 200% 200%;
        animation: gradientShift 4s ease infinite;
        z-index: -1;
    }
</style>
"""


# ========== 页面配置 ==========
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# 应用CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ========== 会话状态初始化 ==========
def init_session_state():
    """初始化所有session state变量"""
    init_auth_state()

    if "page" not in st.session_state:
        st.session_state.page = "welcome"
    if "initialized" not in st.session_state:
        st.session_state.initialized = False

    # 检查数据库是否存在，不存在则自动初始化
    if not st.session_state.initialized:
        try:
            create_all_tables()
            st.session_state.initialized = True
        except Exception as e:
            st.error(f"数据库初始化失败: {e}")


# ========== 首页 ==========
def show_home_page():
    """显示首页 - 简洁版"""
    st.markdown("---")

    # 欢迎信息
    username = get_current_username()
    welcome_msg = f"欢迎回来，{username}" if username else "欢迎使用"

    st.markdown(f"""
    <div class="success-box anim-fade-in-up" style="
        background: linear-gradient(135deg, rgba(25,195,125,0.08), rgba(59,130,246,0.05)) !important;
        border-left: 4px solid #19c37d;
    ">
        <h3 style="color: #ffffff; margin-bottom: 12px;">🎉 {welcome_msg}</h3>
        <p style="color: #c5c5d2; line-height: 1.7;">
            本系统基于<strong style="color: #ffffff;">Kimi大模型</strong>构建，专为<strong style="color: #ffffff;">AI与低空技术</strong>领域的科研工作者设计。
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 快速导航按钮（如果侧边栏不可见，可用此导航）
    st.markdown("""
    <div style="font-size: 0.75rem; color: #8e8ea0; margin-bottom: 0.5rem;">快速导航</div>
    """, unsafe_allow_html=True)
    
    nav_col1, nav_col2, nav_col3, nav_col4, nav_col5, nav_col6, nav_col7 = st.columns(7)
    nav_buttons = [
        (nav_col1, "🏠", "🏠 首页"),
        (nav_col2, "💬", "💬 智能对话"),
        (nav_col3, "📝", "📝 代码辅助"),
        (nav_col4, "📊", "📊 数据分析"),
        (nav_col5, "📄", "📄 论文写作"),
        (nav_col6, "📚", "📚 知识库"),
        (nav_col7, "📊", "📊 用量统计"),
    ]
    for col, icon, page in nav_buttons:
        with col:
            if st.button(icon, use_container_width=True, key=f"navbtn_{page}"):
                st.session_state.page = page
                st.rerun()
    
    st.markdown("---")

    # 功能概览 - 使用 feature-card
    st.markdown("""
    <h3 style="color: #ffffff; margin-top: 2rem; margin-bottom: 1.5rem; font-weight: 600;">
        📋 功能模块
    </h3>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    cards = [
        {
            "icon": "💬",
            "title": "智能对话",
            "desc": "多轮对话上下文理解<br>对话历史<strong style=\"color:#19c37d;\">永久保存</strong>",
        },
        {
            "icon": "📝",
            "title": "代码辅助",
            "desc": "Python代码智能生成<br>代码逐行解释<br>Bug分析修复",
        },
        {
            "icon": "📊",
            "title": "数据分析",
            "desc": "CSV/Excel/JSON上传<br>7种交互式可视化<br>AI生成分析报告",
        },
    ]
    for col, card in zip([col1, col2, col3], cards):
        with col:
            st.markdown(f"""
            <div class="feature-card anim-fade-in-up">
                <span class="feature-icon anim-float">{card['icon']}</span>
                <div class="feature-title">{card['title']}</div>
                <div class="feature-desc">{card['desc']}</div>
            </div>
            """, unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)
    cards2 = [
        {
            "icon": "📄",
            "title": "论文写作",
            "desc": "论文结构智能规划<br>中英文摘要生成<br>四种引用格式",
        },
        {
            "icon": "📚",
            "title": "知识库",
            "desc": "5大领域结构化存储<br>关键词全文检索<br>Markdown导入",
        },
        {
            "icon": "🔐",
            "title": "用户系统",
            "desc": "注册/登录/密码加密<br>API Key AES加密<br>游客免注册体验",
        },
    ]
    for col, card in zip([col4, col5, col6], cards2):
        with col:
            st.markdown(f"""
            <div class="feature-card anim-fade-in-up">
                <span class="feature-icon anim-float">{card['icon']}</span>
                <div class="feature-title">{card['title']}</div>
                <div class="feature-desc">{card['desc']}</div>
            </div>
            """, unsafe_allow_html=True)

    # 快速开始
    st.markdown("---")
    st.markdown("""
    <h3 style="color: #ffffff; font-weight: 600;">🚀 快速开始</h3>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: #40414f; border: 1px solid #4d4d4f; border-radius: 16px; padding: 24px 28px; margin: 16px 0;">
        <ol style="color: #c5c5d2; line-height: 2; margin: 0; padding-left: 20px;">
            <li><strong style="color: #ffffff;">数据库已就绪</strong> — 首次运行自动创建SQLite数据库</li>
            <li><strong style="color: #ffffff;">登录可用</strong> — 注册账号以使用完整功能</li>
            <li><strong style="color: #ffffff;">默认API已配置</strong> — 系统内置Kimi API Key</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    # 技术栈展示
    st.markdown("---")
    st.markdown("""
    <h3 style="color: #ffffff; font-weight: 600;">🛠️ 技术栈</h3>
    """, unsafe_allow_html=True)

    st.markdown("""
    <table style="width: 100%; border-collapse: separate; border-spacing: 0;">
        <thead>
            <tr><th style="padding: 14px 16px; text-align: left;">技术</th><th style="padding: 14px 16px; text-align: left;">用途</th><th style="padding: 14px 16px; text-align: left;">版本</th></tr>
        </thead>
        <tbody>
            <tr><td style="padding: 12px 16px;"><strong style="color: #19c37d;">Kimi API</strong></td><td style="padding: 12px 16px;">大模型能力引擎</td><td style="padding: 12px 16px;">k2.5</td></tr>
            <tr><td style="padding: 12px 16px;"><strong style="color: #3b82f6;">Streamlit</strong></td><td style="padding: 12px 16px;">Web应用框架</td><td style="padding: 12px 16px;">1.28+</td></tr>
            <tr><td style="padding: 12px 16px;"><strong style="color: #f59e0b;">SQLite</strong></td><td style="padding: 12px 16px;">数据库</td><td style="padding: 12px 16px;">3.39+</td></tr>
            <tr><td style="padding: 12px 16px;"><strong style="color: #a855f7;">SQLAlchemy</strong></td><td style="padding: 12px 16px;">ORM数据库操作</td><td style="padding: 12px 16px;">2.0+</td></tr>
        </tbody>
    </table>
    """, unsafe_allow_html=True)


# ========== 侧边栏导航 ==========
def render_sidebar():
    """渲染侧边栏导航"""
    with st.sidebar:
        # Logo区域
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0 0.5rem; margin-bottom: 0.5rem;">
            <div style="font-size: 2rem; margin-bottom: 4px;">🔬</div>
            <div style="font-size: 1rem; font-weight: 700; color: #ffffff; letter-spacing: -0.3px;">AI 科研助手</div>
            <div style="font-size: 0.7rem; color: #8e8ea0; margin-top: 2px;">v2.0 数据库版</div>
        </div>
        <div style="height: 1px; background: linear-gradient(90deg, transparent, #4d4d4f, transparent); margin: 0.5rem 0 1rem;"></div>
        """, unsafe_allow_html=True)

        # 判断当前页面
        current_page = st.session_state.get("page", "welcome")

        if current_page == "welcome":
            # 欢迎页面 - 只显示"进入系统"按钮
            if st.button("🚀 进入系统", use_container_width=True, type="primary", key="sidebar_enter"):
                st.session_state.page = "🏠 首页"
                st.rerun()
            return  # 欢迎页面不显示其他内容

        # 用户认证区域（非欢迎页面）
        show_sidebar_auth()

        # 功能导航
        st.markdown("""
        <div style="font-size: 0.75rem; color: #8e8ea0; text-transform: uppercase; letter-spacing: 1px; margin: 1rem 0 0.5rem; padding-left: 4px;">功能导航</div>
        """, unsafe_allow_html=True)

        # 统一的页面列表（包含登录/注册选项）
        page_options = ["🏠 首页", "💬 智能对话", "📝 代码辅助", "📊 数据分析", "📄 论文写作", "📚 知识库", "📊 用量统计", "🔐 登录/注册"]
        
        # 获取当前应该显示的页面索引
        display_page = current_page
        if display_page == "auth":
            display_page = "🔐 登录/注册"
        elif display_page not in page_options:
            display_page = "🏠 首页"
        
        # 使用 radio 导航
        page = st.radio(
            "页面",
            page_options,
            index=page_options.index(display_page),
            key="sidebar_page",
            label_visibility="collapsed"
        )
        
        # 如果页面变化，更新状态并刷新
        if page != display_page:
            if page == "🔐 登录/注册":
                st.session_state.page = "auth"
            else:
                st.session_state.page = page
            st.rerun()
        
        # 对话模块显示对话历史侧边栏
        if display_page == "💬 智能对话":
            show_conversation_sidebar()

        st.markdown("---")

        # 关于信息
        st.markdown("""
        <div style="font-size: 0.75rem; color: #8e8ea0; text-transform: uppercase; letter-spacing: 1px; margin: 0 0 0.5rem; padding-left: 4px;">关于</div>
        """, unsafe_allow_html=True)

        st.info(f"""
**开发者**：{config.DEVELOPER}
**学号**：{config.STUDENT_ID}
**班级**：{config.CLASS_NAME}
**学院**：{config.COLLEGE}
        """)

        # 数据库状态指示器
        from database.models import engine
        from sqlalchemy import inspect
        try:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            if tables:
                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 6px; font-size: 0.75rem; color: #8e8ea0; margin-top: 8px;">
                    <span style="width: 6px; height: 6px; background: #19c37d; border-radius: 50%; display: inline-block; box-shadow: 0 0 6px rgba(25,195,125,0.5);"></span>
                    数据库已连接（{len(tables)}张表）
                </div>
                """, unsafe_allow_html=True)
            else:
                st.caption("📦 数据库未初始化")
        except Exception:
            st.caption("📦 数据库连接异常")


# ========== 欢迎页面 ==========
def show_welcome_page():
    """显示欢迎页面 - 含设计理念"""
    # 使用 Streamlit 原生组件创建简洁的欢迎页
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 居中标题区域
    c1, c2, c3 = st.columns([1, 3, 1])
    with c2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <div style="font-size: 5rem; margin-bottom: 1rem;">🔬</div>
            <h1 style="font-size: 2.5rem; font-weight: 700; color: #ffffff; margin-bottom: 0.5rem;">AI 智能科研辅助助手</h1>
            <p style="font-size: 1.1rem; color: #8e8ea0; line-height: 1.6;">基于 Kimi 大模型构建，专为 AI 与低空技术领域科研工作者设计</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 功能标签
        st.markdown("""
        <div style="text-align: center; margin: 1.5rem 0;">
            <span style="background: rgba(25,195,125,0.15); color: #19c37d; padding: 4px 12px; border-radius: 16px; font-size: 0.8rem; margin: 0 4px;">💬 智能对话</span>
            <span style="background: rgba(59,130,246,0.15); color: #3b82f6; padding: 4px 12px; border-radius: 16px; font-size: 0.8rem; margin: 0 4px;">📝 代码辅助</span>
            <span style="background: rgba(245,158,11,0.15); color: #f59e0b; padding: 4px 12px; border-radius: 16px; font-size: 0.8rem; margin: 0 4px;">📊 数据分析</span>
            <span style="background: rgba(239,68,68,0.15); color: #ef4444; padding: 4px 12px; border-radius: 16px; font-size: 0.8rem; margin: 0 4px;">📄 论文写作</span>
            <span style="background: rgba(168,85,247,0.15); color: #a855f7; padding: 4px 12px; border-radius: 16px; font-size: 0.8rem; margin: 0 4px;">📚 知识库</span>
        </div>
        """, unsafe_allow_html=True)
        
        # 进入按钮
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 进入系统", use_container_width=True, type="primary", key="enter_main"):
            st.session_state.page = "🏠 首页"
            st.rerun()
        
        # 设计理念
        st.markdown("""
        <div style="margin-top: 3rem; padding: 2rem; background: rgba(64,65,79,0.4); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px;">
            <h3 style="color: #ffffff; font-size: 1.2rem; margin-bottom: 1rem; text-align: center;">💡 设计理念</h3>
            <p style="color: #c5c5d2; font-size: 0.95rem; line-height: 1.8; text-align: center;">
                本系统以<strong style="color: #ffffff;">"让科研更高效"</strong>为核心理念，将前沿AI大模型能力与科研 workflows 深度融合。
                我们追求<strong style="color: #19c37d;">简洁</strong>、<strong style="color: #3b82f6;">专业</strong>、<strong style="color: #f59e0b;">可靠</strong>的产品体验，
                为每一位科研工作者打造专属的智能助手。
            </p>
            <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 1.5rem; flex-wrap: wrap;">
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">⚡</div>
                    <div style="color: #8e8ea0; font-size: 0.8rem;">高效</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">🔒</div>
                    <div style="color: #8e8ea0; font-size: 0.8rem;">安全</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">🌐</div>
                    <div style="color: #8e8ea0; font-size: 0.8rem;">开放</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">🤝</div>
                    <div style="color: #8e8ea0; font-size: 0.8rem;">协作</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 底部信息
        st.markdown("""
        <div style="text-align: center; margin-top: 3rem; font-size: 0.75rem; color: #666;">
            <p>开发者：张驰 | 学号：202530463528 | 自动化科学与工程学院</p>
            <p>AI与低空技术3班 | 版本 v2.0</p>
        </div>
        """, unsafe_allow_html=True)


# ========== 主函数 ==========
def main():
    """主入口函数"""
    # 初始化
    init_session_state()

    # 页面路由
    current_page = st.session_state.get("page", "welcome")

    if current_page == "welcome":
        # 欢迎页面 - 隐藏侧边栏和标题，只显示欢迎内容
        st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none !important;}
            [data-testid="stSidebarCollapsedControl"] {display: none !important;}
        </style>
        """, unsafe_allow_html=True)
        show_welcome_page()
        return  # 直接返回，不渲染其他内容

    # 其他页面 - 侧边栏始终显示，移除旧的隐藏样式，隐藏折叠按钮
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            transform: none !important;
            margin-left: 0 !important;
            min-width: 330px !important;
            width: 330px !important;
        }
        [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }
    </style>
    <script>
        (function() {
            // 1. 移除所有旧的、包含 stSidebar + display:none 的 style 标签
            document.querySelectorAll('style').forEach(function(style) {
                var text = style.textContent || '';
                if (text.indexOf('stSidebar') !== -1 && text.indexOf('display: none') !== -1) {
                    style.remove();
                }
            });
            
            // 2. 强制修复侧边栏和折叠按钮
            function fixSidebar() {
                var sidebar = document.querySelector('[data-testid="stSidebar"]');
                var control = document.querySelector('[data-testid="stSidebarCollapsedControl"]');
                if (sidebar) {
                    sidebar.style.setProperty('display', 'block', 'important');
                    sidebar.style.setProperty('visibility', 'visible', 'important');
                    sidebar.style.setProperty('opacity', '1', 'important');
                    sidebar.style.setProperty('transform', 'none', 'important');
                    sidebar.style.setProperty('margin-left', '0', 'important');
                    sidebar.style.setProperty('min-width', '330px', 'important');
                    sidebar.style.setProperty('width', '330px', 'important');
                }
                if (control) {
                    control.style.setProperty('display', 'none', 'important');
                }
            }
            
            // 立即执行 + 持续监控（防止streamlit动态更新后回退）
            fixSidebar();
            setInterval(fixSidebar, 500);
        })();
    </script>
    """, unsafe_allow_html=True)

    # 显示标题
    st.markdown("""
    <div style="text-align: center; margin-bottom: 0.5rem;">
        <div class="main-title anim-fade-in-up" style="display: inline-block;">
            🔬 AI智能科研辅助助手
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 渲染侧边栏
    render_sidebar()

    if current_page == "auth":
        auth_page = st.session_state.get("auth_page", "login")
        if auth_page == "login":
            show_login_page()
        else:
            show_register_page()
    elif current_page == "🏠 首页":
        show_home_page()
    elif current_page == "💬 智能对话":
        show_chat_page()
    elif current_page == "📝 代码辅助":
        show_code_assist_page()
    elif current_page == "📊 数据分析":
        show_data_analysis_page()
    elif current_page == "📄 论文写作":
        show_paper_writing_page()
    elif current_page == "📚 知识库":
        show_knowledge_base_page()
    elif current_page == "📊 用量统计":
        show_usage_stats_page()

    # 页脚
    st.markdown(f"""
    <div class="footer-text anim-fade-in">
        <p>🔬 {config.APP_TITLE} | 基于Kimi大模型构建 | {config.COLLEGE}</p>
        <p>开发者：{config.DEVELOPER}（{config.STUDENT_ID}）| {config.CLASS_NAME} | 版本 {config.APP_VERSION}</p>
    </div>
    """, unsafe_allow_html=True)


# ========== 启动 ==========
if __name__ == "__main__":
    main()
