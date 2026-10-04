# -*- coding: utf-8 -*-
"""AI 后端：API / 网页模式，支持多会话、图片、日志回调"""
import os
import base64
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class APIBackend:
    def __init__(self, api_key, base_url="https://api.deepseek.com/v1",
                 model="deepseek-chat",
                 system="你是一个严谨的学术写作助手，严格按要求输出。",
                 log=None):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.system = system
        self.log = log or print

    def _encode_image(self, path):
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        ext = os.path.splitext(path)[1].lstrip(".").lower()
        ext = "jpeg" if ext in ("jpg", "jpeg") else ext
        return f"data:image/{ext};base64,{b64}"

    def chat(self, prompt, images=None):
        content = [{"type": "text", "text": prompt}]
        for img in (images or []):
            content.append({
                "type": "image_url",
                "image_url": {"url": self._encode_image(img)},
            })
        self.log(f"[API] 请求模型 {self.model} ...")
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system},
                {"role": "user", "content": content},
            ],
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()


class WebBackend:
    """网页模式。GUI 下用 reply_provider 弹窗获取回答"""
    def __init__(self, url="https://chat.deepseek.com/", log=None, reply_provider=None):
        self.url = url
        self.log = log or print
        self.reply_provider = reply_provider
        self._opened = False

    def chat(self, prompt, images=None):
        prompt_file = os.path.join(BASE_DIR, "_prompt_tmp.txt")
        with open(prompt_file, "w", encoding="utf-8") as f:
            f.write(prompt)

        try:
            import pyperclip
            pyperclip.copy(prompt)
            copied = True
        except Exception:
            copied = False

        self.log("=" * 50)
        self.log(f"[网页] 已保存 prompt：{prompt_file}")
        self.log(f"[网页] 剪贴板：{'已复制' if copied else '未复制'}")
        if images:
            self.log("[网页] 请把以下图片拖入网页对话框：")
            for img in images:
                self.log(f"    {os.path.abspath(img)}")

        if not self._opened:
            self.log(f"[网页] 即将打开：{self.url}")
            webbrowser.open(self.url)
            self._opened = True
        else:
            self.log(f"[网页] 请继续在已打开的网页里操作：{self.url}")
        self.log("=" * 50)

        if self.reply_provider is None:
            raise RuntimeError("网页模式需要 reply_provider（GUI 弹窗）来获取回答")
        return self.reply_provider(prompt, images)


def new_session(backend, log=None):
    log = log or print
    if isinstance(backend, WebBackend):
        backend._opened = False
        log("[新对话] 请在弹出的网页里点击『新建对话』再继续。")
    return backend


def build_backend(mode="web", **kwargs):
    if mode == "api":
        return APIBackend(**kwargs)
    return WebBackend(**kwargs)