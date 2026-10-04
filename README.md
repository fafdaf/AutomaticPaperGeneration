# 水课论文自动生成器 · Lunwen Generator

> 拖几个文件、填几行字，点一下按钮，Word 论文自动落盘。

一个 **开箱即用** 的桌面工具，用 AI 帮你完成课程论文的全流程：
**读要求 → 生成内容 → 分析格式 → 生成 Word 脚本 → 自动运行 → 出错自修复**。

支持拖拽 **Word / PDF / 图片 / 纯文本** 作为要求，支持 **API / 网页** 两种 AI 调用模式，全程可无人值守。

---

## ✨ 功能特性

- 📥 **多种输入方式**
  - 拖拽文件到窗口
  - 点击「浏览」选择文件
  - 直接输入文字要求
  - 三者可 **混合使用**，文字优先级最高

- 📄 **多格式解析**
  - Word（`.docx`，含表格）
  - PDF（`pdfplumber` / `PyPDF2` 双后备）
  - 图片（`.png/.jpg/...` 交给 AI 视觉识别，无需本地 OCR）
  - 纯文本（`.txt/.md`）

- 🤖 **双 AI 后端**
  - **网页模式**：无需 API Key，自动打开 DeepSeek 网页，手动粘贴中转
  - **API 模式**：OpenAI 兼容接口，全自动无人值守（DeepSeek / 通义 / 智谱等）

- 🧠 **两段式对话**
  - **对话 A**：把所有输入统一整理成一份结构化文字要求
  - **对话 B**：在新对话里生成内容 → 分析格式 → 生成 Word 脚本

- 🔧 **脚本自修复**
  - AI 生成的 `python-docx` 脚本若运行报错，自动把错误回传 AI 修复
  - 可配置最大重试次数，防止死循环

- ⚙️ **配置记忆**
  - 自动保存：生成位置、AI 模式、AI 链接、API Key、模型、最大修复次数、窗口大小
  - **不保存要求**：每次启动要求区清空，避免隐私残留

- 🧹 **中间产物自动清理**
  - 任务结束后自动删除所有临时文件
  - 只保留 `config.json` 和最终的 `论文.docx`

- 🚀 **双击即用**
  - 自动检测依赖，缺失时弹窗询问并自动 `pip install`
  - 首次运行自动创建桌面快捷方式

---

## 🖼 界面预览

```
┌─ 水课论文自动生成器 ───────────────────────────────────────┐
│ ┌─ 要求（拖拽 / 浏览 / 直接输入）─────────────────────────┐ │
│ │ 要求文件：[已选择 2 个文件            ] [浏览]           │ │
│ │ 文件列表：[ ...                        ]                │ │
│ │           [移除选中] [清空]                             │ │
│ │ 文字要求：[ 1500字，思修论文，宋体小四 ]                 │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌─ 配置（自动记忆保存）─────────────────────────────────┐  │
│ │ 生成位置：[C:\lunwen                    ] [浏览]        │  │
│ │ AI 模式：(•)网页版 ( )API   AI链接：[https://chat.deep…]│  │
│ │ API Key：[****]              API Base：[https://api.deep…]│ │
│ │ 模型：  [deepseek-chat]      最多修复：[3]              │  │
│ └─────────────────────────────────────────────────────────┘ │
│ [确定生成] [中止]                                             │
│ ┌─ 日志 ──────────────────────────────────────────────────┐ │
│ │ >> [对话A] 整理文字要求 ...                               │ │
│ │ >> [对话B-1/3] 生成论文内容 ...                           │ │
│ │ >> [对话B-2/3] 分析格式 ...                               │ │
│ │ >> [对话B-3/3] 生成 Word 脚本 ...                         │ │
│ │ [完成] Word 位于：C:\lunwen\论文.docx                    │ │
│ └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 环境要求

- Windows 10 / 11
- Python 3.8+

### 使用步骤

1. **下载项目**

   ```bash
   git clone https://github.com/yourname/lunwen-generator.git
   cd lunwen-generator
   ```

2. **双击 `start.pyw`**

   程序会自动：
   - 检查依赖 → 缺失弹窗询问 → 自动 `pip install`
   - 首次运行在桌面创建快捷方式
   - 打开图形界面

3. **在界面里操作**
   - 拖入要求文件 / 输入文字要求
   - 填好生成位置和 AI 配置
   - 点「确定生成」

4. **拿到 `论文.docx`**

   Word 会生成在你设定的位置（默认 `C:\lunwen`），中间产物自动清理。

### 手动装依赖（可选）

如果自动安装失败，可以手动执行：

```bash
pip install python-docx openai
pip install tkinterdnd2 pdfplumber PyPDF2 pyperclip
```

---

## 📁 项目结构

```
lunwen-generator/
├── start.pyw              ★ 双击入口（自动装依赖 + 建快捷方式 + 起 GUI）
├── gui.py                   图形界面
├── main.py                  核心流程（对话 A/B、自修复、清理）
├── ai_backend.py            AI 后端（API / 网页）
├── input_loader.py          输入解析（Word / PDF / 图片 / 文本）
└── config_manager.py        配置持久化
```

各文件职责：

| 文件 | 职责 |
|---|---|
| `start.pyw` | 双击入口：依赖检查、建快捷方式、启动 GUI（无黑窗） |
| `gui.py` | 界面绘制、拖拽处理、后台线程、日志展示 |
| `main.py` | 对话编排、脚本生成、运行、自修复、中间产物清理 |
| `ai_backend.py` | 抽象 AI 通信：API 模式 / 网页模式 |
| `input_loader.py` | 把 Word/PDF/图片/文本统一解析成可喂 AI 的输入 |
| `config_manager.py` | 读写 `config.json`，记住配置但不记要求 |

---

## 🔄 工作流程

```
用户拖文件 / 输入文字
        │
        ▼
   [对话 A] 统一整理成文字要求
        │
        ▼
   [对话 B-1] 生成论文内容
        │
        ▼
   [对话 B-2] 分析每部分格式
        │
        ▼
   [对话 B-3] 生成 python-docx 脚本
        │
        ▼
   写脚本 → 运行 → 生成 论文.docx
        │
        ├─ 成功 ─▶ 清理中间产物 ─▶ 完成
        │
        └─ 失败 ─▶ 回传错误给 AI 修复（≤N 次）
