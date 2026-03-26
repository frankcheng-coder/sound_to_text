"""
Transcription logic using faster-whisper.

Emits progress via a callback so the GUI can stay responsive.
All heavy work runs in a background thread — never call this from the GUI thread.
"""

from __future__ import annotations

import multiprocessing
import os
import threading
from datetime import datetime
from typing import Callable

from faster_whisper import WhisperModel

from utils.srt_writer import write_srt

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------
ProgressCallback = Callable[[int, str], None]
"""Signature: (percent: int, message: str) -> None"""

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
OUTPUT_DIR = "audio_output"
DEFAULT_MODEL = "small"         # tiny | base | small | medium | large-v2
DEFAULT_DEVICE = "cpu"          # cpu | cuda
DEFAULT_COMPUTE = "int8"        # int8 | float16 | float32


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class TranscriptionCancelledError(Exception):
    """Raised when the user cancels transcription."""


def transcribe(
    audio_path: str,
    *,
    model_size: str = DEFAULT_MODEL,
    device: str = DEFAULT_DEVICE,
    compute_type: str = DEFAULT_COMPUTE,
    language: str | None = None,
    progress_callback: ProgressCallback | None = None,
    cancel_event: threading.Event | None = None,
) -> tuple[str, str]:
    """
    Transcribe *audio_path* and save a .txt and a .srt file.

    Args:
        audio_path: Path to the .m4a (or any ffmpeg-supported) audio file.
        model_size: Whisper model variant to load.
        device: Inference device — 'cpu' or 'cuda'.
        compute_type: Quantisation — 'int8', 'float16', or 'float32'.
        language: ISO-639-1 language code, or None for auto-detection.
        progress_callback: Optional callable(percent, message) for status updates.

    Returns:
        Tuple of (txt_path, srt_path) for the saved output files.

    Raises:
        FileNotFoundError: If *audio_path* does not exist.
        ValueError: If transcription produces no segments.
        RuntimeError: Wraps any unexpected error during transcription.
    """
    def _emit(percent: int, message: str) -> None:
        if progress_callback:
            progress_callback(percent, message)

    def _check_cancelled() -> None:
        if cancel_event is not None and cancel_event.is_set():
            raise TranscriptionCancelledError("Transcription cancelled by user.")

    # ------------------------------------------------------------------
    # 1. Validate input
    # ------------------------------------------------------------------
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    txt_path = os.path.join(OUTPUT_DIR, f"{base_name}_{timestamp}.txt")
    srt_path = os.path.join(OUTPUT_DIR, f"{base_name}_{timestamp}.srt")

    _emit(5, "Loading Whisper model…")
    _check_cancelled()

    # ------------------------------------------------------------------
    # 2. Load model
    # ------------------------------------------------------------------
    try:
        model = WhisperModel(model_size, device=device, compute_type=compute_type)
    except Exception as exc:
        raise RuntimeError(f"Failed to load Whisper model '{model_size}': {exc}") from exc

    _check_cancelled()
    _emit(20, "Model loaded. Starting transcription…")

    # ------------------------------------------------------------------
    # 3. Transcribe
    # ------------------------------------------------------------------
    try:
        segments_gen, info = model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            vad_filter=True,
        )
    except Exception as exc:
        raise RuntimeError(f"Transcription failed: {exc}") from exc

    _emit(30, f"Detected language: {info.language} "
              f"(confidence {info.language_probability:.0%}). Processing…")

    # Materialise the generator so we can reuse segments for both outputs.
    # faster-whisper returns a lazy generator — exhaust it once.
    # We iterate one segment at a time so we can check for cancellation.
    segments = []
    try:
        for seg in segments_gen:
            _check_cancelled()
            segments.append(seg)
    except TranscriptionCancelledError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Error while reading transcription segments: {exc}") from exc

    if not segments:
        raise ValueError("Transcription produced no segments. The audio may be silent or too short.")

    _emit(70, "Transcription complete. Writing output files…")

    # ------------------------------------------------------------------
    # 4. Write .txt
    # ------------------------------------------------------------------
    try:
        with open(txt_path, "w", encoding="utf-8") as fh:
            for seg in segments:
                fh.write(seg.text.strip() + "\n")
    except OSError as exc:
        raise RuntimeError(f"Could not write transcript file: {exc}") from exc

    _emit(85, "Transcript saved. Writing SRT…")

    # ------------------------------------------------------------------
    # 5. Write .srt
    # ------------------------------------------------------------------
    try:
        write_srt(segments, srt_path)
    except Exception as exc:
        raise RuntimeError(f"Could not write SRT file: {exc}") from exc

    _emit(100, f"Done! Files saved to '{OUTPUT_DIR}/'")

    return txt_path, srt_path


# ---------------------------------------------------------------------------
# Subprocess entry point  (used by the GUI for killable transcription)
# ---------------------------------------------------------------------------

def _transcribe_in_subprocess(
    queue: multiprocessing.Queue,
    audio_path: str,
    language: str | None,
) -> None:
    """Run transcription and post progress/results to *queue*.

    Messages sent to the queue:
        ("progress", percent, message)
        ("finished", txt_path, srt_path)
        ("error", error_string)
    """
    try:
        txt_path, srt_path = transcribe(
            audio_path,
            language=language,
            progress_callback=lambda pct, msg: queue.put(("progress", pct, msg)),
        )
        queue.put(("finished", txt_path, srt_path))
    except Exception as exc:
        import traceback
        queue.put(("error", f"{type(exc).__name__}: {exc}\n\n{traceback.format_exc()}"))
