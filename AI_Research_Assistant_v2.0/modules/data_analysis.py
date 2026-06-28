"""
AI智能科研辅助助手 - 数据分析模块 (高级美化版)
功能：数据上传预览、7种可视化、统计分析、AI报告、报告归档
ChatGPT风格深色主题 + 丝滑交互动画
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
from io import BytesIO
from modules.chat import call_kimi_api
from database.queries import DatabaseManager
from utils.security import get_api_key_for_user
from utils.helpers import format_file_size, estimate_tokens
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


def show_data_analysis_page():
    """显示数据分析页面 - 高级版"""
    # 头部
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 0.5rem;">
        <h2 style="color: #ffffff; margin: 0; font-weight: 700;">📊 智能数据分析助手</h2>
        <span style="
            background: rgba(245,158,11,0.15);
            color: #f59e0b;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
        ">Data Analysis</span>
    </div>
    <p style="color: #8e8ea0; margin: 0 0 1.5rem; font-size: 0.9rem;">支持CSV/Excel/JSON数据文件，提供7种可视化图表和AI分析报告</p>
    """, unsafe_allow_html=True)

    # 数据上传区域
    st.markdown("""
    <h3 style="color: #ffffff; font-weight: 600; margin-bottom: 0.5rem;">📁 数据上传</h3>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "上传数据文件（支持CSV、Excel、JSON）",
        type=['csv', 'xlsx', 'json'],
        key="data_upload"
    )

    if uploaded_file is not None:
        process_data_file(uploaded_file)
    else:
        # 空状态 - 美观的提示
        st.markdown("""
        <div style="
            border: 2px dashed #4d4d4f;
            border-radius: 16px;
            padding: 48px 24px;
            text-align: center;
            background: rgba(64,65,79,0.3);
            margin: 16px 0;
        ">
            <div style="font-size: 3rem; margin-bottom: 16px;">📂</div>
            <div style="color: #c5c5d2; font-size: 1rem; font-weight: 500; margin-bottom: 8px;">
                拖拽文件到此处，或点击上传
            </div>
            <div style="color: #8e8ea0; font-size: 0.85rem;">
                支持 CSV、Excel (.xlsx)、JSON 格式
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_center, _ = st.columns([1, 3])
        with col_center:
            if st.button("🎲 生成示例数据", use_container_width=True, key="gen_sample"):
                np.random.seed(42)
                sample_df = pd.DataFrame({
                    'ID': range(1, 101),
                    'Category': np.random.choice(['A', 'B', 'C'], 100),
                    'Value1': np.random.normal(100, 15, 100),
                    'Value2': np.random.normal(50, 10, 100),
                    'Value3': np.random.exponential(2, 100),
                    'Date': pd.date_range('2024-01-01', periods=100, freq='D')
                })
                st.session_state['current_df'] = sample_df
                st.session_state['current_filename'] = "示例数据.csv"
                st.success("✅ 示例数据已生成！")
                display_data_overview(sample_df, "示例数据.csv", 0)


def process_data_file(uploaded_file):
    """处理上传的数据文件"""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.json'):
            df = pd.read_json(uploaded_file)
        else:
            st.error("不支持的文件格式")
            return

        st.session_state['current_df'] = df
        st.session_state['current_filename'] = uploaded_file.name

        file_size = len(uploaded_file.getvalue())
        display_data_overview(df, uploaded_file.name, file_size)

    except Exception as e:
        st.error(f"❌ 数据加载失败：{e}")


def display_data_overview(df, filename, file_size):
    """展示数据概览 - 高级版"""
    # 成功提示
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(25,195,125,0.08), rgba(25,195,125,0.03));
        border: 1px solid rgba(25,195,125,0.3);
        border-radius: 12px;
        padding: 16px 20px;
        margin: 16px 0;
        display: flex;
        align-items: center;
        gap: 12px;
    ">
        <span style="font-size: 1.3rem;">✅</span>
        <div>
            <div style="color: #ffffff; font-weight: 500;">成功加载数据</div>
            <div style="color: #8e8ea0; font-size: 0.85rem;">{filename} ({format_file_size(file_size)}) · {df.shape[0]}行 × {df.shape[1]}列</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 数据预览
    st.markdown("<h3 style='color: #ffffff; font-weight: 600; margin: 1.5rem 0 1rem;'>📋 数据预览</h3>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📄 前10行", "ℹ️ 数据信息", "📊 统计描述"])

    with tab1:
        st.dataframe(df.head(10), use_container_width=True)

    with tab2:
        # 统计卡片行
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("行数", df.shape[0])
        with col2:
            st.metric("列数", df.shape[1])
        with col3:
            missing = df.isnull().sum().sum()
            st.metric("缺失值", missing, delta=f"{missing/(df.shape[0]*df.shape[1])*100:.1f}%" if missing > 0 else None, delta_color="inverse")

        st.markdown("<p style='color: #8e8ea0; font-size: 0.85rem; margin: 1rem 0 0.5rem;'>数据类型分布</p>", unsafe_allow_html=True)
        dtype_df = pd.DataFrame({
            '列名': df.dtypes.index,
            '类型': df.dtypes.values,
            '非空数量': df.count().values,
            '唯一值': [df[col].nunique() for col in df.columns]
        })
        st.dataframe(dtype_df, use_container_width=True, hide_index=True)

    with tab3:
        numeric_df = df.select_dtypes(include=[np.number])
        if not numeric_df.empty:
            st.dataframe(numeric_df.describe(), use_container_width=True)
        else:
            st.info("没有数值列")

    # 可视化分析
    st.markdown("<div style='height: 1px; background: linear-gradient(90deg, transparent, #4d4d4f, transparent); margin: 2rem 0;'></div>", unsafe_allow_html=True)
    show_visualization(df)

    # AI分析报告
    st.markdown("<div style='height: 1px; background: linear-gradient(90deg, transparent, #4d4d4f, transparent); margin: 2rem 0;'></div>", unsafe_allow_html=True)
    show_ai_report(df, filename)

    # 数据导出
    st.markdown("<div style='height: 1px; background: linear-gradient(90deg, transparent, #4d4d4f, transparent); margin: 2rem 0;'></div>", unsafe_allow_html=True)
    show_export(df)


