---
name: reference_pure_code_video_styles_atlas
description: 纯代码视频与 Claude Opus 5.5 视频风格总图鉴（8 大本机风格库、600+ 细分画风/镜头卡/配方与按题材选型路由表）
metadata:
  type: reference
  updated: 2026-11-07
---

# 纯代码视频与 Opus 5.5 风格总图鉴（Pure-Code Video Style Atlas）

本图鉴汇总本机已就绪的 **8 大纯代码视频风格与模板库（共 600+ 细分风格、提示词配方、镜头卡与可运行源码）**。所有风格均通过代码（HTML5 / Canvas 2D / SVG / WebGL Shader / Three.js / `@napi-rs/canvas` / p5.brush / Remotion / Manim + WebAudio/Python 合成音轨 + `edge-tts` 词级对齐字幕）逐帧确定性渲染，**无需调用生图大模型**。

后续制作视频时，可直接点名下列**风格编号、中文名或英文 ID**。

---

## 一、按题材 10 秒快速选风格（导演路由表）

| 你要做的视频类型 | 首选风格（点名即用） | 备选风格（拉开差异） | 对应本机引擎与路径 |
|---|---|---|---|
| **1. 产品发布 / App 演示 / 功能快闪** | `high-energy`（高能卡点动态排版 + 3D 卡片）<br>`keynote-ui`（苹果发布会推镜） | `aurora-glass`（弥散极光毛玻璃）<br>`living-screencast`（活体实机光标录屏）<br>`video-shotcraft`（124 张 2.5D 镜头卡） | `./skills/explainer-high-energy/`<br>`./skills/video-shotcraft/`<br>`./upstream/lemo-opuscar/styles/dark-keynote/` |
| **2. 科普讲解 / 机制拆解（带中文配音+词级字幕）** | `textured-editorial`（手绘水彩绘本+剖面图）<br>`warm-gold` / `paper-ink`（叙事机制图解） | `y1_kurzgesagt`（发光扁平宇宙缩放）<br>`19-paperclip`（回形针粗描边贴纸 MG）<br>`teardown`（产品爆炸拆解） | `./skills/claude-animation/`<br>`./skills/motion-story-video/`<br>`./skills/huashu-art-motion/` |
| **3. 数学 / 算法 / 深度学习原理** | `t1_3b1b`（3Blue1Brown 连续形变推导）<br>`manim-video`（Manim 严格数学公式） | `blueprint`（工程蓝图制图）<br>`circuit-board`（微距电路信号流） | `./skills/huashu-art-motion/references/动画语法/t1_3b1b.md`<br>`./skills/manim-video/` |
| **4. 商业分析 / 财经数据 / 战略汇报** | `t3_finance_chart`（诚实坐标系生长图表）<br>`dataviz`（数据叙事） | `y2_vox`（Vox 调查桌面档案+荧光笔）<br>`halftone-dossier`（复古半调案卷）<br>`iso-infographic`（等距 2.5D 信息图） | `./skills/huashu-art-motion/references/动画语法/t3_finance_chart.md`<br>`./upstream/lemo-opuscar/styles/dataviz/` |
| **5. 观点清单 / 推理链 / 个人故事口播** | `y3_whiteboard`（RSA 大白板边讲边画）<br>`dashi-手绘笔记`（手帐荧光笔笔记） | `paper-reel`（9:16 竖屏剪纸吉祥物+盖章）<br>`y4_storytime`（简笔表情包反应喜剧）<br>`18-hanazi`（9:16 竖屏综艺花字） | `./skills/dashi-animationstyle/`<br>`./skills/paper-reel/`<br>`./upstream/mg-styles-15/` |
| **6. 艺术短片 / 历史人文 / 品牌视觉秀** | `09_postimp`（梵高流场笔触）<br>`ukiyoe`（浮世绘） / `ink-wash`（中国水墨） | `risograph`（孔版套色网点）<br>`shadow-puppet`（中国皮影戏）<br>`rubber-hose`（1930s 茶杯头橡皮管卡通） | `./skills/huashu-art-motion/references/风格配方/`<br>`./upstream/lemo-opuscar/styles/` |
| **7. 极客文化 / 游戏感 / 赛博复古** | `pixel-rpg` / `20-pixel`（整数倍像素动画）<br>`ascii-crt`（绿磷 CRT 终端 + 示波器） | `22-hud`（赛博朋克战术 HUD/FUI）<br>`10-synthwave`（80s 霓虹网格 VHS）<br>`lowpoly-island`（低多边形体素积木） | `./upstream/awesome-opus-5-5-video-styles/`<br>`./upstream/lemo-opuscar/styles/ascii-crt/` |

---

## 二、八大本机风格库详细清单与文件入口

