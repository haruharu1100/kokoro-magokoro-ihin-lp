from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import shutil

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUT = ASSETS / "social-short-001-frames"
OUT.mkdir(parents=True, exist_ok=True)

for old in OUT.glob("frame_*.png"):
    old.unlink()

FONT = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
if not Path(FONT).exists():
    FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"

W, H = 720, 1280
FPS = 30
DURATION = 10
TOTAL = FPS * DURATION


def font(size):
    return ImageFont.truetype(FONT, size)


def rounded(draw, xy, r, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def cover_resize(img, size):
    img = img.convert("RGB")
    sw, sh = size
    scale = max(sw / img.width, sh / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    return img.crop(((nw - sw) // 2, (nh - sh) // 2, (nw + sw) // 2, (nh + sh) // 2))


def fit_resize(img, size):
    img = img.convert("RGBA")
    sw, sh = size
    scale = min(sw / img.width, sh / img.height)
    return img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)


def gradient_bg():
    img = Image.new("RGB", (W, H), (248, 251, 247))
    pix = img.load()
    for y in range(H):
        for x in range(W):
            t = x / W * 0.35 + y / H * 0.65
            if t < 0.5:
                u = t / 0.5
                c = (
                    int(248 * (1 - u) + 237 * u),
                    int(251 * (1 - u) + 246 * u),
                    int(247 * (1 - u) + 239 * u),
                )
            else:
                u = (t - 0.5) / 0.5
                c = (
                    int(237 * (1 - u) + 255 * u),
                    int(246 * (1 - u) + 244 * u),
                    int(239 * (1 - u) + 223 * u),
                )
            pix[x, y] = c
    return img.convert("RGBA")


def add_safe_text(draw, text, xy, size, fill, max_width, line_gap=8):
    words = list(text)
    lines = []
    cur = ""
    f = font(size)
    for ch in words:
        test = cur + ch
        if draw.textbbox((0, 0), test, font=f)[2] <= max_width or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=f, fill=fill)
        y += size + line_gap
    return y


def ease(t):
    return 0.5 - math.cos(math.pi * t) / 2


square = Image.open(ASSETS / "google-ad-square.png")
landscape = Image.open(ASSETS / "google-ad-landscape.png")
logo = Image.open(ASSETS / "line-profile-icon.png")

scenes = [
    {
        "start": 0,
        "end": 2.4,
        "title": "遺品整理、\n何から始める？",
        "sub": "まずは写真で相談できます",
        "image": square,
    },
    {
        "start": 2.4,
        "end": 5.0,
        "title": "大切な物を\n確認しながら仕分け",
        "sub": "貴重品探索・供養も対応",
        "image": landscape,
    },
    {
        "start": 5.0,
        "end": 7.6,
        "title": "買取できる品は\n作業費から差し引き",
        "sub": "費用を抑えやすい見積もり",
        "image": square,
    },
    {
        "start": 7.6,
        "end": 10.0,
        "title": "大阪・兵庫・奈良・京都",
        "sub": "心まごころ遺品整理\nLINEで無料相談",
        "image": logo,
    },
]

for i in range(TOTAL):
    sec = i / FPS
    scene = scenes[-1]
    for s in scenes:
        if s["start"] <= sec < s["end"]:
            scene = s
            break

    local_t = (sec - scene["start"]) / (scene["end"] - scene["start"])
    e = ease(max(0, min(1, local_t)))
    frame = gradient_bg()
    d = ImageDraw.Draw(frame, "RGBA")

    d.ellipse((480, -80, 820, 260), fill=(6, 199, 85, 35))
    d.ellipse((-180, 980, 280, 1440), fill=(217, 164, 65, 44))

    img = scene["image"]
    if scene is scenes[-1]:
        visual = fit_resize(img, (360, 360))
        x = (W - visual.width) // 2
        y = 170 + int(16 * math.sin(e * math.pi))
        frame.alpha_composite(visual, (x, y))
    else:
        visual = cover_resize(img, (570, 570)).convert("RGBA")
        scale = 1.0 + 0.055 * e
        visual = visual.resize((int(570 * scale), int(570 * scale)), Image.Resampling.LANCZOS)
        shadow = Image.new("RGBA", (visual.width + 40, visual.height + 40), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        rounded(sd, (20, 20, visual.width + 20, visual.height + 20), 28, fill=(18, 61, 52, 45))
        shadow = shadow.filter(ImageFilter.GaussianBlur(16))
        x = (W - visual.width) // 2
        y = 125
        frame.alpha_composite(shadow, (x - 20, y - 10))
        mask = Image.new("L", visual.size, 0)
        md = ImageDraw.Draw(mask)
        rounded(md, (0, 0, visual.width, visual.height), 28, fill=255)
        frame.paste(visual, (x, y), mask)

    panel_y = 735 if scene is not scenes[-1] else 620
    rounded(d, (48, panel_y, W - 48, H - 92), 28, fill=(255, 255, 255, 235))
    rounded(d, (80, panel_y + 36, 238, panel_y + 78), 21, fill=(21, 102, 78))
    d.text((159, panel_y + 43), "無料相談", font=font(21), fill="white", anchor="ma")

    y = panel_y + 104
    for line in scene["title"].split("\n"):
        d.text((80, y), line, font=font(48), fill=(15, 53, 44))
        y += 58
    y += 16
    for line in scene["sub"].split("\n"):
        d.text((82, y), line, font=font(30), fill=(56, 89, 79))
        y += 42

    rounded(d, (80, H - 148, W - 80, H - 92), 28, fill=(201, 79, 69))
    d.text((W // 2, H - 132), "LINEで無料見積もり", font=font(29), fill="white", anchor="ma")

    fade = min(1, local_t / 0.18, (1 - local_t) / 0.18 if local_t > 0.82 else 1)
    if fade < 1:
        overlay = Image.new("RGBA", (W, H), (255, 253, 250, int((1 - fade) * 255)))
        frame.alpha_composite(overlay)

    frame.convert("RGB").save(OUT / f"frame_{i:04d}.png", quality=92)

print(OUT)
