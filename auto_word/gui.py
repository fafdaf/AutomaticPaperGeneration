# -*- coding: utf-8 -*-
"""图形界面：拖拽/浏览文件 + 文字输入 + 配置（自动保存，要求不保存）"""
import threading
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAS_DND = True
except ImportError:
    HAS_DND = False

from main import run_pipeline
from config_manager import load_config, save_config


class App:
    def __init__(self, root):
        self.root = root
        root.title("水课论文自动生成器")

        self.cfg = load_config()
        geom = self.cfg.get("window") or "880x760+100+80"
        root.geometry(geom)

        self.file_paths = []
        self.log_queue = queue.Queue()
        self.worker = None
        self.stop_flag = threading.Event()

        self._build_ui()
        self._apply_config_to_ui()
        self._poll_log()

        root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _apply_config_to_ui(self):
        self.out_dir.set(self.cfg.get("out_dir", r"C:\lunwen"))
        self.ai_mode.set(self.cfg.get("ai_mode", "web"))
        self.web_url.set(self.cfg.get("web_url", "https://chat.deepseek.com/"))
        self.api_key.set(self.cfg.get("api_key", ""))
        self.api_base.set(self.cfg.get("api_base", "https://api.deepseek.com/v1"))
        self.api_model.set(self.cfg.get("api_model", "deepseek-chat"))
        try:
            self.max_fix.set(int(self.cfg.get("max_fix", 3)))
        except Exception:
            self.max_fix.set(3)

    def _collect_config_from_ui(self):
        try:
            max_fix = int(self.max_fix.get())
        except Exception:
            max_fix = 3
        return {
            "out_dir": self.out_dir.get().strip(),
            "ai_mode": self.ai_mode.get(),
            "web_url": self.web_url.get().strip(),
            "api_key": self.api_key.get().strip(),
            "api_base": self.api_base.get().strip(),
            "api_model": self.api_model.get().strip(),
            "max_fix": max_fix,
            "window": self.root.geometry(),
        }

    def on_close(self):
        save_config(self._collect_config_from_ui())
        self.root.destroy()

    def _build_ui(self):
        pad = {"padx": 8, "pady": 4}

        req_frame = ttk.LabelFrame(
            self.root,
            text="要求（每次启动为空，不自动保存；可拖拽文件、点『浏览』或直接输入文字）"
        )
        req_frame.pack(fill="both", expand=False, **pad)
        req_frame.columnconfigure(1, weight=1)

        ttk.Label(req_frame, text="要求文件：").grid(row=0, column=0, sticky="e", **pad)
        self.file_display = tk.StringVar(value="（尚未选择）")
        ttk.Entry(req_frame, textvariable=self.file_display,
                  state="readonly").grid(row=0, column=1, sticky="ew", **pad)
        ttk.Button(req_frame, text="浏览", command=self.add_files).grid(
            row=0, column=2, sticky="w", **pad)

        ttk.Label(req_frame, text="文件列表：").grid(row=1, column=0, sticky="nw", **pad)
        self.file_listbox = tk.Listbox(req_frame, height=4, selectmode=tk.EXTENDED)
        self.file_listbox.grid(row=1, column=1, columnspan=2, sticky="ew", **pad)

        btn_row = ttk.Frame(req_frame)
        btn_row.grid(row=2, column=1, columnspan=2, sticky="w", **pad)
        ttk.Button(btn_row, text="移除选中", command=self.remove_selected).pack(side="left", padx=2)
        ttk.Button(btn_row, text="清空", command=self.clear_files).pack(side="left", padx=2)

        ttk.Label(req_frame, text="文字要求：").grid(row=3, column=0, sticky="nw", **pad)
        self.text_input = scrolledtext.ScrolledText(req_frame, height=6, wrap="word")
        self.text_input.grid(row=3, column=1, columnspan=2, sticky="ew", **pad)

        if HAS_DND:
            try:
                self.file_listbox.drop_target_register(DND_FILES)
                self.file_listbox.dnd_bind("<<Drop>>", self._on_drop)
                self.text_input.drop_target_register(DND_FILES)
                self.text_input.dnd_bind("<<Drop>>", self._on_drop)
            except Exception as e:
                print("拖拽注册失败：", e)

        cfg = ttk.LabelFrame(self.root, text="配置（自动记忆保存）")
        cfg.pack(fill="x", **pad)
        cfg.columnconfigure(1, weight=1)
        cfg.columnconfigure(3, weight=1)

        ttk.Label(cfg, text="生成位置：").grid(row=0, column=0, sticky="e", **pad)
        self.out_dir = tk.StringVar(value=r"C:\lunwen")
        ttk.Entry(cfg, textvariable=self.out_dir).grid(
            row=0, column=1, columnspan=2, sticky="ew", **pad)
        ttk.Button(cfg, text="浏览", command=self.choose_out_dir).grid(
            row=0, column=3, sticky="w", **pad)

        ttk.Label(cfg, text="AI 模式：").grid(row=1, column=0, sticky="e", **pad)
        self.ai_mode = tk.StringVar(value="web")
        mode_frame = ttk.Frame(cfg)
        mode_frame.grid(row=1, column=1, sticky="w", **pad)
        ttk.Radiobutton(mode_frame, text="网页版", variable=self.ai_mode, value="web").pack(side="left")
        ttk.Radiobutton(mode_frame, text="API", variable=self.ai_mode, value="api").pack(side="left", padx=8)

        ttk.Label(cfg, text="AI 链接：").grid(row=1, column=2, sticky="e", **pad)
        self.web_url = tk.StringVar(value="https://chat.deepseek.com/")
        ttk.Entry(cfg, textvariable=self.web_url).grid(row=1, column=3, sticky="ew", **pad)

        ttk.Label(cfg, text="API Key：").grid(row=2, column=0, sticky="e", **pad)
        self.api_key = tk.StringVar(value="")
        ttk.Entry(cfg, textvariable=self.api_key, show="*").grid(
            row=2, column=1, sticky="ew", **pad)

        ttk.Label(cfg, text="API Base：").grid(row=2, column=2, sticky="e", **pad)
        self.api_base = tk.StringVar(value="https://api.deepseek.com/v1")
        ttk.Entry(cfg, textvariable=self.api_base).grid(
            row=2, column=3, sticky="ew", **pad)

        ttk.Label(cfg, text="模型：").grid(row=3, column=0, sticky="e", **pad)
        self.api_model = tk.StringVar(value="deepseek-chat")
        ttk.Entry(cfg, textvariable=self.api_model).grid(
            row=3, column=1, sticky="ew", **pad)

        ttk.Label(cfg, text="脚本报错最多修复：").grid(row=3, column=2, sticky="e", **pad)
        self.max_fix = tk.IntVar(value=3)
        ttk.Spinbox(cfg, from_=0, to=10, textvariable=self.max_fix, width=5).grid(
            row=3, column=3, sticky="w", **pad)

        btn_bar = ttk.Frame(self.root)
        btn_bar.pack(fill="x", **pad)
        self.gen_btn = ttk.Button(btn_bar, text="确定生成", command=self.on_generate)
        self.gen_btn.pack(side="left", padx=4)
        self.stop_btn = ttk.Button(btn_bar, text="中止", command=self.on_stop, state="disabled")
        self.stop_btn.pack(side="left", padx=4)

        log_frame = ttk.LabelFrame(self.root, text="日志")
        log_frame.pack(fill="both", expand=True, **pad)
        self.log_box = scrolledtext.ScrolledText(log_frame, height=12, wrap="word", state="disabled")
        self.log_box.pack(fill="both", expand=True, **pad)

    def add_files(self):
        paths = filedialog.askopenfilenames(
            title="选择要求文件",
            filetypes=[
                ("所有支持", "*.docx *.pdf *.txt *.md *.png *.jpg *.jpeg *.bmp *.webp *.gif"),
                ("Word", "*.docx"),
                ("PDF", "*.pdf"),
                ("文本", "*.txt *.md"),
                ("图片", "*.png *.jpg *.jpeg *.bmp *.webp *.gif"),
                ("所有文件", "*.*"),
            ],
        )
        for p in paths:
            if p and p not in self.file_paths:
                self.file_paths.append(p)
        self._refresh_file_list()

    def remove_selected(self):
        sel = list(self.file_listbox.curselection())
        for i in reversed(sel):
            self.file_paths.pop(i)
        self._refresh_file_list()

    def clear_files(self):
        self.file_paths.clear()
        self._refresh_file_list()

    def _refresh_file_list(self):
        self.file_listbox.delete(0, tk.END)
        for p in self.file_paths:
            self.file_listbox.insert(tk.END, p)
        if self.file_paths:
            self.file_display.set(f"已选择 {len(self.file_paths)} 个文件")
        else:
            self.file_display.set("（尚未选择）")

    def _on_drop(self, event):
        paths = self._parse_drop(event.data)
        added = 0
        for p in paths:
            if p and p not in self.file_paths:
                self.file_paths.append(p)
                added += 1
        self._refresh_file_list()
        self._log(f"[拖拽] 添加 {added} 个文件。")

    @staticmethod
    def _parse_drop(data):
        items = []
        buf = ""
        in_brace = False
        for ch in data:
            if ch == "{":
                in_brace = True
                continue
            if ch == "}":
                in_brace = False
                continue
            if ch == " " and not in_brace:
                if buf:
                    items.append(buf)
                    buf = ""
                continue
            buf += ch
        if buf:
            items.append(buf)
        return items

    def choose_out_dir(self):
        d = filedialog.askdirectory(title="选择生成位置")
        if d:
            self.out_dir.set(d)

    def on_generate(self):
        if self.worker and self.worker.is_alive():
            messagebox.showinfo("提示", "正在生成中，请稍候。")
            return

        text_input = self.text_input.get("1.0", "end").strip()
        file_paths = list(self.file_paths)

        if not text_input and not file_paths:
            messagebox.showwarning("提示", "请至少提供文字要求或添加文件。")
            return

        out_dir = self.out_dir.get().strip()
        if not out_dir:
            messagebox.showwarning("提示", "请填写生成位置。")
            return

        mode = self.ai_mode.get()
        if mode == "api" and not self.api_key.get().strip():
            if not messagebox.askyesno("确认", "API 模式下未填写 API Key，确定继续吗？"):
                return

        save_config(self._collect_config_from_ui())

        self._clear_log()
        self.gen_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.stop_flag.clear()

        self.worker = threading.Thread(
            target=self._run_worker,
            args=(text_input, file_paths, out_dir, mode),
            daemon=True,
        )
        self.worker.start()

    def _run_worker(self, text_input, file_paths, out_dir, mode):
        def log(msg):
            self.log_queue.put(str(msg))

        def reply_provider(prompt, images):
            return self._ask_reply_main_thread(prompt, images)

        try:
            ok = run_pipeline(
                text_input=text_input,
                file_paths=file_paths,
                target_dir=out_dir,
                ai_mode=mode,
                web_url=self.web_url.get().strip(),
                api_key=self.api_key.get().strip(),
                api_base=self.api_base.get().strip(),
                api_model=self.api_model.get().strip(),
                max_fix=int(self.max_fix.get()),
                log=log,
                reply_provider=reply_provider,
                stop_flag=self.stop_flag.is_set,
            )
            self.log_queue.put(("__DONE__", ok))
        except Exception as e:
            import traceback
            self.log_queue.put("[异常] " + str(e))
            self.log_queue.put(traceback.format_exc())
            self.log_queue.put(("__DONE__", False))

    def _ask_reply_main_thread(self, prompt, images):
        result_q = queue.Queue()

        def show():
            win = tk.Toplevel(self.root)
            win.title("粘贴 AI 回答")
            win.geometry("720x520")

            info = "请到已打开的网页里粘贴 prompt 并发送"
            if images:
                info += f"\n（记得把 {len(images)} 张图片也拖入网页）"
            info += "\n然后把 AI 的完整回答粘贴到下面，点『确定』。"
            ttk.Label(win, text=info, justify="left").pack(anchor="w", padx=8, pady=6)

            txt = scrolledtext.ScrolledText(win, wrap="word")
            txt.pack(fill="both", expand=True, padx=8, pady=4)

            def ok():
                result_q.put(txt.get("1.0", "end").strip())
                win.destroy()

            def cancel():
                result_q.put("")
                win.destroy()

            bar = ttk.Frame(win)
            bar.pack(fill="x", pady=6)
            ttk.Button(bar, text="确定", command=ok).pack(side="left", padx=8)
            ttk.Button(bar, text="取消", command=cancel).pack(side="left")

            win.protocol("WM_DELETE_WINDOW", cancel)

            win.transient(self.root)
            win.grab_set()

        self.root.after(0, show)
        try:
            return result_q.get(timeout=1800)
        except queue.Empty:
            self.log_queue.put("[超时] 网页模式等待用户响应超过 30 分钟，已跳过。")
            return ""

    def on_stop(self):
        if messagebox.askyesno("确认", "确定要中止吗？当前进度可能丢失。"):
            self.stop_flag.set()
            self._log("[中止] 已请求中止，等待当前步骤结束……")

    def _log(self, msg):
        self.log_box.config(state="normal")
        self.log_box.insert("end", str(msg) + "\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def _clear_log(self):
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")

    def _poll_log(self):
        try:
            while True:
                item = self.log_queue.get_nowait()
                if isinstance(item, tuple) and item[0] == "__DONE__":
                    ok = item[1]
                    self.gen_btn.config(state="normal")
                    self.stop_btn.config(state="disabled")
                    self.root.after(50, lambda k=ok: self._show_done(k))
                else:
                    self._log(item)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_log)

    def _show_done(self, ok):
        if ok:
            messagebox.showinfo("完成", "生成成功！请到目标文件夹查看 论文.docx")
        else:
            messagebox.showwarning("结束", "流程结束，但未成功生成。请查看日志。")


def main():
    if HAS_DND:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
        print("[提示] 未安装 tkinterdnd2，拖拽功能不可用（可用『浏览』按钮）。"
              "安装：pip install tkinterdnd2")
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()