### 1. `awesome-opus-5-5-video-styles`（Opus 5.5 视频画风图鉴 · 12 大类 425 案例）
- **本地路径**：`./upstream/awesome-opus-5-5-video-styles/`
- **结构化数据**：`data/cases.json`（含 425 条完整 Prompt）+ `assets/stills/`（425 张效果静帧）
- **12 类核心风格配方（`styles/*.zh-CN.md`）**：
  1. **动态排版（`typography.zh-CN.md`，52 例）**：1–2 款粗黑字体、按节拍遮罩弹入/拉伸/擦除、严格网格、2–3 色配一高饱和强调色。
  2. **产品 UI 宣传片（`productui.zh-CN.md`，80 例）**：纯矢量重建真实产品 UI 状态、光标平滑点击完整流程、闭式弹簧缓动、柔和投影。
  3. **电影感 3D（`cinematic3d.zh-CN.md`，82 例）**：Three.js/WebGL PBR 材质、单主光柔影、景深、缓慢推轨/环绕运镜、2.39:1 宽银幕。
  4. **科普图解与数据可视化（`explainer.zh-CN.md`，38 例）**：一镜一概念、坐标轴自绘、数值滚动、引线标签就近浮现。
  5. **扁平卡通（`cartoon.zh-CN.md`，43 例）**：粗深色轮廓、单层明暗平涂、每次运动带挤压拉伸（Squash & Stretch）。
  6. **生成艺术与霓虹（`generative.zh-CN.md`，34 例）**：程序化粒子、流场、GLSL 着色器或几何铺砖，完全锁定音频节拍。
  7. **低多边形与体素（`lowpoly.zh-CN.md`，32 例）**：平面着色三角面或体素方块、等距/高斜角镜头、粉彩配高饱和点缀色、弹出带过冲。
  8. **手绘 · 线稿 · 漫画（`handdrawn.zh-CN.md`，22 例）**：米白纸底抖动铅笔/墨线、每数帧重绘（Line Boil，8–12fps）、墨黑+单强调色。
  9. **像素风（`pixel.zh-CN.md`，22 例）**：320×180 离屏画布、固定 16–32 色板、最近邻整数倍放大（禁用抗锯齿）、8-bit 芯片音乐。
  10. **拼贴 · 剪纸 · 沙画（`collage.zh-CN.md`，6 例）**：撕边纸片/相片残片、柔和投影与纸纹、12fps 定格步进。
  11. **复古 · 终端 · 老电影（`retro.zh-CN.md`，5 例）**：18fps 黑白胶片闪烁暗角，或绿/琥珀色荧光 CRT 扫描线终端与示波器。
  12. **写实编排（`photoreal.zh-CN.md`，9 例）**：实拍/绿幕素材踩点剪辑 + 克制排版与统一调色。

---

### 2. `lemo-opuscar`（Opus 代码电影导演库 · 11 大类 66 种命名风格）
- **本地路径**：`~/lemo-opuscar/styles/`（索引见 `~/lemo-opuscar/styles/README.md`；按需拉取单个 demo 源码：`sh ./skills/lemo-opuscar/scripts/setup.sh demo <slug>`）
- **全部分类与目录名（每个目录含完整 `STYLE.md` 制作规范）**：
  - **剪辑与纪实**：`caption-news`（字幕新闻）、`newsreel`（1920s 新闻片）、`countdown`（实时倒计时分屏）、`city-symphony`（延时交响）、`visual-investigation`（视觉调查）、`kino-montage`（构成主义蒙太奇）、`telestrator`（体育战术板）、`news-package`（电视新闻包装）
  - **实证影像**：`satellite-briefing`（卫星简报）、`briefing-board`（工程简报板）、`lidar-survey`（点云测绘）、`white-model`（白模投影）、`data-physical`（数据实物化）、`teardown`（产品拆解）、`microscope`（显微叙事）、`archive-lighttable`（档案灯台）
  - **手绘与绘画**：`crayon-book`（蜡笔绘本）、`watercolor`（水彩笔刷）、`ink-wash`（中国水墨）、`impasto`（油画厚涂）、`one-line`（一笔画）、`whiteboard`（白板讲解）、`urban-sketch`（钢笔淡彩）、`chalkboard`（黑板粉笔）
  - **东方传统**：`shadow-puppet`（皮影戏）、`ukiyoe`（浮世绘）、`papercut-red`（红色窗花剪纸）、`paper-lantern`（纸雕灯影）
  - **印刷与版画**：`risograph`（Risograph 孔版印刷）、`halftone-dossier`（复古半调案卷）、`woodcut`（木刻版画）、`engraving`（铜版画）、`silkscreen-poster`（丝印旅行海报）、`printed-long-take`（印刷长镜头）
  - **图形与排版**：`swiss-motion`（瑞士动态排版）、`spy-titles`（60s 间谍片头）、`art-deco`（装饰艺术）、`blueprint`（工程蓝图）、`stained-glass`（彩色玻璃窗）、`pictogram-motion`（象形运动图形）、`ascii-crt`（ASCII/CRT 终端）
  - **信息与发布**：`dataviz`（数据叙事）、`iso-infographic`（等距信息图）、`dark-keynote`（暗色科技发布）、`living-screencast`（活体实机录屏）、`hologram-hud`（科幻全息界面）、`transit-map`（地铁线路图）、`isometric-picture-book`（等距绘本）、`circuit-board`（电路板）
  - **卡通与动画**：`rubber-hose`（1930s 橡皮管卡通）、`cel-anime-80s`（80s 赛璐璐动画）、`scifi-toon`（科幻情景喜剧卡通）、`midcentury-toon`（50s 扁平卡通）
  - **游戏**：`pixel-rpg`（16-bit 像素 RPG）、`hd-2d`（HD-2D）、`microgame`（微游戏快闪）、`game-show`（综艺节奏扁平）
  - **电影与时代**：`silent-film`（1920s 默片）、`backrooms`（后室/新怪谈）
  - **材质与 3D**：`brick-toy`（积木玩具）、`paper-popup`（纸片立体书）、`tilt-shift`（移轴微缩）、`lowpoly-island`（低多边形等距岛）、`glass-product`（玻璃质感产品）、`memphis-diorama`（孟菲斯微缩景观）、`desktop-flythrough`（桌面穿梭）

