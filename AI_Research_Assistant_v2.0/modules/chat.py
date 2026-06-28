"""
AI智能科研辅助助手 - 智能对话模块 (高级美化版)
核心升级：对话历史永久保存、多会话管理、侧边栏会话列表
ChatGPT风格深色主题 + 丝滑交互动画
"""

import streamlit as st
from openai import OpenAI
import time
from database.queries import DatabaseManager
from utils.security import get_api_key_for_user
from utils.helpers import estimate_tokens, format_relative_time
from utils.validators import validate_conversation_title
import config


def call_kimi_api(prompt, system_prompt=None, model=None, api_key=None, temperature=1, max_tokens=2048, stream=False):
    """调用Kimi API获取AI回复，支持流式输出"""
    try:
        client = OpenAI(
            api_key=api_key or config.DEFAULT_API_KEY,
            base_url=config.KIMI_BASE_URL,
        )
        response = client.chat.completions.create(
            model=model or config.DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt or config.DEFAULT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
        )
        if stream:
            def content_generator():
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            return content_generator()
        else:
            return response.choices[0].message.content
    except Exception as e:
        error_msg = f"❌ API调用失败：{str(e)}\n\n请检查：\n1. API Key是否有效\n2. 网络连接是否正常\n3. API额度是否充足"
        if stream:
            def error_generator():
                yield error_msg
            return error_generator()
        return error_msg


