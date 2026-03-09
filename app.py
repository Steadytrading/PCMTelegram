import io
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

DAILY_PROFIT_TEXTS = [
    'Disciplined execution delivered another solid session.',
    'High-probability setups played out well today.',
    'Clean entries and controlled risk led to a strong finish.',
    'Another steady session focused on consistency and risk control.',
    'The strategy performed with discipline and stability today.',
]

DAILY_LOSS_TEXTS = [
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

WEEKLY_TEXTS = [
    'A full week of structured execution and controlled risk.',
    'Weekly performance stayed aligned with a disciplined approach.',
    'Another week focused on consistency, patience and quality setups.',
    'Steady execution supported the strategy throughout the week.',
    'The weekly result reflects discipline and capital-focused trading.',
]

MONTHLY_TEXTS = [
    'Monthly performance reflected disciplined execution and risk-first decision making.',
    'The month was managed with a strong focus on consistency and capital protection.',
    'Structured execution and patience defined the strategy this month.',
    'The monthly result highlights steady management through changing market conditions.',
    'This month reinforced a process-driven approach built for sustainable growth.',
]

HTML = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PCM Trading Generator V2</title>
  <style>
    body { font-family: Arial, sans-serif; background: #071423; color: #f1f5f9; margin: 0; }
    .wrap { max-width: 920px; margin: 32px auto; padding: 20px; }
    .card { background: #0c1c30; border: 1px solid #1e3a5f; border-radius: 18px; padding: 24px; box-shadow: 0 12px 40px rgba(0,0,0,.35); margin-bottom: 18px; }
    h1,h2 { margin-top: 0; }
    label { display: block; margin: 12px 0 6px; color: #cbd5e1; }
    input { width: 100%; padding: 12px; border-radius: 12px; border: 1px solid #274a76; background: #081423; color: #fff; }
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .row3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
    button { margin-top: 16px; background: #1d4ed8; color: #fff; border: 0; padding: 14px 18px; border-radius: 12px; cursor: pointer; font-weight: 700; }
    .hint { color: #94a3b8; font-size: 14px; margin-top: 12px; }
    @media (max-width: 700px) { .row, .row3 { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>PCM Trading Generator V2</h1>
      <p>Daily, weekly and monthly posters in a Telegram-friendly 1080x1350 format. The image is returned as a file download.</p>
      <p class="hint">Tip: use the same seed each day or week if you want deterministic random text and badges.</p>
    </div>

    <div class="card">
      <h2>Daily result</h2>
      <form action="/generate" method="get">
        <label>Result (%)</label>
        <input type="text" name="result" value="3.74" required>
        <div class="row">
          <div>
            <label>Strategy</label>
            <input type="text" name="strategy" value="Strategy 3">
          </div>
          <div>
            <label>Brand</label>
            <input type="text" name="brand" value="PCM Trading">
          </div>
        </div>
        <label>Seed (optional)</label>
        <input type="text" name="seed" placeholder="2026-03-09">
        <button type="submit">Download daily PNG</button>
      </form>
    </div>

    <div class="card">
      <h2>Weekly result</h2>
      <form action="/generate/weekly" method="get">
        <div class="row">
          <div>
            <label>Weekly result (%)</label>
            <input type="text" name="result" value="10.60" required>
          </div>
          <div>
            <label>Week label</label>
            <input type="text" name="period_label" value="Weekly Performance">
          </div>
        </div>
        <div class="row">
          <div>
            <label>Strategy</label>
            <input type="text" name="strategy" value="Strategy 3">
          </div>
          <div>
            <label>Brand</label>
            <input type="text" name="brand" value="PCM Trading">
          </div>
        </div>
        <label>Seed (optional)</label>
        <input type="text" name="seed" placeholder="2026-week-10">
        <button type="submit">Download weekly PNG</button>
      </form>
    </div>

    <div class="card">
      <h2>Monthly performance</h2>
      <form action="/generate/monthly" method="get">
        <div class="row">
          <div>
            <label>Monthly result (%)</label>
            <input type="text" name="result" value="12.40" required>
          </div>
          <div>
            <label>Month label</label>
            <input type="text" name="period_label" value="Monthly Performance">
          </div>
        </div>
        <div class="row3">
          <div>
            <label>Trades</label>
            <input type="text" name="trades" value="42">
          </div>
          <div>
            <label>Win rate (%)</label>
            <input type="text" name="win_rate" value="68">
          </div>
          <div>
            <label>Drawdown (%)</label>
            <input type="text" name="drawdown" value="3.10">
          </div>
        </div>
        <div class="row">
          <div>
            <label>Strategy</label>
            <input type="text" name="strategy" value="Strategy 3">
          </div>
          <div>
            <label>Brand</label>
            <input type="text" name="brand" value="PCM Trading">
          </div>
        </div>
        <label>Seed (optional)</label>
        <input type="text" name="seed" placeholder="2026-03">
        <button type="submit">Download monthly PNG</button>
      </form>
    </div>
  </div>
</body>
</html>
'''


def load_font(size: int, bold: bool = False):
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


def parse_percent(raw: str) -> float:
    return float(str(raw).replace('%', '').replace(',', '.').strip())


def hex_rgba(value: str, alpha: int = 255):
    value = value.lstrip('#')
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def measure(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def draw_centered(draw, y, text, font, fill, width=WIDTH):
    tw, th = measure(draw, text, font)
    draw.text(((width - tw) // 2, y), text, font=font, fill=fill)
    return tw, th


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


def add_glow(base, center_xy, radius, color, alpha=120):
    glow = Image.new('RGBA', base.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    x, y = center_xy
    gd.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color[:3] + (alpha,))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=max(8, radius // 2)))
    return Image.alpha_composite(base, glow)


def make_background():
    img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 255))
    px = img.load()
    for y in range(HEIGHT):
        t = y / max(HEIGHT - 1, 1)
        r = int(1 + 5 * t)
        g = int(8 + 20 * t)
        b = int(22 + 34 * t)
        for x in range(WIDTH):
            px[x, y] = (r, g, b, 255)

    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse((100, 120, WIDTH - 100, HEIGHT - 130), fill=(26, 95, 210, 28))
    overlay = overlay.filter(ImageFilter.GaussianBlur(90))
    img.alpha_composite(overlay)

    draw = ImageDraw.Draw(img)
    major = (54, 111, 182, 86)
    minor = (54, 111, 182, 38)
    for x in range(0, WIDTH, 108):
        draw.line((x, 0, x, HEIGHT), fill=major, width=1)
    for y in range(0, HEIGHT, 108):
        draw.line((0, y, WIDTH, y), fill=major, width=1)
    for x in range(54, WIDTH, 108):
        draw.line((x, 0, x, HEIGHT), fill=minor, width=1)
    for y in range(54, HEIGHT, 108):
        draw.line((0, y, WIDTH, y), fill=minor, width=1)
    return img


def add_cards(base):
    shadow = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((84, 360, WIDTH - 84, HEIGHT - 140), radius=36, fill=(0, 0, 0, 145))
    shadow = shadow.filter(ImageFilter.GaussianBlur(20))
    base.alpha_composite(shadow)

    card = Image.new('RGBA', base.size, (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle((128, 130, WIDTH - 128, HEIGHT - 130), radius=36, fill=(9, 24, 52, 208))
    cd.rounded_rectangle((84, 364, WIDTH - 84, HEIGHT - 140), radius=30, fill=(8, 24, 51, 235), outline=(41, 82, 140, 110), width=2)
    for x in range(130, WIDTH - 128, 54):
        cd.line((x, 130, x, HEIGHT - 130), fill=(84, 137, 207, 30), width=1)
    for y in range(130, HEIGHT - 130, 54):
        cd.line((128, y, WIDTH - 128, y), fill=(84, 137, 207, 24), width=1)
    return Image.alpha_composite(base, card)


def add_logo(base):
    if not LOGO_PATH.exists():
        return base
    logo = Image.open(LOGO_PATH).convert('RGBA')
    logo.thumbnail((250, 250))
    x = (WIDTH - logo.width) // 2
    y = 65
    glow = Image.new('RGBA', base.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((x + 20, y + 20, x + logo.width - 20, y + logo.height - 20), fill=(39, 121, 255, 75))
    glow = glow.filter(ImageFilter.GaussianBlur(26))
    base.alpha_composite(glow)
    base.alpha_composite(logo, (x, y))
    return base


def add_candles(base, bullish=True):
    layer = Image.new('RGBA', base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x0 = 132
    x1 = WIDTH - 132
    y_bottom = 1045
    count = 21
    gap = (x1 - x0) / count
    rng = random.Random(42 if bullish else 84)
    for i in range(count):
        cx = int(x0 + i * gap + gap / 2)
        wick_top = y_bottom - rng.randint(130, 340)
        wick_bottom = y_bottom - rng.randint(30, 110)
        open_y = y_bottom - rng.randint(70, 260)
        close_y = y_bottom - rng.randint(70, 260)
        green = (i + (0 if bullish else 1)) % 3 != 0
        color = (47, 178, 93, 215) if green else (190, 76, 76, 215)
        if green and close_y > open_y:
            open_y, close_y = close_y, open_y
        if not green and open_y > close_y:
            open_y, close_y = close_y, open_y
        draw.line((cx, wick_top, cx, wick_bottom), fill=color[:3] + (200,), width=3)
        draw.rounded_rectangle((cx - 11, min(open_y, close_y), cx + 11, max(open_y, close_y)), radius=5, fill=color)
    layer = layer.filter(ImageFilter.GaussianBlur(0.5))
    return Image.alpha_composite(base, layer)


def add_metric_boxes(base, metrics, accent):
    layer = Image.new('RGBA', base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    title_font = load_font(22, False)
    value_font = load_font(34, True)
    box_y0 = 980
    box_y1 = 1096
    gap = 24
    total_w = WIDTH - 240
    box_w = int((total_w - 2 * gap) / 3)
    x = 120
    for title, value in metrics:
        draw.rounded_rectangle((x, box_y0, x + box_w, box_y1), radius=22, fill=(7, 20, 42, 220), outline=(41, 82, 140, 90), width=2)
        ttw, _ = measure(draw, title, title_font)
        draw.text((x + (box_w - ttw) // 2, box_y0 + 18), title, font=title_font, fill=(169, 188, 219, 240))
        tx, _ = measure(draw, value, value_font)
        draw.text((x + (box_w - tx) // 2, box_y0 + 52), value, font=value_font, fill=accent)
        x += box_w + gap
    return Image.alpha_composite(base, layer)


def choose_daily_copy(value, seed):
    rng = random.Random(seed) if seed else random.Random()
    if value >= 0:
        return rng.choice(DAILY_PROFIT_TEXTS), rng.choice(PROFIT_BADGES), '#2dd481'
    return rng.choice(DAILY_LOSS_TEXTS), rng.choice(LOSS_BADGES), '#ef5a5a'


def choose_period_copy(value, seed, monthly=False):
    rng = random.Random(seed) if seed else random.Random()
    texts = MONTHLY_TEXTS if monthly else WEEKLY_TEXTS
    badge_pool = PROFIT_BADGES if value >= 0 else LOSS_BADGES
    color = '#2dd481' if value >= 0 else '#ef5a5a'
    return rng.choice(texts), rng.choice(badge_pool), color


def render_common_layout(result_text, heading, body_text, badge_text, accent_hex, strategy, brand, badge_y=972, show_badge=True):
    accent = hex_rgba(accent_hex)
    img = make_background()
    img = add_cards(img)
    img = add_logo(img)
    img = add_candles(img, bullish='-' not in result_text)

    title_font = load_font(54, True)
    result_font = load_font(168, True)
    body_font = load_font(38, False)
    small_font = load_font(28, False)
    brand_font = load_font(36, True)
    strategy_font = load_font(25, False)
    badge_font = load_font(32, True)

    draw = ImageDraw.Draw(img)
    draw_centered(draw, 415, heading, title_font, (225, 233, 248, 255))
    img = add_glow(img, (WIDTH // 2, 565), 150, accent, alpha=80)
    draw = ImageDraw.Draw(img)
    draw_centered(draw, 500, result_text, result_font, (255, 255, 255, 255))
    line_y = 692
    draw.rounded_rectangle((300, line_y, WIDTH - 300, line_y + 6), radius=4, fill=accent)

    lines = wrap_text(draw, body_text, body_font, 790)
    current_y = 750
    for line in lines[:2]:
        draw_centered(draw, current_y, line, body_font, (231, 236, 244, 255))
        current_y += 52

    subtext = f'{brand} focuses on disciplined entries, strict risk management and steady execution.'
    sub_lines = wrap_text(draw, subtext, small_font, 720)
    current_y += 6
    for line in sub_lines[:2]:
        draw_centered(draw, current_y, line, small_font, (190, 206, 228, 235))
        current_y += 38

    if show_badge:
        bw, bh = measure(draw, badge_text, badge_font)
        pad_x = 36
        bx0 = (WIDTH - (bw + pad_x * 2)) // 2
        by0 = badge_y
        bx1 = bx0 + bw + pad_x * 2
        by1 = by0 + bh + 30
        badge_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        bd = ImageDraw.Draw(badge_layer)
        bd.rounded_rectangle((bx0, by0, bx1, by1), radius=28, fill=accent[:3] + (220,))
        badge_layer = badge_layer.filter(ImageFilter.GaussianBlur(0.4))
        img = Image.alpha_composite(img, badge_layer)
        draw = ImageDraw.Draw(img)
        draw.text((bx0 + pad_x, by0 + 12), badge_text, font=badge_font, fill=(255, 255, 255, 255))

    draw_centered(draw, 1120, 'Copy trading available on Vantage', load_font(28, False), (195, 205, 224, 240))
    draw_centered(draw, 1168, brand, brand_font, (255, 255, 255, 255))
    draw_centered(draw, 1214, strategy, strategy_font, (160, 181, 212, 230))
    return img


def save_image(img):
    img = ImageEnhance.Sharpness(img).enhance(1.12)
    out = io.BytesIO()
    img.convert('RGB').save(out, format='PNG', optimize=True)
    out.seek(0)
    return out


def generate_daily(result_value, strategy, brand, seed=None):
    value = parse_percent(result_value)
    result_text = f'{value:+.2f}%'
    body_text, badge_text, accent_hex = choose_daily_copy(value, seed)
    img = render_common_layout(result_text, "TODAY'S RESULT", body_text, badge_text, accent_hex, strategy, brand)
    return save_image(img)


def generate_weekly(result_value, strategy, brand, period_label, seed=None):
    value = parse_percent(result_value)
    result_text = f'{value:+.2f}%'
    body_text, badge_text, accent_hex = choose_period_copy(value, seed, monthly=False)
    img = render_common_layout(result_text, period_label.upper(), body_text, badge_text, accent_hex, strategy, brand)
    return save_image(img)


def generate_monthly(result_value, strategy, brand, period_label, trades, win_rate, drawdown, seed=None):
    value = parse_percent(result_value)
    result_text = f'{value:+.2f}%'
    body_text, badge_text, accent_hex = choose_period_copy(value, seed, monthly=True)
    img = render_common_layout(result_text, period_label.upper(), body_text, badge_text, accent_hex, strategy, brand, show_badge=False)
    accent = hex_rgba(accent_hex)
    drawdown_val = f'-{abs(parse_percent(drawdown)):.2f}%'
    metrics = [
        ('TRADES', str(trades).strip()),
        ('WIN RATE', f'{parse_percent(win_rate):.0f}%'),
        ('DRAWDOWN', drawdown_val),
    ]
    img = add_metric_boxes(img, metrics, accent)
    return save_image(img)


def make_filename(prefix, result_value):
    safe = str(result_value).replace('%', '').replace('+', 'plus').replace('-', 'minus').replace('.', '_').replace(',', '_')
    return f'{prefix}_{safe}.png'


@app.route('/')
def index():
    return render_template_string(HTML)


@app.route('/health')
def health():
    return {'status': 'ok'}


@app.route('/generate')
def generate():
    result_value = request.args.get('result', '0')
    strategy = request.args.get('strategy', 'Strategy 3').strip() or 'Strategy 3'
    brand = request.args.get('brand', 'PCM Trading').strip() or 'PCM Trading'
    seed = request.args.get('seed', '').strip() or None
    try:
        image_io = generate_daily(result_value, strategy, brand, seed)
    except Exception as exc:
        return Response(f'Invalid input: {exc}', status=400, mimetype='text/plain')
    return send_file(image_io, mimetype='image/png', as_attachment=True, download_name=make_filename('pcm_daily', result_value))


@app.route('/generate/weekly')
def generate_weekly_route():
    result_value = request.args.get('result', '0')
    strategy = request.args.get('strategy', 'Strategy 3').strip() or 'Strategy 3'
    brand = request.args.get('brand', 'PCM Trading').strip() or 'PCM Trading'
    period_label = request.args.get('period_label', 'Weekly Performance').strip() or 'Weekly Performance'
    seed = request.args.get('seed', '').strip() or None
    try:
        image_io = generate_weekly(result_value, strategy, brand, period_label, seed)
    except Exception as exc:
        return Response(f'Invalid input: {exc}', status=400, mimetype='text/plain')
    return send_file(image_io, mimetype='image/png', as_attachment=True, download_name=make_filename('pcm_weekly', result_value))


@app.route('/generate/monthly')
def generate_monthly_route():
    result_value = request.args.get('result', '0')
    strategy = request.args.get('strategy', 'Strategy 3').strip() or 'Strategy 3'
    brand = request.args.get('brand', 'PCM Trading').strip() or 'PCM Trading'
    period_label = request.args.get('period_label', 'Monthly Performance').strip() or 'Monthly Performance'
    trades = request.args.get('trades', '0').strip() or '0'
    win_rate = request.args.get('win_rate', '0').strip() or '0'
    drawdown = request.args.get('drawdown', '0').strip() or '0'
    seed = request.args.get('seed', '').strip() or None
    try:
        image_io = generate_monthly(result_value, strategy, brand, period_label, trades, win_rate, drawdown, seed)
    except Exception as exc:
        return Response(f'Invalid input: {exc}', status=400, mimetype='text/plain')
    return send_file(image_io, mimetype='image/png', as_attachment=True, download_name=make_filename('pcm_monthly', result_value))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
