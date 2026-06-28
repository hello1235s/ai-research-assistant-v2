"""
AI智能科研辅助助手 - 数据库操作封装
所有数据库操作集中管理，业务层不直接操作SQL
"""

from sqlalchemy import desc, func
from database.models import (
    get_session, User, Conversation, Message, PaperProject,
    CodeSnippet, AnalysisReport, ApiUsageLog, KnowledgeEntry
)
from utils.security import hash_password, verify_password, encrypt_api_key, decrypt_api_key
from datetime import datetime


class DatabaseManager:
    """数据库管理器 - 提供所有CRUD操作的封装"""

    def __init__(self):
        self.session = get_session()

    def close(self):
        """关闭会话"""
        self.session.close()

    def commit(self):
        """提交事务"""
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    # ========== 用户相关操作 ==========

    def create_user(self, username: str, password: str, api_key: str = None, default_model: str = "kimi-k2.5") -> User:
        """创建新用户"""
        password_hash = hash_password(password)
        api_key_enc = encrypt_api_key(api_key) if api_key else None

        user = User(
            username=username,
            password_hash=password_hash,
            api_key_encrypted=api_key_enc,
            default_model=default_model
        )
        self.session.add(user)
        self.commit()
        return user

    def get_user_by_username(self, username: str) -> User:
        """根据用户名获取用户"""
        return self.session.query(User).filter(User.username == username).first()

    def get_user_by_id(self, user_id: int) -> User:
        """根据ID获取用户"""
        return self.session.query(User).filter(User.id == user_id).first()

    def authenticate_user(self, username: str, password: str) -> User:
        """验证用户登录"""
        user = self.get_user_by_username(username)
        if user and verify_password(password, user.password_hash):
            # 更新最后登录时间
            user.last_login = datetime.now()
            self.commit()
            return user
        return None

    def update_user_api_key(self, user_id: int, api_key: str) -> bool:
        """更新用户API Key"""
        user = self.get_user_by_id(user_id)
        if user:
            user.api_key_encrypted = encrypt_api_key(api_key) if api_key else None
            self.commit()
            return True
        return False

    def get_user_api_key(self, user_id: int) -> str:
        """获取用户解密的API Key（若无则返回None）"""
        user = self.get_user_by_id(user_id)
        if user and user.api_key_encrypted:
            return decrypt_api_key(user.api_key_encrypted)
        return None

    def update_user_model(self, user_id: int, model: str) -> bool:
        """更新用户默认模型"""
        user = self.get_user_by_id(user_id)
        if user:
            user.default_model = model
            self.commit()
            return True
        return False

    def user_exists(self, username: str) -> bool:
        """检查用户名是否已存在"""
        return self.session.query(User).filter(User.username == username).first() is not None

    # ========== 对话相关操作 ==========

    def create_conversation(self, user_id: int, title: str = "新对话", model: str = None, system_prompt: str = None) -> Conversation:
        """创建新对话会话"""
        conv = Conversation(
            user_id=user_id,
            title=title,
            model=model or "kimi-k2.5",
            system_prompt=system_prompt
        )
        self.session.add(conv)
        self.commit()
        return conv

    def get_conversation(self, conv_id: int, user_id: int = None) -> Conversation:
        """获取对话（可选验证用户权限）"""
        query = self.session.query(Conversation).filter(Conversation.id == conv_id)
        if user_id:
            query = query.filter(Conversation.user_id == user_id)
        return query.first()

    def get_user_conversations(self, user_id: int, page: int = 1, per_page: int = 20):
        """获取用户的对话列表（按更新时间倒序）"""
        offset = (page - 1) * per_page
        conversations = self.session.query(Conversation) \
            .filter(Conversation.user_id == user_id) \
            .order_by(desc(Conversation.is_pinned), desc(Conversation.updated_at)) \
            .offset(offset).limit(per_page).all()
        total = self.session.query(Conversation).filter(Conversation.user_id == user_id).count()
        return conversations, total

    def update_conversation_title(self, conv_id: int, title: str) -> bool:
        """更新对话标题"""
        conv = self.session.query(Conversation).filter(Conversation.id == conv_id).first()
        if conv:
            conv.title = title
            conv.updated_at = datetime.now()
            self.commit()
            return True
        return False

    def toggle_conversation_pin(self, conv_id: int) -> bool:
        """切换对话置顶状态"""
        conv = self.session.query(Conversation).filter(Conversation.id == conv_id).first()
        if conv:
            conv.is_pinned = not conv.is_pinned
            self.commit()
            return True
        return False

    def delete_conversation(self, conv_id: int) -> bool:
        """删除对话及其所有消息"""
        conv = self.session.query(Conversation).filter(Conversation.id == conv_id).first()
        if conv:
            self.session.delete(conv)
            self.commit()
            return True
        return False

    def add_message(self, conv_id: int, role: str, content: str, token_count: int = None, latency_ms: int = None) -> Message:
        """添加消息到对话"""
        msg = Message(
            conversation_id=conv_id,
            role=role,
            content=content,
            token_count=token_count,
            latency_ms=latency_ms
        )
        self.session.add(msg)
        # 同时更新对话的updated_at
        conv = self.session.query(Conversation).filter(Conversation.id == conv_id).first()
        if conv:
            conv.updated_at = datetime.now()
        self.commit()
        return msg

    def get_conversation_messages(self, conv_id: int):
        """获取对话的所有消息"""
        return self.session.query(Message) \
            .filter(Message.conversation_id == conv_id) \
            .order_by(Message.timestamp).all()

    def auto_title_conversation(self, conv_id: int, first_user_message: str):
        """自动设置对话标题（基于第一条用户消息的前20字）"""
        title = first_user_message[:20] + "..." if len(first_user_message) > 20 else first_user_message
        self.update_conversation_title(conv_id, title)

    # ========== 论文项目相关操作 ==========

    def create_paper_project(self, user_id: int, title: str, paper_type: str = "本科课程论文", topic: str = None) -> PaperProject:
        """创建论文项目"""
        project = PaperProject(
            user_id=user_id,
            title=title,
            paper_type=paper_type,
            topic=topic
        )
        self.session.add(project)
        self.commit()
        return project

    def get_paper_projects(self, user_id: int):
        """获取用户的所有论文项目"""
        return self.session.query(PaperProject) \
            .filter(PaperProject.user_id == user_id) \
            .order_by(desc(PaperProject.updated_at)).all()

    def get_paper_project(self, project_id: int, user_id: int = None) -> PaperProject:
        """获取论文项目"""
        query = self.session.query(PaperProject).filter(PaperProject.id == project_id)
        if user_id:
            query = query.filter(PaperProject.user_id == user_id)
        return query.first()

    def update_paper_project(self, project_id: int, **kwargs) -> bool:
        """更新论文项目"""
        project = self.session.query(PaperProject).filter(PaperProject.id == project_id).first()
        if project:
            for key, value in kwargs.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            project.updated_at = datetime.now()
            self.commit()
            return True
        return False

    def delete_paper_project(self, project_id: int) -> bool:
        """删除论文项目"""
        project = self.session.query(PaperProject).filter(PaperProject.id == project_id).first()
        if project:
            self.session.delete(project)
            self.commit()
            return True
        return False

    # ========== 代码片段相关操作 ==========

    def create_code_snippet(self, user_id: int, title: str, code: str, language: str = "python",
                            description: str = None, tags: str = None, source: str = None) -> CodeSnippet:
        """保存代码片段"""
        snippet = CodeSnippet(
            user_id=user_id,
            title=title,
            code=code,
            language=language,
            description=description,
            tags=tags,
            source=source
        )
        self.session.add(snippet)
        self.commit()
        return snippet

    def get_code_snippets(self, user_id: int, language: str = None, tag: str = None):
        """获取代码片段列表（支持筛选）"""
        query = self.session.query(CodeSnippet).filter(CodeSnippet.user_id == user_id)
        if language:
            query = query.filter(CodeSnippet.language == language)
        if tag:
            query = query.filter(CodeSnippet.tags.like(f"%{tag}%"))
        return query.order_by(desc(CodeSnippet.created_at)).all()

    def get_code_snippet(self, snippet_id: int) -> CodeSnippet:
        """获取单个代码片段"""
        return self.session.query(CodeSnippet).filter(CodeSnippet.id == snippet_id).first()

    def delete_code_snippet(self, snippet_id: int) -> bool:
        """删除代码片段"""
        snippet = self.session.query(CodeSnippet).filter(CodeSnippet.id == snippet_id).first()
        if snippet:
            self.session.delete(snippet)
            self.commit()
            return True
        return False

    # ========== 分析报告相关操作 ==========

    def save_analysis_report(self, user_id: int, filename: str, report_content: str,
                             file_size: int = None, row_count: int = None, column_count: int = None,
                             stats_summary: str = None) -> AnalysisReport:
        """保存分析报告"""
        report = AnalysisReport(
            user_id=user_id,
            filename=filename,
            file_size=file_size,
            row_count=row_count,
            column_count=column_count,
            report_content=report_content,
            stats_summary=stats_summary
        )
        self.session.add(report)
        self.commit()
        return report

    def get_analysis_reports(self, user_id: int, page: int = 1, per_page: int = 10):
        """获取用户的分析报告列表"""
        offset = (page - 1) * per_page
        reports = self.session.query(AnalysisReport) \
            .filter(AnalysisReport.user_id == user_id) \
            .order_by(desc(AnalysisReport.created_at)) \
            .offset(offset).limit(per_page).all()
        total = self.session.query(AnalysisReport).filter(AnalysisReport.user_id == user_id).count()
        return reports, total

    def get_analysis_report(self, report_id: int) -> AnalysisReport:
        """获取单个分析报告"""
        return self.session.query(AnalysisReport).filter(AnalysisReport.id == report_id).first()

    def delete_analysis_report(self, report_id: int) -> bool:
        """删除分析报告"""
        report = self.session.query(AnalysisReport).filter(AnalysisReport.id == report_id).first()
        if report:
            self.session.delete(report)
            self.commit()
            return True
        return False

    # ========== API用量日志相关操作 ==========

    def log_api_usage(self, user_id: int = None, endpoint: str = "chat.completions",
                      model: str = "", input_tokens: int = 0, output_tokens: int = 0,
                      latency_ms: int = None, status: str = "success", error_msg: str = None):
        """记录API调用日志"""
        log = ApiUsageLog(
            user_id=user_id,
            endpoint=endpoint,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            status=status,
            error_msg=error_msg
        )
        self.session.add(log)
        self.commit()
        return log

    def get_user_usage_stats(self, user_id: int):
        """获取用户用量统计"""
        total_calls = self.session.query(ApiUsageLog) \
            .filter(ApiUsageLog.user_id == user_id, ApiUsageLog.status == "success").count()
        total_input = self.session.query(func.sum(ApiUsageLog.input_tokens)) \
            .filter(ApiUsageLog.user_id == user_id).scalar() or 0
        total_output = self.session.query(func.sum(ApiUsageLog.output_tokens)) \
            .filter(ApiUsageLog.user_id == user_id).scalar() or 0

        # 按模型统计
        model_stats = self.session.query(
            ApiUsageLog.model,
            func.count(ApiUsageLog.id).label("call_count"),
            func.sum(ApiUsageLog.input_tokens).label("input_tokens"),
            func.sum(ApiUsageLog.output_tokens).label("output_tokens")
        ).filter(ApiUsageLog.user_id == user_id, ApiUsageLog.status == "success") \
         .group_by(ApiUsageLog.model).all()

        return {
            "total_calls": total_calls,
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "model_breakdown": [
                {"model": m.model, "calls": m.call_count, "input_tokens": m.input_tokens or 0, "output_tokens": m.output_tokens or 0}
                for m in model_stats
            ]
        }

    # ========== 知识库相关操作 ==========

    def search_knowledge(self, query: str, category: str = None, limit: int = 10):
        """搜索知识库条目（基于关键词匹配）"""
        query_lower = f"%{query.lower()}%"
        q = self.session.query(KnowledgeEntry).filter(
            (KnowledgeEntry.title.ilike(query_lower)) |
            (KnowledgeEntry.content.ilike(query_lower)) |
            (KnowledgeEntry.keywords.ilike(query_lower))
        )
        if category:
            q = q.filter(KnowledgeEntry.category == category)
        return q.limit(limit).all()

    def get_knowledge_categories(self):
        """获取所有知识库分类"""
        return [cat[0] for cat in self.session.query(KnowledgeEntry.category).distinct().all()]

    def get_knowledge_by_category(self, category: str):
        """获取分类下的所有条目"""
        return self.session.query(KnowledgeEntry) \
            .filter(KnowledgeEntry.category == category) \
            .order_by(KnowledgeEntry.section_path).all()

    def bulk_insert_knowledge(self, entries: list):
        """批量插入知识库条目"""
        for entry_data in entries:
            entry = KnowledgeEntry(**entry_data)
            self.session.add(entry)
        self.commit()

    def count_knowledge_entries(self) -> int:
        """统计知识库条目总数"""
        return self.session.query(KnowledgeEntry).count()

    def clear_knowledge_base(self):
        """清空知识库（用于重新导入）"""
        self.session.query(KnowledgeEntry).delete()
        self.commit()
