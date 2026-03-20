<div align="center">

# 🎙️ Sound to Text

**Turn your iPhone voice memos into text — instantly!**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-macOS-000000?style=for-the-badge&logo=apple&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![AI Powered](https://img.shields.io/badge/AI-Whisper-blueviolet?style=for-the-badge&logo=openai&logoColor=white)

*Drop an `.m4a` file. Hit a button. Get a transcript + subtitles. That's literally it.* 🚀

</div>

---

## ✨ What Does It Do?

Got a voice memo on your iPhone? This app uses **OpenAI's Whisper AI** under the hood to turn your audio into:

- 📄 **A plain text transcript** — copy-paste anywhere
- 🎬 **An `.srt` subtitle file** — drop it into any video editor

Built with [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) for blazing speed and [`PySide6`](https://doc.qt.io/qtforpython-6/) for the slick GUI.

---

## 🛠️ What You'll Need

| 📦 Dependency | 🔢 Version |
|:---|:---|
| 🐍 Python | 3.10 or later |
| 🎞️ ffmpeg | any recent version (must be on `$PATH`) |
| 🖥️ PySide6 | ≥ 6.6.0 |
| 🤖 faster-whisper | ≥ 1.0.0 |

---

## ⚡ Quick Start

Get up and running in under 2 minutes:

```bash
# Step 1 — Install ffmpeg (the audio magic)
brew install ffmpeg

# Step 2 — Jump into the project folder
cd sound_to_text

# Step 3 — Set up your Python environment
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Step 4 — Launch the app! 🎉
./run.sh
```

> **First launch heads-up:** Whisper will download the AI model (~150 MB) on first run and cache it forever. After that, it's instant!

---

## 🎮 How to Use It

It's stupidly simple:

1. 🖱️ **Drag & drop** your `.m4a` file onto the drop zone — or click to browse
2. 👀 Your file path shows up below the zone
3. 🔴 Hit **Transcribe**
4. 📊 Watch the progress bar do its thing
5. 🎉 Find your files in `audio_output/`:

```
audio_output/
├── yourfile.txt   ← plain transcript
└── yourfile.srt   ← subtitles with timestamps
```

A popup will tell you where your files landed — or what went wrong if something breaks.

---

## 🧠 Choose Your AI Model

Want more accuracy? Need it faster? You can swap models by editing `DEFAULT_MODEL` in `transcription/transcriber.py`:

| Model | Size | Speed | Accuracy | Best For |
|:---:|:---:|:---:|:---:|:---|
| `tiny` | ~75 MB | ⚡⚡⚡⚡ | ⭐ | Quick drafts |
| `base` | ~150 MB | ⚡⚡⚡ | ⭐⭐ | Everyday use |
| `small` | ~490 MB | ⚡⚡ | ⭐⭐⭐ | **Default — great balance** |
| `medium` | ~1.5 GB | ⚡ | ⭐⭐⭐⭐ | Important recordings |
| `large-v2` | ~3 GB | 🐢 | ⭐⭐⭐⭐⭐ | Maximum accuracy |

> **Got a GPU?** Set `DEFAULT_DEVICE = "cuda"` and `DEFAULT_COMPUTE = "float16"` for turbo speed! 🏎️

---

## 📁 Project Structure

```
sound_to_text/
├── 🚀 main.py                  # App entry point
├── 🏃 run.sh                   # One-command launcher
├── 📋 requirements.txt
├── 📖 README.md
├── 🖥️ gui/
│   ├── __init__.py
│   └── main_window.py          # PySide6 window, drop zone, worker thread
├── 🤖 transcription/
│   ├── __init__.py
│   └── transcriber.py          # faster-whisper transcription logic
└── 🔧 utils/
    ├── __init__.py
    └── srt_writer.py           # SRT file writer helper
```

---

## 🆘 Something Broke?

Don't panic. Here's the fix:

| 😬 Problem | 💡 Fix |
|:---|:---|
| `faster_whisper` not found | Run `pip install faster-whisper` inside your venv |
| `ffmpeg` not found | `brew install ffmpeg` then restart your terminal |
| "Only .m4a files accepted" | Convert first: `ffmpeg -i input.mp3 output.m4a` |
| Blank transcript | Your audio might be silent — check it plays correctly |
| Model download frozen | Check your internet — it caches after the first download |

---

<div align="center">

Made with ❤️ and a lot of ☕ · Powered by [faster-whisper](https://github.com/SYSTRAN/faster-whisper) + [PySide6](https://doc.qt.io/qtforpython-6/)

</div>
