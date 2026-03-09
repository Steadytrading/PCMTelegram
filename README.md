# PCM Trading Generator V2

Telegram-ready image generator for PCM Trading, built for GitHub + Render.

## What it does

- Generates a **daily** result poster in 1080x1350 PNG
- Generates a **weekly** result poster in 1080x1350 PNG
- Generates a **monthly** performance poster in 1080x1350 PNG
- Uses 5 randomized profit texts and 5 randomized loss texts for daily posts
- Randomizes badges for variation
- Uses your selected PCM logo
- Returns the PNG as a **downloaded file automatically** in the browser

## Local run

```bash
pip install -r requirements.txt
python app.py
```

Open:

```bash
http://127.0.0.1:5000/
```

## Render deploy

1. Push this folder to a GitHub repo.
2. In Render, create a new **Web Service** from the repo.
3. Render should detect `render.yaml` automatically.
4. If needed, use these values manually:

```bash
Build Command: pip install -r requirements.txt
Start Command: gunicorn --bind 0.0.0.0:$PORT app:app
```

## Example URLs

### Daily

```text
/generate?result=3.74&strategy=Strategy%203&brand=PCM%20Trading&seed=2026-03-09
```

### Weekly

```text
/generate/weekly?result=10.60&period_label=Weekly%20Performance&strategy=Strategy%203&brand=PCM%20Trading&seed=2026-week-10
```

### Monthly

```text
/generate/monthly?result=12.40&period_label=Monthly%20Performance&trades=42&win_rate=68&drawdown=3.10&strategy=Strategy%203&brand=PCM%20Trading&seed=2026-03
```

## Notes

- Use a fixed `seed` if you want the same random text and badge for the same day, week, or month.
- The PNG is returned with `as_attachment=True`, so it downloads instead of opening inline.
