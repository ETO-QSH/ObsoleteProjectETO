from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

INPUT_DIR = Path("../output/heat_map")
OUTPUT_DIR = Path("../output/heat_map/stitched")
OUTPUT_DIR.mkdir(exist_ok=True)

W, H = 640, 720

regions = {
    "Strait_of_Hormuz": {
        "hx": 67, "hy": 116,
        "title": "霍尔木兹海峡",
    },
    "Strait_of_Malacca": {
        "hx": 60, "hy": 116,
        "title": "马六甲海峡",
    },
    "Cape_of_Good_Hope": {
        "hx": 63, "hy": 116,
        "title": "好望角",
    },
    "Suez_Canal": {
        "hx": 63, "hy": 116,
        "title": "苏伊士运河",
    },
}

HEATMAP = 480
AXIS_X = 80
AXIS_Y = 40
TITLE_H = 80
BIG = 1120


def extract(img, hx, hy, keep):
    kl, kr, kt, kb = keep

    left = hx - (AXIS_X if kl else 0)
    upper = hy - (AXIS_Y if kt else 0)
    right = hx + HEATMAP + (AXIS_X if kr else 0)
    lower = hy + HEATMAP + (AXIS_Y if kb else 0)

    cw = (AXIS_X if kl else 0) + HEATMAP + (AXIS_X if kr else 0)
    ch = (AXIS_Y if kt else 0) + HEATMAP + (AXIS_Y if kb else 0)
    canvas = Image.new('RGB', (cw, ch), 'white')

    iw, ih = img.size
    vl, vu = max(0, left), max(0, upper)
    vr, vlw = min(iw, right), min(ih, lower)

    if vl < vr and vu < vlw:
        patch = img.crop((vl, vu, vr, vlw))
        canvas.paste(patch, (vl - left, vu - upper))

    return canvas


for name, cfg in regions.items():
    hx, hy = cfg["hx"], cfg["hy"]

    imgs = {
        'lt': INPUT_DIR / f"{name}_2025_rho_{W}x{H}.png",
        'rt': INPUT_DIR / f"{name}_2025_speed_{W}x{H}.png",
        'lb': INPUT_DIR / f"{name}_2026_rho_{W}x{H}.png",
        'rb': INPUT_DIR / f"{name}_2026_speed_{W}x{H}.png",
    }
    if not all(p.exists() for p in imgs.values()):
        print(f"⚠ 跳过 {name}: 文件缺失")
        continue

    big = Image.new('RGB', (BIG, BIG), 'white')

    big.paste(extract(Image.open(imgs['lt']), hx, hy, (1, 0, 1, 0)), (0, TITLE_H))
    big.paste(extract(Image.open(imgs['rt']), hx, hy, (0, 1, 1, 0)), (AXIS_X + HEATMAP, TITLE_H))
    big.paste(extract(Image.open(imgs['lb']), hx, hy, (1, 0, 0, 1)), (0, TITLE_H + AXIS_Y + HEATMAP))
    big.paste(extract(Image.open(imgs['rb']), hx, hy, (0, 1, 0, 1)), (AXIS_X + HEATMAP, TITLE_H + AXIS_Y + HEATMAP))

    draw = ImageDraw.Draw(big)
    font = ImageFont.truetype("Lolita.ttf", 32)

    txt = f"{cfg['title']} - 船舶密度与航速热力图 - 2025vs2026"
    bbox = draw.textbbox((0, 0), txt, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((BIG - tw) // 2, (TITLE_H - th) // 2 - bbox[1]), txt, fill='black', font=font)

    out = OUTPUT_DIR / f"{name}_stitched_A_{BIG}x{BIG}.png"
    big.save(out, quality=95)
    print(f"✅ {out.name}")

for name, cfg in regions.items():
    hx, hy = cfg["hx"], cfg["hy"]

    imgs = {
        'lt': INPUT_DIR / f"{name}_2025_tanker_{W}x{H}.png",
        'rt': INPUT_DIR / f"{name}_2025_lng_{W}x{H}.png",
        'lb': INPUT_DIR / f"{name}_2026_tanker_{W}x{H}.png",
        'rb': INPUT_DIR / f"{name}_2026_lng_{W}x{H}.png",
    }
    if not all(p.exists() for p in imgs.values()):
        print(f"⚠ 跳过 {name}: 文件缺失")
        continue

    big = Image.new('RGB', (BIG, BIG), 'white')

    big.paste(extract(Image.open(imgs['lt']), hx, hy, (1, 0, 1, 0)), (0, TITLE_H))
    big.paste(extract(Image.open(imgs['rt']), hx, hy, (0, 1, 1, 0)), (AXIS_X + HEATMAP, TITLE_H))
    big.paste(extract(Image.open(imgs['lb']), hx, hy, (1, 0, 0, 1)), (0, TITLE_H + AXIS_Y + HEATMAP))
    big.paste(extract(Image.open(imgs['rb']), hx, hy, (0, 1, 0, 1)), (AXIS_X + HEATMAP, TITLE_H + AXIS_Y + HEATMAP))

    draw = ImageDraw.Draw(big)
    font = ImageFont.truetype("Lolita.ttf", 32)

    txt = f"{cfg['title']} - 石油与天然气运力热力图 - 2025vs2026"
    bbox = draw.textbbox((0, 0), txt, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((BIG - tw) // 2, (TITLE_H - th) // 2 - bbox[1]), txt, fill='black', font=font)

    out = OUTPUT_DIR / f"{name}_stitched_B_{BIG}x{BIG}.png"
    big.save(out, quality=95)
    print(f"✅ {out.name}")

print(f"\\n📁 输出: {OUTPUT_DIR}")
