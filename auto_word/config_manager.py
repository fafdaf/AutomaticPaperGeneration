# -*- coding: utf-8 -*-
"""配置持久化：只保存配置项，不保存要求（文件列表/文字）"""
import os
import json

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULT_CONFIG = {
    "out_dir": r"C:\lunwen",
    "ai_mode": "web",
    "web_url": "https://chat.deepseek.com/",
    "api_key": "",
    "api_base": "https://api.deepseek.com/v1",
    "api_model": "deepseek-chat",
    "max_fix": 3,
    "window": "880x760+100+80",
}


def load_config():
    cfg = dict(DEFAULT_CONFIG)
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            if isinstance(saved, dict):
                for k in DEFAULT_CONFIG:
                    if k in saved:
                        cfg[k] = saved[k]
        except Exception as e:
            print(f"[配置] 读取失败，用默认值：{e}")
    return cfg


def save_config(cfg: dict):
    try:
        data = {k: cfg.get(k, DEFAULT_CONFIG[k]) for k in DEFAULT_CONFIG}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[配置] 保存失败：{e}")
        return False