# Hotel Vlog Maker

Hotel Vlog Maker helps you turn a folder of hotel photos and videos into a short vertical social video for Instagram Reels, TikTok, YouTube Shorts, or Facebook Reels.

The workflow is designed for practical hotel-review content: arrival, lobby, facilities, room tour, bathroom, in-room details, dining, and a closing verdict.

## What this project does

- Analyzes local hotel media folders
- Builds a storyboard for a short-form vertical video
- Renders a 9:16 video with optional captions using ffmpeg
- Supports bilingual captions and top/bottom caption placement

## Repository structure

- [SKILL.md](SKILL.md) – project guidance and workflow instructions
- [agents/openai.yaml](agents/openai.yaml) – agent configuration
- [references/storyboard-format.md](references/storyboard-format.md) – storyboard JSON schema
- [scripts/build_social_hotel_vlog.py](scripts/build_social_hotel_vlog.py) – render script

## Prerequisites

- Python 3
- ffmpeg installed and available in your PATH

### Install ffmpeg

- Windows: `winget install Gyan.FFmpeg`
- macOS: `brew install ffmpeg`

## Quick start

1. Prepare a folder of hotel media files.
2. Create a storyboard JSON file following the format in [references/storyboard-format.md](references/storyboard-format.md).
3. Run the renderer:

```bash
python scripts/build_social_hotel_vlog.py --assets-dir /path/to/media --storyboard storyboard.json --output hotel-vlog.mp4 --caption-position top --fit-to-max
```

### Example

```bash
python scripts/build_social_hotel_vlog.py --assets-dir ./media --storyboard ./storyboard.json --output ./output/hotel-vlog.mp4 --caption-position top --fit-to-max
```

## Storyboard format

The storyboard is a JSON file with `segments`, where each segment contains:

- `duration` – segment length in seconds
- `caption` – optional caption text
- `clips` – list of source clips or clip objects

See [references/storyboard-format.md](references/storyboard-format.md) for full details.

## Notes

- The default output is a vertical 1080x1920 video under 60 seconds.
- The script uses only the Python standard library.
- If ffmpeg is missing, rendering will fail until ffmpeg is installed.

## License

This project is provided as-is for local creative workflow use.
