---
name: pure-code-video
description: Unified pure-code video style picker (530+ styles), director routing table, deterministic 60fps virtual-clock HTML renderer, @napi-rs/canvas hand-drawn watercolour explainer pipeline, bundled 121 CC0 SFX & BPM/Bit beat loops sound-effects pass (-16 LUFS beat-grid mixer), and custom human/cloned voiceover alignment. Zero image-generation models required.
---

# Pure-Code Video (`pure-code-video` v1.2.0)

Use this skill when the user asks to create motion-graphics promos, hand-drawn watercolour explainers, mathematical animations, or Opus 5.5 style pure-code videos **without calling image-generation models**.

## 1. Visual Style Picker (530+ Styles)
- Live Interactive Gallery: https://rrlan.github.io/pure-code-video/
- Full Director Routing Table: see `ATLAS.md`.
- Offline CLI lookup:
  - `python3 run.py search <keyword>`
  - `python3 run.py recipe <style-id>`

## 2. Two Reference Visual Production Pipelines
1. **High-Energy Beat-Locked HTML + WebGL/Canvas (`templates/high-energy-html/`)**:
   - Virtual-clock Playwright frame stepping (`window.__setTime(t)`) for zero-drop 60fps capture.
2. **Textured-Editorial Hand-Drawn Watercolour Explainer (`templates/handdrawn-explainer/`)**:
   - Bundled `@napi-rs/canvas` brush & paper grain library (`templates/handdrawn-explainer/lib/`).

## 3. Integrated Sound Pass (`sound-effects` — 109 Bundled CC0 SFX + Beat Grid + `-16 LUFS` Mix)
- Full rules & cue table: see `references/SOUND-PASS.md`, `references/MUSIC.md`, and `references/SFX-LICENSES.md`.
- Bundled CC0 SFX library (`sfx/`): 109 real recorded CC0 sound effects across 13 categories (`whoosh`, `click`, `pop`, `riser`, `impact`, `tick`, `ambience`, `ding`, `glitch`, `transition`, `typing`, `ui-blip`).
- CLI commands:
  - `python3 run.py beat-gen --preset 128bpm-launch --seconds 15 --out bgm.wav --grid-out beats.json`
  - `python3 run.py sfx-list [--category beats|whoosh]`
  - `python3 run.py sound-pass --video silent.mp4 --cues cues.json --music track.mp3 --out out/` (automatically prepares external Python venv with `librosa`, `soundfile`, `scipy`, `matplotlib` and mixes to `-16 LUFS` / true peak `< -4 dBFS`).

## 4. Custom Voiceover & Voice Cloning Pipelines
Supports 3 ways to voice a pure-code video:
1. **Your Own Recorded Voice (`voice-trim` + `voice-align`)**:
   - Trim filler words ("嗯/呃"), repeats, and long pauses: `python3 run.py voice-trim raw.wav script.json --out clean.wav`
   - Align your voice to the script on local CPU (`FireRedASR2-CTC` or `--backend whisper`): `python3 run.py voice-align clean.wav script.json timestamps.json`
2. **Cloned Voice Synthesis (`voice-clone` / Local IndexTTS2)**:
   - Cloud cloned voice (`FISH_AUDIO_API_KEY` + `FISH_AUDIO_REFERENCE_ID`): `python3 run.py voice-clone script.json full.wav timestamps.json`
   - Local zero-shot voice cloning from a 20s reference WAV: pairs with local ComfyUI `IndexTTS2` (`human-share-local`), then runs `voice-align` for millisecond word timestamps.
3. **Standard Neural TTS (`templates/handdrawn-explainer/make_voice.py`)**:
   - Zero-config `edge-tts` (`zh-CN-YunxiNeural`) with automatic `WordBoundary` karaoke timestamps.