def show_visualization(df):
    """展示可视化分析 - 高级版"""
    st.markdown("<h3 style='color: #ffffff; font-weight: 600; margin-bottom: 1rem;'>📊 可视化分析</h3>", unsafe_allow_html=True)

    viz_type = st.selectbox(
        "选择可视化类型",
        ["散点图", "柱状图", "直方图", "箱线图", "热力图", "折线图", "饼图"],
        key="viz_type"
    )

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    all_cols = df.columns.tolist()

    # 图表容器
    chart_container = st.container()
    with chart_container:
        if viz_type == "散点图":
            if len(numeric_cols) >= 2:
                col1, col2, col3 = st.columns(3)
                with col1:
                    x_col = st.selectbox("X轴", numeric_cols, key="scatter_x")
                with col2:
                    y_col = st.selectbox("Y轴", numeric_cols, index=min(1, len(numeric_cols)-1), key="scatter_y")
                with col3:
                    color_col = st.selectbox("颜色（可选）", ["无"] + all_cols, key="scatter_c")

                fig = px.scatter(df, x=x_col, y=y_col,
                               color=None if color_col == "无" else color_col,
                               title=f"{x_col} vs {y_col} 散点图",
                               template="plotly_dark")
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#ececf1'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("需要至少2个数值列")

        elif viz_type == "柱状图":
            if categorical_cols and numeric_cols:
                col1, col2 = st.columns(2)
                with col1:
                    x_col = st.selectbox("X轴（分类）", categorical_cols, key="bar_x")
                with col2:
                    y_col = st.selectbox("Y轴（数值）", numeric_cols, key="bar_y")

                fig = px.bar(df, x=x_col, y=y_col, title=f"{x_col} - {y_col} 柱状图",
                           template="plotly_dark", color_discrete_sequence=['#19c37d'])
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#ececf1')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("需要分类列和数值列")

        elif viz_type == "直方图":
            if numeric_cols:
                col1, col2 = st.columns(2)
                with col1:
                    col = st.selectbox("选择列", numeric_cols, key="hist_col")
                with col2:
                    bins = st.slider("分箱数", 5, 100, 20, key="hist_bins")

                fig, ax = plt.subplots(figsize=(10, 6))
                ax.hist(df[col].dropna(), bins=bins, color='#3b82f6', edgecolor='#565869', alpha=0.8)
                ax.set_title(f"{col} 分布直方图", color='#ffffff', fontsize=14, fontweight='bold')
                ax.set_xlabel(col, color='#c5c5d2')
                ax.set_ylabel("频数", color='#c5c5d2')
                ax.tick_params(colors='#8e8ea0')
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#4d4d4f')
                ax.spines['bottom'].set_color('#4d4d4f')
                ax.grid(True, alpha=0.1, color='#ffffff')
                st.pyplot(fig)
            else:
                st.warning("需要数值列")

        elif viz_type == "箱线图":
            if numeric_cols:
                col1, col2 = st.columns(2)
                with col1:
                    col = st.selectbox("选择列", numeric_cols, key="box_col")
                with col2:
                    group_col = st.selectbox("分组列（可选）", ["无"] + categorical_cols, key="box_group")

                fig, ax = plt.subplots(figsize=(10, 6))
                if group_col != "无":
                    df.boxplot(column=col, by=group_col, ax=ax)
                    plt.title(f"{col} 按 {group_col} 分组箱线图", color='#ffffff')
                else:
                    bp = ax.boxplot(df[col].dropna(), patch_artist=True,
                                   boxprops=dict(facecolor='#19c37d', alpha=0.6, color='#4d4d4f'),
                                   medianprops=dict(color='#ffffff', linewidth=2),
                                   whiskerprops=dict(color='#8e8ea0'),
                                   capprops=dict(color='#8e8ea0'),
                                   flierprops=dict(marker='o', markerfacecolor='#f59e0b', markersize=5))
                    ax.set_title(f"{col} 箱线图", color='#ffffff', fontsize=14, fontweight='bold')
                ax.tick_params(colors='#8e8ea0')
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#4d4d4f')
                ax.spines['bottom'].set_color('#4d4d4f')
                ax.grid(True, alpha=0.1, color='#ffffff')
                st.pyplot(fig)
            else:
                st.warning("需要数值列")

        elif viz_type == "热力图":
            if len(numeric_cols) >= 2:
                corr = df[numeric_cols].corr()
                fig, ax = plt.subplots(figsize=(10, 8))
                mask = np.triu(np.ones_like(corr, dtype=bool))
                sns.heatmap(corr, mask=mask, annot=True, cmap='RdYlGn', center=0,
                           square=True, ax=ax, fmt='.2f',
                           cbar_kws={"shrink": 0.8})
                ax.set_title("相关性热力图", color='#ffffff', fontsize=14, fontweight='bold')
                st.pyplot(fig)
            else:
                st.warning("需要至少2个数值列")

        elif viz_type == "折线图":
            if numeric_cols:
                col1, col2 = st.columns(2)
                with col1:
                    x_col = st.selectbox("X轴", all_cols, key="line_x")
                with col2:
                    y_col = st.selectbox("Y轴", numeric_cols, key="line_y")

                fig = px.line(df, x=x_col, y=y_col, title=f"{y_col} 趋势图",
                            template="plotly_dark", color_discrete_sequence=['#19c37d'])
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#ececf1')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("需要数值列")

        elif viz_type == "饼图":
            if categorical_cols:
                col = st.selectbox("选择列", categorical_cols, key="pie_col")
                value_counts = df[col].value_counts().head(10)

                fig = px.pie(values=value_counts.values, names=value_counts.index,
                            title=f"{col} 分布饼图", template="plotly_dark",
                            color_discrete_sequence=px.colors.sequential.Emrld)
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#ececf1')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("需要分类列")


