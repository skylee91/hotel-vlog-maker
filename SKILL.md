---
name: hotel-vlog-maker
description: Create short vertical social hotel vlogs and practical-review reels from local hotel media folders. Use when the user asks to analyze hotel, resort, room-tour, staycation, travel, or dining photos/videos; generate a storyboard; or render an Instagram Reel, TikTok, YouTube Short, or Facebook Reel under 60 seconds. Supports video-only edits, top or bottom bilingual captions, and Windows/macOS ffmpeg workflows.
---

# Hotel Vlog Maker

## Workflow

1. Inventory the folder before planning. List media with `rg --files` where available, otherwise use native shell listing. Separate videos from photos, capture durations/dimensions when possible, and create contact sheets or thumbnails when visual analysis is needed.
2. Lock user constraints. Default social output is `1080x1920`, `9:16`, under `60s`. Honor explicit choices such as video-only, no photos, caption position, caption language, tone, music/no music, and platform.
3. Build a practical hotel-review arc from the actual assets: arrival/signage -> lobby first impression -> facilities -> room/suite -> bathroom -> in-room details -> breakfast/dining -> closing verdict. Reorder only when the user asks.
4. Keep pacing brisk for short clips. Use about `0.5-1.5s` for detail shots and `2-4s` for anchor shots. Avoid long holds unless the source clip has smooth motion or the user wants a cinematic edit.
5. Write a decision-complete storyboard with time ranges, clip filenames, and captions. If rendering, convert the storyboard into the JSON format in `references/storyboard-format.md` and run `scripts/build_social_hotel_vlog.py`.

## Asset Rules

- Never use still photos when the user says video-only. Exclude `.jpg`, `.jpeg`, `.png`, `.heic`, and other still-image files in that mode.
- Do not claim amenities, service quality, pricing, room category, or location advantages unless visible in the assets or provided by the user.
- Prefer real footage over stock, generated visuals, or generic overlays.
- If a clip is shorter than its assigned slot, hold the last frame only briefly; choose more clips before relying on long freeze frames.

## Caption Rules

- Default to top captions for the workflow created from this St. Regis Beijing project unless the user asks otherwise.
- Keep captions concise and platform-safe. Use a top safe margin around `140-180px` for vertical `1080x1920` exports.
- For bilingual captions, use one short English line and one short Chinese line. Avoid long sentences.
- Use a subtle dark translucent backing, outline, or shadow so captions remain readable over bright lobby, bathroom, and breakfast shots.

## Rendering

Use the bundled script when ffmpeg is available:

```bash
python scripts/build_social_hotel_vlog.py --assets-dir /path/to/media --storyboard storyboard.json --output hotel-vlog.mp4 --caption-position top --fit-to-max
```

On Windows, quote paths and use `python` or the Codex bundled Python. On macOS, use `python3` if `python` is not Python 3. The script uses only the Python standard library and requires `ffmpeg` in `PATH`.

If ffmpeg is missing, tell the user rendering needs ffmpeg. Common installs are `winget install Gyan.FFmpeg` on Windows and `brew install ffmpeg` on macOS; do not install without user approval.