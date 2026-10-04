# -*- coding: utf-8 -*-
"""核心流程，被 GUI 调用"""
import os
import sys
import subprocess

from ai_backend import build_backend, new_session

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 项目目录下的中间产物（任务结束后删除）
TEMP_FILES_IN_PROJECT = [
    "normalized_requirements.txt",
    "_prompt_tmp.txt",
]


def _cleanup_temp_files(log, target_dir=None):
    """删除中间产物：
    - 项目目录：normalized_requirements.txt、_prompt_tmp.txt
    - 目标目录：generate_word.py
    保留：config.json、论文.docx、GUI 日志
    """
    for name in TEMP_FILES_IN_PROJECT:
        path = os.path.join(BASE_DIR, name)
        if os.path.exists(path):
            try:
                os.remove(path)
                log(f"[清理] 已删除：{path}")
            except Exception as e:
                log(f"[清理] 删除失败 {path}：{e}")

    if target_dir:
        sp = os.path.join(target_dir, "generate_word.py")
        if os.path.exists(sp):
            try:
                os.remove(sp)
                log(f"[清理] 已删除：{sp}")
            except Exception as e:
                log(f"[清理] 删除失败 {sp}：{e}")


def stepA_normalize(ai, text_blocks, images, log):
    joined = "\n\n---\n\n".join(text_blocks) if text_blocks else "（无文本输入）"
    img_note = (
        f"\n\n【附加图片 {len(images)} 张】请识别图片中的文字与格式要求，一并整理。"
        if images else ""
    )
    prompt = (
        "请把下面的全部输入内容，统一整理成一份**结构化的文字要求**，用于后续生成课程论文。\n"
        "1. 若各部分内容有冲突，**以最前面一段（用户手动输入）为准**，并标注冲突点。\n"
        "2. 合并重复信息，去矛盾（若矛盾，标注并建议）。\n"
        "3. 明确提取：论文题目/主题、字数、章节结构、语言风格、引用要求等。\n"
        "4. 明确提取：格式要求（字体、字号、加粗、对齐、行距、缩进、页边距等）。\n"
        "5. 用条目标号输出，不遗漏细节。\n"
        "6. 只输出整理后的\"文字要求\"，不要任何解释。\n\n"
        "【原始文本输入】（第一段为手动补充，优先级最高）\n"
        f"{joined}\n"
        f"{img_note}"
    )
    log(">> [对话A] 整理文字要求 ...")
    return ai.chat(prompt, images=images)


def stepB1_content(ai, req, log):
    prompt = (
        "请根据以下要求，撰写一篇完整的课程论文。\n"
        "要求：\n"
        f"{req}\n\n"
        "请直接输出论文正文（标题、摘要、关键词、各级标题、正文、参考文献），\n"
        "用清晰层级标记（如【标题】【摘要】【一、xxx】），不要任何解释。"
    )
    log(">> [对话B-1/3] 生成论文内容 ...")
    return ai.chat(prompt)


def stepB2_format(ai, req, content, log):
    prompt = (
        "以下是一篇论文内容和格式要求。\n\n"
        "【格式要求】\n"
        f"{req}\n\n"
        "【论文内容】\n"
        f"{content}\n\n"
        "请逐条列出论文各组成部分（标题、作者、摘要、关键词、各级标题、正文、参考文献）\n"
        "应采用的格式（字体、字号、加粗、对齐、行距、缩进等），用清单输出。"
    )
    log(">> [对话B-2/3] 分析格式 ...")
    return ai.chat(prompt)


def stepB3_script(ai, req, content, fmt, log):
    prompt = (
        "请编写一个 Python 脚本，使用 python-docx 生成 Word 文档。\n\n"
        "【论文内容】\n"
        f"{content}\n\n"
        "【格式规范】\n"
        f"{fmt}\n\n"
        "【原始要求】\n"
        f"{req}\n\n"
        "要求：\n"
        "1. 只用 python-docx + 标准库。\n"
        "2. 保存到脚本目录下 \"论文.docx\"，用 os.path.dirname(os.path.abspath(__file__)) 定位。\n"
        "3. 中文字体同时设置 w:eastAsia：\n"
        "   run.font.name='宋体'\n"
        "   run._element.rPr.rFonts.set(qn('w:eastAsia'),'宋体')\n"
        "4. 严格按格式规范设置字体、字号、加粗、对齐、行距、首行缩进。\n"
        "5. 可直接运行，结束打印\"生成完成\"。\n"
        "6. 只输出 Python 代码，用 ```python 包裹，无多余说明。"
    )
    log(">> [对话B-3/3] 生成 Word 脚本 ...")
    return ai.chat(prompt)


