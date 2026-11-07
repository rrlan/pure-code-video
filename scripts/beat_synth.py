#!/usr/bin/env python3
"""Deterministic pure-code BPM Beat & Bit-Era Rhythm Loop Synthesizer (48kHz).
Generates sample-accurate 64/96/110/120/128/140/160 BPM and 8-bit/16-bit/64-bit rhythm loops
plus exact beat-grid JSON timestamps (kicks, snares, bars, beats).
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import tempfile
import wave
import numpy as np

SR = 48000

PRESETS = {
    "128bpm-launch": {
        "bpm": 128,
        "title_zh": "128 BPM · 高能产品发布快剪律动 (Launch Promo)",
        "usage": "1拍=0.46875s，四四拍重低音底鼓+清脆军鼓+16分音符合成琶音；适合高能产品发布、大字砸屏与3D快剪。",
        "bars": 4,
    },
    "64bpm-cinematic": {
        "bpm": 64,
        "title_zh": "64 BPM · 电影感深沉重拍慢律动 (Cinematic Half-Time)",
        "usage": "1拍=0.9375s，深潜808超低音+宽广空间军鼓+大气弦乐铺底；适合深度纪实、宏大开场与慢推镜头。",
        "bars": 2,
    },
    "64bpm-lofi": {
        "bpm": 64,
        "title_zh": "64 BPM · Lo-Fi 温暖叙事与科普律动 (Warm Study Groove)",
        "usage": "1拍=0.9375s，柔和切分底鼓+刷子军鼓+温暖七和弦电钢；适合手绘水彩科普、绘本故事与中文口播垫乐。",
        "bars": 2,
    },
    "96bpm-boombap": {
        "bpm": 96,
        "title_zh": "96 BPM · 调查档案与数据拆解律动 (Explainer Groove)",
        "usage": "1拍=0.625s，利落现代Boom-Bap鼓组+低音贝斯拨弦；适合Vox风档案桌面、商业分析与逻辑推演。",
        "bars": 3,
    },
    "110bpm-synthwave": {
        "bpm": 110,
        "title_zh": "110 BPM · 80s 霓虹合成器夜驰 (Retro Synthwave)",
        "usage": "1拍=0.545s，复古门限混响军鼓+八度跳跃模拟贝斯；适合赛博霓虹、VHS复古与极客文化。",
        "bars": 4,
    },
    "120bpm-minimal": {
        "bpm": 120,
        "title_zh": "120 BPM · 极简科技时钟脉冲 (0.500s/拍 精准网格)",
        "usage": "1拍严格=0.500s（1小节=2.000s），精密微脉冲底鼓+时钟刻度Tick+清澈泛音；适合UI演示、架构图与数学推导。",
        "bars": 4,
    },
    "128bpm-electro": {
        "bpm": 128,
        "title_zh": "128 BPM · 赛博高能电子酸贝斯 (Cyber Acid Electro)",
        "usage": "1拍=0.46875s，失真重型底鼓+303谐振滤波扫频贝斯+高速镲片；适合硬核科技、算力展示与高能数据。",
        "bars": 4,
    },
    "140bpm-garage": {
        "bpm": 140,
        "title_zh": "140 BPM · 灵动切分两步舞曲 (2-Step Future Garage)",
        "usage": "1拍=0.4286s，跳跃切分鼓点+温暖Sub-Bass滑音；适合年轻化短视频、App快闪与轻快动效合集。",
        "bars": 4,
    },
    "160bpm-dnb": {
        "bpm": 160,
        "title_zh": "160 BPM · 极速流体鼓打贝斯 (Liquid Drum & Bass)",
        "usage": "1拍=0.375s，高速切分碎拍Breakbeat+深潜重低音+空灵和弦；适合极速代码滚动、密集快剪与高燃冲刺。",
        "bars": 4,
    },
    "8bit-chiptune-128": {
        "bpm": 128,
        "title_zh": "8-Bit · 红白机方波芯片节拍 (8-Bit Chiptune 128 BPM)",
        "usage": "纯正占空比脉冲方波旋律+三角波贝斯+白噪芯片鼓组；专为复古像素风（Pixel Art）与游戏感短片设计。",
        "bars": 4,
    },
    "16bit-arcade-130": {
        "bpm": 130,
        "title_zh": "16-Bit · 街机 FM 金属合成律动 (16-Bit FM Arcade 130 BPM)",
        "usage": "世嘉MD/街机风格FM调频金属弹跳贝斯+紧凑数码鼓机；适合复古街机、排行榜与硬核极客主题。",
        "bars": 4,
    },
    "64bit-jungle-150": {
        "bpm": 150,
        "title_zh": "64-Bit · 千禧主机 3D 丛林碎拍 (64-Bit Y2K Jungle 150 BPM)",
        "usage": "N64/PS1千禧年代风格高速Jungle碎拍+空灵3D环境泛音垫；完美搭配低多边形3D、体素与赛博HUD。",
        "bars": 4,
    },
}


def add_sound(buf: np.ndarray, start_s: float, sig: np.ndarray, pan: float = 0.0):
    idx = int(round(start_s * SR))
    if idx < 0 or idx >= len(buf):
        return
    end = min(len(buf), idx + len(sig))
    seg = sig[: end - idx]
    l_gain = math.cos((pan + 1.0) * math.pi / 4.0)
    r_gain = math.sin((pan + 1.0) * math.pi / 4.0)
    buf[idx:end, 0] += seg * l_gain
    buf[idx:end, 1] += seg * r_gain


def kick_dsp(dur=0.32, f0=145.0, f1=42.0, punch=0.85, drive=1.3):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    freq = f1 + (f0 - f1) * np.exp(-t * 28.0)
    phase = 2 * np.pi * np.cumsum(freq) / SR
    env = np.exp(-t * 9.5) * (1.0 - np.exp(-t * 400.0))
    click = np.exp(-t * 180.0) * np.sin(2 * np.pi * 1200.0 * t) * 0.22
    return np.tanh((np.sin(phase) * env + click) * drive) * punch


def snare_dsp(dur=0.22, tone_hz=185.0, snappy=0.55, amp=0.55, rng=None):
    if rng is None:
        rng = np.random.default_rng(42)
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    body = np.sin(2 * np.pi * (tone_hz + 90 * np.exp(-t * 40)) * t) * np.exp(-t * 22.0)
    noise = rng.standard_normal(len(t)) * np.exp(-t * 16.0)
    return np.tanh((body * (1.0 - snappy) + noise * snappy) * 1.4) * amp


def hat_dsp(dur=0.06, open_hat=False, amp=0.22, rng=None):
    if rng is None:
        rng = np.random.default_rng(99)
    d = 0.20 if open_hat else dur
    t = np.linspace(0, d, int(SR * d), endpoint=False)
    decay = 14.0 if open_hat else 55.0
    # Metallic square-wave cluster + high-frequency noise
    metal = (
        np.sign(np.sin(2 * np.pi * 3420 * t))
        + np.sign(np.sin(2 * np.pi * 5180 * t))
        + np.sign(np.sin(2 * np.pi * 7890 * t))
    ) / 3.0
    noise = rng.standard_normal(len(t))
    hp = np.diff(noise, prepend=0.0)
    return (metal * 0.35 + hp * 0.65) * np.exp(-t * decay) * amp


def bass_note(freq: float, dur: float, style: str = "sub", amp: float = 0.38):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    env = np.exp(-t * 5.0) * (1.0 - np.exp(-t * 160.0))
    if style == "acid":
        mod = np.sin(2 * np.pi * freq * 2.0 * t) * np.exp(-t * 14.0) * 3.2
        sig = np.tanh(np.sin(2 * np.pi * freq * t + mod) * 1.8)
    elif style == "fm16":
        mod = np.sin(2 * np.pi * freq * 3.0 * t) * np.exp(-t * 12.0) * 2.6
        sig = np.sin(2 * np.pi * freq * t + mod)
    elif style == "chip8":
        # Triangle wave quantized to 16 steps
        tri = 2.0 * np.abs(2.0 * ((t * freq) % 1.0) - 1.0) - 1.0
        sig = np.round(tri * 8.0) / 8.0
    elif style == "synthwave":
        saw = 2.0 * ((t * freq) % 1.0) - 1.0
        sub = np.sin(2 * np.pi * freq * 0.5 * t)
        sig = np.tanh((saw * 0.6 + sub * 0.7) * 1.3)
    else:
        sig = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 2.0 * t) * np.exp(-t * 10.0)
    return sig * env * amp


def synth_note(freq: float, dur: float, wave_type: str = "pluck", amp: float = 0.18):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    fade_out = np.clip((dur - t) / min(0.06, dur * 0.3), 0.0, 1.0)
    if wave_type == "chip8":
        # 25% pulse wave
        pulse = np.where(((t * freq) % 1.0) < 0.25, 1.0, -1.0)
        env = np.exp(-t * 6.5) * (1.0 - np.exp(-t * 300.0))
        return pulse * env * amp
    elif wave_type == "pad":
        env = (1.0 - np.exp(-t * 8.0)) * fade_out
        s = (
            np.sin(2 * np.pi * freq * t)
            + 0.6 * np.sin(2 * np.pi * freq * 1.004 * t)
            + 0.4 * np.sin(2 * np.pi * freq * 1.5 * t)
        ) / 2.0
        return s * env * amp
    else:
        env = np.exp(-t * 8.0) * (1.0 - np.exp(-t * 250.0))
        s = np.sin(2 * np.pi * freq * t + np.sin(2 * np.pi * freq * 2.0 * t) * np.exp(-t * 15.0))
        return s * env * amp


def synthesize_preset(preset_id: str, seconds: float | None = None):
    meta = PRESETS[preset_id]
    bpm = meta["bpm"]
    beat_s = 60.0 / bpm
    bar_s = beat_s * 4.0
    total_s = seconds if seconds is not None else (meta["bars"] * bar_s)
    total_beats = int(math.ceil(total_s / beat_s))

    buf = np.zeros((int(round(total_s * SR)), 2), dtype=np.float64)
    rng = np.random.default_rng(abs(hash(preset_id)) % (2**31))

    kicks_t = []
    snares_t = []
    beats_t = [round(b * beat_s, 4) for b in range(total_beats) if b * beat_s < total_s]

    for b in range(total_beats):
        bt = b * beat_s
        if bt >= total_s:
            break
        in_bar = b % 4

        if preset_id in ("128bpm-launch", "128bpm-electro"):
            # Four-on-the-floor kick
            add_sound(buf, bt, kick_dsp(0.30, 155, 44, punch=0.82, drive=1.5 if "electro" in preset_id else 1.25))
            kicks_t.append(round(bt, 4))
            if in_bar in (1, 3):
                add_sound(buf, bt, snare_dsp(0.20, 195, snappy=0.6, amp=0.50, rng=rng))
                snares_t.append(round(bt, 4))
            for sub in range(4):
                st = bt + sub * (beat_s / 4.0)
                add_sound(buf, st, hat_dsp(open_hat=(sub == 2), amp=0.18 if sub == 2 else 0.11, rng=rng), pan=0.15 if sub % 2 else -0.15)
                arp_notes = [174.61, 207.65, 261.63, 349.23] if "launch" in preset_id else [87.31, 87.31, 174.61, 155.56]
                fn = arp_notes[(b * 4 + sub) % len(arp_notes)]
                if "electro" in preset_id:
                    add_sound(buf, st, bass_note(fn, beat_s / 4.0, style="acid", amp=0.34))
                else:
                    add_sound(buf, st, synth_note(fn * 2.0, beat_s / 4.0, wave_type="pluck", amp=0.16), pan=(sub - 1.5) * 0.2)
            if "launch" in preset_id and sub in (0, 2):
                add_sound(buf, bt, bass_note(87.31 if in_bar < 2 else 69.30, beat_s * 0.9, style="sub", amp=0.40))

        elif preset_id == "64bpm-cinematic":
            if in_bar in (0, 2):
                add_sound(buf, bt, kick_dsp(0.55, 120, 36, punch=0.88, drive=1.4))
                kicks_t.append(round(bt, 4))
                add_sound(buf, bt, bass_note(55.0 if in_bar == 0 else 43.65, beat_s * 1.9, style="sub", amp=0.45))
            if in_bar in (1, 3):
                add_sound(buf, bt, snare_dsp(0.38, 150, snappy=0.65, amp=0.52, rng=rng))
                snares_t.append(round(bt, 4))
            if in_bar == 0:
                for chord_hz in (220.0, 261.63, 329.63):
                    add_sound(buf, bt, synth_note(chord_hz, bar_s * 0.95, wave_type="pad", amp=0.11))
            for sub in range(2):
                add_sound(buf, bt + sub * (beat_s / 2.0), hat_dsp(amp=0.10, rng=rng))

        elif preset_id == "64bpm-lofi":
            if in_bar == 0:
                add_sound(buf, bt, kick_dsp(0.35, 110, 45, punch=0.72, drive=1.1))
                kicks_t.append(round(bt, 4))
            if in_bar == 2:
                add_sound(buf, bt + beat_s * 0.25, kick_dsp(0.35, 110, 45, punch=0.68, drive=1.1))
                kicks_t.append(round(bt + beat_s * 0.25, 4))
            if in_bar in (1, 3):
                add_sound(buf, bt, snare_dsp(0.18, 175, snappy=0.45, amp=0.42, rng=rng))
                snares_t.append(round(bt, 4))
            for sub in range(2):
                swing = 0.04 * beat_s if sub == 1 else 0.0
                add_sound(buf, bt + sub * (beat_s / 2.0) + swing, hat_dsp(amp=0.11, rng=rng))
            if in_bar in (0, 2):
                chords = [(261.63, 329.63, 392.00, 493.88), (220.00, 261.63, 329.63, 392.00)]
                for hz in chords[0 if in_bar == 0 else 1]:
                    add_sound(buf, bt, synth_note(hz, beat_s * 1.85, wave_type="pad", amp=0.10))

        elif preset_id == "96bpm-boombap":
            if in_bar == 0:
                add_sound(buf, bt, kick_dsp(0.32, 130, 44, punch=0.80))
                kicks_t.append(round(bt, 4))
            elif in_bar == 2:
                add_sound(buf, bt - beat_s * 0.5, kick_dsp(0.28, 125, 44, punch=0.68))
                add_sound(buf, bt, kick_dsp(0.32, 130, 44, punch=0.80))
                kicks_t.append(round(bt, 4))
            if in_bar in (1, 3):
                add_sound(buf, bt, snare_dsp(0.20, 190, snappy=0.55, amp=0.52, rng=rng))
                snares_t.append(round(bt, 4))
            for sub in range(2):
                add_sound(buf, bt + sub * (beat_s / 2.0), hat_dsp(amp=0.14, rng=rng))
            bass_seq = [73.42, 73.42, 87.31, 65.41]
            add_sound(buf, bt, bass_note(bass_seq[in_bar], beat_s * 0.85, style="sub", amp=0.38))

        elif preset_id == "110bpm-synthwave":
            if in_bar in (0, 2):
                add_sound(buf, bt, kick_dsp(0.34, 140, 42, punch=0.84))
                kicks_t.append(round(bt, 4))
            if in_bar in (1, 3):
                add_sound(buf, bt, snare_dsp(0.32, 180, snappy=0.65, amp=0.56, rng=rng))
                snares_t.append(round(bt, 4))
            for sub in range(2):
                st = bt + sub * (beat_s / 2.0)
                root_hz = 65.41 if (b // 4) % 2 == 0 else 55.0
                add_sound(buf, st, bass_note(root_hz * (2.0 if sub == 1 else 1.0), beat_s * 0.45, style="synthwave", amp=0.36))
                add_sound(buf, st, hat_dsp(amp=0.13, rng=rng))

        elif preset_id == "120bpm-minimal":
            add_sound(buf, bt, kick_dsp(0.22, 135, 48, punch=0.72, drive=1.1))
            kicks_t.append(round(bt, 4))
            for sub in range(4):
                st = bt + sub * (beat_s / 4.0)
                add_sound(buf, st, hat_dsp(dur=0.03, amp=0.15 if sub == 0 else 0.08, rng=rng), pan=(sub - 1.5) * 0.18)
            if in_bar in (0, 2):
                add_sound(buf, bt, synth_note(523.25 if in_bar == 0 else 659.25, beat_s * 0.4, wave_type="pluck", amp=0.15))

        elif preset_id == "140bpm-garage":
            if in_bar == 0:
                add_sound(buf, bt, kick_dsp(0.28, 140, 45, punch=0.80))
                kicks_t.append(round(bt, 4))
            elif in_bar == 2:
                add_sound(buf, bt + beat_s * 0.5, kick_dsp(0.28, 140, 45, punch=0.78))
                kicks_t.append(round(bt + beat_s * 0.5, 4))
            if in_bar in (1, 3):
                add_sound(buf, bt, snare_dsp(0.18, 210, snappy=0.5, amp=0.50, rng=rng))
                snares_t.append(round(bt, 4))
            for sub in (0, 2, 3):
                add_sound(buf, bt + sub * (beat_s / 4.0), hat_dsp(open_hat=(sub == 2), amp=0.15, rng=rng))
            if in_bar in (0, 2):
                add_sound(buf, bt, bass_note(65.41 if in_bar == 0 else 77.78, beat_s * 1.4, style="sub", amp=0.40))

        elif preset_id == "160bpm-dnb":
            if in_bar == 0:
                add_sound(buf, bt, kick_dsp(0.24, 150, 46, punch=0.82))
                kicks_t.append(round(bt, 4))
            elif in_bar == 2:
                add_sound(buf, bt + beat_s * 0.5, kick_dsp(0.24, 150, 46, punch=0.80))
                kicks_t.append(round(bt + beat_s * 0.5, 4))
            if in_bar in (1, 3):
                add_sound(buf, bt, snare_dsp(0.16, 220, snappy=0.6, amp=0.54, rng=rng))
                snares_t.append(round(bt, 4))
            for sub in range(2):
                add_sound(buf, bt + sub * (beat_s / 2.0), hat_dsp(amp=0.16, rng=rng))
            if in_bar == 0:
                add_sound(buf, bt, bass_note(55.0, bar_s * 0.95, style="sub", amp=0.42))
                for hz in (220.0, 261.63, 329.63, 392.0):
                    add_sound(buf, bt, synth_note(hz, bar_s * 0.95, wave_type="pad", amp=0.09))

        elif preset_id == "8bit-chiptune-128":
            if in_bar in (0, 2):
                add_sound(buf, bt, kick_dsp(0.16, 160, 55, punch=0.70))
                kicks_t.append(round(bt, 4))
            if in_bar in (1, 3):
                add_sound(buf, bt, snare_dsp(0.12, 240, snappy=0.85, amp=0.45, rng=rng))
                snares_t.append(round(bt, 4))
            melody = [523.25, 659.25, 783.99, 1046.50, 783.99, 659.25, 587.33, 659.25]
            for sub in range(2):
                st = bt + sub * (beat_s / 2.0)
                note = melody[(b * 2 + sub) % len(melody)]
                add_sound(buf, st, synth_note(note, beat_s * 0.45, wave_type="chip8", amp=0.22), pan=0.2)
                add_sound(buf, st, bass_note(note / 4.0, beat_s * 0.45, style="chip8", amp=0.32), pan=-0.2)

        elif preset_id == "16bit-arcade-130":
            add_sound(buf, bt, kick_dsp(0.24, 150, 48, punch=0.80))
            kicks_t.append(round(bt, 4))
            if in_bar in (1, 3):
                add_sound(buf, bt, snare_dsp(0.18, 200, snappy=0.6, amp=0.52, rng=rng))
                snares_t.append(round(bt, 4))
            fm_riff = [110.0, 110.0, 130.81, 146.83, 164.81, 146.83, 130.81, 98.0]
            for sub in range(2):
                st = bt + sub * (beat_s / 2.0)
                fn = fm_riff[(b * 2 + sub) % len(fm_riff)]
                add_sound(buf, st, bass_note(fn, beat_s * 0.42, style="fm16", amp=0.38))
                add_sound(buf, st, hat_dsp(amp=0.14, rng=rng))

        elif preset_id == "64bit-jungle-150":
            if in_bar == 0:
                add_sound(buf, bt, kick_dsp(0.24, 145, 45, punch=0.80))
                add_sound(buf, bt + beat_s * 0.75, kick_dsp(0.20, 145, 45, punch=0.70))
                kicks_t.append(round(bt, 4))
            if in_bar in (1, 3):
                add_sound(buf, bt, snare_dsp(0.15, 225, snappy=0.65, amp=0.52, rng=rng))
                add_sound(buf, bt + beat_s * 0.5, snare_dsp(0.12, 235, snappy=0.65, amp=0.36, rng=rng))
                snares_t.append(round(bt, 4))
            for sub in range(4):
                add_sound(buf, bt + sub * (beat_s / 4.0), hat_dsp(dur=0.04, amp=0.14, rng=rng))
            if in_bar == 0:
                for hz in (293.66, 349.23, 440.0, 523.25):
                    add_sound(buf, bt, synth_note(hz, bar_s * 0.98, wave_type="pad", amp=0.10))
                add_sound(buf, bt, bass_note(73.42, bar_s * 0.95, style="sub", amp=0.40))

    # Soft limiter so peaks sit cleanly at -1.5 dBFS
    peak = np.max(np.abs(buf))
    if peak > 0:
        buf = np.tanh(buf / peak * 1.15) * 0.84

    grid_info = {
        "preset": preset_id,
        "title_zh": meta["title_zh"],
        "bpm": bpm,
        "beat_period_s": round(beat_s, 5),
        "bar_period_s": round(bar_s, 5),
        "duration_s": round(total_s, 2),
        "beats": beats_t,
        "kicks": kicks_t,
        "snares": snares_t,
    }
    return buf, grid_info


def write_wav_or_ogg(buf: np.ndarray, out_path: Path):
    pcm = (np.clip(buf, -1.0, 1.0) * 32767.0).astype(np.int16)
    if out_path.suffix.lower() == ".wav":
        with wave.open(str(out_path), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(SR)
            wf.writeframes(pcm.tobytes())
    else:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
            tmp_wav = Path(tf.name)
        try:
            with wave.open(str(tmp_wav), "wb") as wf:
                wf.setnchannels(2)
                wf.setsampwidth(2)
                wf.setframerate(SR)
                wf.writeframes(pcm.tobytes())
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(tmp_wav), "-c:a", "vorbis", "-strict", "-2", "-q:a", "5", str(out_path), "-loglevel", "error"],
                check=True,
            )
        finally:
            tmp_wav.unlink(missing_ok=True)


def main():
    ap = argparse.ArgumentParser(description="生成纯代码锁拍 BPM 律动 Loop 与节拍时间轴 JSON")
    ap.add_argument("--preset", choices=list(PRESETS.keys()), default="128bpm-launch", help="预设节拍风格")
    ap.add_argument("--seconds", type=float, default=None, help="指定生成时长（秒），默认生成 2~4 小节标准 Loop")
    ap.add_argument("--out", type=Path, default=None, help="输出音频路径（.wav 或 .ogg）")
    ap.add_argument("--grid-out", type=Path, default=None, help="输出节拍网格 JSON 路径")
    ap.add_argument("--build-all-bundled", type=Path, default=None, help="批量生成全部 12 款内置节拍 Loop 到指定目录")
    args = ap.parse_args()

    if args.build_all_bundled:
        out_dir = args.build_all_bundled
        out_dir.mkdir(parents=True, exist_ok=True)
        summary = []
        for pid in PRESETS:
            buf, info = synthesize_preset(pid)
            ogg_path = out_dir / f"beat-{pid}.ogg"
            write_wav_or_ogg(buf, ogg_path)
            summary.append({"preset": pid, "file": f"beats/beat-{pid}.ogg", **info})
        print(f"Generated {len(summary)} BPM & Bit rhythm loops in {out_dir}")
        return

    buf, info = synthesize_preset(args.preset, args.seconds)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        write_wav_or_ogg(buf, args.out)
    if args.grid_out:
        args.grid_out.parent.mkdir(parents=True, exist_ok=True)
        args.grid_out.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(info, ensure_ascii=False))


if __name__ == "__main__":
    main()
