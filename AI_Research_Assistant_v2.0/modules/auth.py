"""
AI智能科研辅助助手 - 用户认证模块 (高级美化版)
提供：注册、登录、登出、个人设置
ChatGPT风格深色主题 + 丝滑交互动画
"""

import streamlit as st
from database.queries import DatabaseManager
from utils.validators import validate_username, validate_password
from utils.security import get_api_key_for_user
import config


def init_auth_state():
    """初始化认证相关的session state"""
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "auth_page" not in st.session_state:
        st.session_state.auth_page = "login"
    if "current_model" not in st.session_state:
        st.session_state.current_model = config.DEFAULT_MODEL


def is_logged_in() -> bool:
    """检查用户是否已登录（游客 user_id=0 不算登录）"""
    user_id = st.session_state.get("user_id")
    return user_id is not None and user_id != 0


def get_current_user_id() -> int:
    """获取当前登录用户ID"""
    return st.session_state.get("user_id")


def get_current_username() -> str:
    """获取当前登录用户名"""
    return st.session_state.get("username", "")


def login_user(user_id: int, username: str, default_model: str = None):
    """设置用户登录状态"""
    st.session_state.user_id = user_id
    st.session_state.username = username
    if default_model:
        st.session_state.current_model = default_model


def logout_user():
    """清除用户登录状态（登出）"""
    keys_to_clear = ["user_id", "username", "current_model", "messages",
                     "current_conv_id", "page"]
    for key in keys_to_clear:
        if key in st.session_state:
            if key == "messages":
                st.session_state[key] = []
            elif key == "page":
                st.session_state[key] = "🏠 首页"
            else:
                st.session_state[key] = None


def show_login_page():
    """显示登录页面 - ChatGPT风格高级版"""
    # 居中容器
    col1, col2, col3 = st.columns([1, 2.5, 1])

    with col2:
        st.markdown("""
        <div class="auth-page anim-scale-in">
            <div class="auth-title">🔐 账号登录</div>
            <div class="auth-subtitle">登录以使用对话保存、代码收藏等完整功能</div>
        </div>
        """, unsafe_allow_html=True)

        # 使用原生表单但应用CSS样式
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "用户名",
                placeholder="请输入用户名",
                key="login_username"
            )
            password = st.text_input(
                "密码",
                type="password",
                placeholder="请输入密码",
                key="login_password"
            )

            col_login, col_guest = st.columns(2)
            with col_login:
                submit = st.form_submit_button("🔐 登录", use_container_width=True)
            with col_guest:
                guest = st.form_submit_button("🚀 免登录进入", use_container_width=True)

            if submit:
                if not username or not password:
                    st.error("Please fill in username and password")
                    return

                db = DatabaseManager()
                try:
                    user = db.authenticate_user(username, password)
                    if user:
                        login_user(user.id, user.username, user.default_model)
                        st.session_state.page = "🏠 首页"  # 登录后跳转首页
                        st.success("Login successful! Welcome {}".format(username))
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                finally:
                    db.close()

            if guest:
                st.session_state.user_id = 0
                st.session_state.username = "Guest"
                st.session_state.current_model = config.DEFAULT_MODEL
                st.session_state.page = "🏠 首页"  # 游客跳转首页
                st.info("Entered as guest, some features are limited")
                st.rerun()

        st.markdown("""
        <div class="auth-divider"><span>或</span></div>
        """, unsafe_allow_html=True)

        if st.button("📝 没有账号？立即注册", use_container_width=True, key="goto_register"):
            st.session_state.auth_page = "register"
            st.rerun()