def init_chat_state():
    """初始化对话模块的session state"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_conv_id" not in st.session_state:
        st.session_state.current_conv_id = None
    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None


def get_user_api_key():
    """获取当前用户可用的API Key"""
    user_id = st.session_state.get("user_id")
    if user_id and user_id > 0:
        db = DatabaseManager()
        try:
            user = db.get_user_by_id(user_id)
            if user:
                return get_api_key_for_user(user)
        finally:
            db.close()
    return config.DEFAULT_API_KEY


def load_conversation(conv_id: int):
    """从数据库加载对话到session state"""
    user_id = st.session_state.get("user_id", 0)
    db = DatabaseManager()
    try:
        conv = db.get_conversation(conv_id, user_id=user_id if user_id and user_id > 0 else None)
        if conv:
            st.session_state.current_conv_id = conv_id
            st.session_state.messages = []
            for msg in conv.messages:
                st.session_state.messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            if conv.model:
                st.session_state.current_model = conv.model
    finally:
        db.close()


def save_message(conv_id: int, role: str, content: str, latency_ms: int = None):
    """保存消息到数据库"""
    tokens = estimate_tokens(content)
    db = DatabaseManager()
    try:
        db.add_message(conv_id, role, content, token_count=tokens, latency_ms=latency_ms)
    finally:
        db.close()


def create_new_conversation(title: str = "新对话") -> int:
    """创建新对话并返回ID"""
    user_id = st.session_state.get("user_id", 0)
    model = st.session_state.get("current_model", config.DEFAULT_MODEL)
    db = DatabaseManager()
    try:
        conv = db.create_conversation(
            user_id=user_id if user_id and user_id > 0 else 1,
            title=title,
            model=model,
            system_prompt=config.CHAT_SYSTEM_PROMPT
        )
        return conv.id
    finally:
        db.close()


def show_conversation_sidebar():
    """显示对话历史侧边栏 - 高级版"""
    user_id = st.session_state.get("user_id", 0)
    if user_id == 0:
        return

    with st.sidebar:
        st.markdown("""
        <div style="
            font-size: 0.75rem;
            color: #8e8ea0;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin: 1rem 0 0.5rem;
            padding-left: 4px;
        ">对话历史</div>
        """, unsafe_allow_html=True)

        # 新建对话按钮
        if st.button("➕ 新建对话", use_container_width=True, key="new_conv_btn"):
            st.session_state.messages = []
            st.session_state.current_conv_id = None
            st.session_state.pending_prompt = None
            st.rerun()

        # 获取对话列表
        db = DatabaseManager()
        try:
            conversations, total = db.get_user_conversations(user_id=user_id, per_page=50)

            if not conversations:
                st.caption("暂无历史对话")
                return

            for conv in conversations:
                pin_icon = "📌 " if conv.is_pinned else "💬 "
                time_str = format_relative_time(conv.updated_at)
                title = conv.title or "新对话"
                is_active = conv.id == st.session_state.get("current_conv_id")

                # 自定义对话按钮样式
                btn_style = "primary" if is_active else "secondary"
                btn_label = f"{pin_icon}{title}"

                col_btn, col_menu = st.columns([6, 1])
                with col_btn:
                    if st.button(btn_label, use_container_width=True, key=f"conv_{conv.id}", type=btn_style):
                        load_conversation(conv.id)
                        st.rerun()

                with col_menu:
                    if st.button("⋮", key=f"conv_menu_{conv.id}"):
                        st.session_state[f"show_menu_{conv.id}"] = not st.session_state.get(f"show_menu_{conv.id}", False)

                # 操作菜单
                if st.session_state.get(f"show_menu_{conv.id}", False):
                    menu_col1, menu_col2, menu_col3 = st.columns(3)
                    with menu_col1:
                        if st.button("📌", key=f"pin_{conv.id}", help="置顶"):
                            db.toggle_conversation_pin(conv.id)
                            st.session_state[f"show_menu_{conv.id}"] = False
                            st.rerun()
                    with menu_col2:
                        if st.button("✏️", key=f"rename_{conv.id}", help="重命名"):
                            st.session_state[f"renaming_{conv.id}"] = True
                    with menu_col3:
                        if st.button("🗑️", key=f"del_{conv.id}", help="删除"):
                            db.delete_conversation(conv.id)
                            if st.session_state.get("current_conv_id") == conv.id:
                                st.session_state.messages = []
                                st.session_state.current_conv_id = None
                            st.rerun()

                # 重命名输入框
                if st.session_state.get(f"renaming_{conv.id}", False):
                    new_title = st.text_input(
                        "新标题",
                        value=title,
                        key=f"rename_input_{conv.id}",
                        label_visibility="collapsed"
                    )
                    if st.button("保存", key=f"save_rename_{conv.id}"):
                        clean_title = validate_conversation_title(new_title)
                        db.update_conversation_title(conv.id, clean_title)
                        st.session_state[f"renaming_{conv.id}"] = False
                        st.session_state[f"show_menu_{conv.id}"] = False
                        st.rerun()

        finally:
            db.close()


def show_chat_page():
    """显示智能对话主页面 - ChatGPT风格高级版"""
    init_chat_state()

    # 头部区域
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 0.5rem;">
        <h2 style="color: #ffffff; margin: 0; font-weight: 700;">💬 智能科研对话助手</h2>
        <span style="
            background: rgba(25,195,125,0.15);
            color: #19c37d;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
        ">AI Powered</span>
    </div>
    <p style="color: #8e8ea0; margin: 0 0 1.5rem; font-size: 0.9rem;">基于Kimi大模型，支持多轮对话和历史保存</p>
    """, unsafe_allow_html=True)

    # 快捷问题 - 使用网格布局
    st.markdown("<p style='color: #8e8ea0; font-size: 0.85rem; margin-bottom: 8px;'>📌 快捷问题</p>", unsafe_allow_html=True)

    quick_questions = [
        ("解释PID控制原理", "请详细解释PID控制原理，包括比例、积分、微分三个环节的作用，以及参数调节方法。请用中文回答。"),
        ("无人机导航方法", "无人机有哪些常用的导航方法？请分别介绍GPS导航、惯性导航、视觉导航、组合导航的原理、优缺点和适用场景。"),
        ("Python数据分析技巧", "Python数据分析有哪些实用技巧？请介绍Pandas高效操作、数据清洗方法、可视化技巧，并给出代码示例。"),
    ]

    qcol1, qcol2, qcol3 = st.columns(3)
    for i, (label, prompt_text) in enumerate(quick_questions):
        col = [qcol1, qcol2, qcol3][i]
        with col:
            if st.button(label, key=f"quick_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": prompt_text})
                st.session_state.pending_prompt = prompt_text
                if not st.session_state.get("current_conv_id"):
                    conv_id = create_new_conversation(label)
                    st.session_state.current_conv_id = conv_id
                    save_message(conv_id, "user", prompt_text)
                st.rerun()

    st.markdown("<div style='height: 1px; background: linear-gradient(90deg, transparent, #4d4d4f, transparent); margin: 1.5rem 0;'></div>", unsafe_allow_html=True)

    # 如果数据库中有当前对话的消息但session中没有，加载它们
    current_conv_id = st.session_state.get("current_conv_id")
    if current_conv_id and not st.session_state.messages:
        load_conversation(current_conv_id)
        st.rerun()

    # 渲染所有消息
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 处理待响应的prompt
    if st.session_state.pending_prompt:
        prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None

        api_key = get_user_api_key()
        model = st.session_state.get("current_model", config.DEFAULT_MODEL)

        conv_id = st.session_state.get("current_conv_id")
        is_new_conv = False
        if not conv_id:
            first_msg = st.session_state.messages[-1]["content"] if st.session_state.messages else prompt
            conv_id = create_new_conversation(validate_conversation_title(first_msg[:30]))
            st.session_state.current_conv_id = conv_id
            is_new_conv = True

        if is_new_conv:
            db = DatabaseManager()
            try:
                for msg in st.session_state.messages[:-1]:
                    if msg["role"] == "user":
                        save_message(conv_id, msg["role"], msg["content"])
            finally:
                db.close()

        # 同步缺失的消息
        db = DatabaseManager()
        try:
            existing_msgs = db.get_conversation_messages(conv_id)
            existing_content = {m.content for m in existing_msgs}
            for msg in st.session_state.messages:
                if msg["content"] not in existing_content:
                    save_message(conv_id, msg["role"], msg["content"])
                    existing_content.add(msg["content"])
        finally:
            db.close()

        # 调用API并流式输出
        start_time = time.time()

        # ===== RAG 增强：检索知识库 =====
        system_prompt = config.CHAT_SYSTEM_PROMPT
        if config.ENABLE_KNOWLEDGE_RAG:
            try:
                db_rag = DatabaseManager()
                kb_results = db_rag.search_knowledge(prompt, limit=3)
                if kb_results:
                    kb_context = "\n\n".join([
                        f"【{entry.title}】\n{entry.content[:600]}"
                        for entry in kb_results
                    ])
                    system_prompt = (
                        f"{config.CHAT_SYSTEM_PROMPT}\n\n"
                        f"以下是与用户问题相关的知识库参考资料，请结合这些资料回答（如果资料与问题无关，则忽略）：\n\n"
                        f"{kb_context}"
                    )
                db_rag.close()
            except Exception:
                pass

        with st.chat_message("assistant"):
            stream_response = call_kimi_api(
                prompt=prompt,
                system_prompt=system_prompt,
                model=model,
                api_key=api_key,
                temperature=1,
                max_tokens=2048,
                stream=True
            )
            response = st.write_stream(stream_response)

        latency = int((time.time() - start_time) * 1000)

        # 保存AI回复
        save_message(conv_id, "assistant", response, latency_ms=latency)
        st.session_state.messages.append({"role": "assistant", "content": response})

        # 记录API用量
        if st.session_state.get("user_id", 0) > 0:
            db = DatabaseManager()
            try:
                db.log_api_usage(
                    user_id=st.session_state.user_id,
                    endpoint="chat.completions",
                    model=model,
                    input_tokens=estimate_tokens(prompt),
                    output_tokens=estimate_tokens(response),
                    latency_ms=latency
                )
            finally:
                db.close()

        # 更新对话标题
        db = DatabaseManager()
        try:
            conv = db.get_conversation(conv_id)
            if conv and conv.title == "新对话" and st.session_state.messages:
                first_user_msg = next((m["content"] for m in st.session_state.messages if m["role"] == "user"), None)
                if first_user_msg:
                    db.update_conversation_title(conv_id, validate_conversation_title(first_user_msg[:30]))
        finally:
            db.close()

        st.rerun()

    # 输入框
    if prompt := st.chat_input("请输入您的问题..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.pending_prompt = prompt
        st.rerun()

    # 底部操作栏
    col_spacer, col_clear = st.columns([8, 1])
    with col_clear:
        if st.button("🗑️", key="clear_chat", help="清除当前对话"):
            st.session_state.messages = []
            st.session_state.pending_prompt = None
            st.session_state.current_conv_id = None
            st.rerun()
