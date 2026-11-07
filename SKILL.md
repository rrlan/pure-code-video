---
name: pure-code-video
description: Unified pure-code video style picker, director routing table, deterministic 60fps virtual-clock HTML renderer, and @napi-rs/canvas hand-drawn watercolour explainer pipeline with word-level Chinese TTS captions. Zero image-generation models required.
---

# Pure-Code Video (`pure-code-video`)

Use this skill when the user asks to create motion-graphics promos, hand-drawn watercolour explainers, mathematical animations, or Opus 5.5 style pure-code videos **without calling image-generation models**.

## 1. Visual Style Picker
- Live Interactive Gallery: https://rrlan.github.io/pure-code-video/
- Full Director Routing Table: see `ATLAS.md`.

## 2. Two Reference Production Pipelines Included
1. **High-Energy Beat-Locked HTML + WebGL/Canvas (`templates/high-energy-html/`)**:
   - Uses virtual-clock Playwright frame stepping (`window.__setTime(t)`) so 60fps capture never drops a frame.
   - Synthesizes sample-accurate 48kHz audio directly in code and muxes with `ffmpeg -c:v libx264 -crf 17 -pix_fmt yuv420p`.
2. **Textured-Editorial Hand-Drawn Watercolour Explainer (`templates/handdrawn-explainer/`)**:
   - Uses `@napi-rs/canvas` paper grain + 3-phase drawing (blue construction lines -> tapered brush ink -> watercolour wash).
   - Pairs with `edge-tts` (`zh-CN-YunxiNeural`) and `WordBoundary` events for millisecond-accurate karaoke captions.
