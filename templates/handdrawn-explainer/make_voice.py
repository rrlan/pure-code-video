import asyncio, json, subprocess, hashlib
from pathlib import Path
import edge_tts

lines = [
  {
    "id": "s1",
    "text": "切叶蚁每天高举比体重重十倍的树叶，却从来不吃一口。",
    "en": "Leafcutter ants carry leaves 10× their weight, yet never eat a single bite."
  },
  {
    "id": "s2",
    "text": "它们真正想要的，是用碎叶在地底培育一片白色的共生真菌。",
    "en": "Instead, they mulch the leaves underground to cultivate a white symbiotic fungus."
  },
  {
    "id": "s3",
    "text": "真菌分解树叶的纤维素，长出富含营养的菌丝球，哺育整座蚁群。",
    "en": "The fungus breaks down cellulose into nutrient-rich tips that feed the whole colony."
  },
  {
    "id": "s4",
    "text": "早在人类学会耕种的五千万年前，它们就已经演化出地下农业。",
    "en": "50 million years before human farming, they had already evolved underground agriculture."
  }
]

out_dir = Path("work/handdrawn_audio")
out_dir.mkdir(parents=True, exist_ok=True)

def probe_dur(p):
  return float(subprocess.check_output([
    "ffprobe", "-v", "error", "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1", str(p)
  ], text=True).strip())

def detect_speech_end(p, total):
  log = subprocess.run(
    ["ffmpeg", "-hide_banner", "-i", str(p), "-af", "silencedetect=n=-45dB:d=0.15", "-f", "null", "-"],
    capture_output=True, text=True
  ).stderr
  starts = [float(l.split("silence_start:")[1]) for l in log.splitlines() if "silence_start:" in l]
  tail = [x for x in starts if x > 0.3]
  end = tail[-1] if tail and tail[-1] > total - 1.2 else total
  return min(total, end + 0.08)

async def main():
  timeline = []
  cursor = 0.50 # 0.50s lead-in for sketch -> ink -> color build-up
  gap = 0.32
  all_words = []
  word_counter = 1

  for item in lines:
    lid = item["id"]
    mp3_path = out_dir / f"{lid}.mp3"
    comm = edge_tts.Communicate(item["text"], voice="zh-CN-YunxiNeural", rate="+12%", boundary="WordBoundary")
    boundaries = []
    with open(mp3_path, "wb") as f:
      async for chunk in comm.stream():
        if chunk["type"] == "audio":
          f.write(chunk["data"])
        elif chunk["type"] == "WordBoundary":
          boundaries.append(chunk)

    full_dur = probe_dur(mp3_path)
    end_t = detect_speech_end(mp3_path, full_dur)
    # Ensure end_t covers the last WordBoundary
    if boundaries:
      last_wb_end = (boundaries[-1]["offset"] + boundaries[-1]["duration"]) / 1e7 + 0.06
      end_t = min(full_dur, max(end_t, last_wb_end))

    wav_path = out_dir / f"{lid}.wav"
    subprocess.run([
      "ffmpeg", "-v", "error", "-y", "-i", str(mp3_path),
      "-to", f"{end_t:.3f}", "-ar", "48000", "-ac", "1", str(wav_path)
    ], check=True)
    speech_dur = round(probe_dur(wav_path), 3)

    line_words = []
    for idx, b in enumerate(boundaries):
      ws_local = round(b["offset"] / 1e7, 3)
      we_local = round(min(speech_dur, ws_local + max(0.05, b["duration"] / 1e7)), 3)
      if idx > 0 and ws_local < line_words[-1]["local_end"]:
        line_words[-1]["local_end"] = ws_local
        line_words[-1]["end"] = round(cursor + ws_local, 3)
      if we_local <= ws_local:
        we_local = round(min(speech_dur, ws_local + 0.05), 3)
      wobj = {
        "id": f"w{word_counter:03d}",
        "text": b["text"],
        "local_start": ws_local,
        "local_end": we_local,
        "start": round(cursor + ws_local, 3),
        "end": round(cursor + we_local, 3)
      }
      word_counter += 1
      line_words.append(wobj)
      all_words.append(wobj)

    timeline.append({
      "id": lid,
      "zh": item["text"],
      "en": item["en"],
      "wav": str(wav_path),
      "start": round(cursor, 3),
      "end": round(cursor + speech_dur, 3),
      "duration": speech_dur,
      "words": line_words
    })
    cursor = round(cursor + speech_dur + gap, 3)

  total_dur = round(cursor + 0.70, 2) # ~18.5s total

  # Build single master voice WAV of exact length total_dur with each line placed at its exact start
  filter_parts = [f"aevalsrc=0:d={total_dur}:s=48000:c=mono[base]"]
  mix_inputs = ["[base]"]
  cmd = ["ffmpeg", "-v", "error", "-y"]
  for idx, l in enumerate(timeline):
    cmd += ["-i", l["wav"]]
    delay_ms = int(round(l["start"] * 1000))
    filter_parts.append(f"[{idx}:a]adelay={delay_ms}|{delay_ms}[v{idx}]")
    mix_inputs.append(f"[v{idx}]")
  filter_parts.append(f"{''.join(mix_inputs)}amix=inputs={len(mix_inputs)}:normalize=0,alimiter=limit=0.95[out]")
  master_wav = out_dir / "voice_master.wav"
  cmd += ["-filter_complex", ";".join(filter_parts), "-map", "[out]", "-ar", "48000", "-ac", "1", str(master_wav)]
  subprocess.run(cmd, check=True)

  voice_sha256 = hashlib.sha256(master_wav.read_bytes()).hexdigest()

  # Write verifier-compatible transcript.json for voice_master.wav
  transcript = {
    "segments": [
      {
        "id": l["id"],
        "start": l["start"],
        "end": l["end"],
        "text": l["zh"],
        "words": [{"id": w["id"], "text": w["text"], "start": w["start"], "end": w["end"]} for w in l["words"]]
      }
      for l in timeline
    ]
  }
  (out_dir / "transcript.json").write_text(json.dumps(transcript, ensure_ascii=False, indent=2))

  meta = {
    "total_duration": total_dur,
    "voice_master": str(master_wav),
    "voice_sha256": voice_sha256,
    "lines": timeline,
    "words": all_words
  }
  (out_dir / "timeline.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
  print("Master voice duration:", total_dur, "s | SHA256:", voice_sha256[:16])
  for l in timeline:
    print(l["id"], f"{l['start']}s -> {l['end']}s ({l['duration']}s)", [(w["id"], w["text"], w["start"], w["end"]) for w in l["words"]])

asyncio.run(main())
