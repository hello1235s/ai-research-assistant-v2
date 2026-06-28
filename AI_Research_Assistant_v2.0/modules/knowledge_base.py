"""
AI智能科研辅助助手 - 知识库模块 (高级美化版)
功能：结构化知识检索、分类浏览、全文搜索
ChatGPT风格深色主题 + 丝滑交互动画
"""

import streamlit as st
from database.queries import DatabaseManager


def get_category_display_name(category: str) -> str:
    """获取分类的中文显示名"""
    mapping = {
        "python_basics": "Python编程基础",
        "data_analysis": "数据分析与可视化",
        "machine_learning": "机器学习基础",
        "paper_writing": "论文写作规范",
        "uav_tech": "无人机与低空技术"
    }
    return mapping.get(category, category)


def get_category_icon(category: str) -> str:
    """获取分类图标"""
    icons = {
        "python_basics": "🐍",
        "data_analysis": "📊",
        "machine_learning": "🤖",
        "paper_writing": "📄",
        "uav_tech": "🚁"
    }
    return icons.get(category, "📚")


def get_category_color(category: str) -> str:
    """获取分类主题色"""
    colors = {
        "python_basics": "#3b82f6",
        "data_analysis": "#f59e0b",
        "machine_learning": "#8b5cf6",
        "paper_writing": "#ec4899",
        "uav_tech": "#10b981"
    }
    return colors.get(category, "#6b7280")


def show_knowledge_base_page():
    """显示知识库页面 - 高级版"""
    # 头部
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 0.5rem;">
        <h2 style="color: #ffffff; margin: 0; font-weight: 700;">📚 科研知识库</h2>
        <span style="
            background: rgba(16,185,129,0.15);
            color: #10b981;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
        ">Knowledge Base</span>
    </div>
    <p style="color: #8e8ea0; margin: 0 0 1.5rem; font-size: 0.9rem;">结构化存储的5大领域知识，支持关键词检索和分类浏览</p>
    """, unsafe_allow_html=True)

    # 初始化数据库检查
    db = DatabaseManager()
    try:
        count = db.count_knowledge_entries()
        if count == 0:
            st.warning("⚠️ 知识库尚未初始化，请运行 `python database/init_db.py`")
            return

        # 统计卡片行
        col_stat, col_cat = st.columns([1, 3])
        with col_stat:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(25,195,125,0.1), rgba(25,195,125,0.05));
                border: 1px solid rgba(25,195,125,0.3);
                border-radius: 16px;
                padding: 20px;
                text-align: center;
            ">
                <div style="font-size: 2rem; font-weight: 800; color: #19c37d;">{count}</div>
                <div style="font-size: 0.8rem; color: #8e8ea0; margin-top: 4px;">知识条目</div>
            </div>
            """, unsafe_allow_html=True)

        with col_cat:
            categories = db.get_knowledge_categories()
            cat_cols = st.columns(len(categories))
            for i, cat in enumerate(categories):
                with cat_cols[i]:
                    color = get_category_color(cat)
                    display = get_category_display_name(cat)
                    icon = get_category_icon(cat)
                    cat_count = len(db.get_knowledge_by_category(cat))
                    st.markdown(f"""
                    <div style="
                        background: {color}10;
                        border: 1px solid {color}30;
                        border-radius: 12px;
                        padding: 12px 8px;
                        text-align: center;
                        transition: all 0.25s ease;
                    ">
                        <div style="font-size: 1.5rem; margin-bottom: 4px;">{icon}</div>
                        <div style="font-size: 0.75rem; color: {color}; font-weight: 600;">{display}</div>
                        <div style="font-size: 0.7rem; color: #8e8ea0;">{cat_count}条</div>
                    </div>
                    """, unsafe_allow_html=True)
    finally:
        db.close()

    st.markdown("<div style='height: 1px; background: linear-gradient(90deg, transparent, #4d4d4f, transparent); margin: 1.5rem 0;'></div>", unsafe_allow_html=True)

    # 搜索区域
    search_col, category_col = st.columns([3, 1])

    with search_col:
        search_term = st.text_input(
            "🔍 全文检索",
            placeholder="输入关键词搜索知识库...",
            key="kb_search"
        )

    with category_col:
        db = DatabaseManager()
        try:
            categories = db.get_knowledge_categories()
            category_options = ["全部"] + [get_category_display_name(c) for c in categories]
            selected_category_display = st.selectbox("分类筛选", category_options, key="kb_category")
            selected_category = None if selected_category_display == "全部" else categories[category_options.index(selected_category_display) - 1]
        finally:
            db.close()

    # 执行搜索或浏览
    if search_term:
        show_search_results(search_term, selected_category)
    else:
        show_category_browser(selected_category)


