# Storyboard JSON Format

Use this format with `scripts/build_social_hotel_vlog.py` after the visual storyboard is approved.

```json
{
  "width": 1080,
  "height": 1920,
  "fps": 30,
  "segments": [
    {
      "duration": 3,
      "caption": "St. Regis Beijing in 56 sec / 北京瑞吉酒店56秒体验",
      "clips": ["IMG_3416.MOV"]
    },
    {
      "duration": 4,
      "caption": "Grand lobby arrival / 大堂气派",
      "clips": ["IMG_3417.MOV", "IMG_3419.MOV"]
    }
  ]
}
```

## Fields

- `width`, `height`, `fps`: Optional output settings. Defaults are `1080`, `1920`, and `30`.
- `segments`: Required array in final edit order.
- `segments[].duration`: Required segment duration in seconds.
- `segments[].caption`: Optional caption displayed for the whole segment. Use `English / Chinese` for bilingual captions; the render script splits the slash into two lines.
- `segments[].clips`: Required list. Each item can be a filename string or an object:

```json
{ "file": "IMG_3460.MOV", "start": 1.2, "duration": 2.5 }
```

If clip-level duration is omitted, the script evenly divides the segment duration across its clips.

## Recommended Hotel Review Arc

1. Arrival hook
2. Lobby first impression
3. Facilities check
4. Room or suite tour
5. Bedroom
6. Bathroom and amenities
7. In-room extras
8. Breakfast or dining
9. Closing verdict