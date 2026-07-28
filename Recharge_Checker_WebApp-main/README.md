# DishHome Renew Recharge Analytics — Django (shared) version

This is the same dashboard/report tool you had before, rebuilt so the
report is stored in a shared MySQL database instead of your browser's
local storage. Whoever uploads the CSVs is the "publisher" — everyone
else who opens the same URL sees that exact report immediately, with no
upload needed on their side.

## How it works

- You upload the Churn CSV + Revenue CSV, same as before. The matching
  logic (48-hour upgrade rule, period detection, fiscal year, etc.) all
  still runs in your browser, unchanged.
- Once processed, the browser sends the result to `POST /api/save-report/`,
  which replaces the shared report in the database.
- Every page load calls `GET /api/get-report/` to pull the current shared
  report — so any PC on the same URL sees your latest upload.
- Snapshots (📸 Save Snapshot) work the same way — they're saved
  server-side (Snapshot model) instead of `localStorage`.
- A basic login screen protects the app (Django's built-in auth) — you
  create user accounts for your team; there's no self-signup.

## 1. Requirements

- Python 3.10+
- MySQL server (your existing Docker MySQL setup works fine) — or swap
  the `DATABASES` block in `dishhome_webapp/settings.py` for
  PostgreSQL/SQLite if you'd rather use something else.

## 2. Setup

```bash
# from inside this project folder
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Create the database and a MySQL user (adjust names/password as you like):

```sql
CREATE DATABASE dishhome_reports CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'dishhome_user'@'%' IDENTIFIED BY 'change-me';
GRANT ALL PRIVILEGES ON dishhome_reports.* TO 'dishhome_user'@'%';
FLUSH PRIVILEGES;
```

Tell Django how to reach it — either edit the defaults directly in
`dishhome_webapp/settings.py`, or set environment variables before
running the server:

```bash
export DB_NAME=dishhome_reports
export DB_USER=dishhome_user
export DB_PASSWORD=change-me
export DB_HOST=localhost
export DB_PORT=3306
export DJANGO_SECRET_KEY="pick-a-long-random-string"
export DJANGO_DEBUG=True                 # set to False once it's live
export DJANGO_ALLOWED_HOSTS="*"          # e.g. "192.168.1.50,report.dishhome.local" in production
```

Run migrations and create your first login:

```bash
python manage.py migrate
python manage.py createsuperuser   # this becomes a login for the report app too
```

You can create more team logins the same way (`createsuperuser`), or via
`/admin/` once one account exists.

## 3. Run it

For a quick test on your own network:

```bash
python manage.py runserver 0.0.0.0:8000
```

Find your PC's LAN IP (`ipconfig` on Windows / `ip addr` on Linux) —
say it's `192.168.1.50` — then anyone on the same network/office WiFi
can open:

```
http://192.168.1.50:8000/
```

They'll hit the login screen, log in with an account you created, and
see the same shared report you uploaded.

## 4. Going to production

`runserver` is fine for testing but not for real deployment. For a
proper always-on setup:

- Run it behind **Gunicorn** + **Nginx** (standard Django deployment —
  same pattern you'd use for a Laravel app behind PHP-FPM + Nginx).
- Set `DJANGO_DEBUG=False` and a real `DJANGO_ALLOWED_HOSTS`.
- Put it behind HTTPS (Let's Encrypt via Nginx / Certbot is the usual
  route) and uncomment the `SESSION_COOKIE_SECURE` /
  `CSRF_COOKIE_SECURE` lines at the bottom of `settings.py`.
- If you want it reachable from outside your office network, you'll
  need a public server (a small VPS works fine) or port-forwarding +
  dynamic DNS if you're hosting from your own machine.

## 5. Project layout

```
django_webapp/
  manage.py
  requirements.txt
  dishhome_webapp/        # project settings, URLs
  reports/
    models.py              # Renewal, ReportMeta, Snapshot
    views.py                # login + JSON API + dashboard page
    urls.py
    templates/reports/
      index.html            # the dashboard (same UI as before)
      login.html
```

## 6. Notes / limits

- The `Renewal` table always reflects the *latest* upload — uploading
  again fully replaces it (same "whole report replace" behavior as
  before, just centralized). Snapshots are the way to keep history.
- There's no per-manager permission system — every logged-in user sees
  the same shared report and can upload/overwrite it. If you need
  read-only accounts later, that's a small addition to `views.py`.
- CSV upload + churn/revenue matching still happens in the browser —
  the server only stores the *result*, so file size limits are
  whatever your browser can handle (same as before).
