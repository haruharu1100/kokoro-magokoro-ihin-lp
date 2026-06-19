from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUT = ASSETS / "social-short-006-frames"
OUT.mkdir(parents=True, exist_ok=True)

for old in OUT.glob("frame_*.png"):
    old.unlink()

FONT = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
if not Path(FONT).exists():
    FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"

W, H = 1080, 1920
FPS = 30
TOTAL = 300


def font(size):
    return ImageFont.truetype(FONT, size)


def rounded(draw, xy, r, fill):
    draw.rounded_rectangle(xy, radius=r, fill=fill)


def center(draw, text, y, size, fill, gap=16):
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
    d.ellipse((-150, 1510, 330, 1990), fill=(217, 164, 65, 75))
    d.ellipse((810, -150, 1280, 320), fill=(255, 255, 255, 36))
    d.ellipse((830, 1410, 1290, 1870), fill=(255, 255, 255, 18))
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

    # Designed for Instagram Reels: no important text near the top/bottom UI.
    y0 = 365 + int(10 * math.sin(e * math.pi))
    card = (210, y0, W - 210, y0 + 720)

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow, "RGBA")
    rounded(sd, (card[0] + 12, card[1] + 18, card[2] + 12, card[3] + 18), 46, (0, 0, 0, 52))
    frame.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(20)))

    rounded(d, card, 46, (255, 253, 250, 255))
    rounded(d, (260, y0 + 58, 455, y0 + 124), 33, (201, 79, 69, 255))
    d.text((357, y0 + 74), "無料相談", font=font(30), fill="white", anchor="ma")

    center(d, a, y0 + 190, 76, (15, 53, 44))
    center(d, b, y0 + 330, 78, (15, 53, 44))
    center(d, c, y0 + 500, 44, (56, 89, 79))

    rounded(d, (270, y0 + 600, W - 270, y0 + 680), 40, (21, 102, 78, 255))
    d.text((W // 2, y0 + 623), "まずは写真でOK", font=font(36), fill="white", anchor="ma")

    d.text((W // 2, 1270), "心まごころ遺品整理", font=font(42), fill="white", anchor="ma")
    d.text((W // 2, 1345), "大阪・兵庫・奈良・京都", font=font(38), fill="white", anchor="ma")

    fade_in = local / 0.14 if idx > 0 else 1
    fade = min(1, fade_in, (1 - local) / 0.14 if local > 0.86 else 1)
    if fade < 1:
        frame.alpha_composite(Image.new("RGBA", (W, H), (18, 105, 80, int((1 - fade) * 145))))

    frame.convert("RGB").save(OUT / f"frame_{i:04d}.png", quality=92)

cover = Image.open(OUT / "frame_0000.png")
cover.save(ASSETS / "social-short-006-cover.png", quality=95)
cover.crop((0, 420, 1080, 1500)).save(ASSETS / "social-short-006-profile-grid-preview.png", quality=95)
print(OUT)
