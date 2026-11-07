# Pure-Code Video (`pure-code-video` v1.1.0)

> **零生图大模型的纯代码视频全栈工具箱**：530+ 款视觉风格选片台 · 双确定性渲染引擎 · 109 个 CC0 实录音效与 `-16 LUFS` 节拍混音 · 真人录音预剪 / 个人音色克隆 / 逐字字幕对齐。

- **在线可视化选片台 (GitHub Pages)**：[https://rrlan.github.io/pure-code-video/](https://rrlan.github.io/pure-code-video/)
- **开源仓库**：[https://github.com/rrlan/pure-code-video](https://github.com/rrlan/pure-code-video)

---

## 一张表看懂：这个工具箱包含哪 4 大能力模块？

| 模块 | 工具 / 脚本入口 | 解决什么问题（核心能力） | 怎么用（命令或操作） |
|---|---|---|---|
| **1. 视觉风格选片与配方库**<br>*(530+ 款画风)* | 网页选片台 /<br>`run.py search`<br>`run.py recipe` | 聚合 **105 款核心命名风格**（15 种 Opus 5.5 MG 动效、66 款 Lemo-Opuscar 电影画风、8 大王牌频道解说语法、6 款名画流场、8 款中文口播风格）+ **425 个社区实测案例与完整 Prompt**。 | • **网页端**：打开选片台，点卡片「复制点单口令」（自带完整色板/物理/运镜配方）直接发给 AI<br>• **命令行**：`python3 run.py search 水彩` / `python3 run.py recipe mg-05-cel-boil` |
| **2. 纯代码画面渲染引擎**<br>*(零生图大模型)* | ① `templates/high-energy-html/render.mjs`<br>② `templates/handdrawn-explainer/` | 提供两套零掉帧确定性渲染基座：<br>① **60fps 虚拟时钟锁拍 HTML 渲染器**：劫持浏览器时钟（`window.__setTime(t)`），多复杂的 WebGL/3D 体素/弹簧排版都 100% 不掉帧；<br>② **手绘水彩与毛笔墨线引擎（`lib/`）**：基于 `@napi-rs/canvas` 实现水彩纸纹、蓝铅笔结构线→毛笔墨线→水彩晕染（`Pen.wash`）与 12fps 手绘抽帧感。 | • **HTML 锁拍渲染**：`node templates/high-energy-html/render.mjs`<br>• **手绘水彩渲染**：`node templates/handdrawn-explainer/handdrawn-leafcutter-21s.mjs` |
| **3. 实录音效设计与节拍混音**<br>*(内置 109 个 CC0 音效)* | `run.py sfx-list`<br>`run.py sound-pass`<br>(`scripts/sound_pass.py`) | 告别廉价的电子蜂鸣音：<br>• **内置 109 个 CC0 真实录音音效**（13 大类：`whoosh` 转场风声、`click` 点击、`pop` 弹出、`riser` 蓄力、`impact` 重击、`tick` 刻度、`glitch` 故障、`ambience` 环境音等）；<br>• **底鼓节拍网格校准**：用 `librosa` 提取 `<120Hz` 真实底鼓并自动对齐画面硬切点；<br>• **广播级自动混音**：按「人声 > 音效 > 配乐」自动闪避（Ducking），压限至 **`-16 LUFS` / 真峰值 `< -4 dBFS`**，并导出波形检查图与可试听替换网页 `report.html`。 | • **查看内置音效**：`python3 run.py sfx-list --category whoosh`<br>• **一键配音效混音**：`python3 run.py sound-pass --video silent.mp4 --cues cues.json --music bgm.mp3 --out out/`<br>*(首次运行自动在外部缓存创建 Python 音频环境，无需手动装包)* |
| **4. 配音与「你自己的声音」字幕对齐**<br>*(支持真声 / 克隆 / TTS)* | ① `run.py voice-trim`<br>② `run.py voice-align`<br>③ `run.py voice-clone`<br>④ `make_voice.py` | 支持 **3 种人声配音路线**，全部输出毫秒级逐字/逐词时间戳 JSON 驱动代码动画与卡拉 OK 字幕：<br>• **路线 A（你自己录真声）**：先用 `voice-trim` 自动剪掉“嗯/呃/结巴重说/长气口”，再用 `voice-align` 在本机 CPU 上与文稿做逐字时间戳对齐；<br>• **路线 B（克隆你的声音读稿）**：给 15–30 秒你的声音样本，用 Fish Audio 克隆音色 ID（`voice-clone`）或本地 ComfyUI `IndexTTS2` 自动按新文稿生成你的声音并导出字级时间戳；<br>• **路线 C（零配置标准神经语音）**：调用 `edge-tts` 生成自然中文配音 + 逐词边界时间戳。 | • **真声去口水词**：`python3 run.py voice-trim raw.wav script.json --out clean.wav`<br>• **真声/克隆音逐字对齐**：`python3 run.py voice-align clean.wav script.json timestamps.json`<br>• **克隆音色合成**：`python3 run.py voice-clone script.json full.wav timestamps.json`<br>• **标准 TTS 合成**：`python3 templates/handdrawn-explainer/make_voice.py` |

---

## 一、快速上手（3 种使用姿势）

### 姿势 1：零安装网页点单（适合所有 AI 用户）
1. 打开在线选片台：[https://rrlan.github.io/pure-code-video/](https://rrlan.github.io/pure-code-video/)
2. 点击任意风格卡片上的 **「复制点单口令」**（会自动把该风格的视觉特征、色板/字体/弹簧物理配方与虚拟时钟渲染规范一起复制进剪贴板）。
3. 粘贴给 Claude / Codex / Cursor / ChatGPT，在末尾填上你的视频主题即可。

### 姿势 2：一键安装为 Agent Skill（推荐 Codex / Claude Code 用户）
**无需 GitHub 账号**，安装与后续更新均执行同一条命令：

```bash
curl -fsSL https://raw.githubusercontent.com/rrlan/skill-releases/main/install.py -o /tmp/rrlan-skill-install.py && python3 /tmp/rrlan-skill-install.py pure-code-video
```

- 安装到指定项目目录：在命令末尾追加 `--project /path/to/project`
- 或使用 `skills` CLI 从源码仓库安装：`npx skills@1.7.2 add rrlan/pure-code-video --skill pure-code-video --agent codex -g`
- 安装后直接对 Agent 说：
  > `用 pure-code-video 的手绘水彩风（或 mg-05-cel-boil）做一条 20 秒科普视频，配中文语音、词级字幕和 CC0 转场音效，主题是：……`

### 姿势 3：嵌入你自己的网站或博客
在任意网页中加入一行 `<iframe>`（`?embed=1` 会自动隐藏顶部品牌栏，呈现纯净选片面板）：

```html
<iframe
  src="https://rrlan.github.io/pure-code-video/?embed=1"
  style="width: 100%; height: 860px; border: 0; border-radius: 16px;"
  loading="lazy"
></iframe>
```

---

## 二、命令行工具箱详解 (`run.py`)

安装完成后，可通过 `python3 ~/.agents/skills/pure-code-video/run.py <子命令>` 调用全部工具：

### 1. 环境与资源自检 (`doctor`)
```bash
python3 ~/.agents/skills/pure-code-video/run.py doctor
```
检查 530 款风格配方、109 个内置 CC0 音效文件、双渲染模板以及本机 `node` / `ffmpeg` 状态。

### 2. 搜索风格与提取配方 (`search` / `recipe`)
```bash
# 按关键词搜索画风或案例（如：水彩、3b1b、等轴、像素、浮世绘）
python3 ~/.agents/skills/pure-code-video/run.py search 水彩

# 按风格 ID 导出完整 JSON 配方与原始 Prompt
python3 ~/.agents/skills/pure-code-video/run.py recipe claude-textured-editorial
python3 ~/.agents/skills/pure-code-video/run.py recipe mg-05-cel-boil
```

### 3. 给视频配真实音效与节拍混音 (`sfx-list` / `sound-pass`)
```bash
# 查看内置的 109 个 CC0 音效及默认音效包（支持按分类筛选）
python3 ~/.agents/skills/pure-code-video/run.py sfx-list --category whoosh

# 为无声视频自动对齐音乐鼓点、挂载音效并按 -16 LUFS 标准混音
python3 ~/.agents/skills/pure-code-video/run.py sound-pass \
  --video silent.mp4 \
  --cues cues.json \
  --music track.mp3 \
  --out ./sound-out
```
- `cues.json` 格式示例：
  ```json
  [
    {"t": 0.8, "type": "scene_cut", "desc": "开场切入主标题"},
    {"t": 2.4, "type": "appear", "desc": "核心数据卡片弹出"},
    {"t": 5.0, "type": "build_up", "desc": "蓄力上扬"},
    {"t": 6.2, "type": "reveal", "desc": "结论重音落定"}
  ]
  ```
- 支持的 11 种标准动作类型（`type`）：`movement` / `scene_cut`（对应 `whoosh`）、`appear` / `success`（对应 `pop`）、`click`（对应 `click`）、`typing`（对应 `typing`）、`build_up`（对应 `riser`）、`reveal`（对应 `impact`）、`error_or_tech`（对应 `glitch`）、`hover_or_small_ui`（对应 `tick`）、`bed`（对应 `ambience`）。
- 输出产物：`after.mp4`（混音成片）、`SOUND.md`（响度与真峰值报告 + 5 个重点复核时间戳）、`CREDITS.txt`（CC0 署名清单）、`beatgrid.png`（底鼓节拍对齐图）与 `report.html`（可视化试听与替换面板）。

### 4. 用「你自己的声音」配音并驱动代码动画 (`voice-trim` / `voice-align` / `voice-clone`)

#### 方案 A：你自己用手机/麦克风录真声（推荐，最自然）
```bash
# 第一步：自动预剪口水词（嗯/呃/那个）、结巴重说与过长停顿（先 --dry-run 看报告，确认后输出 clean.wav）
python3 ~/.agents/skills/pure-code-video/run.py voice-trim raw.wav script.json --dry-run --words-out asr_words.json
python3 ~/.agents/skills/pure-code-video/run.py voice-trim raw.wav script.json --words asr_words.json --out clean.wav

# 第二步：本机 CPU 逐字对齐（支持默认 FireRedASR2-CTC 或 --backend whisper），生成毫秒级逐字时间戳
python3 ~/.agents/skills/pure-code-video/run.py voice-align clean.wav script.json timestamps.json --backend whisper
```

#### 方案 B：克隆你自己的音色自动读稿（不用每次自己录）
- **云端克隆（Fish Audio）**：在网站上传一段 15–30 秒你的清晰语音拿到 `REFERENCE_ID`，设置环境变量 `FISH_AUDIO_API_KEY` 与 `FISH_AUDIO_REFERENCE_ID` 后运行：
  ```bash
  python3 ~/.agents/skills/pure-code-video/run.py voice-clone script.json full.wav timestamps.json
  ```
  一条命令同时产出用你声音读的 `full.wav` 和逐字对齐好的 `timestamps.json`。
- **纯本地离线克隆（ComfyUI `IndexTTS2`）**：准备 20 秒你的干声 `reference.wav`，配合本机 `IndexTTS2` 节点按文稿合成你的声音，再运行上面的 `voice-align` 生成逐字时间戳。

---

## 三、仓库目录结构

```text
pure-code-video/
├── index.html                  # 可交互选片台网页（支持本地打开、GitHub Pages 与 ?embed=1 嵌入）
├── assets/                     # 530 款风格的预览视频、动态 WebP、GIF 与海报剧照
├── SKILL.md                    # Agent 技能主入口（供 Codex / Claude Code / Cursor 读取）
├── ATLAS.md                    # 按题材 10 秒选风格的导演路由表与总图鉴
├── INSTALL.md                  # 在线安装、ZIP 安装与命令速查手册
├── install.py                  # 自动化安装与更新入口（对接 skills@1.7.2）
├── run.py                      # 统一 CLI 入口（doctor / search / recipe / sfx-list / sound-pass / voice-*）
├── requirements.txt            # 音效与节拍分析 Python 依赖（由 skill_runtime.py 自动管理外部缓存环境）
├── recipes/
│   ├── core-styles.json        # 105 款核心命名风格完整配方
│   └── community-cases.json    # 425 个 Opus 5.5 社区实测案例与原始 Prompt
├── sfx/                        # 109 个 CC0 1.0 真实录音音效（13 大分类）+ manifest.json
├── references/                 # 音效混音规范 (SOUND-PASS.md)、免费配乐表 (MUSIC.md) 与 CC0 署名表
├── scripts/
│   ├── codevid.py              # CLI 主逻辑
│   ├── skill_runtime.py        # 外部可复用 Python 虚拟环境自动管理器
│   ├── sound_pass.py           # 节拍网格检测、CC0 音效挂载与 -16 LUFS 混音引擎
│   ├── report.py               # 音效试听与替换网页生成器
│   ├── voice_trim.py           # 真人录音口水词/结巴/气口自动预剪器
│   ├── timestamps_cpu.py       # 本机 CPU 逐字时间戳对齐器 (FireRedASR2 / Whisper)
│   ├── tts_fishaudio.py        # 个人克隆音色合成与时间戳对齐器
│   └── make_timing.py          # 时间戳转动画帧率时间轴工具
└── templates/
    ├── high-energy-html/       # 模板 1：128BPM 高能节拍快剪 + 60fps 虚拟时钟 Playwright 渲染器
    └── handdrawn-explainer/    # 模板 2：手绘水彩绘本科普 + 笔刷引擎 lib/ + edge-tts 词级字幕合成器
```

## 四、许可证与致谢

- 代码、渲染器与工程模板采用 **MIT License**；内置 109 个音效采用 **CC0 1.0 Public Domain**；案例图鉴元数据采用 **CC BY 4.0**。
- 上游致谢名单详见 [`THIRD_PARTY_NOTICES.md`](./THIRD_PARTY_NOTICES.md) 与 [`references/SFX-LICENSES.md`](./references/SFX-LICENSES.md)。