```

---

## 🎛 配置说明

首次运行会自动生成 `config.json`：

```json
{
  "out_dir": "C:\\lunwen",
  "ai_mode": "web",
  "web_url": "https://chat.deepseek.com/",
  "api_key": "",
  "api_base": "https://api.deepseek.com/v1",
  "api_model": "deepseek-chat",
  "max_fix": 3,
  "window": "880x760+100+80"
}
```

| 字段 | 说明 |
|---|---|
| `out_dir` | 论文生成位置 |
| `ai_mode` | `web`（网页模式）或 `api`（API 模式） |
| `web_url` | 网页模式的 AI 网址 |
| `api_key` | API Key（**明文存储，注意保密**） |
| `api_base` | API 接口地址 |
| `api_model` | 模型名，含图片需用视觉模型（如 `gpt-4o`） |
| `max_fix` | 脚本报错最多让 AI 修复几次 |
| `window` | 窗口大小和位置 |

> ⚠️ **注意**：API Key 明文存在 `config.json` 里。如果要分享整个文件夹，先清空这个字段或删掉此文件。

---

## 💡 使用建议

### 网页模式 vs API 模式

| | 网页模式 | API 模式 |
|---|---|---|
| 配置 | 无需 Key | 需 API Key |
| 交互 | 每步手动粘贴（4 次） | 全自动 |
| 成本 | 免费 | 按量付费 |
| 适合 | 偶尔用、无 Key | 批量、反复生成 |

### 拿到 DeepSeek API Key

1. 访问 [platform.deepseek.com](https://platform.deepseek.com/)
2. 注册并实名
3. 在「API Keys」里创建一个 Key（`sk-` 开头）
4. 填进界面的「API Key」字段

### 含图片时的注意事项

- **网页模式**：程序会打印图片路径，你手动把图片拖入 DeepSeek 网页对话框
- **API 模式**：`deepseek-chat` 不支持图片，需换成视觉模型（`gpt-4o`、`qwen-vl-max` 等）

---

## ❓ 常见问题

**Q：双击 `start.pyw` 没反应？**
用命令行跑 `python start.pyw` 看报错。

**Q：生成到 `C:\lunwen` 报权限错误？**
改到用户目录，比如 `D:\论文`。

**Q：中间产物会残留吗？**
不会。任务结束后 `normalized_requirements.txt`、`_prompt_tmp.txt`、`generate_word.py` 都会自动删除。只保留 `config.json` 和 `论文.docx`。

**Q：想清空配置？**
删掉项目目录下的 `config.json` 即可。

**Q：脚本反复报错？**
调小「最大修复次数」，或保留失败时的脚本手动排查（可改 `main.py` 里的清理逻辑为「仅成功时清理」）。

---

## ⚠️ 免责声明

本工具仅用于 **辅助生成** 课程论文初稿、格式排版练习。

- 请 **自行审核** 生成内容的正确性和原创性
- **不要** 直接提交给学校作为原创成果
- 使用 AI 生成内容请遵守所在学校/机构的学术诚信规范

作者不对使用本工具产生的任何后果负责。

---

## 📜 License

MIT License

---

## 🙏 致谢

- [python-docx](https://github.com/python-openxml/python-docx) — Word 文档生成
- [OpenAI SDK](https://github.com/openai/openai-python) — API 调用
- [tkinterdnd2](https://github.com/pmgagne/tkinterdnd2) — 拖拽支持
- [DeepSeek](https://www.deepseek.com/) — 默认 AI 后端