---

### 3. `mg-styles-15`（Vincent 的 15 种 Opus 5.5 MG 动态设计风格 · 含完整提示词与源码）
- **本地路径**：`./upstream/mg-styles-15/`（提示词在 `prompts/`，可运行源码在 `demos/`）
- **15 套已调优风格**：
  1. `05-cel-boil`：逐帧手绘 / 线条沸腾（手作质感）
  2. `03-isometric`：等轴 2.5D（城市/系统模块化生长）
  3. `01-flat-vector`：扁平矢量几何（一圆变万物）
  4. `02-line-art`：一笔画连续线条动画
  5. `04-3d-render`：C4D/Blender 软体物理着陆质感
  6. `08-morph`：连续无缝形变（一形万象）
  7. `19-paperclip`：粗描边贴纸人硬核科普 MG（回形针风格）
  8. `22-hud`：赛博朋克 HUD / FUI 目标锁定界面
  9. `06-collage`：复古杂志剪报拼贴
  10. `12-aurora-glass`：弥散极光渐变 + 玻璃拟态
  11. `09-bauhaus`：包豪斯纯几何节奏构成
  12. `10-synthwave`：80s 复古霓虹夜驰 / VHS 扫描线
  13. `20-pixel`：复古像素冒险
  14. `07-liquid`：液态水滴融合与表面张力流动
  15. `18-hanazi`：9:16 竖屏高能综艺花字

---

### 4. `huashu-art-motion` & `huashu-motion`（8 种解说动画语法 + 36 种名画渲染器 + 20 种运动语言）
- **本地路径**：`./skills/huashu-art-motion/` 与 `./skills/huashu-motion/`
- **8 种口播解说动画语法（`references/动画语法/`，可直接喂 JSON 渲片段）**：
  - `y1_kurzgesagt`（Kurzgesagt 发光扁平宇宙与对数尺度推拉）
  - `y2_vox`（Vox 调查记者桌面、档案剪报与 12fps 荧光笔划线）
  - `y3_whiteboard`（RSA 白板手绘边讲边写，收尾拉远看全图）
  - `y4_storytime`（第一人称简笔角色 0.1s 换姿势 + 停顿反应特写）
  - `y5_kinetic_type`（重音砸词大字报，一镜一焦点）
  - `t1_3b1b`（3Blue1Brown 黑底连续公式/几何变换推导）
  - `t2_keynote_ui`（发布会界面实拍推近 + 数据落定）
  - `t3_finance_chart`（先搭坐标轴再生长的严谨财经图表）
- **20 种商业宣传片运动语言（`huashu-motion/references/library/languages/`）**：
  - `cursor-demo`、`continuous-morph`、`card-montage`、`kinetic-type`、`modular-grid`、`data-story`、`mechanism`、`system-diagram`、`flat-world`、`editorial-collage`、`hand-drawn`、`character`、`3d-object`、`generative-field`、`liquid-glass`、`photo-led`、`showreel`、`retro-digital`、`art-styles`、`talking-head`。
