import io
import math
import os
import random
from datetime import datetime
from pathlib import Path

from flask import Flask, Response, render_template_string, request, send_file
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / 'static' / 'pcm_logo.png'

WIDTH = 1080
HEIGHT = 1350

PROFIT_TEXTS = [
    'Disciplined execution delivered another solid session.',
    'High-probability setups played out well today.',
    'Clean entries and controlled risk led to a strong finish.',
    'Another steady session focused on consistency and risk control.',
    'The strategy performed with discipline and stability today.',
]

LOSS_TEXTS = [
    'A defensive session with risk kept under control.',
    'Not every day is green. Capital protection comes first.',
    'A small setback, but discipline and risk management held.',
    'Market conditions were tougher today, but the strategy stayed controlled.',
    'A controlled drawdown with focus on protecting capital.',
]

PROFIT_BADGES = [
    'LOW RISK STRATEGY',
    'CONSISTENT GAINS',
    'DISCIPLINED EXECUTION',
    'PRECISION ENTRIES',
    'CONTROLLED GROWTH',
]

LOSS_BADGES = [
    'CAPITAL PROTECTION',
    'RISK MANAGED DAY',
    'DEFENSIVE SESSION',
    'CONTROLLED DRAWDOWN',
    'DISCIPLINED RESPONSE',
]

