#!/usr/bin/env python3
"""Build a vertical social hotel vlog from a JSON storyboard using ffmpeg.

The script is intentionally dependency-light: Python standard library plus ffmpeg
in PATH. It works on Windows and macOS when paths are quoted normally.
"""

from __future__ import annotations

import argparse
import json
import platform
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ClipSlot:
    file: Path
    start: float
    duration: float


@dataclass
class CaptionEvent:
    start: float
    end: float
    text: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a vertical social hotel vlog from a storyboard JSON file.")
    parser.add_argument("--assets-dir", required=True, help="Folder containing source media files.")
    parser.add_argument("--storyboard", required=True, help="Storyboard JSON path.")
    parser.add_argument("--output", required=True, help="Output MP4 path.")
    parser.add_argument("--caption-position", choices=["top", "bottom"], default="top")
    parser.add_argument("--max-duration", type=float, default=60.0, help="Maximum allowed total duration in seconds.")
    parser.add_argument("--fit-to-max", action="store_true", help="Scale all durations down if the plan exceeds max duration.")
    parser.add_argument("--font", default=None, help="ASS subtitle font name. Defaults to Microsoft YaHei on Windows and PingFang SC on macOS.")
    parser.add_argument("--dry-run", action="store_true", help="Print the ffmpeg command without running it.")
    return parser.parse_args()


def load_storyboard(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if isinstance(data, list):
        data = {"segments": data}
    if not data.get("segments"):
        raise ValueError("Storyboard JSON must contain a non-empty 'segments' array.")
    return data


def normalize_timeline(data: dict, assets_dir: Path, max_duration: float, fit_to_max: bool) -> tuple[list[ClipSlot], list[CaptionEvent], float]:
    clips: list[ClipSlot] = []
    captions: list[CaptionEvent] = []
    cursor = 0.0

    for index, segment in enumerate(data["segments"]):
        seg_duration = float(segment.get("duration", 0))
        raw_clips = segment.get("clips") or segment.get("assets") or []
        if seg_duration <= 0:
            raise ValueError(f"Segment {index + 1} has no positive duration.")
        if not raw_clips:
            raise ValueError(f"Segment {index + 1} has no clips.")

        default_duration = seg_duration / len(raw_clips)
        segment_start = cursor
        for item in raw_clips:
            if isinstance(item, str):
                filename = item
                clip_start = 0.0
                clip_duration = default_duration
            else:
                filename = item.get("file") or item.get("name")
                clip_start = float(item.get("start", 0.0))
                clip_duration = float(item.get("duration", default_duration))
            if not filename:
                raise ValueError(f"Segment {index + 1} has a clip without a file name.")
            source = assets_dir / filename
            if not source.exists():
                raise FileNotFoundError(f"Missing source clip: {source}")
            clips.append(ClipSlot(source, clip_start, clip_duration))
            cursor += clip_duration

        caption = str(segment.get("caption") or segment.get("top_caption") or "").strip()
        if caption:
            captions.append(CaptionEvent(segment_start, cursor, caption))

    total = cursor
    if total > max_duration:
        if not fit_to_max:
            raise ValueError(f"Planned duration {total:.2f}s exceeds max {max_duration:.2f}s. Use --fit-to-max or shorten the plan.")
        scale = max_duration / total
        clips = [ClipSlot(slot.file, slot.start, slot.duration * scale) for slot in clips]
        captions = [CaptionEvent(event.start * scale, event.end * scale, event.text) for event in captions]
        total = max_duration

    return clips, captions, total


def ass_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours}:{minutes:02d}:{secs:05.2f}"


def ass_text(text: str) -> str:
    cleaned = text.replace("{", "\\{").replace("}", "\\}").strip()
    if "\n" not in cleaned and " / " in cleaned:
        cleaned = cleaned.replace(" / ", "\\N", 1)
    return cleaned.replace("\n", "\\N")


def default_font() -> str:
    system = platform.system().lower()
    if "darwin" in system:
        return "PingFang SC"
    if "windows" in system:
        return "Microsoft YaHei"
    return "Noto Sans CJK SC"


def write_ass(path: Path, captions: list[CaptionEvent], width: int, height: int, position: str, font: str) -> None:
    alignment = 8 if position == "top" else 2
    margin_v = 160 if position == "top" else 180
    font_size = 54 if height >= 1800 else 42
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {width}",
        f"PlayResY: {height}",
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: TopCaption,{font},{font_size},&H00FFFFFF,&H000000FF,&HCC000000,&H99000000,1,0,0,0,100,100,0,0,3,3,1,{alignment},72,72,{margin_v},1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for event in captions:
        lines.append(f"Dialogue: 0,{ass_time(event.start)},{ass_time(event.end)},TopCaption,,0,0,0,,{ass_text(event.text)}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def ffmpeg_filter_path(path: Path) -> str:
    value = path.resolve().as_posix()
    if len(value) >= 2 and value[1] == ":":
        value = value[0] + r"\:" + value[2:]
    return value.replace("'", r"\'")


def build_command(ffmpeg: str, clips: list[ClipSlot], ass_path: Path | None, output: Path, width: int, height: int, fps: int, total: float) -> list[str]:
    command = [ffmpeg, "-hide_banner", "-y"]
    for slot in clips:
        command.extend(["-i", str(slot.file)])
    silent_input_index = len(clips)
    command.extend(["-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"])

    parts: list[str] = []
    for index, slot in enumerate(clips):
        d = max(0.05, slot.duration)
        start = max(0.0, slot.start)
        parts.append(
            f"[{index}:v]trim=start={start:.3f},setpts=PTS-STARTPTS,"
            f"tpad=stop_mode=clone:stop_duration={d:.3f},trim=duration={d:.3f},"
            f"scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},fps={fps},setsar=1[v{index}]"
        )
    parts.append("".join(f"[v{index}]" for index in range(len(clips))) + f"concat=n={len(clips)}:v=1:a=0,format=yuv420p[vcat]")
    if ass_path is not None:
        parts.append(f"[vcat]subtitles=filename='{ffmpeg_filter_path(ass_path)}'[vout]")
        video_label = "[vout]"
    else:
        video_label = "[vcat]"

    command.extend([
        "-filter_complex", ";".join(parts),
        "-map", video_label,
        "-map", f"{silent_input_index}:a",
        "-t", f"{total:.3f}",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        str(output),
    ])
    return command


def main() -> int:
    args = parse_args()
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        if args.dry_run:
            ffmpeg = "ffmpeg"
        else:
            print("ffmpeg was not found in PATH.", file=sys.stderr)
            print("Install ffmpeg first: Windows: winget install Gyan.FFmpeg | macOS: brew install ffmpeg", file=sys.stderr)
            return 2

    assets_dir = Path(args.assets_dir).expanduser().resolve()
    storyboard_path = Path(args.storyboard).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    data = load_storyboard(storyboard_path)
    width = int(data.get("width", 1080))
    height = int(data.get("height", 1920))
    fps = int(data.get("fps", 30))
    clips, captions, total = normalize_timeline(data, assets_dir, args.max_duration, args.fit_to_max)

    ass_path = None
    if captions:
        ass_path = output.with_suffix(".captions.ass")
        write_ass(ass_path, captions, width, height, args.caption_position, args.font or default_font())

    command = build_command(ffmpeg, clips, ass_path, output, width, height, fps, total)
    printable = " ".join(shlex.quote(part) for part in command)
    if args.dry_run:
        print(printable)
        return 0

    print(f"Rendering {len(clips)} clips to {output} ({total:.2f}s)...")
    completed = subprocess.run(command)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())