def show_register_page():
    """显示注册页面 - ChatGPT风格高级版"""
    col1, col2, col3 = st.columns([1, 2.5, 1])

    with col2:
        st.markdown("""
        <div class="auth-page anim-scale-in">
            <div class="auth-title">📝 账号注册</div>
            <div class="auth-subtitle">创建一个账号，解锁全部科研辅助功能</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("register_form", clear_on_submit=False):
            username = st.text_input(
                "用户名",
                placeholder="3-20位字符，支持中文、字母、数字、下划线",
                key="reg_username"
            )
            password = st.text_input(
                "密码",
                type="password",
                placeholder="至少6位字符",
                key="reg_password"
            )
            password2 = st.text_input(
                "确认密码",
                type="password",
                placeholder="再次输入密码",
                key="reg_password2"
            )

            # 密码强度提示
            password_strength = ""
            if password:
                if len(password) >= 12:
                    password_strength = "<span style='color: #19c37d;'>强</span>"
                elif len(password) >= 8:
                    password_strength = "<span style='color: #f59e0b;'>中</span>"
                else:
                    password_strength = "<span style='color: #ef4444;'>弱</span>"

            if password_strength:
                st.markdown(f"""
                <div style="text-align: right; font-size: 0.8rem; color: #8e8ea0; margin: -8px 0 8px;">
                    密码强度: {password_strength}
                </div>
                """, unsafe_allow_html=True)

            submit = st.form_submit_button("注 册", use_container_width=True)

            if submit:
                valid, msg = validate_username(username)
                if not valid:
                    st.error(f"❌ {msg}")
                    return

                valid, msg = validate_password(password)
                if not valid:
                    st.error(f"❌ {msg}")
                    return

                if password != password2:
                    st.error("❌ 两次输入的密码不一致")
                    return

                db = DatabaseManager()
                try:
                    if db.user_exists(username):
                        st.error("❌ 该用户名已被注册")
                        return

                    user = db.create_user(username=username, password=password)
                    st.success(f"✅ 注册成功！欢迎 {username}，请登录")
                    st.balloons()
                    st.session_state.auth_page = "login"
                    st.rerun()
                finally:
                    db.close()

        st.markdown("""
        <div class="auth-divider"><span>或</span></div>
        """, unsafe_allow_html=True)

        if st.button("🔐 已有账号？去登录", use_container_width=True, key="goto_login"):
            st.session_state.auth_page = "login"
            st.rerun()


def show_sidebar_auth():
    """在侧边栏显示用户信息和操作 - 高级版"""
    if is_logged_in() and get_current_user_id() != 0:
        # 登录用户卡片
        st.markdown(f"""
        <div class="user-card" style="margin: 0.5rem 0;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #19c37d, #3b82f6);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.2rem;
                    flex-shrink: 0;
                ">👤</div>
                <div style="flex: 1; min-width: 0;">
                    <div style="font-size: 0.95rem; font-weight: 600; color: #ffffff; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        {get_current_username()}
                    </div>
                    <div style="font-size: 0.75rem; color: #8e8ea0; margin-top: 2px;">
                        {st.session_state.get("current_model", config.DEFAULT_MODEL)}
                    </div>
                </div>
                <div style="
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: #19c37d;
                    box-shadow: 0 0 6px rgba(25,195,125,0.5);
                    flex-shrink: 0;
                "></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # API Key 设置
        with st.expander("🔑 个人API Key"):
            db = DatabaseManager()
            try:
                user = db.get_user_by_id(get_current_user_id())
                current_key = ""
                if user and user.api_key_encrypted:
                    decrypted = get_api_key_for_user(user)
                    if decrypted:
                        current_key = decrypted

                new_key = st.text_input(
                    "个人Kimi API Key",
                    value=current_key,
                    type="password",
                    placeholder="留空则使用系统默认Key",
                    help="使用个人Key可获得独立的API额度",
                    key="sidebar_api_key"
                )

                col_save, col_clear = st.columns(2)
                with col_save:
                    if st.button("💾 保存", use_container_width=True, key="save_key_btn"):
                        if new_key:
                            db.update_user_api_key(get_current_user_id(), new_key)
                            st.success("✅ 已保存")
                        else:
                            db.update_user_api_key(get_current_user_id(), None)
                            st.success("✅ 已恢复默认")
                        st.rerun()

                with col_clear:
                    if st.button("🗑️ 清除", use_container_width=True, key="clear_key_btn"):
                        db.update_user_api_key(get_current_user_id(), None)
                        st.success("✅ 已恢复默认")
                        st.rerun()

                st.markdown("""
                <div style="font-size: 0.75rem; color: #8e8ea0; margin-top: 8px;">
                    <a href="https://platform.moonshot.cn" target="_blank" style="color: #19c37d; text-decoration: none;">→ 获取个人API Key</a>
                </div>
                """, unsafe_allow_html=True)
            finally:
                db.close()

        # 模型选择
        model = st.selectbox(
            "选择模型",
            config.AVAILABLE_MODELS,
            index=config.AVAILABLE_MODELS.index(st.session_state.get("current_model", config.DEFAULT_MODEL)) if st.session_state.get("current_model", config.DEFAULT_MODEL) in config.AVAILABLE_MODELS else 0,
            key="sidebar_model"
        )
        if model != st.session_state.get("current_model"):
            st.session_state.current_model = model
            db = DatabaseManager()
            try:
                db.update_user_model(get_current_user_id(), model)
            finally:
                db.close()

        st.markdown("<div style='height: 1px; background: linear-gradient(90deg, transparent, #4d4d4f, transparent); margin: 1rem 0;'></div>", unsafe_allow_html=True)

        # 修改密码
        with st.expander("🔒 修改密码"):
            old_password = st.text_input("当前密码", type="password", key="old_pwd")
            new_password = st.text_input("新密码", type="password", key="new_pwd")
            new_password2 = st.text_input("确认新密码", type="password", key="new_pwd2")
            if st.button("🔐 修改密码", use_container_width=True, key="change_pwd_btn"):
                if not old_password or not new_password:
                    st.error("❌ 请填写完整信息")
                elif new_password != new_password2:
                    st.error("❌ 两次新密码不一致")
                elif len(new_password) < 6:
                    st.error("❌ 新密码至少6位")
                else:
                    from utils.security import verify_password, hash_password
                    db = DatabaseManager()
                    try:
                        user = db.get_user_by_id(get_current_user_id())
                        if user and verify_password(old_password, user.password_hash):
                            user.password_hash = hash_password(new_password)
                            db.commit()
                            st.success("✅ 密码修改成功，请重新登录")
                            logout_user()
                            st.rerun()
                        else:
                            st.error("❌ 当前密码错误")
                    finally:
                        db.close()

        st.markdown("<div style='height: 1px; background: linear-gradient(90deg, transparent, #4d4d4f, transparent); margin: 1rem 0;'></div>", unsafe_allow_html=True)

        # 登出按钮
        if st.button("🚪 退出登录", use_container_width=True, key="logout_btn"):
            logout_user()
            st.rerun()
    else:
        # 游客卡片
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #40414f, #3c3d4a);
            border: 1px solid #4d4d4f;
            border-radius: 12px;
            padding: 18px;
            margin: 0.5rem 0;
            text-align: center;
            transition: all 0.25s ease;
        ">
            <div style="
                width: 44px;
                height: 44px;
                border-radius: 50%;
                background: linear-gradient(135deg, #4d4d5f, #565869);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.3rem;
                margin: 0 auto 10px;
            ">👤</div>
            <div style="font-size: 1rem; font-weight: 600; color: #ffffff;">游客模式</div>
            <div style="font-size: 0.8rem; color: #8e8ea0; margin-top: 4px;">登录以使用完整功能</div>
        </div>
        """, unsafe_allow_html=True)

        # 根据当前页面显示不同按钮
        if st.session_state.get("page") == "auth":
            if st.button("← 返回首页", use_container_width=True, key="auth_back_home"):
                st.session_state.page = "🏠 首页"
                st.rerun()
        else:
            if st.button("🔐 登录 / 注册", use_container_width=True, key="auth_nav_btn"):
                st.session_state.page = "auth"
                st.rerun()

        # 模型选择（游客也可用）
        model = st.selectbox(
            "选择模型",
            config.AVAILABLE_MODELS,
            index=0,
            key="guest_model"
        )
        st.session_state.current_model = model

        st.markdown("<div style='height: 1px; background: linear-gradient(90deg, transparent, #4d4d4f, transparent); margin: 1rem 0;'></div>", unsafe_allow_html=True)


def require_login():
    """装饰器功能：要求登录，未登录则显示登录页面"""
    if not is_logged_in():
        show_login_page()
        return False
    return True