def show_ai_report(df, filename):
    """AI分析报告生成 - 高级版"""
    st.markdown("<h3 style='color: #ffffff; font-weight: 600; margin-bottom: 1rem;'>🤖 AI 分析报告</h3>", unsafe_allow_html=True)

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    col_report, col_history = st.columns([1, 2])
    with col_report:
        if st.button("📊 生成AI分析报告", use_container_width=True, key="gen_report"):
            with st.spinner("⏳ Kimi AI 正在分析数据..."):
                data_summary = (
                    f"数据文件：{filename}，"
                    f"规模：{df.shape[0]}行×{df.shape[1]}列，"
                    f"数值列：{len(numeric_cols)}个，"
                    f"分类列：{len(categorical_cols)}个，"
                    f"缺失值：{df.isnull().sum().sum()}个。"
                )

                try:
                    stats_str = df.describe().to_string()
                except Exception:
                    stats_str = "统计数据生成失败"

                prompt = (
                    f"请根据以下数据信息生成一份专业的数据分析报告：\n\n"
                    f"{data_summary}\n\n"
                    f"统计摘要：\n{stats_str}\n\n"
                    f"请包含：\n"
                    f"1. 数据概览\n"
                    f"2. 关键发现\n"
                    f"3. 数据质量问题诊断\n"
                    f"4. 分析建议（可视化建议、统计检验建议、建模建议）\n"
                    f"5. 下一步行动建议"
                )

                api_key = get_user_api_key()
                model = st.session_state.get("current_model", config.DEFAULT_MODEL)

                report = call_kimi_api(
                    prompt=prompt,
                    system_prompt=config.ANALYSIS_SYSTEM_PROMPT,
                    model=model,
                    api_key=api_key,
                    max_tokens=4096
                )

                st.session_state['current_report'] = report
                st.markdown(report)

                # 保存报告到数据库
                user_id = st.session_state.get("user_id", 0)
                if user_id and user_id > 0:
                    db = DatabaseManager()
                    try:
                        db.save_analysis_report(
                            user_id=user_id,
                            filename=filename,
                            report_content=report,
                            file_size=len(str(df).encode()),
                            row_count=df.shape[0],
                            column_count=df.shape[1],
                            stats_summary=str(df.describe().to_dict()) if numeric_cols else None
                        )
                        st.success("✅ 报告已保存到个人档案")
                    finally:
                        db.close()
    with col_history:
        if st.button("📚 查看历史报告", use_container_width=True, key="view_history"):
            show_report_history()

    # 显示已生成的报告
    if 'current_report' in st.session_state and st.session_state['current_report']:
        st.markdown("""
        <div style="
            background: rgba(64,65,79,0.5);
            border: 1px solid #4d4d4f;
            border-radius: 16px;
            padding: 24px;
            margin-top: 16px;
        ">
        """, unsafe_allow_html=True)
        st.markdown(st.session_state['current_report'])
        st.markdown("</div>", unsafe_allow_html=True)


