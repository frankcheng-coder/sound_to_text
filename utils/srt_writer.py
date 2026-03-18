"""
SRT subtitle file writer.

Converts faster-whisper segment objects (or any objects with .start, .end,
.text attributes) into a valid .srt file.
"""

from __future__ import annotations

import os
from typing import Iterable, Protocol, runtime_checkable


@runtime_checkable
class Segment(Protocol):
    """Minimal interface for a transcription segment."""

    start: float
    end: float
    text: str


def _format_timestamp(seconds: float) -> str:
    """Convert float seconds to SRT timestamp format: HH:MM:SS,mmm."""
    assert seconds >= 0, "Timestamp must be non-negative"
    millis = round(seconds * 1000)
    hours, remainder = divmod(millis, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, ms = divmod(remainder, 1_000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def write_srt(segments: Iterable[Segment], output_path: str) -> None:
    """
    Write an SRT subtitle file from an iterable of segments.

    Args:
        segments: Iterable of objects with .start, .end, and .text attributes.
        output_path: Absolute or relative path where the .srt file will be saved.

    Raises:
        OSError: If the file cannot be written.
        ValueError: If no segments are provided.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    entries: list[str] = []
    for index, seg in enumerate(segments, start=1):
        start_ts = _format_timestamp(seg.start)
        end_ts = _format_timestamp(seg.end)
        text = seg.text.strip()
        entries.append(f"{index}\n{start_ts} --> {end_ts}\n{text}\n")

    if not entries:
        raise ValueError("No segments found — cannot write an empty SRT file.")

    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(entries))
