"""
AI智能科研辅助助手 - 代码辅助模块 (高级美化版)
功能：代码生成、代码解释、代码调试、代码收藏
ChatGPT风格深色主题 + 丝滑交互动画
"""

import streamlit as st
from modules.chat import call_kimi_api
from database.queries import DatabaseManager
from utils.security import get_api_key_for_user
import config


def get_user_api_key():
    """获取当前用户可用的API Key"""
    user_id = st.session_state.get("user_id")
    if user_id is not None and user_id > 0:
        db = DatabaseManager()
        try:
            user = db.get_user_by_id(user_id)
            if user:
                return get_api_key_for_user(user)
        finally:
            db.close()
    return config.DEFAULT_API_KEY


def save_code_snippet(title: str, code: str, language: str = "python", description: str = "", tags: str = ""):
    """保存代码片段到个人库"""
    user_id = st.session_state.get("user_id", 0)
    if user_id == 0:
        st.warning("请先登录以使用代码收藏功能")
        return False

    db = DatabaseManager()
    try:
        db.create_code_snippet(
            user_id=user_id,
            title=title,
            code=code,
            language=language,
            description=description,
            tags=tags,
            source="AI生成"
        )
        return True
    finally:
        db.close()


def show_code_assist_page():
    """显示代码辅助页面 - 高级版"""
    # 头部
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 0.5rem;">
        <h2 style="color: #ffffff; margin: 0; font-weight: 700;">📝 代码开发辅助助手</h2>
        <span style="
            background: rgba(59,130,246,0.15);
            color: #3b82f6;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
        ">Code Assistant</span>
    </div>
    <p style="color: #8e8ea0; margin: 0 0 1.5rem; font-size: 0.9rem;">AI驱动的代码生成、解释和调试工具</p>
    """, unsafe_allow_html=True)

    api_key = get_user_api_key()
    model = st.session_state.get("current_model", config.DEFAULT_MODEL)

    tab1, tab2, tab3, tab4 = st.tabs(["💻 代码生成", "🔍 代码解释", "🐛 代码调试", "📚 我的代码库"])

    # ========== Tab 1: 代码生成 ==========
    with tab1:
        st.markdown("<h3 style='color: #ffffff; font-weight: 600; margin-bottom: 1rem;'>🎯 代码生成</h3>", unsafe_allow_html=True)

        code_task = st.selectbox(
            "选择代码任务类型",
            ["数据处理脚本", "机器学习模型", "可视化图表", "文件处理", "算法实现", "Web开发", "其他"],
            key="code_gen_task"
        )

        # 代码需求输入区 - 使用更大更美观的输入框
        code_requirement = st.text_area(
            "描述您的代码需求",
            placeholder="例如：生成一个Python脚本，用于读取CSV文件并计算各列的统计描述...",
            height=120,
            key="code_gen_req"
        )

        # 按钮行
        col_gen, col_example, _ = st.columns([1.2, 1.2, 3])

        def load_example_callback():
            """回调函数：在widget渲染前设置示例值"""
            st.session_state.code_gen_req = "写一个Python函数，实现对无人机飞行数据的异常检测，使用Isolation Forest算法，并返回异常值的索引和分数。"

        with col_gen:
            generate_btn = st.button("🚀 生成代码", use_container_width=True, key="gen_code_btn")
        with col_example:
            st.button("🎲 加载示例", use_container_width=True, key="load_example", on_click=load_example_callback)

        if generate_btn:
            if code_requirement:
                with st.spinner("⏳ Kimi AI 正在生成代码..."):
                    prompt = (
                        f"请根据以下需求生成Python代码：\n\n"
                        f"任务类型：{code_task}\n"
                        f"需求描述：{code_requirement}\n\n"
                        f"要求：\n"
                        f"1. 生成完整可运行的代码\n"
                        f"2. 添加详细注释\n"
                        f"3. 提供使用示例\n"
                        f"4. 说明需要安装的依赖库\n"
                        f"5. 使用markdown代码块输出"
                    )
                    code_result = call_kimi_api(
                        prompt=prompt,
                        system_prompt=config.CODE_SYSTEM_PROMPT,
                        model=model,
                        api_key=api_key,
                        max_tokens=4096
                    )

                    # 提取代码块用于收藏
                    code_to_save = code_result
                    if "```python" in code_result:
                        import re
                        match = re.search(r'```python\n(.*?)\n```', code_result, re.DOTALL)
                        if match:
                            code_to_save = match.group(1)

                    # 结果显示在美观的容器中
                    st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, rgba(25,195,125,0.05), rgba(59,130,246,0.03));
                        border: 1px solid #4d4d4f;
                        border-radius: 16px;
                        padding: 24px;
                        margin-top: 16px;
                    ">
                        <div style="
                            display: flex;
                            align-items: center;
                            gap: 8px;
                            margin-bottom: 16px;
                            padding-bottom: 12px;
                            border-bottom: 1px solid #4d4d4f;
                        ">
                            <span style="font-size: 1.2rem;">🤖</span>
                            <span style="color: #ffffff; font-weight: 600;">AI 生成的代码</span>
                            <span style="
                                background: rgba(25,195,125,0.15);
                                color: #19c37d;
                                padding: 2px 8px;
                                border-radius: 8px;
                                font-size: 0.75rem;
                                margin-left: auto;
                            ">{task}</span>
                        </div>
                    </div>
                    """.format(task=code_task), unsafe_allow_html=True)

                    st.markdown(code_result)

                    # 收藏区域
                    user_id = st.session_state.get("user_id", 0)
                    if user_id and user_id > 0:
                        st.markdown("<div style='height: 1px; background: linear-gradient(90deg, transparent, #4d4d4f, transparent); margin: 1rem 0;'></div>", unsafe_allow_html=True)
                        col_save, col_title = st.columns([1, 3])
                        with col_title:
                            snippet_title = st.text_input(
                                "收藏标题",
                                value=f"{code_task} - {code_requirement[:20]}...",
                                key="save_title"
                            )
                        with col_save:
                            if st.button("⭐ 收藏代码", use_container_width=True, key="save_code_btn"):
                                if save_code_snippet(
                                    title=snippet_title,
                                    code=code_to_save,
                                    language="python",
                                    description=code_requirement,
                                    tags=code_task
                                ):
                                    st.success("✅ 已收藏到个人代码库")
                                else:
                                    st.error("❌ 收藏失败")
            else:
                st.warning("请输入代码需求描述")

    # ========== Tab 2: 代码解释 ==========
    with tab2:
        st.markdown("<h3 style='color: #ffffff; font-weight: 600; margin-bottom: 1rem;'>🔍 代码解释</h3>", unsafe_allow_html=True)

        code_input = st.text_area(
            "粘贴需要解释的代码",
            placeholder="在此粘贴Python代码...",
            height=200,
            key="code_explain_input"
        )

        if st.button("🔍 解释代码", use_container_width=True, key="explain_btn"):
            if code_input:
                with st.spinner("⏳ Kimi AI 正在分析代码..."):
                    prompt = (
                        f"请详细解释以下Python代码：\n\n"
                        f"```python\n{code_input}\n```\n\n"
                        f"请从以下几个方面解释：\n"
                        f"1. 整体功能概述\n"
                        f"2. 逐段/逐行解释关键逻辑\n"
                        f"3. 参数和变量说明\n"
                        f"4. 潜在问题或优化建议\n"
                        f"5. 使用示例"
                    )
                    explanation = call_kimi_api(
                        prompt=prompt,
                        system_prompt="你是一名Python编程专家，擅长代码分析和解释。请用中文详细解释代码的功能、逻辑和关键步骤。",
                        model=model,
                        api_key=api_key,
                        max_tokens=4096
                    )
                    st.markdown(explanation)
            else:
                st.warning("请粘贴需要解释的代码")

    # ========== Tab 3: 代码调试 ==========
    with tab3:
        st.markdown("<h3 style='color: #ffffff; font-weight: 600; margin-bottom: 1rem;'>🐛 代码调试</h3>", unsafe_allow_html=True)

        st.markdown("""
        <div style="
            background: rgba(245,158,11,0.05);
            border: 1px solid rgba(245,158,11,0.2);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            color: #f59e0b;
            font-size: 0.9rem;
        ">
            💡 提供报错代码和错误信息，AI将分析原因并给出修复方案
        </div>
        """, unsafe_allow_html=True)

        error_code = st.text_area(
            "粘贴报错代码",
            placeholder="在此粘贴报错的代码...",
            height=150,
            key="debug_code"
        )

        error_message = st.text_area(
            "粘贴错误信息",
            placeholder="在此粘贴报错信息（Traceback）...",
            height=100,
            key="debug_error"
        )

        if st.button("🔧 分析错误", use_container_width=True, key="debug_btn"):
            if error_code and error_message:
                with st.spinner("⏳ Kimi AI 正在分析错误..."):
                    prompt = (
                        f"请分析以下Python代码的错误并给出修复方案：\n\n"
                        f"【错误信息】\n{error_message}\n\n"
                        f"【报错代码】\n```python\n{error_code}\n```\n\n"
                        f"请从以下几个方面分析：\n"
                        f"1. 错误类型和原因\n"
                        f"2. 定位出错的代码行\n"
                        f"3. 给出修正后的完整代码\n"
                        f"4. 解释修复原理\n"
                        f"5. 给出预防类似错误的建议"
                    )
                    debug_result = call_kimi_api(
                        prompt=prompt,
                        system_prompt="你是一名Python调试专家，擅长分析代码错误并给出修复方案。请用中文回答。",
                        model=model,
                        api_key=api_key,
                        max_tokens=4096
                    )
                    st.markdown(debug_result)
            else:
                st.warning("请提供代码和错误信息")

    # ========== Tab 4: 我的代码库 ==========
    with tab4:
        st.markdown("<h3 style='color: #ffffff; font-weight: 600; margin-bottom: 1rem;'>📚 我的代码收藏</h3>", unsafe_allow_html=True)

        user_id = st.session_state.get("user_id", 0)
        if user_id == 0:
            st.info("👤 登录后可查看个人代码库")
            return

        db = DatabaseManager()
        try:
            snippets = db.get_code_snippets(user_id)

            if not snippets:
                st.info("暂无收藏的代码，在「代码生成」中收藏你的第一个代码片段吧")
                return

            # 筛选器
            col_filter, col_lang = st.columns(2)
            with col_filter:
                filter_tag = st.text_input("🔍 按标签筛选", placeholder="输入标签关键词", key="snippet_filter")
            with col_lang:
                languages = list(set([s.language for s in snippets]))
                filter_lang = st.selectbox("按语言筛选", ["全部"] + languages, key="snippet_lang")

            # 应用筛选
            filtered = snippets
            if filter_tag:
                filtered = [s for s in filtered if filter_tag.lower() in (s.tags or "").lower()]
            if filter_lang != "全部":
                filtered = [s for s in filtered if s.language == filter_lang]

            st.caption(f"共 {len(filtered)} 条代码片段")

            for snippet in filtered:
                with st.expander(f"📌 {snippet.title} ({snippet.language})"):
                    st.code(snippet.code, language=snippet.language)
                    if snippet.description:
                        st.caption(f"📝 {snippet.description}")
                    if snippet.tags:
                        st.caption(f"🏷️ 标签: {snippet.tags}")
                    st.caption(f"📅 {snippet.created_at.strftime('%Y-%m-%d %H:%M')}")

                    if st.button("🗑️ 删除", key=f"del_snippet_{snippet.id}"):
                        db.delete_code_snippet(snippet.id)
                        st.rerun()
        finally:
            db.close()
