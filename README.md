# WitgoedAanbod.nl

Affiliate website for comparing appliances (wasmachines, drogers, koelkasten, etc.) on Bol.com.

## Setup

### 1. Clone & Install

```bash
git clone <repo-url>
cd witgoed-aanbod
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables

```bash
cp .env.example .env
# Edit .env and add your credentials:
# - BOL_CLIENT_ID
# - BOL_CLIENT_SECRET
# - BOL_PARTNER_ID
# - ANTHROPIC_API_KEY
```

### 3. Initialize Database

```bash
python init_db.py
```

### 4. Run Development Server

```bash
python app.py
```

Visit: http://localhost:5000

## Structure

```
witgoed-aanbod/
├── app.py              # Main Flask app
├── models.py           # Database models
├── config.py           # Configuration
├── routes/             # Blueprint routes
├── templates/          # HTML templates
├── static/             # CSS, JS, images
├── init_db.py          # Database initialization
├── requirements.txt    # Dependencies
└── README.md          # This file
```

## Features

- ✅ Product catalog from Bol.com
- ✅ Search & filtering (category, price)
- ✅ Product detail pages with SEO schema
- ✅ Responsive mobile design
- ✅ Affiliate disclaimer
- ✅ Legal pages (privacy, cookies, T&C)

## Next Steps

1. Get Bol.com API credentials
2. Build sync_products.py script
3. Integrate Claude API for AI content
4. Setup APScheduler for 6-hour sync
5. Deploy to DigitalOcean

## License

MIT License - see LICENSE file
