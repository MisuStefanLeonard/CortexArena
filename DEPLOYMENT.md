# Mind Arena - Production Deployment Guide

Complete guide for deploying Mind Arena to production.

## Pre-Deployment Checklist

- [ ] All tests pass locally
- [ ] Code reviewed and merged to main branch
- [ ] Environment variables configured
- [ ] Database backups in place
- [ ] Static files collected
- [ ] HTTPS certificate ready
- [ ] Domain configured
- [ ] Email service configured

## Deployment Options

### 1. Heroku Deployment

#### Prerequisites
- Heroku account
- Heroku CLI installed

#### Steps

```bash
# Login to Heroku
heroku login

# Create app
heroku create mind-arena-production

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:standard-0

# Set environment variables
heroku config:set \
  DEBUG=False \
  SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())") \
  ALLOWED_HOSTS=mind-arena-production.herokuapp.com

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser

# View logs
heroku logs --tail
```

### 2. AWS Deployment

#### EC2 Setup

```bash
# Launch EC2 instance (Ubuntu 22.04 LTS)
# SSH into instance

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y \
  python3.13 \
  python3-pip \
  postgresql \
  postgresql-contrib \
  nginx \
  supervisor \
  git

# Create app directory
sudo mkdir -p /var/www/mind-arena
sudo chown $USER:$USER /var/www/mind-arena
cd /var/www/mind-arena

# Clone repository
git clone https://github.com/yourusername/mind-arena.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Configure database
sudo -u postgres psql
CREATE DATABASE mindarena_prod;
CREATE USER mindarena_prod WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE mindarena_prod TO mindarena_prod;
\q

# Create .env file
cat > .env << EOF
DEBUG=False
SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
DATABASE_URL=postgresql://mindarena_prod:strong_password@localhost/mindarena_prod
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
EOF

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Configure Gunicorn
sudo tee /etc/supervisor/conf.d/mind-arena.conf << EOF
[program:mind-arena]
command=/var/www/mind-arena/venv/bin/gunicorn \
  --workers 3 \
  --bind 127.0.0.1:8000 \
  arena.wsgi:application
directory=/var/www/mind-arena
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/mind-arena.log
EOF

# Start supervisor
sudo systemctl restart supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Configure Nginx
sudo tee /etc/nginx/sites-available/mind-arena << 'EOF'
upstream mind_arena {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://mind_arena;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/mind-arena/staticfiles/;
    }

    location /media/ {
        alias /var/www/mind-arena/media/;
    }
}
EOF

# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/mind-arena /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Setup SSL with Certbot
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 3. DigitalOcean Deployment

```bash
# Create App Platform app
doctl apps create --spec app.yaml

# Or use Docker
docker build -t mind-arena:latest .
docker tag mind-arena:latest registry.digitalocean.com/yourusername/mind-arena:latest
docker push registry.digitalocean.com/yourusername/mind-arena:latest
```

### 4. Docker Deployment

```bash
# Build image
docker build -t mind-arena:latest .

# Push to registry
docker tag mind-arena:latest yourusername/mind-arena:latest
docker push yourusername/mind-arena:latest

# Deploy with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

## Post-Deployment

### 1. Verify Installation

```bash
# Check application
curl https://yourdomain.com

# Check admin panel
curl https://yourdomain.com/admin

# Check health
python manage.py check --deploy
```

### 2. Configure Logging

```bash
# Django logging configuration in settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/errors.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

### 3. Setup Backups

```bash
# Daily database backup
0 2 * * * pg_dump mindarena_prod | gzip > /backups/db-$(date +\%Y\%m\%d).sql.gz

# Upload to cloud storage
0 3 * * * aws s3 sync /backups s3://your-backup-bucket/
```

### 4. Monitor Application

- Setup error tracking (Sentry)
- Configure log aggregation (ELK Stack)
- Setup uptime monitoring (Uptime Robot)
- Configure alerts

## Production Settings

Update `arena/settings.py`:

```python
# Security
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECRET_KEY = os.environ.get('SECRET_KEY')

# SSL/TLS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
}

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
```

## Scaling Considerations

### Database Optimization
- Enable query caching
- Index frequently queried fields
- Archive old sessions/stats

### Application Scaling
- Load balance across multiple servers
- Use CDN for static files
- Implement caching layer (Redis)

### Performance Monitoring
- Monitor CPU/Memory usage
- Track database query times
- Monitor API response times

## Troubleshooting

### 502 Bad Gateway
```bash
# Check Gunicorn
sudo supervisorctl status mind-arena

# Check logs
sudo tail -f /var/log/mind-arena.log

# Restart
sudo supervisorctl restart mind-arena
```

### Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic --noinput --clear
```

### Database Connection Issues
```bash
# Test connection
psql postgresql://user:password@host/database

# Check Django connection
python manage.py dbshell
```

## Security Hardening

- [ ] Enable HTTPS/SSL
- [ ] Configure firewall
- [ ] Setup fail2ban
- [ ] Enable database encryption
- [ ] Configure security headers
- [ ] Enable CSRF protection
- [ ] Use strong SECRET_KEY
- [ ] Regularly update dependencies
- [ ] Setup vulnerability scanning
- [ ] Configure rate limiting

## Maintenance

### Regular Tasks
- Monitor logs daily
- Check disk space weekly
- Update dependencies monthly
- Review security patches immediately
- Backup database daily

### Upgrade Process
1. Test on staging environment
2. Backup production database
3. Deploy to production
4. Run migrations: `python manage.py migrate`
5. Collect static: `python manage.py collectstatic`
6. Restart application
7. Monitor for issues

## Support

For deployment issues:
- Check application logs
- Review Django documentation
- Open issue on GitHub
- Contact deployment platform support

---

**Last Updated**: December 2025