def show_search_results(search_term: str, category: str = None):
    """显示搜索结果 - 高级版"""
    db = DatabaseManager()
    try:
        results = db.search_knowledge(search_term, category=category, limit=20)

        if not results:
            st.markdown(f"""
            <div style="
                text-align: center;
                padding: 48px 24px;
                color: #8e8ea0;
            ">
                <div style="font-size: 3rem; margin-bottom: 16px;">🔍</div>
                <div style="font-size: 1rem; font-weight: 500; color: #c5c5d2; margin-bottom: 8px;">
                    未找到包含 "{search_term}" 的知识条目
                </div>
                <div style="font-size: 0.85rem;">请尝试其他关键词</div>
            </div>
            """, unsafe_allow_html=True)
            return

        # 结果统计
        st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 16px;
            color: #8e8ea0;
            font-size: 0.9rem;
        ">
            <span style="color: #19c37d; font-weight: 600;">{len(results)}</span>
            <span>条相关结果</span>
            <span style="color: #4d4d4f;">|</span>
            <span style="font-size: 0.8rem;">关键词: "{search_term}"</span>
        </div>
        """, unsafe_allow_html=True)

        for entry in results:
            icon = get_category_icon(entry.category)
            display_cat = get_category_display_name(entry.category)
            color = get_category_color(entry.category)

            # 高亮关键词
            import re
            try:
                content = re.sub(
                    f'({re.escape(search_term)})',
                    r'<mark style="background: rgba(25,195,125,0.3); color: #ffffff; padding: 1px 4px; border-radius: 3px;">\1</mark>',
                    entry.content,
                    flags=re.IGNORECASE
                )
            except re.error:
                content = entry.content

            with st.expander(f"{icon} [{display_cat}] {entry.title}"):
                st.markdown(content, unsafe_allow_html=True)

                if entry.keywords:
                    st.markdown(f"""
                    <div style="margin-top: 12px;">
                        <span style="color: #8e8ea0; font-size: 0.8rem;">🏷️ 关键词: </span>
                        <span style="color: {color}; font-size: 0.8rem;">{entry.keywords}</span>
                    </div>
                    """, unsafe_allow_html=True)
    finally:
        db.close()


def show_category_browser(category: str = None):
    """按分类浏览知识库 - 高级版"""
    db = DatabaseManager()
    try:
        categories = [category] if category else db.get_knowledge_categories()

        for cat in categories:
            icon = get_category_icon(cat)
            display_name = get_category_display_name(cat)
            color = get_category_color(cat)

            # 分类标题
            st.markdown(f"""
            <div style="
                display: flex;
                align-items: center;
                gap: 12px;
                margin: 2rem 0 1rem;
                padding-bottom: 8px;
                border-bottom: 2px solid {color}40;
            ">
                <span style="font-size: 1.5rem;">{icon}</span>
                <span style="color: #ffffff; font-weight: 700; font-size: 1.1rem;">{display_name}</span>
                <div style="
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: {color};
                    box-shadow: 0 0 8px {color}80;
                "></div>
            </div>
            """, unsafe_allow_html=True)

            entries = db.get_knowledge_by_category(cat)
            if not entries:
                st.caption("暂无条目")
                continue

            # 两列布局
            cols = st.columns(2)
            for i, entry in enumerate(entries[:10]):
                with cols[i % 2]:
                    with st.expander(f"📖 {entry.title}"):
                        content_preview = entry.content[:800] + "..." if len(entry.content) > 800 else entry.content
                        st.markdown(content_preview)

                        if entry.keywords:
                            st.markdown(f"""
                            <div style="margin-top: 8px;">
                                <span style="color: {color}; font-size: 0.8rem;">🏷️ {entry.keywords}</span>
                            </div>
                            """, unsafe_allow_html=True)

            if len(entries) > 10:
                st.caption(f"... 还有 {len(entries) - 10} 条内容")

            st.markdown("<div style='height: 1px; background: linear-gradient(90deg, transparent, #4d4d4f, transparent); margin: 1rem 0;'></div>", unsafe_allow_html=True)
    finally:
        db.close()