- **36 种名画与媒介材料渲染器（`huashu-art-motion/references/风格配方/`）**：
  - ★★★ 标杆实做：`09_postimp`（梵高流场笔触）、`13_pop`（利希滕斯坦波普网点）、`14_8bit`（8-bit 像素）、`16_2026`（当代颗粒点彩扁平插画）、`26_vaporwave`（蒸汽波）、`30_matisse`（马蒂斯剪纸）、`22_constructivism`（俄国构成主义）、`12_bauhaus`（包豪斯）、`04_roman`（庞贝马赛克）、`01_cave`（洞穴岩画）、`02_egypt`（埃及壁画）、`03_greek`（希腊黑绘）、`05_gothic`（哥特泥金手抄本）、`10_nouveau`（慕夏新艺术）、`18_klimt`（克里姆特金箔）、`21_kusama`（草间弥生波点）、`24_hopper`（霍珀硬边光影）、`31_haring`（凯斯·哈林）、`33_rubberhose`（1930 橡皮管卡通）、`34_shadowpuppet`（中国皮影）。

---

### 5. `claude-animation` + `hiapi-hand-painted-animation-skill`（手绘水彩绘本与角色表演引擎）
- **本地路径**：`./skills/claude-animation/` 与 `./upstream/hiapi-hand-painted-animation-skill/`
- **5 种内置预设风格（`references/styles.md`）**：
  1. `Textured editorial`（精细绘本科普：水彩纸纹、斜向光束、蓝色画师辅助线 `antGuides`、三层材质着色、12fps 角色抽帧）
  2. `Brush ink + watercolour`（毛笔墨线 + 10fps 线条沸腾 + `pen.wash` 水彩洇染 + 豆子人 `bean.mjs`）
  3. `Line doodle`（极简米白底黑线红点缀速写）
  4. `3D extruded type`（圆柱环绕立体擠出大字）
  5. `Faceted low-poly poster`（低多边形折面风景无缝循环海报 + 环境音）

---

### 6. `dashi-animationstyle` & `paper-reel` & `motion-story-video`（中文口播驱动风格包）
- **`dashi-animationstyle`（7 套口播画风，`./skills/dashi-animationstyle/styles/`）**：
  - `扁平流程图`、`手绘笔记`、`复古报刊`、`复古剪纸`、`超现实拼贴`、`立体卡通`、`黑底科技`（另含 `霓虹赛博`）。
- **`motion-story-video`（3 套叙事图解风格包，`./skills/motion-story-video/`）**：
  - `warm-gold`（暖黑金机制图解，已验证）、`paper-ink`（纸白墨蓝系统图解）、`editorial-social`（社会观察编辑插画）。
- **`paper-reel`（9:16 竖屏剪纸口播短片，`./skills/paper-reel/`）**：
  - 满幅剪纸场景（教室/安检台/工作室/软木板）+ 逐词碎纸片字幕 `prChips()` + 关键词触发盖章/计数器。

---

### 7. `video-shotcraft` & `herk-edit-kit` & `motion-prompt`（电影感镜头配方卡与动效词典）
- **`video-shotcraft`（124 张镜头配方卡，`./skills/video-shotcraft/references/shots/`）**：
  - 覆盖 10 大镜头类别：`opening`（开场）、`ui-entrance`（界面入场）、`camera`（2.5D 运镜）、`interaction`（光标与交互）、`data`（数据生长）、`typography`（排版动效）、`transition`（转场）、`effects`（光效材质）、`rhythm`（节奏卡点）、`outro`（收尾定版），自带 `Ink Press` 完整模板。
- **`herk-edit-kit`（406 张动效卡，`./skills/herk-edit-kit/`）** 与 **`motion-prompt`（编号运动图形词典，`./skills/motion-prompt/`）**。

---

### 8. `explainer-*` & `motion-launch-videos`（15 套单文件纯代码循环/发布短片）
- **本地路径**：`./skills/`
- **3 套产品宣传片**：`explainer-high-energy`（128BPM 高能快剪，本轮第 1 支样片所选）、`explainer-engaging`（10–30s 一镜到底连续变形）、`explainer-default`（45–90s 完整产品功能演示）。
- **12 套专项动效**：`motion-3d`（真 3D 倒角字）、`motion-cartoon`（原创吉祥物循环）、`motion-charts`（动态数据故事）、`motion-globe`（全球网络点阵地球）、`motion-particles`（千级粒子流场）、`motion-photo`（产品图集快剪）、`motion-pixel`（像素风循环）、`motion-shapes`（2D 几何图形循环）、`motion-ui`（3D 倾斜手机/桌面 UI 演示）、`motion-overlays`（带透明通道叠加层）、`motion-captions`（口播动态字幕包装）。