HTML = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PCM Trading Result Generator</title>
  <style>
    body { font-family: Arial, sans-serif; background: #071423; color: #f1f5f9; margin: 0; }
    .wrap { max-width: 760px; margin: 40px auto; padding: 24px; }
    .card { background: #0c1c30; border: 1px solid #1e3a5f; border-radius: 18px; padding: 24px; box-shadow: 0 12px 40px rgba(0,0,0,.35); }
    h1 { margin-top: 0; }
    label { display: block; margin: 14px 0 6px; color: #cbd5e1; }
    input, select { width: 100%; padding: 12px; border-radius: 12px; border: 1px solid #274a76; background: #081423; color: #fff; }
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    button { margin-top: 18px; background: #1d4ed8; color: #fff; border: 0; padding: 14px 18px; border-radius: 12px; cursor: pointer; font-weight: 700; }
    .hint { color: #94a3b8; font-size: 14px; margin-top: 12px; }
    a { color: #93c5fd; }
    @media (max-width: 700px) { .row { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>PCM Trading Result Generator</h1>
      <p>Create a Telegram-ready 1080x1350 result image.</p>
      <form action="/generate" method="get">
        <label>Result (%)</label>
        <input type="text" name="result" value="3.74" placeholder="3.74 or -1.20" required>

        <div class="row">
          <div>
            <label>Strategy name</label>
            <input type="text" name="strategy" value="Strategy 3">
          </div>
          <div>
            <label>Brand name</label>
            <input type="text" name="brand" value="PCM Trading">
          </div>
        </div>

        <div class="row">
          <div>
            <label>Date label</label>
            <input type="text" name="date_label" value="{{ today }}">
          </div>
          <div>
            <label>Seed (optional)</label>
            <input type="text" name="seed" placeholder="Same seed = same random text/badge">
          </div>
        </div>

        <button type="submit">Generate PNG</button>
      </form>
      <p class="hint">Tip: use a seed such as the date (e.g. 2026-03-09) so the result stays consistent all day.</p>
    </div>
  </div>
</body>
</html>
'''


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = []
    if bold:
        candidates.extend([
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf',
        ])
    else:
        candidates.extend([
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf',
        ])
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def hex_rgba(value: str, alpha: int = 255):
    value = value.lstrip('#')
    if len(value) != 6:
        raise ValueError('Invalid hex color')
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def measure(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ''
    for word in words:
        trial = f'{current} {word}'.strip()
        if measure(draw, trial, font)[0] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_centered_text(draw, y, text, font, fill, width=WIDTH, anchor_middle=True):
    tw, th = measure(draw, text, font)
    x = (width - tw) // 2 if anchor_middle else 0
    draw.text((x, y), text, font=font, fill=fill)
    return tw, th


def add_glow(base, center_xy, radius, color, alpha=120):
    glow = Image.new('RGBA', base.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    x, y = center_xy
    gd.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color[:3] + (alpha,))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=radius // 2))
    return Image.alpha_composite(base, glow)


def draw_background(img):
    # Gradient
    px = img.load()
    for y in range(HEIGHT):
        t = y / max(HEIGHT - 1, 1)
        r = int(2 + 6 * t)
        g = int(10 + 22 * t)
        b = int(24 + 34 * t)
        for x in range(WIDTH):
            px[x, y] = (r, g, b, 255)

    # Light radial center
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse((110, 140, WIDTH - 110, HEIGHT - 140), fill=(26, 95, 210, 35))
    overlay = overlay.filter(ImageFilter.GaussianBlur(90))
    img.alpha_composite(overlay)

    # Grid
    draw = ImageDraw.Draw(img)
    grid_major = (54, 111, 182, 95)
    grid_minor = (54, 111, 182, 45)
    for x in range(0, WIDTH, 108):
        draw.line((x, 0, x, HEIGHT), fill=grid_major, width=1)
    for y in range(0, HEIGHT, 108):
        draw.line((0, y, WIDTH, y), fill=grid_major, width=1)
    for x in range(54, WIDTH, 108):
        draw.line((x, 0, x, HEIGHT), fill=grid_minor, width=1)
    for y in range(54, HEIGHT, 108):
        draw.line((0, y, WIDTH, y), fill=grid_minor, width=1)

    # Vignette
    vignette = Image.new('RGBA', img.size, (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    vd.rectangle((0, 0, WIDTH, HEIGHT), fill=(0, 0, 0, 120))
    vd.rounded_rectangle((60, 60, WIDTH - 60, HEIGHT - 60), radius=70, fill=(0, 0, 0, 0))
    vignette = vignette.filter(ImageFilter.GaussianBlur(60))
    img.alpha_composite(vignette)


def draw_card(base):
    shadow = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((84, 360, WIDTH - 84, HEIGHT - 140), radius=36, fill=(0, 0, 0, 140))
    shadow = shadow.filter(ImageFilter.GaussianBlur(20))
    base.alpha_composite(shadow)

    card = Image.new('RGBA', base.size, (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle((128, 130, WIDTH - 128, HEIGHT - 130), radius=36, fill=(10, 28, 57, 210))
    cd.rounded_rectangle((84, 364, WIDTH - 84, HEIGHT - 140), radius=30, fill=(8, 26, 53, 235), outline=(41, 82, 140, 110), width=2)
    for x in range(130, WIDTH - 128, 54):
        cd.line((x, 130, x, HEIGHT - 130), fill=(84, 137, 207, 35), width=1)
    for y in range(130, HEIGHT - 130, 54):
        cd.line((128, y, WIDTH - 128, y), fill=(84, 137, 207, 28), width=1)
    return Image.alpha_composite(base, card)


def draw_logo(base):
    if not LOGO_PATH.exists():
        return base
    logo = Image.open(LOGO_PATH).convert('RGBA')
    logo = logo.resize((250, 250))
    glow = Image.new('RGBA', base.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    x = (WIDTH - 250) // 2
    y = 66
    gd.ellipse((x + 18, y + 18, x + 232, y + 232), fill=(39, 121, 255, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(25))
    base.alpha_composite(glow)
    base.alpha_composite(logo, (x, y))
    return base


def draw_candlesticks(base, bullish=True):
    layer = Image.new('RGBA', base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x0 = 135
    x1 = WIDTH - 135
    y_bottom = 1055
    count = 22
    usable = x1 - x0
    gap = usable / count
    random_gen = random.Random(42 if bullish else 84)
    center_shift = -20 if bullish else 20
    for i in range(count):
        cx = int(x0 + i * gap + gap / 2)
        wick_top = y_bottom - random_gen.randint(130, 340)
        wick_bottom = y_bottom - random_gen.randint(30, 110)
        open_y = y_bottom - random_gen.randint(70, 260)
        close_y = y_bottom - random_gen.randint(70, 260)
        make_green = (i + (0 if bullish else 1)) % 3 != 0
        body_color = (47, 178, 93, 215) if make_green else (190, 76, 76, 215)
        if make_green and close_y > open_y:
            open_y, close_y = close_y, open_y
        if not make_green and open_y > close_y:
            open_y, close_y = close_y, open_y
        cx += center_shift
        draw.line((cx, wick_top, cx, wick_bottom), fill=body_color[:3] + (200,), width=3)
        left = cx - 11
        right = cx + 11
        top = min(open_y, close_y)
        bottom = max(open_y, close_y)
        draw.rounded_rectangle((left, top, right, bottom), radius=5, fill=body_color)
    layer = layer.filter(ImageFilter.GaussianBlur(0.5))
    return Image.alpha_composite(base, layer)


def choose_copy(result: float, seed_value: str | None):
    rng = random.Random(seed_value) if seed_value else random.Random()
    if result >= 0:
        return rng.choice(PROFIT_TEXTS), rng.choice(PROFIT_BADGES), '#2dd481'
    return rng.choice(LOSS_TEXTS), rng.choice(LOSS_BADGES), '#ef5a5a'


def generate_result_image(result_value: str, strategy: str, brand: str, date_label: str, seed: str | None = None):
    value = float(str(result_value).replace('%', '').replace(',', '.').strip())
    result_text = f'{value:+.2f}%'
    main_text, badge_text, accent_hex = choose_copy(value, seed)
    accent = hex_rgba(accent_hex)

    img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw_background(img)
    img = draw_card(img)
    img = draw_logo(img)
    img = draw_candlesticks(img, bullish=value >= 0)

    draw = ImageDraw.Draw(img)
    title_font = load_font(54, bold=True)
    result_font = load_font(164, bold=True)
    body_font = load_font(36, bold=False)
    small_font = load_font(26, bold=False)
    brand_font = load_font(36, bold=True)
    badge_font = load_font(34, bold=True)

    # top label
    draw_centered_text(draw, 415, "TODAY'S RESULT", title_font, (225, 233, 248, 255))

    # result glow and text
    glow_center = (WIDTH // 2, 565)
    img = add_glow(img, glow_center, 150, accent, alpha=80)
    draw = ImageDraw.Draw(img)
    draw_centered_text(draw, 500, result_text, result_font, (255, 255, 255, 255))

    # accent line
    line_y = 692
    draw.rounded_rectangle((300, line_y, WIDTH - 300, line_y + 6), radius=4, fill=accent)

    # main text
    max_width = 760
    lines = wrap_text(draw, main_text, body_font, max_width)
    current_y = 750
    for line in lines:
        draw_centered_text(draw, current_y, line, body_font, (231, 236, 244, 255))
        current_y += 50

    subtext = f'{brand} focuses on disciplined entries, strict risk management and steady execution.'
    sub_lines = wrap_text(draw, subtext, small_font, 720)
    current_y += 10
    for line in sub_lines:
        draw_centered_text(draw, current_y, line, small_font, (190, 206, 228, 235))
        current_y += 38

    # badge
    bw, bh = measure(draw, badge_text, badge_font)
    badge_pad_x = 38
    badge_pad_y = 18
    bx0 = (WIDTH - (bw + badge_pad_x * 2)) // 2
    by0 = 972
    bx1 = bx0 + bw + badge_pad_x * 2
    by1 = by0 + bh + badge_pad_y * 2 - 8
    badge_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge_layer)
    bd.rounded_rectangle((bx0, by0, bx1, by1), radius=28, fill=accent[:3] + (220,))
    badge_layer = badge_layer.filter(ImageFilter.GaussianBlur(0.4))
    img = Image.alpha_composite(img, badge_layer)
    draw = ImageDraw.Draw(img)
    draw.text((bx0 + badge_pad_x, by0 + 12), badge_text, font=badge_font, fill=(255, 255, 255, 255))

    # footer
    draw_centered_text(draw, 1120, 'Copy trading available on Vantage', load_font(28, False), (195, 205, 224, 240))
    draw_centered_text(draw, 1168, brand, brand_font, (255, 255, 255, 255))
    draw_centered_text(draw, 1214, strategy, load_font(24, False), (160, 181, 212, 230))
    draw_centered_text(draw, 1244, date_label, load_font(22, False), (132, 156, 192, 220))

    # sharpen slightly
    img = ImageEnhance.Sharpness(img).enhance(1.12)

    out = io.BytesIO()
    img.convert('RGB').save(out, format='PNG', optimize=True)
    out.seek(0)
    return out


@app.route('/')
def index():
    return render_template_string(HTML, today=datetime.utcnow().strftime('%B %-d, %Y') if os.name != 'nt' else datetime.utcnow().strftime('%B %d, %Y'))


@app.route('/health')
def health():
    return {'status': 'ok'}


@app.route('/generate')
def generate():
    result_value = request.args.get('result', '0')
    strategy = request.args.get('strategy', 'Strategy 3').strip() or 'Strategy 3'
    brand = request.args.get('brand', 'PCM Trading').strip() or 'PCM Trading'
    date_label = request.args.get('date_label', datetime.utcnow().strftime('%B %d, %Y')).strip()
    seed = request.args.get('seed', '').strip() or None

    try:
        image_io = generate_result_image(result_value, strategy, brand, date_label, seed)
    except Exception as exc:
        return Response(f'Invalid input: {exc}', status=400, mimetype='text/plain')

    safe_result = str(result_value).replace('%', '').replace('+', 'plus').replace('-', 'minus').replace('.', '_')
    filename = f'pcm_result_{safe_result}.png'
    return send_file(image_io, mimetype='image/png', as_attachment=False, download_name=filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
