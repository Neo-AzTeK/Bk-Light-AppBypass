import argparse
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def build_scroll_frames(text: str, width: int = 64, height: int = 16, step: int = 2) -> list[Image.Image]:
    font = ImageFont.load_default()
    dummy = Image.new("1", (1, 1), 0)
    d = ImageDraw.Draw(dummy)
    bbox = d.textbbox((0, 0), text, font=font)
    tw = max(1, bbox[2] - bbox[0])
    th = max(1, bbox[3] - bbox[1])

    strip_w = tw + width
    strip = Image.new("1", (strip_w, height), 0)
    sd = ImageDraw.Draw(strip)
    y = max(0, (height - th) // 2)
    sd.text((width, y), text, fill=1, font=font)

    frames: list[Image.Image] = []
    for x in range(0, strip_w, max(1, step)):
        frame = Image.new("P", (width, height), 0)
        crop = strip.crop((x, 0, x + width, height)).convert("P")
        # Palette index 0=black, 1=white
        frame.putpalette([0, 0, 0, 255, 255, 255] + [0, 0, 0] * 254)
        frame.paste(crop, (0, 0))
        frames.append(frame)
    if not frames:
        frames.append(Image.new("P", (width, height), 0))
    return frames


def save_gif(frames: list[Image.Image], out: Path, duration_ms: int = 80) -> bytes:
    out.parent.mkdir(parents=True, exist_ok=True)
    buf = BytesIO()
    frames[0].save(
        buf,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        optimize=True,
        duration=duration_ms,
        loop=0,
        disposal=2,
        transparency=0,
    )
    data = buf.getvalue()
    out.write_bytes(data)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a compact 64x16 scrolling GIF from text")
    parser.add_argument("text")
    parser.add_argument("--out", type=Path, default=Path("tmp/custom_scroll.gif"))
    parser.add_argument("--step", type=int, default=2)
    parser.add_argument("--duration", type=int, default=80)
    args = parser.parse_args()

    frames = build_scroll_frames(args.text, step=args.step)
    data = save_gif(frames, args.out, duration_ms=args.duration)
    print(f"GIF saved: {args.out} ({len(data)} bytes, {len(frames)} frames)")


if __name__ == "__main__":
    main()
