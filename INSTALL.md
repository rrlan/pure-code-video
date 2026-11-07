# 安装与更新指南 (`pure-code-video`)

## 一、公开渠道一键安装与更新（无需 GitHub 账号）

安装与后续更新均执行同一条命令：

```bash
curl -fsSL https://raw.githubusercontent.com/rrlan/skill-releases/main/install.py -o /tmp/rrlan-skill-install.py && python3 /tmp/rrlan-skill-install.py pure-code-video
```

安装到指定项目目录：

```bash
curl -fsSL https://raw.githubusercontent.com/rrlan/skill-releases/main/install.py -o /tmp/rrlan-skill-install.py && python3 /tmp/rrlan-skill-install.py pure-code-video --project /path/to/project
```

## 二、使用 `skills` CLI 从源码仓库安装

```bash
npx skills@1.7.2 add rrlan/pure-code-video --skill pure-code-video --agent codex -g
```

## 三、本地 ZIP 解压安装与换包更新

解压 `pure-code-video-1.0.0.zip` 后运行：

```bash
python3 pure-code-video/install.py
```

## 四、环境前提与常用自检命令

- 前提：Python 3.9+、Node.js（含 `npx`）；渲染视频成片需本机装有 `ffmpeg` 与 Playwright Chromium，生成中文语音需 `edge-tts`。
- 自检与配方检索：
  - `python3 ~/.agents/skills/pure-code-video/run.py doctor`
  - `python3 ~/.agents/skills/pure-code-video/run.py search 水彩`
  - `python3 ~/.agents/skills/pure-code-video/run.py recipe claude-textured-editorial`