def show_report_history():
    """显示历史分析报告"""
    user_id = st.session_state.get("user_id", 0)
    if user_id == 0:
        st.info("👤 登录后可查看历史报告")
        return

    db = DatabaseManager()
    try:
        reports, total = db.get_analysis_reports(user_id)

        if not reports:
            st.info("暂无历史报告")
            return

        st.caption(f"共 {total} 条历史报告")
        for report in reports:
            with st.expander(f"📄 {report.filename} - {report.created_at.strftime('%Y-%m-%d %H:%M')}"):
                if report.report_content:
                    st.markdown(report.report_content)
                st.caption(f"数据规模: {report.row_count}行 × {report.column_count}列")

                col_export, col_del = st.columns([1, 1])
                with col_export:
                    report_md = f"# 数据分析报告：{report.filename}\n\n{report.report_content or ''}"
                    st.download_button(
                        "📥 导出报告",
                        report_md.encode('utf-8'),
                        f"report_{report.id}.md",
                        "text/markdown",
                        key=f"export_report_{report.id}"
                    )
                with col_del:
                    if st.button("🗑️ 删除", key=f"del_report_{report.id}"):
                        db.delete_analysis_report(report.id)
                        st.rerun()
    finally:
        db.close()


def show_export(df):
    """数据导出 - 高级版"""
    st.markdown("<h3 style='color: #ffffff; font-weight: 600; margin-bottom: 1rem;'>💾 数据导出</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 下载 CSV",
            csv,
            "processed_data.csv",
            "text/csv",
            use_container_width=True
        )

    with col2:
        try:
            buffer = BytesIO()
            df.to_excel(buffer, index=False, engine='openpyxl')
            st.download_button(
                "📥 下载 Excel",
                buffer.getvalue(),
                "processed_data.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except Exception:
            st.button("📥 Excel（需安装openpyxl）", disabled=True, use_container_width=True)

    with col3:
        json_data = df.to_json(orient='records', force_ascii=False).encode('utf-8')
        st.download_button(
            "📥 下载 JSON",
            json_data,
            "processed_data.json",
            "application/json",
            use_container_width=True
        )
