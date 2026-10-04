# -*- coding: utf-8 -*-
"""
双击此文件即可启动水课论文自动生成器。
功能：
  1. 自动检测依赖，缺失则自动 pip 安装
  2. 首次运行自动在桌面创建快捷方式
  3. 启动 GUI（无黑窗）
说明：
  - 全程不用 tkinter，避免与 GUI 的 Tk() 冲突
  - 弹窗用 Windows 原生 MessageBox
"""
import os
import sys
import subprocess
import importlib

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)


REQUIRED = {
    "docx": "python-docx",
    "openai": "openai",
}

OPTIONAL = {
    "tkinterdnd2": "tkinterdnd2",
    "pdfplumber": "pdfplumber",
    "PyPDF2": "PyPDF2",
    "pyperclip": "pyperclip",
}

PIP_INDEX = "https://pypi.tuna.tsinghua.edu.cn/simple"


def _msgbox(msg, title="提示", icon=0x40):
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, msg, title, icon)
            return
        except Exception:
            pass
    print(f"[{title}] {msg}")


def _ask_yes_no(title, msg):
    if os.name != "nt":
        return True
    try:
        import ctypes
        MB_YESNO = 0x04
        MB_ICONQUESTION = 0x20
        IDYES = 6
        res = ctypes.windll.user32.MessageBoxW(0, msg, title, MB_YESNO | MB_ICONQUESTION)
        return res == IDYES
    except Exception:
        return True


def _module_ok(mod_name):
    try:
        importlib.import_module(mod_name)
        return True
    except Exception:
        return False


def _pip_install(packages):
    if not packages:
        return True
    print(f"[依赖] 正在安装：{', '.join(packages)}")
    ok = True
    for pkg in packages:
        try:
            cmd = [sys.executable, "-m", "pip", "install", pkg]
            if PIP_INDEX:
                cmd += ["-i", PIP_INDEX]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode == 0:
                print(f"[依赖] {pkg} 安装成功")
            else:
                ok = False
                print(f"[依赖] {pkg} 安装失败：")
                print(r.stdout)
                print(r.stderr)
        except Exception as e:
            ok = False
            print(f"[依赖] {pkg} 安装异常：{e}")
    return ok


def check_and_install_deps():
    missing_required = [pkg for mod, pkg in REQUIRED.items() if not _module_ok(mod)]
    if missing_required:
        msg = (
            "检测到缺少以下必需依赖：\n\n  "
            + "\n  ".join(missing_required)
            + "\n\n是否现在自动安装？（需要联网）"
        )
        if _ask_yes_no("缺少依赖", msg):
            ok = _pip_install(missing_required)
            if not ok:
                _msgbox(
                    "部分依赖安装失败，程序可能无法正常运行。\n"
                    "可手动运行：\n  pip install " + " ".join(missing_required),
                    "安装失败", 0x10
                )
            else:
                importlib.invalidate_caches()
        else:
            print("[依赖] 用户取消安装必需依赖，尝试继续运行。")

    missing_optional = [pkg for mod, pkg in OPTIONAL.items() if not _module_ok(mod)]
    if missing_optional:
        print("[提示] 可选依赖未安装：", ", ".join(missing_optional))
        msg = (
            "检测到缺少以下可选依赖：\n\n  "
            + "\n  ".join(missing_optional)
            + "\n\n是否一并安装？（拖拽/PDF 等功能需要）"
        )
        if _ask_yes_no("缺少可选依赖", msg):
            _pip_install(missing_optional)
            importlib.invalidate_caches()


def ensure_desktop_shortcut():
    if os.name != "nt":
        return
    try:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.isdir(desktop):
            return

        # 桌面快捷方式名称（可改）
        lnk = os.path.join(desktop, "LunwenGenerator.lnk")
        if os.path.exists(lnk):
            return

        # 目标脚本改成 start.pyw
        script = os.path.join(HERE, "start.pyw")

        pyw = sys.executable
        if pyw.lower().endswith("python.exe"):
            cand = pyw[:-len("python.exe")] + "pythonw.exe"
            if os.path.exists(cand):
                pyw = cand

        ps = (
            f"$ws = New-Object -ComObject WScript.Shell;"
            f"$sc = $ws.CreateShortcut('{lnk}');"
            f"$sc.TargetPath = '{pyw}';"
            f"$sc.Arguments = '\"{script}\"';"
            f"$sc.WorkingDirectory = '{HERE}';"
            f"$sc.IconLocation = '{pyw},0';"
            f"$sc.Description = 'Lunwen Generator';"
            f"$sc.Save();"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
             "-Command", ps],
            check=False, capture_output=True
        )
        print("[快捷方式] 已尝试在桌面创建：LunwenGenerator")
    except Exception as e:
        print("[快捷方式] 创建失败（可忽略）：", e)


def main():
    check_and_install_deps()
    ensure_desktop_shortcut()
    try:
        from gui import main as gui_main
        gui_main()
    except Exception as e:
        import traceback
        _msgbox(f"{e}\n\n{traceback.format_exc()}", "启动失败", 0x10)


if __name__ == "__main__":
    main()