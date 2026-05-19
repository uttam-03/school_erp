# EduCore ERP - School Management System

## LOCAL pe Chalana (VS Code)

### Step 1: .env file banao
```
.env.example → copy karo → naam do ".env"
```
`.env` mein sirf ye change karo:
```
SECRET_KEY=koi-bhi-50-character-random-string
DEBUG=True
```
DATABASE_URL khali chhodo — SQLite automatically use hoga ✅

### Step 2: Packages install karo
```bash
pip install -r requirements.txt
```

### Step 3: Database setup karo
```bash
python manage.py migrate
python manage.py create_admin
python manage.py load_timeslots
```

### Step 4: Server chalao
```bash
python manage.py runserver
```

### Step 5: Login karo
```
URL      → http://127.0.0.1:8000/accounts/login/
Email    → admin@school.com
Password → Admin@123456
```

---

## RENDER pe Deploy karna (Live Website)

### Step 1: GitHub pe code push karo
```bash
git init
git add .
git commit -m "EduCore ERP"
git remote add origin https://github.com/USERNAME/school-erp.git
git push -u origin main
```

### Step 2: Render pe PostgreSQL Database banao
1. [render.com](https://render.com) → New → **PostgreSQL**
2. Name: `school-erp-db`
3. Region: Singapore
4. Plan: **Free**
5. Create Database
6. **"Internal Database URL"** copy karo

### Step 3: Render pe Web Service banao
1. New → **Web Service**
2. GitHub repo connect karo
3. Settings:
   - Build Command: `./build.sh`
   - Start Command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`

### Step 4: Environment Variables set karo
| Key | Value |
|-----|-------|
| `DATABASE_URL` | Step 2 mein copy kiya hua URL |
| `SECRET_KEY` | koi bhi random 50 char string |
| `DEBUG` | `False` |
| `RENDER_EXTERNAL_HOSTNAME` | `yourapp.onrender.com` |

### Step 5: Deploy!
Render automatically:
- Dependencies install karega
- Migrations chalayega
- Admin user banayega (admin@school.com / Admin@123456)

---

## Default Login
| Role | Email | Password |
|------|-------|----------|
| Superuser/Admin | admin@school.com | Admin@123456 |

**Note: Pehle login ke baad password zaroor change karo!**

---

## How it Works

```
Local PC          →  SQLite (db.sqlite3 file)  — kuch install nahi
Render (Live)     →  PostgreSQL (cloud)         — free, permanent
```

Same code — alag database — automatically detect hota hai!
