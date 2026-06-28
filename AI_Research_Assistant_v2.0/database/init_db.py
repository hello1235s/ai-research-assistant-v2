"""
AI智能科研辅助助手 - 数据库初始化脚本
首次运行时执行：自动建表 + 知识库导入
用法：python database/init_db.py
"""

import os
import sys
import re
import io

# 修复Windows终端编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 将上级目录加入路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import create_all_tables, SessionLocal
from database.queries import DatabaseManager
from config import KNOWLEDGE_BASE_DIR


def parse_markdown_file(filepath: str, category: str) -> list:
    """
    解析Markdown文件，提取结构化条目
    返回: [{"category", "title", "content", "source_file", "section_path", "keywords"}, ...]
    """
    entries = []
    source_file = os.path.basename(filepath)

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  [警告] 无法读取文件 {filepath}: {e}")
        return entries

    # 按二级标题 (## ) 分割文档
    sections = re.split(r'\n(?=##\s)', content)

    for idx, section in enumerate(sections):
        section = section.strip()
        if not section:
            continue

        # 提取标题
        title_match = re.match(r'^#{1,3}\s+(.+)$', section, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else f"章节{idx+1}"

        # 提取关键词（从代码块和加粗文本中提取）
        keywords = set()
        # 加粗文本
        bold_words = re.findall(r'\*\*(.+?)\*\*', section)
        keywords.update(bold_words[:10])  # 最多10个
        # 代码引用
        code_words = re.findall(r'`(.+?)`', section)
        keywords.update(code_words[:5])  # 最多5个

        entries.append({
            "category": category,
            "title": title,
            "content": section,
            "source_file": source_file,
            "section_path": f"{idx+1}",
            "keywords": ", ".join(list(keywords)[:15])
        })

    return entries


def init_knowledge_base(db: DatabaseManager):
    """初始化知识库 - 从Markdown文件导入到数据库"""
    print("[知识库] 正在导入知识库...")

    # 检查是否已导入
    existing_count = db.count_knowledge_entries()
    if existing_count > 0:
        print(f"  [信息] 知识库已有 {existing_count} 条记录，跳过导入")
        print(f"         如需重新导入，请删除数据库文件后重新运行")
        return

    if not os.path.exists(KNOWLEDGE_BASE_DIR):
        print(f"  [警告] 知识库目录不存在: {KNOWLEDGE_BASE_DIR}")
        return

    # 知识库文件映射: (文件名, 分类标识)
    kb_files = [
        ("01_python_basics.md", "python_basics"),
        ("02_data_analysis_visualization.md", "data_analysis"),
        ("03_machine_learning.md", "machine_learning"),
        ("04_paper_writing.md", "paper_writing"),
        ("05_uav_low_altitude_tech.md", "uav_tech"),
    ]

    total_entries = 0
    for filename, category in kb_files:
        filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  [警告] 文件不存在: {filename}")
            continue

        print(f"  [解析] {filename}...", end=" ")
        entries = parse_markdown_file(filepath, category)
        if entries:
            db.bulk_insert_knowledge(entries)
            total_entries += len(entries)
            print(f"[OK] {len(entries)} 条")
        else:
            print("[警告] 无内容")

    print(f"[知识库] 导入完成，共 {total_entries} 条记录")


def init_database():
    """完整的数据库初始化流程"""
    print("=" * 60)
    print("[初始化] AI智能科研辅助助手 - 数据库初始化")
    print("=" * 60)

    # 1. 创建数据表
    print("\n[建表] 创建数据表...")
    create_all_tables()
    print("  [OK] 所有数据表已创建")

    # 2. 初始化知识库
    db = DatabaseManager()
    try:
        init_knowledge_base(db)
        print("\n[完成] 数据库初始化成功！")
    except Exception as e:
        print(f"\n[错误] 初始化出错: {e}")
        raise
    finally:
        db.close()

    # 3. 显示数据库文件信息
    from config import DATABASE_PATH
    if os.path.exists(DATABASE_PATH):
        size_kb = os.path.getsize(DATABASE_PATH) / 1024
        print(f"[文件] 数据库: {DATABASE_PATH}")
        print(f"[大小] {size_kb:.1f} KB")

    print("\n" + "=" * 60)
    print("[启动] 可以启动应用了: streamlit run app.py")
    print("=" * 60)


if __name__ == "__main__":
    init_database()
