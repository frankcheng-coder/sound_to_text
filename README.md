# Sound to Text

A macOS desktop application that transcribes iPhone `.m4a` audio files into a plain-text transcript and an `.srt` subtitle file, powered by [faster-whisper](https://github.com/SYSTRAN/faster-whisper) and [PySide6](https://doc.qt.io/qtforpython-6/).

---

## Requirements

| Dependency | Version |
|---|---|
| Python | 3.10 or later |
| ffmpeg | any recent version (must be on `$PATH`) |
| PySide6 | ≥ 6.6.0 |
| faster-whisper | ≥ 1.0.0 |

---

## Installation

### 1 — Install ffmpeg

```bash
brew install ffmpeg
```

Verify it is on your PATH:

```bash
ffmpeg -version
```

### 2 — Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3 — Install Python dependencies

```bash
pip install -r requirements.txt
```

---

## Quick Start

```bash
# 1. Install ffmpeg (if not already installed)
brew install ffmpeg

# 2. Navigate to the project folder
cd /Users/pengcheng/personal_projects/sound_to_text

# 3. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Launch the app
python main.py
```

On first launch, faster-whisper will download the Whisper `base` model (~150 MB) and cache it locally. Subsequent runs only need steps 2, `source .venv/bin/activate`, and `python main.py`.

---

## Usage

1. **Drop** an `.m4a` file onto the drop zone — or **click** the zone to open a file browser.
2. The file path is displayed below the drop zone.
3. Click **Transcribe**.
4. Watch the progress bar and status messages.
5. When complete, two files appear in `audio_output/`:
   - `audio_output/<filename>.txt` — plain transcript
   - `audio_output/<filename>.srt` — subtitles with timestamps

A popup confirms the output paths on success, or shows an error message on failure.

---

## Project Structure

```
sound_to_text/
├── main.py                    # App entry point
├── requirements.txt
├── README.md
├── gui/
│   ├── __init__.py
│   └── main_window.py         # PySide6 window, drop zone, worker thread
├── transcription/
│   ├── __init__.py
│   └── transcriber.py         # faster-whisper transcription logic
└── utils/
    ├── __init__.py
    └── srt_writer.py          # SRT file writer helper
```

---

## Configuration

To use a different Whisper model, edit `DEFAULT_MODEL` in `transcription/transcriber.py`:

| Model | Size | Speed | Accuracy |
|---|---|---|---|
| `tiny` | ~75 MB | fastest | lowest |
| `base` | ~150 MB | fast | good |
| `small` | ~490 MB | medium | better (default) |
| `medium` | ~1.5 GB | slow | high |
| `large-v2` | ~3 GB | slowest | best |

For GPU acceleration (if you have CUDA), set `DEFAULT_DEVICE = "cuda"` and `DEFAULT_COMPUTE = "float16"` in the same file.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `faster_whisper` not found | Run `pip install faster-whisper` inside your venv |
| `ffmpeg` not found error | `brew install ffmpeg` and relaunch terminal |
| Popup: "Only .m4a files accepted" | Convert your file first: `ffmpeg -i input.mp3 output.m4a` |
| Blank transcript | Audio may be silent — check the file plays correctly |
| Model download hangs | Check internet connection; model is cached after first download |
