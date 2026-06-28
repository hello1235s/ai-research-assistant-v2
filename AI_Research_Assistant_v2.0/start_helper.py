#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI科研助手 v2.0 - 一键启动助手
由 start.bat 传入的 Daimon Python 3.12 执行
"""
import sys
import os
import subprocess
import time
import warnings

# Suppress numpy warnings globally (must be set before any numpy import)
os.environ["PYTHONWARNINGS"] = "ignore"
warnings.filterwarnings("ignore")

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_DIR)


def print_title():
    print()
    print("=" * 60)
    print("  AI 智能科研辅助助手 v2.0")
    print("  Developer: Zhang Chi | AI & Low-Altitude Tech 3")
    print("=" * 60)
    print()


def check_python():
    """检查当前 Python 版本"""
    print("[Step 1] Check Python environment...")
    v = sys.version_info
    if v.major < 3 or (v.major == 3 and v.minor < 10):
        print("[ERROR] Python version too low, need 3.10+")
        print("  Current: {}.{}.{}".format(v.major, v.minor, v.micro))
        print("[HINT] Please install Python 3.10+ from https://www.python.org/downloads/")
        return False
    if v.major == 3 and v.minor >= 13:
        print("[WARN]   Python {}.{}.{} - some packages may not be fully compatible".format(v.major, v.minor, v.micro))
        print("[HINT]   If you encounter errors, use Python 3.10-3.12 for best compatibility")
    else:
        print("[OK]     Python {}.{}.{}".format(v.major, v.minor, v.micro))
    return True


def check_package(module_name, display_name):
    """检查单个包是否已安装，并验证是否能正常导入"""
    v = sys.version_info
    
    # Python 3.13+: numpy C-level crash on Windows, use subprocess to protect main process
    if v.major == 3 and v.minor >= 13:
        try:
            # Run import in a child process with -W ignore
            env = os.environ.copy()
            env["PYTHONWARNINGS"] = "ignore"
            result = subprocess.run(
                [sys.executable, "-W", "ignore", "-c",
                 "import {mod}; print('OK')".format(mod=module_name)],
                capture_output=True, text=True, timeout=15, env=env
            )
            if result.returncode == 0 and "OK" in result.stdout:
                print("[OK]     {}".format(display_name))
                return True
            else:
                # Import failed, check if pip installed it
                result2 = subprocess.run(
                    [sys.executable, "-m", "pip", "show", module_name],
                    capture_output=True, text=True, timeout=15, env=env
                )
                if result2.returncode == 0:
                    print("[WARN]   {} - installed but may not work on 3.13".format(display_name))
                    return True
                else:
                    print("[MISS]   {}".format(display_name))
                    return False
        except Exception as e:
            print("[WARN]   {} - check error: {}".format(display_name, e))
            return True
    else:
        try:
            __import__(module_name)
            print("[OK]     {}".format(display_name))
            return True
        except ImportError:
            print("[MISS]   {}".format(display_name))
            return False
        except Exception as e:
            print("[WARN]   {} - import error: {}".format(display_name, e))
            return False


def install_dependencies():
    """安装缺失的依赖包"""
    print("\n[Step 2] Check dependencies...")

    packages = [
        ("sqlalchemy", "SQLAlchemy"),
        ("bcrypt", "bcrypt"),
        ("cryptography", "cryptography"),
        ("openai", "OpenAI"),
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
        ("streamlit", "Streamlit"),
        ("matplotlib", "Matplotlib"),
        ("plotly", "Plotly"),
        ("seaborn", "Seaborn"),
        ("openpyxl", "openpyxl"),
        ("docx", "python-docx"),
        ("sklearn", "scikit-learn"),
    ]

    missing = []
    for mod, name in packages:
        if not check_package(mod, name):
            missing.append(name)

    v = sys.version_info
    force_reinstall = (v.major == 3 and v.minor >= 13)

    if missing or force_reinstall:
        if missing:
            print("\n[INFO]   {} packages missing, installing...".format(len(missing)))
        if force_reinstall:
            print("\n[WARN]   Python 3.13+ detected, forcing dependency reinstall...")
        print("[HINT]   This may take 1-3 minutes, please wait...")

        # Python 3.13: force upgrade numpy first (fixes MINGW-W64 compatibility)
        if force_reinstall:
            print("[INFO]   Upgrading numpy for Python 3.13 compatibility...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "numpy",
                "--index-url", "https://pypi.tuna.tsinghua.edu.cn/simple",
                "--trusted-host", "pypi.tuna.tsinghua.edu.cn",
                "-q"
            ], capture_output=True, text=True)
            print("[INFO]   Numpy upgraded, now installing all dependencies...")

        req_file = os.path.join(PROJECT_DIR, "requirements.txt")
        
        # Use Tsinghua mirror for faster download in China
        cmd = [
            sys.executable, "-m", "pip", "install", "-r", req_file,
            "--index-url", "https://pypi.tuna.tsinghua.edu.cn/simple",
            "--trusted-host", "pypi.tuna.tsinghua.edu.cn",
            "-q"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print("[ERROR]  Dependency installation failed")
            print(result.stderr)
            return False
        print("[OK]     Dependencies installed")
    else:
        print("[OK]     All dependencies ready")
    return True


def init_database():
    """检查并初始化数据库"""
    print("\n[Step 3] Check database...")
    db_path = os.path.join(PROJECT_DIR, "research_assistant.db")

    if not os.path.exists(db_path):
        print("[INFO]   Database not found, initializing...")
        init_script = os.path.join(PROJECT_DIR, "database", "init_db.py")
        result = subprocess.run([sys.executable, init_script], capture_output=True, text=True)

        if result.returncode != 0:
            print("[ERROR]  Database initialization failed")
            print(result.stderr)
            return False
        print("[OK]     Database initialized")
    else:
        print("[OK]     Database exists (research_assistant.db)")
    return True


def kill_old_streamlit():
    """关闭占用 8501 端口的旧进程（包括所有 Python 进程）"""
    print("[Step 0] Checking for old Streamlit processes...")
    
    # 方法1：通过端口查找并关闭
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True, text=True
        )
        killed = 0
        for line in result.stdout.split("\n"):
            if ":8501" in line and "LISTENING" in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    if pid.isdigit():
                        subprocess.run(
                            ["taskkill", "/F", "/PID", pid],
                            capture_output=True
                        )
                        killed += 1
        if killed > 0:
            print("[OK]     Closed {} old process(es) on port 8501".format(killed))
            time.sleep(2)
        else:
            print("[OK]     No old processes on port 8501")
    except Exception as e:
        print("[WARN]   Could not check old processes: {}".format(e))
    
    # 方法2：也关闭所有名为 streamlit.exe 的进程
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq streamlit.exe", "/FO", "CSV"],
            capture_output=True, text=True
        )
        if "streamlit.exe" in result.stdout:
            subprocess.run(
                ["taskkill", "/F", "/IM", "streamlit.exe"],
                capture_output=True
            )
            print("[OK]     Killed all streamlit.exe processes")
            time.sleep(1)
    except Exception:
        pass


def start_app():
    """启动 Streamlit - 直接在前台运行，显示输出"""
    print("\n[Step 4] Starting Streamlit...")
    print("=" * 60)
    print("  Please open browser: http://localhost:8501")
    print("  (Ctrl+C to stop)")
    print("=" * 60)
    print()

    app_file = os.path.join(PROJECT_DIR, "app.py")
    
    v = sys.version_info
    if v.major == 3 and v.minor >= 13:
        # Python 3.13: suppress numpy warnings with -W ignore
        cmd = [sys.executable, "-W", "ignore", "-m", "streamlit", "run", app_file, "--server.port=8501"]
        print("[INFO]   Python 3.13+ detected, suppressing warnings...")
    else:
        cmd = [sys.executable, "-m", "streamlit", "run", app_file, "--server.port=8501"]
    
    result = subprocess.run(cmd, cwd=PROJECT_DIR)
    
    if result.returncode != 0:
        print("\n[ERROR]  Streamlit exited with code: {}".format(result.returncode))
        print("[HINT]   If you use Python 3.13, try installing Python 3.10-3.12 for best stability.")
    else:
        print("\n[INFO] Streamlit has stopped.")
    
    print("\n[INFO] Press Enter to close this window.")
    input()


def quick_start():
    """快速启动（跳过依赖检查）"""
    print_title()
    kill_old_streamlit()

    db_path = os.path.join(PROJECT_DIR, "research_assistant.db")
    if not os.path.exists(db_path):
        print("[DB]     Initializing...")
        init_script = os.path.join(PROJECT_DIR, "database", "init_db.py")
        subprocess.run([sys.executable, init_script])
        print()

    print("[START]  Starting Streamlit...")
    print("[URL]    http://localhost:8501")
    print()

    app_file = os.path.join(PROJECT_DIR, "app.py")
    process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", app_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    print("Streamlit is running.")
    print("Press Enter to stop.")
    input()

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"

    if mode == "quick":
        quick_start()
        return

    # 完整启动流程
    print_title()
    kill_old_streamlit()

    if not check_python():
        input("\nPress Enter to exit...")
        sys.exit(1)

    if not install_dependencies():
        input("\nPress Enter to exit...")
        sys.exit(1)

    if not init_database():
        input("\nPress Enter to exit...")
        sys.exit(1)

    start_app()


if __name__ == "__main__":
    main()
