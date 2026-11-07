# Pure-Code Video (`pure-code-video`)

> **530+ Pure-Code Video & Opus 5.5 Animation Styles** — Interactive Visual Picker, Complete Prompt Recipes, Deterministic 60fps Virtual-Clock Renderer & Hand-Drawn Watercolour Voiceover Pipeline. **Zero image-generation models required.**

- **在线选片台 (GitHub Pages)**: [https://rrlan.github.io/pure-code-video/](https://rrlan.github.io/pure-code-video/)

---

## 核心特性

1. **105 款核心命名风格库（带实测 MP4 / 动态 WebP / GIF / 电影海报）**
   - **Pure-Code 原创实测样片（2 款）**：128 BPM 高能体素快剪（`argon-high-energy`）+ 手绘水彩切叶蚁科普短片（`claude-textured-editorial`，含中文神经语音配音与逐词卡拉 OK 字幕）。
   - **Opus 5.5 十五种 MG 动效（15 款）**：逐帧手绘线条沸腾、等轴 2.5D 城市、一笔画、3D 软体、一形万象连续形变、粗描边贴纸科普、赛博 HUD 等。
   - **Lemo-Opuscar 电影级代码短片库（66 款）**：浮世绘、水墨、皮影戏、橡皮管卡通、黏土定格、CRT 终端、3D 着色器等。
   - **花叔 8 大王牌频道解说语法 + 6 款名画流场渲染器**：Kurzgesagt、Vox、3Blue1Brown、RSA 白板、Apple Keynote、梵高厚涂流场、莫奈水影、8-Bit 闯关等。
   - **大师中文口播长视频风格（8 款）**：手帐荧光笔笔记、现代扁平流程图、复古报刊、手工剪纸等。
2. **425 个 Opus 5.5 社区实测案例库（含完整原始 Prompt）**
   - 支持按 10 大分类与关键词实时搜索，一键复制点单口令或原始 Prompt。
3. **支持一键嵌入任意个人网站（Iframe Embed Mode）**
   ```html
   <iframe
     src="https://rrlan.github.io/pure-code-video/?embed=1"
     style="width: 100%; height: 860px; border: 0; border-radius: 16px;"
     loading="lazy"
   ></iframe>
   ```

## 作为 Agent Skill 安装（Claude Code / Codex / Cursor）

```bash
git clone https://github.com/rrlan/pure-code-video.git ~/.codex/skills/pure-code-video
```

安装后直接复制选片台上的「点单口令」发给 Agent：
> `请用【手绘水彩绘本科普（风格ID: claude-textured-editorial）】画风帮我做一条纯代码视频，主题是：……`

## 许可证与致谢

- 代码与工程模板采用 **MIT License**，案例图鉴与元数据采用 **CC BY 4.0**。
- 上游致谢名单详见 [`THIRD_PARTY_NOTICES.md`](./THIRD_PARTY_NOTICES.md)。
