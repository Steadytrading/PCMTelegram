# PCM Trading Result Generator

Telegram-ready daily result image generator for PCM Trading.

## Features

- 1080x1350 PNG output
- Profit / loss layout with random text variation
- Random badge variation
- Uses your PCM logo
- Ready for GitHub + Render

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
4. If needed, use:

```bash
Build Command: pip install -r requirements.txt
Start Command: gunicorn --bind 0.0.0.0:$PORT app:app
```

## URL usage

Example:

```text
/generate?result=3.74&strategy=Strategy%203&brand=PCM%20Trading&date_label=March%209,%202026&seed=2026-03-09
```

Use a fixed `seed` value for the day if you want the same random text/badge every time you generate that specific day.
