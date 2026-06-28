"""
AI智能科研辅助助手 - API用量统计模块
功能：展示用户API调用统计、按模型分组、可视化图表
"""

import streamlit as st
import plotly.express as px
from database.queries import DatabaseManager
from utils.helpers import format_relative_time
import config


def show_usage_stats_page():
    """显示API用量统计页面"""
    user_id = st.session_state.get("user_id")
    if user_id is None or user_id == 0:
        st.info("👤 登录后可查看个人用量统计")
        return

    # 头部
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 0.5rem;">
        <h2 style="color: #ffffff; margin: 0; font-weight: 700;">📊 API 用量统计</h2>
        <span style="
            background: rgba(59,130,246,0.15);
            color: #3b82f6;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
        ">Usage Analytics</span>
    </div>
    <p style="color: #8e8ea0; margin: 0 0 1.5rem; font-size: 0.9rem;">查看您的 API 调用统计和 Token 用量分析</p>
    """, unsafe_allow_html=True)

    if user_id == 0:
        st.info("👤 登录后可查看个人用量统计")
        return

    db = DatabaseManager()
    try:
        stats = db.get_user_usage_stats(user_id)
        total_calls = stats["total_calls"]
        total_input = stats["total_input_tokens"]
        total_output = stats["total_output_tokens"]
        model_breakdown = stats["model_breakdown"]

        if total_calls == 0:
            st.info("暂无 API 调用记录，快去使用智能对话功能吧！")
            return

        # 核心统计卡片
        st.markdown("""
        <h3 style="color: #ffffff; font-weight: 600; margin: 1.5rem 0 1rem;">📈 核心指标</h3>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        cards = [
            ("💬", "总调用次数", total_calls, "#19c37d"),
            ("📥", "输入 Token", f"{total_input:,}", "#3b82f6"),
            ("📤", "输出 Token", f"{total_output:,}", "#f59e0b"),
            ("📊", "总 Token", f"{total_input + total_output:,}", "#a855f7"),
        ]
        for col, (icon, label, value, color) in zip([col1, col2, col3, col4], cards):
            with col:
                st.markdown(f"""
                <div style="
                    background: {color}10;
                    border: 1px solid {color}30;
                    border-radius: 16px;
                    padding: 20px;
                    text-align: center;
                    transition: all 0.25s ease;
                ">
                    <div style="font-size: 1.5rem; margin-bottom: 8px;">{icon}</div>
                    <div style="font-size: 1.6rem; font-weight: 800; color: {color};">{value}</div>
                    <div style="font-size: 0.8rem; color: #8e8ea0; margin-top: 4px;">{label}</div>
                </div>
                """, unsafe_allow_html=True)

        # 按模型分组统计
        if model_breakdown:
            st.markdown("""
            <div style='height: 1px; background: linear-gradient(90deg, transparent, #4d4d4f, transparent); margin: 2rem 0;'></div>
            <h3 style="color: #ffffff; font-weight: 600; margin: 1.5rem 0 1rem;">🤖 按模型统计</h3>
            """, unsafe_allow_html=True)

            col_chart, col_table = st.columns([2, 1])

            with col_chart:
                # 饼图：按模型调用次数
                fig = px.pie(
                    values=[m["calls"] for m in model_breakdown],
                    names=[m["model"] for m in model_breakdown],
                    title="各模型调用次数占比",
                    template="plotly_dark",
                    color_discrete_sequence=px.colors.sequential.Emrld
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#ececf1',
                    title_font_color='#ffffff'
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_table:
                st.markdown("""
                <table style="width: 100%; border-collapse: separate; border-spacing: 0;">
                    <thead>
                        <tr>
                            <th style="padding: 12px 10px; text-align: left;">模型</th>
                            <th style="padding: 12px 10px; text-align: right;">调用</th>
                            <th style="padding: 12px 10px; text-align: right;">Token</th>
                        </tr>
                    </thead>
                    <tbody>
                """, unsafe_allow_html=True)
                for m in model_breakdown:
                    model_total = (m["input_tokens"] or 0) + (m["output_tokens"] or 0)
                    st.markdown(f"""
                        <tr>
                            <td style="padding: 10px; color: #ececf1;">{m['model']}</td>
                            <td style="padding: 10px; text-align: right; color: #19c37d; font-weight: 600;">{m['calls']}</td>
                            <td style="padding: 10px; text-align: right; color: #3b82f6;">{model_total:,}</td>
                        </tr>
                    """, unsafe_allow_html=True)
                st.markdown("</tbody></table>", unsafe_allow_html=True)

            # 柱状图：各模型 Token 用量对比
            st.markdown("""
            <h3 style="color: #ffffff; font-weight: 600; margin: 1.5rem 0 1rem;">📊 Token 用量对比</h3>
            """, unsafe_allow_html=True)

            fig2 = px.bar(
                x=[m["model"] for m in model_breakdown],
                y=[(m["input_tokens"] or 0) + (m["output_tokens"] or 0) for m in model_breakdown],
                title="各模型总 Token 用量",
                template="plotly_dark",
                color_discrete_sequence=['#3b82f6']
            )
            fig2.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#ececf1',
                title_font_color='#ffffff'
            )
            st.plotly_chart(fig2, use_container_width=True)

        # 最近调用记录
        st.markdown("""
        <div style='height: 1px; background: linear-gradient(90deg, transparent, #4d4d4f, transparent); margin: 2rem 0;'></div>
        <h3 style="color: #ffffff; font-weight: 600; margin: 1.5rem 0 1rem;">🕐 最近调用记录</h3>
        """, unsafe_allow_html=True)

        from sqlalchemy import desc
        from database.models import ApiUsageLog
        recent_logs = db.session.query(ApiUsageLog).filter(
            ApiUsageLog.user_id == user_id
        ).order_by(desc(ApiUsageLog.timestamp)).limit(20).all()

        if recent_logs:
            for log in recent_logs:
                status_icon = "✅" if log.status == "success" else "❌"
                status_color = "#19c37d" if log.status == "success" else "#ef4444"
                time_str = format_relative_time(log.timestamp)
                st.markdown(f"""
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    padding: 10px 14px;
                    background: #40414f;
                    border: 1px solid #4d4d4f;
                    border-radius: 10px;
                    margin: 6px 0;
                ">
                    <span style="color: {status_color}; font-size: 1rem;">{status_icon}</span>
                    <div style="flex: 1; min-width: 0;">
                        <div style="color: #ececf1; font-size: 0.85rem; font-weight: 500;">{log.model} · {log.endpoint}</div>
                        <div style="color: #8e8ea0; font-size: 0.75rem; margin-top: 2px;">
                            In: {(log.input_tokens or 0):,} · Out: {(log.output_tokens or 0):,} · Latency: {(log.latency_ms or 0)}ms
                        </div>
                    </div>
                    <div style="color: #8e8ea0; font-size: 0.75rem; flex-shrink: 0;">{time_str}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("暂无调用记录")

    finally:
        db.close()
