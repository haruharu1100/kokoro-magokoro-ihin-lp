from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUT = ASSETS / "social-short-002-frames"
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


def text_center(draw, y, text, size, fill, line_gap=8):
    f = font(size)
    lines = text.split("\n")
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=f)
        draw.text(((W - (bbox[2] - bbox[0])) / 2, y), line, font=f, fill=fill)
        y += size + line_gap
    return y


def fit(img, box):
    img = img.convert("RGBA")
    bw, bh = box
    scale = min(bw / img.width, bh / img.height)
    return img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)


def make_base():
    img = Image.new("RGBA", (W, H), (18, 105, 80, 255))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, 0, W, H), fill=(18, 105, 80, 255))
    d.ellipse((455, -90, 835, 290), fill=(255, 255, 255, 38))
    d.ellipse((-170, 910, 280, 1360), fill=(217, 164, 65, 70))
    d.ellipse((495, 830, 760, 1095), fill=(255, 255, 255, 22))
    return img


logo = Image.open(ASSETS / "google-ad-logo-square.png")
logo_small = fit(logo, (160, 160))

scenes = [
    ("遺品整理\nまずは写真で相談", "大阪・兵庫・奈良・京都対応", (201, 79, 69)),
    ("仕分け・供養・買取\nまとめて対応", "大切な物を確認しながら進めます", (217, 164, 65)),
    ("買取できる品は\n作業費から差し引き", "費用を抑えやすい見積もり", (201, 79, 69)),
    ("LINEで無料相談", "心まごころ遺品整理", (6, 199, 85)),
]

for i in range(TOTAL):
    sec = i / FPS
    idx = min(3, int(sec / 2.5))
    local = (sec - idx * 2.5) / 2.5
    title, sub, accent = scenes[idx]
    e = 0.5 - math.cos(math.pi * min(1, max(0, local))) / 2

    frame = make_base()
    d = ImageDraw.Draw(frame, "RGBA")

    # Everything important stays inside the center square crop used on Instagram profiles.
    card_y = 270 + int(10 * math.sin(e * math.pi))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow, "RGBA")
    rounded(sd, (52, card_y + 16, W - 52, card_y + 612), 34, fill=(0, 0, 0, 48))
    frame.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(16)))

    rounded(d, (48, card_y, W - 48, card_y + 596), 34, fill=(255, 253, 250, 255))
    rounded(d, (86, card_y + 36, 236, card_y + 80), 22, fill=accent)
    d.text((161, card_y + 44), "無料相談", font=font(21), fill="white", anchor="ma")

    if idx == 3:
        frame.alpha_composite(logo_small, ((W - logo_small.width) // 2, card_y + 108))
        y = card_y + 300
    else:
        y = card_y + 128

    y = text_center(d, y, title, 52 if idx != 3 else 58, (15, 53, 44), 10)
    y += 16
    text_center(d, y, sub, 29, (56, 89, 79), 8)

    rounded(d, (82, card_y + 492, W - 82, card_y + 548), 28, fill=(21, 102, 78))
    d.text((W // 2, card_y + 509), "写真を送るだけでも概算OK", font=font(25), fill="white", anchor="ma")

    d.text((W // 2, 1080), "心まごころ遺品整理", font=font(34), fill="white", anchor="ma")
    d.text((W // 2, 1128), "LINEで無料見積もり", font=font(43), fill="white", anchor="ma")

    fade_in = local / 0.16 if idx > 0 else 1
    fade = min(1, fade_in, (1 - local) / 0.16 if local > 0.84 else 1)
    if fade < 1:
        frame.alpha_composite(Image.new("RGBA", (W, H), (18, 105, 80, int((1 - fade) * 130))))

    frame.convert("RGB").save(OUT / f"frame_{i:04d}.png", quality=92)

# Instagram cover image: same first frame, separately selectable as cover.
Image.open(OUT / "frame_0000.png").save(ASSETS / "social-short-002-cover.png", quality=95)
print(OUT)