def stepG_fix(ai, code, error, log):
    prompt = (
        "你之前生成的 Python 脚本运行报错了。请修复并输出**完整的修正后脚本**。\n\n"
        "【原脚本】\n"
        "```python\n"
        f"{code}\n"
        "```\n\n"
        "【运行报错】\n"
        f"{error}\n\n"
        "要求：\n"
        "1. 只修复报错，保持原功能和格式设置不变。\n"
        "2. 只输出完整 Python 代码，用 ```python 包裹，无解释。\n"
        "3. 中文字体仍通过 w:eastAsia 设置。"
    )
    log(">> [G] 让 AI 修复脚本 ...")
    return ai.chat(prompt)


def extract_code(text):
    if "```" in text:
        for p in text.split("```"):
            p = p.strip()
            low = p.lower()
            if low.startswith("python"):
                return p[6:].strip()
            if low.startswith("py\n") or low.startswith("py "):
                return p[2:].strip()
            if p.startswith("import") or p.startswith("from") or p.startswith("#"):
                return p
    return text.strip()


def run_script(target_dir, log):
    log(f"执行：{sys.executable} -u generate_word.py  (cwd={target_dir})")
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        r = subprocess.run(
            [sys.executable, "-u", "generate_word.py"],
            cwd=target_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        out = (r.stdout or "") + ("\n[stderr]\n" + r.stderr if r.stderr else "")
        return r.returncode == 0, out
    except Exception as e:
        return False, f"[运行异常] {e}"


def run_pipeline(*, text_input, file_paths, target_dir,
                 ai_mode, web_url, api_key, api_base, api_model,
                 max_fix, log, reply_provider=None, stop_flag=None):
    from input_loader import classify_paths

    # 前置校验：不支持的文件格式给出提示
    bad = []
    for p in file_paths:
        ext = os.path.splitext(p)[1].lower()
        if ext == ".doc":
            bad.append(f"{os.path.basename(p)}（.doc 旧格式，请转 .docx）")
    if bad:
        log("[警告] 以下文件无法解析：" + "；".join(bad))

    # 收集输入
    text_blocks, images = classify_paths(file_paths)
    if text_input.strip():
        text_blocks.insert(0, text_input.strip())

    if not text_blocks and not images:
        log("[错误] 没有有效输入（既无文字，也无文件）。")
        _cleanup_temp_files(log, target_dir)
        return False

    def make_backend():
        if ai_mode == "api":
            return build_backend(
                "api",
                api_key=api_key,
                base_url=api_base,
                model=api_model,
                log=log,
            )
        return build_backend(
            "web", url=web_url, log=log, reply_provider=reply_provider
        )

    try:
        # 对话 A
        ai_a = make_backend()
        normalized = stepA_normalize(ai_a, text_blocks, images, log)
        if not normalized.strip():
            log("[错误] 对话A 未返回有效要求。")
            return False

        # 中间产物：整理后的要求（临时保存，结束删）
        norm_file = os.path.join(BASE_DIR, "normalized_requirements.txt")
        with open(norm_file, "w", encoding="utf-8") as f:
            f.write(normalized)
        log(f"[F] 整理后的要求已保存（临时）：{norm_file}")

        if stop_flag and stop_flag():
            log("[中止] 用户取消。")
            return False

        # 对话 B
        ai_b = new_session(make_backend(), log=log)
        content = stepB1_content(ai_b, normalized, log)
        fmt = stepB2_format(ai_b, normalized, content, log)
        raw = stepB3_script(ai_b, normalized, content, fmt, log)
        code = extract_code(raw)

        if not os.path.exists(target_dir):
            try:
                os.makedirs(target_dir)
                log(f"已创建目录：{target_dir}")
            except PermissionError:
                log(f"[错误] 无权限创建 {target_dir}")
                return False

        # 运行 + G 修复
        prev_code = None
        for attempt in range(max_fix + 1):
            if prev_code is not None and code == prev_code:
                log("[G] 修复后脚本与上次相同，停止重试。")
                return False
            prev_code = code

            sp = os.path.join(target_dir, "generate_word.py")
            with open(sp, "w", encoding="utf-8") as f:
                f.write(code)
            log(f"脚本已写入：{sp}")

            ok, out = run_script(target_dir, log)
            log("---- 运行输出 ----")
            log(out[:5000] + ("\n...(已截断)" if len(out) > 5000 else ""))
            log("------------------")

            if ok:
                log(f"[完成] 脚本运行成功（第 {attempt + 1} 次尝试）")
                log(f"[完成] Word 位于：{os.path.join(target_dir, '论文.docx')}")
                return True
            if stop_flag and stop_flag():
                log("[中止] 用户取消。")
                return False
            if attempt == max_fix:
                log(f"[G] 已达最大修复次数 {max_fix}，仍失败。")
                return False
            raw = stepG_fix(ai_b, code, out, log)
            code = extract_code(raw)

        return False

    finally:
        # 无论成功、失败、异常、中止，都清理中间产物
        _cleanup_temp_files(log, target_dir)