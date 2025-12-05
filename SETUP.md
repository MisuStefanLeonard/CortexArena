# Mind Arena - Detailed Setup Guide

A complete guide to set up Mind Arena on your local machine.

## Prerequisites

- **Python 3.13+** - [Download here](https://www.python.org/downloads/)
- **PostgreSQL 12+** - [Download here](https://www.postgresql.org/download/)
- **Git** - [Download here](https://git-scm.com/)
- **pip** - Usually comes with Python

### Verify Installation

```bash
python --version
psql --version
git --version
```

## Step 1: Database Setup

### Windows

1. Install PostgreSQL and remember your password
2. Open Command Prompt and create database:
   ```bash
   psql -U postgres
   CREATE DATABASE mindarena;
   CREATE USER mindarena_user WITH PASSWORD 'your_secure_password';
   ALTER ROLE mindarena_user SET client_encoding TO 'utf8';
   ALTER ROLE mindarena_user SET default_transaction_isolation TO 'read committed';
   ALTER ROLE mindarena_user SET default_transaction_deferrable TO on;
   ALTER ROLE mindarena_user SET default_transaction_level TO 'read committed';
   GRANT ALL PRIVILEGES ON DATABASE mindarena TO mindarena_user;
   \q
   ```

### macOS

```bash
# Install PostgreSQL via Homebrew
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb mindarena
psql -d mindarena -c "CREATE USER mindarena_user WITH PASSWORD 'your_secure_password';"
psql -d mindarena -c "GRANT ALL PRIVILEGES ON DATABASE mindarena TO mindarena_user;"
```

### Linux (Ubuntu/Debian)

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE mindarena;
CREATE USER mindarena_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE mindarena TO mindarena_user;
\q
```

## Step 2: Clone Repository

```bash
git clone https://github.com/yourusername/mind-arena.git
cd mind-arena
```

## Step 3: Create Virtual Environment

### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

## Step 4: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# (Optional) Install development dependencies
pip install -r requirements-dev.txt
```

## Step 5: Configure Environment

Create a `.env` file in the project root:

```env
# Django
DEBUG=True
SECRET_KEY=your-very-secret-key-here-generate-new-for-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://mindarena_user:your_secure_password@localhost/mindarena

# Email (Optional - for password reset)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Generate SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Step 6: Update Settings

Edit `arena/settings.py`:

```python
# Load environment variables
from decouple import config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mindarena',
        'USER': 'mindarena_user',
        'PASSWORD': 'your_secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Or use DATABASE_URL from .env
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}
```

## Step 7: Apply Migrations

```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate
```

## Step 8: Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts:
- Username: `admin`
- Email: `your-email@example.com`
- Password: `your-secure-password`

## Step 9: Create Test Data (Optional)

```bash
python manage.py shell
```

```python
from core.models import GameType, Game

# Create game types
memory_type, _ = GameType.objects.get_or_create(name='Memory')
reaction_type, _ = GameType.objects.get_or_create(name='Reaction')
logic_type, _ = GameType.objects.get_or_create(name='Logic')
attention_type, _ = GameType.objects.get_or_create(name='Attention')

print("Game types created!")
exit()
```

## Step 10: Run Development Server

```bash
python manage.py runserver
```

Visit: `http://localhost:8000`

### Access Admin Panel
Visit: `http://localhost:8000/admin`
Login with superuser credentials

## Step 11: Create Test Account

1. Go to `http://localhost:8000/register/`
2. Fill in the form:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `TestPassword123!`
3. Click Register
4. You'll be automatically logged in and redirected to home

## Troubleshooting

### Database Connection Error

**Error**: `FATAL: Ident authentication failed for user "mindarena_user"`

**Solution**: Use password authentication in `pg_hba.conf`
```bash
# Find pg_hba.conf location
psql -U postgres -c "SHOW hba_file;"

# Edit and change 'ident' to 'md5' or 'password'
```

### Port Already in Use

**Error**: `Address already in use`

**Solution**: Run on different port
```bash
python manage.py runserver 8001
```

### Static Files Not Loading

**Error**: CSS/JavaScript not loading

**Solution**: Collect static files
```bash
python manage.py collectstatic
```

### Migration Issues

**Error**: Migration conflicts

**Solution**: Reset database (for development only!)
```bash
# Drop all tables
python manage.py migrate zero

# Reapply all migrations
python manage.py migrate
```

### Virtual Environment Issues

**Error**: Commands not found or wrong Python version

**Solution**: Verify virtual environment is activated
```bash
which python  # Should show venv path
python --version  # Should show 3.13+
```

## Common Commands

### Run Tests
```bash
python manage.py test
```

### Create Django App
```bash
python manage.py startapp appname
```

### Django Shell
```bash
python manage.py shell
```

### Check System Health
```bash
python manage.py check
```

### Format Code
```bash
black .
```

### Run Linter
```bash
flake8 .
```

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `False` |
| `SECRET_KEY` | Django secret | Required |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost` |
| `DATABASE_URL` | Database connection | Required |
| `EMAIL_BACKEND` | Email service | Console |

## Production Setup

For production deployment, see [DEPLOYMENT.md](DEPLOYMENT.md)

## Docker Setup (Alternative)

```bash
docker build -t mind-arena .
docker run -p 8000:8000 mind-arena
```

## Next Steps

1. ✅ Register an account at `/register/`
2. ✅ Play some games
3. ✅ Check `/stats/` for performance
4. ✅ Explore `/begin/` adventure
5. ✅ View admin panel at `/admin/`

## Getting Help

- Check README.md for overview
- Review CONTRIBUTING.md for development guidelines
- Check troubleshooting section above
- Open an issue on GitHub

---

**Happy coding! 🚀**
