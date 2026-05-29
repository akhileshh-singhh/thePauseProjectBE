# The Pause Project — Django API (PostgreSQL)

REST API for workshops, gallery, testimonials, site settings, and contact messages.

## 1. Configure database

Preferred setup is PostgreSQL using `DATABASE_URL`.

Set in `backend/.env`:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME
DB_SSL_REQUIRE=true
USE_SQLITE=false
```

For local Postgres without SSL:

```env
DB_SSL_REQUIRE=false
```

MySQL fallback still works when `DATABASE_URL` is not set.

## 2. Configure backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` for MySQL (matches Docker Compose defaults):

```env
USE_SQLITE=false
MYSQL_DATABASE=pause_project
MYSQL_USER=pause
MYSQL_PASSWORD=pausepass
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
```

For quick dev **without** MySQL, set `USE_SQLITE=true`.

## 3. Migrate & seed

```bash
python manage.py migrate
python manage.py seed_from_json --clear
python manage.py createsuperuser
python manage.py runserver
```

## 4. Connect Next.js

In `the-pause-project/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api
```

```bash
cd ..
npm run dev
```

- Public site: http://localhost:3000 (refreshes from API every 60s)
- Admin UI: http://localhost:3000/admin/login
- Django admin: http://127.0.0.1:8000/django-admin/

## Event scheduling

Events use structured fields:

- `event_date` — calendar date (admin: date picker)
- `start_time` / `end_time` — session times (admin: time pickers)

The API formats these for the public site as e.g. `20 May 2026` and `4:00 PM – 7:00 PM`.
