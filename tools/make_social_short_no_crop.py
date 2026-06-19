from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUT = ASSETS / "social-short-005-frames"
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


def center(draw, text, y, size, fill, gap=12):
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
    d.ellipse((-120, 930, 210, 1260), fill=(217, 164, 65, 80))
    d.ellipse((545, -95, 850, 210), fill=(255, 255, 255, 35))
    d.ellipse((540, 870, 850, 1180), fill=(255, 255, 255, 18))
    return img


scenes = [
    ("遺品整理", "写真相談OK", "関西対応"),
    ("仕分け", "供養・買取", "まとめて対応"),
    ("買取品は", "費用から差引", "見積無料"),
    ("LINEで", "無料相談", "心まごころ"),
]

for i in range(TOTAL):
    sec = i / FPS
    idx = min(3, int(sec / 2.5))
    local = (sec - idx * 2.5) / 2.5
    e = 0.5 - math.cos(math.pi * min(1, max(0, local))) / 2
    a, b, c = scenes[idx]

    frame = base()
    d = ImageDraw.Draw(frame, "RGBA")

    # All readable content stays in the central Instagram-safe area.
    y0 = 230 + int(8 * math.sin(e * math.pi))
    card = (126, y0, W - 126, y0 + 585)

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow, "RGBA")
    rounded(sd, (card[0] + 8, card[1] + 12, card[2] + 8, card[3] + 12), 32, fill=(0, 0, 0, 48))
    frame.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(14)))

    rounded(d, card, 32, fill=(255, 253, 250, 255))
    rounded(d, (172, y0 + 38, 292, y0 + 84), 23, fill=(201, 79, 69))
    d.text((232, y0 + 47), "無料相談", font=font(20), fill="white", anchor="ma")

    center(d, a, y0 + 135, 54, (15, 53, 44))
    center(d, b, y0 + 235, 56, (15, 53, 44))
    center(d, c, y0 + 354, 32, (56, 89, 79))

    rounded(d, (170, y0 + 466, W - 170, y0 + 526), 30, fill=(21, 102, 78))
    d.text((W // 2, y0 + 483), "まずは写真でOK", font=font(25), fill="white", anchor="ma")

    d.text((W // 2, 905), "心まごころ遺品整理", font=font(30), fill="white", anchor="ma")
    d.text((W // 2, 962), "大阪・兵庫・奈良・京都", font=font(28), fill="white", anchor="ma")

    fade_in = local / 0.14 if idx > 0 else 1
    fade = min(1, fade_in, (1 - local) / 0.14 if local > 0.86 else 1)
    if fade < 1:
        frame.alpha_composite(Image.new("RGBA", (W, H), (18, 105, 80, int((1 - fade) * 145))))

    frame.convert("RGB").save(OUT / f"frame_{i:04d}.png", quality=92)

Image.open(OUT / "frame_0000.png").save(ASSETS / "social-short-005-cover.png", quality=95)
Image.open(OUT / "frame_0000.png").crop((0, 0, 720, 720)).save(ASSETS / "social-short-005-grid-preview-top.png", quality=95)
Image.open(OUT / "frame_0000.png").crop((0, 280, 720, 1000)).save(ASSETS / "social-short-005-grid-preview-center.png", quality=95)
print(OUT)
