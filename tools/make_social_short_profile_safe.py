from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUT = ASSETS / "social-short-003-frames"
OUT.mkdir(parents=True, exist_ok=True)

for old in OUT.glob("frame_*.png"):
    old.unlink()

FONT = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
if not Path(FONT).exists():
    FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"

W, H = 720, 1280
FPS = 30
TOTAL = 300


def font(size):
    return ImageFont.truetype(FONT, size)


def rounded(draw, xy, r, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def centered(draw, text, y, size, fill, gap=8):
    f = font(size)
    for line in text.split("\n"):
        bbox = draw.textbbox((0, 0), line, font=f)
        draw.text(((W - (bbox[2] - bbox[0])) / 2, y), line, font=f, fill=fill)
        y += size + gap
    return y


def base():
    img = Image.new("RGBA", (W, H), (18, 105, 80, 255))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, 0, W, H), fill=(18, 105, 80, 255))
    d.ellipse((-130, 760, 280, 1170), fill=(217, 164, 65, 75))
    d.ellipse((500, -140, 890, 250), fill=(255, 255, 255, 34))
    d.ellipse((500, 920, 830, 1250), fill=(255, 255, 255, 24))
    return img


scenes = [
    ("遺品整理\nまずは写真で相談", "大阪・兵庫・奈良・京都対応"),
    ("仕分け・供養・買取", "まとめてプロにお任せ"),
    ("買取できる品は", "作業費から差し引き"),
    ("LINEで無料見積もり", "心まごころ遺品整理"),
]

for i in range(TOTAL):
    sec = i / FPS
    idx = min(3, int(sec / 2.5))
    local = (sec - idx * 2.5) / 2.5
    e = 0.5 - math.cos(math.pi * min(1, max(0, local))) / 2
    title, sub = scenes[idx]

    frame = base()
    d = ImageDraw.Draw(frame, "RGBA")

    # This whole card fits in the first 720px height, so Instagram profile crops stay readable.
    y0 = 96 + int(8 * math.sin(e * math.pi))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow, "RGBA")
    rounded(sd, (42, y0 + 14, W - 42, y0 + 594), 34, fill=(0, 0, 0, 50))
    frame.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(16)))

    rounded(d, (38, y0, W - 38, y0 + 580), 34, fill=(255, 253, 250, 255))
    rounded(d, (78, y0 + 36, 222, y0 + 82), 23, fill=(201, 79, 69))
    d.text((150, y0 + 44), "無料相談", font=font(22), fill="white", anchor="ma")

    centered(d, title, y0 + 150, 54 if idx != 1 else 50, (15, 53, 44), 12)
    centered(d, sub, y0 + 315, 30, (56, 89, 79), 8)

    rounded(d, (76, y0 + 444, W - 76, y0 + 510), 33, fill=(21, 102, 78))
    d.text((W // 2, y0 + 464), "写真だけでも概算OK", font=font(30), fill="white", anchor="ma")

    d.text((W // 2, 825), "心まごころ遺品整理", font=font(38), fill="white", anchor="ma")
    d.text((W // 2, 885), "大阪・兵庫・奈良・京都", font=font(34), fill="white", anchor="ma")
    d.text((W // 2, 1045), "LINEで無料相談", font=font(54), fill="white", anchor="ma")

    # No fade on the first scene: the cover must be crisp.
    fade_in = local / 0.14 if idx > 0 else 1
    fade = min(1, fade_in, (1 - local) / 0.14 if local > 0.86 else 1)
    if fade < 1:
        frame.alpha_composite(Image.new("RGBA", (W, H), (18, 105, 80, int((1 - fade) * 150))))

    frame.convert("RGB").save(OUT / f"frame_{i:04d}.png", quality=92)

Image.open(OUT / "frame_0000.png").save(ASSETS / "social-short-003-cover.png", quality=95)
print(OUT)
