"""
AI智能科研辅助助手 - 论文写作模块 (高级美化版)
功能：结构规划、摘要生成、文献整理、写作检查、项目持久化
ChatGPT风格深色主题 + 丝滑交互动画
"""

import streamlit as st
from modules.chat import call_kimi_api
from database.queries import DatabaseManager
from utils.security import get_api_key_for_user
import config


def get_user_api_key():
    """获取当前用户可用的API Key"""
    user_id = st.session_state.get("user_id", 0)
    if user_id and user_id > 0:
        db = DatabaseManager()
        try:
            user = db.get_user_by_id(user_id)
            if user:
                return get_api_key_for_user(user)
        finally:
            db.close()
    return config.DEFAULT_API_KEY


def show_paper_writing_page():
    """显示论文写作页面 - 高级版"""
    # 头部
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 0.5rem;">
        <h2 style="color: #ffffff; margin: 0; font-weight: 700;">📄 智能论文写作辅助助手</h2>
        <span style="
            background: rgba(168,85,247,0.15);
            color: #a855f7;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
        ">Paper Writing</span>
    </div>
    <p style="color: #8e8ea0; margin: 0 0 1.5rem; font-size: 0.9rem;">AI驱动的论文结构规划、摘要生成和写作检查</p>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 结构规划", "✍️ 摘要生成", "📚 文献整理", "🔍 写作检查", "📁 我的论文"])

    api_key = get_user_api_key()
    model = st.session_state.get("current_model", config.DEFAULT_MODEL)

    # ========== Tab 1: 结构规划 ==========
    with tab1:
        st.markdown("<h3 style='color: #ffffff; font-weight: 600; margin-bottom: 1rem;'>🎯 论文结构规划</h3>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            paper_type = st.selectbox(
                "论文类型",
                ["本科课程论文", "本科毕业设计", "学术论文", "技术报告", "综述论文"],
                key="paper_type"
            )
        with col2:
            research_topic = st.text_input("研究主题", placeholder="请输入研究主题...", key="paper_topic")

        # 预定义结构模板
        structures = {
            "本科课程论文": [
                "1. 引言（研究背景、目的、意义）",
                "2. 相关工作/文献综述",
                "3. 方法/系统设计",
                "4. 实验/结果分析",
                "5. 结论与展望",
                "6. 参考文献"
            ],
            "本科毕业设计": [
                "1. 绪论（背景、现状、意义）",
                "2. 需求分析",
                "3. 总体设计",
                "4. 详细设计与实现",
                "5. 系统测试",
                "6. 总结与展望",
                "7. 参考文献"
            ],
            "学术论文": [
                "1. 摘要（中英文）",
                "2. 关键词",
                "3. 引言",
                "4. 文献综述",
                "5. 方法",
                "6. 实验",
                "7. 结果分析",
                "8. 讨论",
                "9. 结论",
                "10. 参考文献"
            ],
            "技术报告": [
                "1. 摘要",
                "2. 项目背景",
                "3. 技术方案",
                "4. 实现过程",
                "5. 测试结果",
                "6. 总结与建议",
                "7. 附录"
            ],
            "综述论文": [
                "1. 摘要",
                "2. 引言",
                "3. 研究背景",
                "4. 国内外研究现状",
                "5. 关键技术综述",
                "6. 发展趋势与挑战",
                "7. 总结与展望",
                "8. 参考文献"
            ]
        }

        if st.button("📋 生成结构", use_container_width=True, key="gen_structure"):
            if research_topic:
                structure = structures.get(paper_type, structures["本科课程论文"])

                # 美观的结构展示
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(59,130,246,0.08), rgba(168,85,247,0.05));
                    border: 1px solid #4d4d4f;
                    border-radius: 16px;
                    padding: 24px 28px;
                    margin: 16px 0;
                ">
                    <div style="
                        display: flex;
                        align-items: center;
                        gap: 8px;
                        margin-bottom: 20px;
                        padding-bottom: 16px;
                        border-bottom: 1px solid #4d4d4f;
                    ">
                        <span style="font-size: 1.3rem;">📄</span>
                        <span style="color: #ffffff; font-weight: 600; font-size: 1.1rem;">{paper_type}</span>
                        <span style="color: #8e8ea0;">|</span>
                        <span style="color: #c5c5d2;">{research_topic}</span>
                    </div>
                    <div style="color: #8e8ea0; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">
                        建议结构
                    </div>
                """, unsafe_allow_html=True)

                for item in structure:
                    st.markdown(f"""
                    <div style="
                        display: flex;
                        align-items: center;
                        gap: 12px;
                        padding: 10px 0;
                        border-bottom: 1px solid rgba(77,77,79,0.3);
                        color: #ececf1;
                    ">
                        <span style="
                            width: 28px;
                            height: 28px;
                            border-radius: 50%;
                            background: rgba(25,195,125,0.15);
                            color: #19c37d;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 0.8rem;
                            font-weight: 600;
                            flex-shrink: 0;
                        ">{item.split('.')[0]}</span>
                        <span>{item.split('.', 1)[1].strip()}</span>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

                # 写作建议
                st.markdown("""
                <div style="
                    background: rgba(245,158,11,0.05);
                    border: 1px solid rgba(245,158,11,0.2);
                    border-radius: 12px;
                    padding: 20px;
                    margin-top: 16px;
                ">
                    <div style="color: #f59e0b; font-weight: 600; margin-bottom: 12px;">📝 写作建议</div>
                    <ul style="color: #c5c5d2; margin: 0; padding-left: 20px; line-height: 2;">
                        <li>每个章节应有明确的目标和范围</li>
                        <li>章节之间要有逻辑衔接</li>
                        <li>图表编号要连续（图1、图2...）</li>
                        <li>公式编号要规范（式(1)、式(2)...）</li>
                        <li>引用文献需在正文中标注</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

                # 保存到项目
                user_id = st.session_state.get("user_id", 0)
                if user_id and user_id > 0:
                    if st.button("💾 保存为论文项目", use_container_width=True, key="save_project"):
                        db = DatabaseManager()
                        try:
                            project = db.create_paper_project(
                                user_id=user_id,
                                title=research_topic,
                                paper_type=paper_type,
                                topic=research_topic
                            )
                            st.success(f"✅ 论文项目已创建（ID: {project.id}）")
                        finally:
                            db.close()
            else:
                st.warning("请输入研究主题")

    # ========== Tab 2: 摘要生成 ==========
    with tab2:
        st.markdown("<h3 style='color: #ffffff; font-weight: 600; margin-bottom: 1rem;'>✍️ 摘要生成</h3>", unsafe_allow_html=True)

        abstract_title = st.text_input("论文标题", placeholder="请输入论文标题...", key="abstract_title")
        abstract_content = st.text_area(
            "论文内容概要",
            placeholder="简要描述研究背景、方法、结果和结论...",
            height=150,
            key="abstract_content"
        )

        if st.button("✨ 生成摘要", use_container_width=True, key="gen_abstract"):
            if abstract_title and abstract_content:
                with st.spinner("⏳ Kimi AI 正在生成摘要..."):
                    prompt = (
                        f"请根据以下论文信息生成规范的中英文摘要和关键词：\n\n"
                        f"论文标题：{abstract_title}\n\n"
                        f"内容概要：{abstract_content}\n\n"
                        f"要求：\n"
                        f"1. 中文摘要300字左右，包含研究目的、方法、结果、结论四要素\n"
                        f"2. 英文摘要与中文对应\n"
                        f"3. 提供3-5个中英文关键词\n"
                        f"4. 符合学术规范"
                    )
                    abstract_result = call_kimi_api(
                        prompt=prompt,
                        system_prompt=config.PAPER_SYSTEM_PROMPT,
                        model=model,
                        api_key=api_key,
                        max_tokens=2048
                    )
                    st.markdown(abstract_result)
            else:
                st.warning("请填写标题和内容概要")

    # ========== Tab 3: 文献整理 ==========
    with tab3:
        st.markdown("<h3 style='color: #ffffff; font-weight: 600; margin-bottom: 1rem;'>📚 文献整理</h3>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            ref_format = st.selectbox("引用格式", ["GB/T 7714", "APA", "MLA", "IEEE"], key="ref_format")
        with col2:
            ref_type = st.selectbox("文献类型", ["期刊论文", "专著", "会议论文", "学位论文", "网络资源"], key="ref_type")

        ref_info = st.text_area(
            "文献信息",
            placeholder="格式：作者. 标题. 期刊/出版社, 年份, 卷(期): 页码.",
            height=100,
            key="ref_info"
        )

        with st.expander("📋 逐项填写（可选）"):
            col_a, col_b = st.columns(2)
            with col_a:
                ref_author = st.text_input("作者", key="ref_author")
                ref_title = st.text_input("标题", key="ref_title")
                ref_year = st.text_input("年份", key="ref_year")
            with col_b:
                ref_journal = st.text_input("期刊/出版社", key="ref_journal")
                ref_volume = st.text_input("卷(期)", key="ref_volume")
                ref_pages = st.text_input("页码", key="ref_pages")

            if ref_author and ref_title:
                assembled = f"{ref_author}. {ref_title}"
                if ref_journal:
                    assembled += f". {ref_journal}"
                if ref_year:
                    assembled += f", {ref_year}"
                if ref_volume:
                    assembled += f", {ref_volume}"
                if ref_pages:
                    assembled += f": {ref_pages}"
                st.caption(f"自动组装：{assembled}")
                
                def use_assembled():
                    st.session_state["ref_info"] = assembled
                
                st.button("使用组装内容", on_click=use_assembled, key="use_assembled_btn")

        if st.button("📝 格式化引用", use_container_width=True, key="format_ref"):
            if ref_info:
                formats = {
                    "GB/T 7714": format_gbt7714(ref_author or ref_info, ref_title, ref_journal, ref_year, ref_volume, ref_pages, ref_type),
                    "APA": format_apa(ref_author, ref_title, ref_journal, ref_year, ref_volume, ref_pages),
                    "MLA": format_mla(ref_author, ref_title, ref_journal, ref_year, ref_pages),
                    "IEEE": format_ieee(ref_author, ref_title, ref_journal, ref_year, ref_volume, ref_pages)
                }

                result = formats.get(ref_format, ref_info)

                # 美观的引用结果展示
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(25,195,125,0.05), rgba(59,130,246,0.03));
                    border: 1px solid #4d4d4f;
                    border-radius: 12px;
                    padding: 20px;
                    margin-top: 16px;
                ">
                    <div style="color: #8e8ea0; font-size: 0.8rem; margin-bottom: 8px;">{ref_format} 格式</div>
                </div>
                """, unsafe_allow_html=True)
                st.code(result)
            else:
                st.warning("请输入文献信息")

    # ========== Tab 4: 写作检查 ==========
    with tab4:
        st.markdown("<h3 style='color: #ffffff; font-weight: 600; margin-bottom: 1rem;'>🔍 写作规范检查</h3>", unsafe_allow_html=True)

        check_text = st.text_area(
            "粘贴需要检查的文本",
            placeholder="在此粘贴论文段落...",
            height=200,
            key="check_text"
        )

        if st.button("🔍 检查", use_container_width=True, key="check_writing"):
            if check_text:
                checks = []
                word_count = len(check_text)
                checks.append(f"✅ 字数统计：<strong style='color: #ffffff;'>{word_count}</strong> 字")

                # 口语化词汇检查
                informal_words = ["的", "了", "呢", "吧", "啊", "哦", "嗯"]
                found_informal = []
                for word in informal_words:
                    count = check_text.count(word)
                    if count > 5:
                        found_informal.append(f"'{word}'出现{count}次")
                if found_informal:
                    checks.append(f"⚠️ 口语化词汇：{', '.join(found_informal[:3])}")

                # 标点检查
                cn_punct = sum(check_text.count(c) for c in "，。！？；：")
                en_punct = sum(check_text.count(c) for c in ",.!?;:'\"")
                if en_punct > cn_punct:
                    checks.append("⚠️ 英文标点较多，建议使用中文标点")
                else:
                    checks.append("✅ 标点符号使用规范")

                # 段落长度检查
                paragraphs = [p for p in check_text.split('\n') if p.strip()]
                long_paras = sum(1 for p in paragraphs if len(p) > 300)
                if long_paras > 0:
                    checks.append(f"ℹ️ 有 <strong style='color: #ffffff;'>{long_paras}</strong> 段文字较长（>300字），建议适当分段")

                # 检查结果展示
                st.markdown("""
                <div style="
                    background: rgba(64,65,79,0.5);
                    border: 1px solid #4d4d4f;
                    border-radius: 16px;
                    padding: 24px;
                    margin: 16px 0;
                ">
                    <div style="color: #ffffff; font-weight: 600; font-size: 1.1rem; margin-bottom: 16px;">📋 检查结果</div>
                """, unsafe_allow_html=True)

                for check in checks:
                    icon = "✅" if "✅" in check else "⚠️" if "⚠️" in check else "ℹ️"
                    color = "#19c37d" if "✅" in check else "#f59e0b" if "⚠️" in check else "#3b82f6"
                    st.markdown(f"""
                    <div style="
                        display: flex;
                        align-items: center;
                        gap: 8px;
                        padding: 8px 0;
                        border-bottom: 1px solid rgba(77,77,79,0.3);
                        color: #c5c5d2;
                    ">
                        <span style="color: {color};">{icon}</span>
                        <span>{check.replace('✅ ', '').replace('⚠️ ', '').replace('ℹ️ ', '')}</span>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

                # 改进建议
                st.markdown("""
                <div style="
                    background: rgba(25,195,125,0.05);
                    border: 1px solid rgba(25,195,125,0.2);
                    border-radius: 12px;
                    padding: 20px;
                    margin-top: 16px;
                ">
                    <div style="color: #19c37d; font-weight: 600; margin-bottom: 12px;">💡 改进建议</div>
                    <ul style="color: #c5c5d2; margin: 0; padding-left: 20px; line-height: 2;">
                        <li>使用学术化表达，避免口语化</li>
                        <li>注意段落逻辑衔接（使用过渡句）</li>
                        <li>确保数据引用准确（标注来源）</li>
                        <li>检查图表引用是否对应正文</li>
                        <li>避免绝对化表述（如'最好'、'必然'）</li>
                        <li>使用被动语态描述实验方法</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

                # ===== AI 深度写作检查 =====
                st.markdown("<div style='height: 1px; background: linear-gradient(90deg, transparent, #4d4d4f, transparent); margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
                if st.button("🤖 AI 深度分析", use_container_width=True, key="ai_check_writing"):
                    with st.spinner("⏳ Kimi AI 正在深度分析写作质量..."):
                        prompt = (
                            f"请对以下学术文本进行深度写作质量检查，用中文回答：\n\n"
                            f"{check_text}\n\n"
                            f"请从以下方面分析：\n"
                            f"1. 语法和用词错误（具体指出错误位置和修正建议）\n"
                            f"2. 学术表达规范性（是否口语化、是否使用专业术语）\n"
                            f"3. 逻辑连贯性（段落衔接、论证逻辑）\n"
                            f"4. 结构完整性（是否包含必要的学术要素）\n"
                            f"5. 改进建议（逐条给出具体修改建议）"
                        )
                        ai_result = call_kimi_api(
                            prompt=prompt,
                            system_prompt="你是一名资深学术写作专家，擅长中英文论文写作质量评估。请用中文详细分析文本问题并给出具体修改建议。",
                            model=model,
                            api_key=api_key,
                            max_tokens=4096
                        )
                        st.markdown("""
                        <div style="
                            background: linear-gradient(135deg, rgba(168,85,247,0.05), rgba(59,130,246,0.03));
                            border: 1px solid #4d4d4f;
                            border-radius: 16px;
                            padding: 24px;
                            margin-top: 16px;
                        ">
                            <div style="color: #a855f7; font-weight: 600; font-size: 1.1rem; margin-bottom: 16px;">🤖 AI 深度分析</div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(ai_result)
            else:
                st.warning("请粘贴需要检查的文本")

    # ========== Tab 5: 我的论文 ==========
    with tab5:
        st.markdown("<h3 style='color: #ffffff; font-weight: 600; margin-bottom: 1rem;'>📁 我的论文项目</h3>", unsafe_allow_html=True)

        user_id = st.session_state.get("user_id", 0)
        if user_id == 0:
            st.info("👤 登录后可管理论文项目")
            return

        db = DatabaseManager()
        try:
            projects = db.get_paper_projects(user_id)

            if not projects:
                st.info("暂无论文项目，在「结构规划」中创建你的第一个项目吧")
                return

            for project in projects:
                status_colors = {
                    "已完成": ("🟢", "#19c37d"),
                    "进行中": ("🟡", "#f59e0b"),
                    "已归档": ("⚪", "#8e8ea0")
                }
                icon, color = status_colors.get(project.status, ("⚪", "#8e8ea0"))

                with st.expander(f"{icon} {project.title}"):
                    st.markdown(f"""
                    <div style="
                        display: flex;
                        align-items: center;
                        gap: 12px;
                        margin-bottom: 12px;
                    ">
                        <span style="
                            background: {color}20;
                            color: {color};
                            padding: 2px 10px;
                            border-radius: 8px;
                            font-size: 0.8rem;
                            font-weight: 500;
                        ">{project.status}</span>
                        <span style="color: #8e8ea0; font-size: 0.85rem;">{project.paper_type}</span>
                        <span style="color: #4d4d4f;">|</span>
                        <span style="color: #8e8ea0; font-size: 0.85rem;">{project.created_at.strftime('%Y-%m-%d')}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    if project.topic:
                        st.write(f"**主题**: {project.topic}")

                    # ===== 论文章节内容编辑器 =====
                    st.markdown("<div style='height: 1px; background: linear-gradient(90deg, transparent, #4d4d4f, transparent); margin: 1rem 0;'></div>", unsafe_allow_html=True)
                    import json
                    current_content = {}
                    if project.content:
                        try:
                            current_content = json.loads(project.content)
                        except Exception:
                            current_content = {}

                    with st.expander("📝 编辑论文内容"):
                        abstract = st.text_area("摘要", value=current_content.get("abstract", ""), height=80, key=f"abstract_{project.id}")
                        introduction = st.text_area("引言", value=current_content.get("introduction", ""), height=100, key=f"intro_{project.id}")
                        method = st.text_area("方法", value=current_content.get("method", ""), height=100, key=f"method_{project.id}")
                        results = st.text_area("结果", value=current_content.get("results", ""), height=100, key=f"results_{project.id}")
                        conclusion = st.text_area("结论", value=current_content.get("conclusion", ""), height=80, key=f"conclusion_{project.id}")

                        if st.button("💾 保存内容", key=f"save_content_{project.id}"):
                            content_json = json.dumps({
                                "title": project.title,
                                "abstract": abstract,
                                "introduction": introduction,
                                "method": method,
                                "results": results,
                                "conclusion": conclusion
                            }, ensure_ascii=False)
                            db.update_paper_project(project.id, content=content_json)
                            st.success("✅ 内容已保存")
                            st.rerun()

                    # 预览
                    if project.content and any(current_content.values()):
                        with st.expander("📖 预览论文内容"):
                            section_names = {
                                "abstract": "摘要",
                                "introduction": "引言",
                                "method": "方法",
                                "results": "结果",
                                "conclusion": "结论"
                            }
                            for section_key, section_name in section_names.items():
                                text = current_content.get(section_key, "")
                                if text:
                                    st.markdown(f"**{section_name}**")
                                    st.markdown(text)
                                    st.markdown("---")

                    new_status = st.selectbox(
                        "更新状态",
                        ["进行中", "已完成", "已归档"],
                        index=["进行中", "已完成", "已归档"].index(project.status) if project.status in ["进行中", "已完成", "已归档"] else 0,
                        key=f"status_{project.id}"
                    )
                    if new_status != project.status:
                        db.update_paper_project(project.id, status=new_status)
                        st.rerun()

                    if st.button("🗑️ 删除项目", key=f"del_paper_{project.id}"):
                        db.delete_paper_project(project.id)
                        st.rerun()
        finally:
            db.close()


# ========== 引用格式函数 ==========

def format_gbt7714(author, title, journal, year, volume, pages, ref_type="期刊论文"):
    """GB/T 7714 格式"""
    type_map = {
        "期刊论文": "[J]",
        "专著": "[M]",
        "会议论文": "[C]",
        "学位论文": "[D]",
        "网络资源": "[EB/OL]"
    }
    type_marker = type_map.get(ref_type, "[J]")
    parts = [f"[1] {author}. {title}{type_marker}"]
    if journal:
        parts.append(f". {journal}")
    if year:
        parts.append(f", {year}")
    if volume:
        parts.append(f", {volume}")
    if pages:
        parts.append(f": {pages}")
    parts.append(".")
    return "".join(parts)


def format_apa(author, title, journal, year, volume, pages):
    """APA 格式"""
    parts = [f"{author}. ({year}). {title}."]
    if journal:
        parts.append(f" {journal}")
    if volume:
        parts.append(f", {volume}")
    if pages:
        parts.append(f", {pages}")
    parts.append(".")
    return "".join(parts)


def format_mla(author, title, journal, year, pages):
    """MLA 格式"""
    parts = [f'{author}. "{title}."']
    if journal:
        parts.append(f" {journal}")
    if year:
        parts.append(f", {year}")
    if pages:
        parts.append(f", pp. {pages}")
    parts.append(".")
    return "".join(parts)


def format_ieee(author, title, journal, year, volume, pages):
    """IEEE 格式"""
    parts = [f"[1] {author}, \"{title},\""]
    if journal:
        parts.append(f" {journal}")
    if volume:
        parts.append(f", vol. {volume}")
    if pages:
        parts.append(f", pp. {pages}")
    if year:
        parts.append(f", {year}")
    parts.append(".")
    return "".join(parts)
