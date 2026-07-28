# Deploying to a VPS (accessible from anywhere, not just your office)

This gets you a real public URL — `https://report.yourdomain.com` (or
just `https://<vps-ip>`) — that works from home, another city, wherever,
as long as there's internet.

## 0. What you need

- A VPS: any Ubuntu 22.04 droplet/instance works — DigitalOcean, Vultr,
  Hetzner, AWS Lightsail, or a local Nepali VPS provider. The cheapest
  tier (1 vCPU / 1GB RAM) is plenty for this app.
- (Optional but recommended) A domain name pointed at the VPS's IP —
  e.g. `report.yourdomain.com` → A record → VPS IP. You can skip this
  and use the raw IP, but then you can't get a free HTTPS certificate
  from Let's Encrypt (it needs a domain).

## 1. Basic server setup

SSH into the VPS, then:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-pip python3-dev \
    build-essential default-libmysqlclient-dev pkg-config \
    nginx mysql-server git
```

Secure MySQL and create the database (same as your local setup):

```bash
sudo mysql_secure_installation

sudo mysql -u root -p
```
```sql
CREATE DATABASE dishhome_reports CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'dishhome_user'@'localhost' IDENTIFIED BY 'change-me';
GRANT ALL PRIVILEGES ON dishhome_reports.* TO 'dishhome_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## 2. Get the project onto the server

Simplest: `scp` the whole `django_webapp` folder up, or push it to a
private Git repo and clone it. Either way, put it at `/opt/dishhome_webapp`:

```bash
sudo mkdir -p /opt/dishhome_webapp
sudo chown $USER:$USER /opt/dishhome_webapp
# then scp/git clone the contents of django_webapp/ into /opt/dishhome_webapp
```

## 3. Python environment

```bash
cd /opt/dishhome_webapp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

## 4. Environment config

```bash
cp deploy/.env.example .env
nano .env    # fill in DJANGO_SECRET_KEY, your domain, DB password, etc.
```

Load it and run migrations:

```bash
set -a; source .env; set +a
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 5. Gunicorn as a background service

```bash
sudo cp deploy/gunicorn.service /etc/systemd/system/dishhome_webapp.service
sudo nano /etc/systemd/system/dishhome_webapp.service   # confirm paths match /opt/dishhome_webapp

sudo systemctl daemon-reload
sudo systemctl enable dishhome_webapp
sudo systemctl start dishhome_webapp
sudo systemctl status dishhome_webapp   # should say "active (running)"
```

This keeps the app running permanently, restarts it on crash, and
starts it automatically if the VPS reboots — no PC of yours needs to
stay on.

## 6. Nginx in front of it

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/dishhome_webapp
sudo nano /etc/nginx/sites-available/dishhome_webapp   # set server_name to your domain (or VPS IP)

sudo ln -s /etc/nginx/sites-available/dishhome_webapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

At this point `http://your-domain-or-ip` should already load the login
page.

## 7. HTTPS (only possible with a real domain)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d report.yourdomain.com
```

Certbot edits the Nginx config for you and sets up auto-renewal. Now
`https://report.yourdomain.com` works from anywhere — home, another
city, mobile data, all of it.

## 8. Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## Day-to-day after this

- Anyone on your team just opens `https://report.yourdomain.com`,
  logs in, and sees the shared report.
- To deploy an update later: pull/copy the new files into
  `/opt/dishhome_webapp`, then `sudo systemctl restart dishhome_webapp`.
- Logs if something looks wrong: `sudo journalctl -u dishhome_webapp -f`
