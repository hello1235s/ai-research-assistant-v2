# AI智能科研辅助助手 v2.0

> 人工智能导论课程设计 | 基于 Kimi + Streamlit + SQLite 的 Web 应用
> 开发者：张驰 | 学号：202530463528 | 班级：AI与低空技术3班

---

## 项目简介

本系统基于 **Kimi 大语言模型** 和 **Streamlit Web 框架**，面向 AI 与低空技术领域的科研辅助场景，提供智能对话、代码辅助、数据分析、论文写作和知识库五大核心功能。

**v2.0 重大升级：** 引入 SQLite 数据库持久化存储，实现用户系统、对话历史保存、API Key安全加密、知识库结构化检索等核心增强。

### 核心特色

- 🗄️ **SQLite数据库** — 对话历史、用户数据、代码收藏、报告归档全部持久化
- 🔐 **用户认证系统** — 注册/登录/登出，bcrypt密码加密
- 🔒 **API Key安全** — AES-256加密存储，前端永不暴露明文
- 💬 **多会话管理** — 对话列表、置顶、重命名、删除
- 📚 **结构化知识库** — 5大领域Markdown导入数据库，支持全文检索
- ⭐ **代码收藏** — AI生成的代码一键保存到个人库
- 📊 **报告归档** — 数据分析报告自动保存，历史回溯
- 🎨 **ChatGPT 风格深色主题** — 沉浸式科研体验
- 🚀 **流式输出** — AI 回复实时逐字显示
- ✨ **丰富交互动画** — 卡片悬停、按钮光晕等丝滑效果

---

## 目录结构

```
ai_research_v2/
├── app.py                          # 主应用入口
├── config.py                       # 全局配置（API/数据库/安全参数）
├── requirements.txt                # 依赖清单
├── database/                       # 数据库模块
│   ├── __init__.py
│   ├── models.py                   # SQLAlchemy 数据模型（8张表）
│   ├── queries.py                  # 数据库操作封装（CRUD）
│   └── init_db.py                  # 数据库初始化+知识库导入脚本
├── utils/                          # 工具模块
│   ├── __init__.py
│   ├── security.py                 # bcrypt密码哈希 + AES加密
│   ├── validators.py               # 输入验证（用户名/密码/API Key）
│   └── helpers.py                  # 通用工具（token估算/时间格式化）
├── modules/                        # 功能模块
│   ├── __init__.py
│   ├── auth.py                     # 用户认证（登录/注册/登出）
│   ├── chat.py                     # 智能对话（持久化多会话）
│   ├── code_assist.py              # 代码辅助（生成/解释/调试/收藏）
│   ├── data_analysis.py            # 数据分析（7种可视化/AI报告）
│   ├── paper_writing.py            # 论文写作（结构/摘要/文献/项目）
│   └── knowledge_base.py           # 知识库（结构化检索/分类浏览）
├── knowledge_base/                 # 知识库源文件（Markdown）
│   ├── 01_python_basics.md
│   ├── 02_data_analysis_visualization.md
│   ├── 03_machine_learning.md
│   ├── 04_paper_writing.md
│   └── 05_uav_low_altitude_tech.md
├── data/                           # 示例数据集目录
└── docs/                           # 技术文档
    └── 数据库设计说明.md
```

---

## 快速启动

### 方式一：双击启动（推荐）

直接双击 `start.bat`，脚本会自动检测 Python 环境、安装依赖并启动应用。

启动后访问：`http://localhost:8501`

### 方式二：命令行启动

```bash
# 1. 进入项目目录
cd ai_research_v2

# 2. 安装依赖（首次运行）
pip install -r requirements.txt

# 3. 初始化数据库（导入知识库，只需执行一次）
python database/init_db.py

# 4. 启动应用
streamlit run app.py
```

启动后访问：`http://localhost:8501`

**注意：**
- 首次运行会自动创建SQLite数据库文件（`research_assistant.db`）
- 知识库导入只需执行一次，后续启动无需重复
- 系统已预置默认 Kimi API Key，无需额外配置即可使用

---

## 功能模块

| 模块 | 核心功能 | v2.0数据库增强 |
|------|----------|---------------|
| **智能对话** | 多轮对话、科研问答、快捷问题 | 对话历史永久保存、多会话管理 |
| **代码辅助** | 代码生成、代码解释、代码调试 | 代码收藏到个人库 |
| **数据分析** | 数据上传、描述统计、7种可视化图表 | 报告归档、历史回溯 |
| **论文写作** | 结构规划、摘要生成、文献整理 | 论文项目持久化管理 |
| **知识库** | 5个领域文档检索与浏览 | 结构化存储、全文检索 |
| **用户系统** | — | 注册/登录/密码加密/API Key安全存储 |

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| AI 引擎 | Kimi API（Moonshot AI） | 大语言模型，支持流式输出 |
| Web 框架 | Streamlit 1.28+ | 纯 Python 构建 Web 界面 |
| 数据库 | SQLite + SQLAlchemy 2.0 | 零配置嵌入式关系型数据库 |
| 安全 | bcrypt + cryptography | 密码哈希 + AES对称加密 |
| 数据处理 | Pandas、NumPy | 数据读取、清洗、统计 |
| 可视化 | Matplotlib、Plotly、Seaborn | 7 种图表类型 |
| 文档生成 | python-docx | 报告自动生成 |
| 机器学习 | scikit-learn | 分类、回归、聚类 |

---

## 数据库设计

### 数据表清单（8张表）

| 表名 | 用途 | 核心字段 |
|------|------|---------|
| `users` | 用户账户 | username, password_hash(bcrypt), api_key_encrypted(AES) |
| `conversations` | 对话会话 | user_id, title, model, is_pinned |
| `messages` | 消息记录 | conversation_id, role, content, token_count, latency_ms |
| `paper_projects` | 论文项目 | user_id, title, paper_type, status, content |
| `code_snippets` | 代码收藏 | user_id, title, language, code, tags |
| `analysis_reports` | 分析报告 | user_id, filename, report_content, stats_summary |
| `api_usage_logs` | API调用日志 | user_id, model, input_tokens, output_tokens, latency_ms |
| `knowledge_entries` | 知识库条目 | category, title, content, source_file, keywords |

完整的数据库设计文档见：`docs/数据库设计说明.md`

---

## 开发者信息

- **姓名**：张驰
- **学号**：202530463528
- **班级**：AI 与低空技术 3 班
- **学院**：自动化科学与工程学院
- **课程**：人工智能导论
- **完成日期**：2026-06-21

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0 | 2026-06-21 | 初版，Streamlit纯内存实现 |
| v2.0 | 2026-06-21 | 添加SQLite数据库、用户系统、对话持久化、API Key加密、知识库结构化 |
