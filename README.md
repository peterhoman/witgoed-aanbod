# WitgoedAanbod.nl

Modern affiliate website for comparing appliances (wasmachines, drogers, koelkasten, vaatwassers, magnetrons, ovens) with Bol.com integration.

## Features

✅ **Product Catalog** - Syncs from Bol.com API
✅ **AI Content** - Claude generates descriptions & meta tags
✅ **Auto Sync** - APScheduler runs every 6 hours
✅ **Modern Design** - 2027 trend, responsive, mobile-first
✅ **SEO Ready** - Sitemap, schema.org, canonical tags
✅ **Search & Filters** - Category, price range, availability
✅ **Legal Pages** - Privacy, affiliate disclaimer, cookies, T&C
✅ **Affiliate Links** - Automatic Bol.com partner tracking

## Tech Stack

- **Backend:** Python Flask
- **Database:** SQLite (PostgreSQL for production)
- **Frontend:** HTML/CSS/JavaScript (Responsive)
- **AI:** Claude API (Anthropic)
- **Sync:** Bol.com API + APScheduler
- **Hosting:** DigitalOcean App Platform
- **CI/CD:** GitHub + Auto-deploy

## Local Setup

### 1. Clone & Install

```bash
git clone <repo-url>
cd witgoed-aanbod
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add:
```
BOL_CLIENT_ID=your-bol-client-id
BOL_CLIENT_SECRET=your-bol-client-secret
BOL_PARTNER_ID=your-bol-partner-id
ANTHROPIC_API_KEY=your-claude-api-key
SITE_URL=http://localhost:5000
```

### 3. Initialize Database

```bash
python init_db.py
```

### 4. Run Development Server

```bash
python wsgi.py
```

Visit: http://localhost:5000

### 5. Manual Sync (Optional)

```bash
python sync_products.py
```

## Deployment (DigitalOcean)

### Prerequisites

- DigitalOcean account
- GitHub account with this repo
- TransIP domain (witgoedaanbod.nl)

### Steps

1. **Create DigitalOcean App:**
   - Go to DigitalOcean → Apps
   - Connect GitHub repo
   - Set environment variables (from .env)
   - Deploy

2. **Configure Domain:**
   - TransIP → DNS Settings
   - Point to DigitalOcean app
   - Update SITE_URL in DigitalOcean

3. **Database:**
   - Use DigitalOcean PostgreSQL (managed)
   - Update DATABASE_URL in .env

4. **First Sync:**
   - SSH into app: `doctl apps exec <app-id> /bin/bash`
   - Run: `python sync_products.py`

5. **Schedule Sync:**
   - APScheduler starts automatically
   - Runs every 6 hours

## Project Structure

```
witgoed-aanbod/
├── app.py              # Flask app factory
├── wsgi.py             # WSGI entry point
├── models.py           # Database models
├── config.py           # Config (dev/prod)
├── sync_products.py    # Bol.com sync script
├── ai_content.py       # Claude API integration
├── scheduler.py        # APScheduler config
├── init_db.py          # DB initialization
├── routes/
│   ├── main.py         # Homepage, categories
│   ├── products.py     # Product detail, search
│   ├── legal.py        # Legal pages
│   └── seo.py          # Sitemap, robots.txt
├── templates/          # HTML (Jinja2)
├── static/
│   ├── css/main.css
│   └── js/main.js
├── requirements.txt
├── Procfile
├── railway.toml
└── .env.example
```

## API Endpoints

- `GET /` - Homepage
- `GET /category/<slug>` - Category page
- `GET /product/<slug>` - Product detail
- `GET /search?q=...` - Search products
- `GET /api/categories` - Categories JSON
- `GET /sitemap.xml` - SEO sitemap
- `GET /robots.txt` - SEO robots file
- `GET /privacy` - Privacy policy
- `GET /disclaimer` - Affiliate disclaimer
- `GET /cookies` - Cookie policy
- `GET /voorwaarden` - Terms & conditions
- `GET /contact` - Contact form

## Environment Variables

Required (add to .env):

```
FLASK_ENV=production
SECRET_KEY=<random-secure-key>
DATABASE_URL=postgresql://...
BOL_CLIENT_ID=<from Bol.com Seller Center>
BOL_CLIENT_SECRET=<from Bol.com Seller Center>
BOL_PARTNER_ID=<from Bol.com Partner Program>
ANTHROPIC_API_KEY=<from Claude Console>
SITE_URL=https://witgoedaanbod.nl
SYNC_INTERVAL=6
```

## License

MIT License - See LICENSE file for details
