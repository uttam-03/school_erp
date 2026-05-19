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

