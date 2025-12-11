# Phase 1 Quick Start Guide

## 🚀 Quick Setup Commands

```powershell
# 1. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file (edit with your credentials)
# Copy example below and save as .env

# 4. Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 5. Run application
flask run
```

---

## 📋 Important Table Names

**DO NOT use these existing table names:**
- `accounts` (exists in imageToCode project)
- `user` (exists in database)

**USE these new table names:**
- `tutorial_users` ✅
- `tutorials` ✅
- `tutorial_password_resets` ✅
- `tutorial_enrollments` (Phase 3)
- `tutorial_orders` (Phase 3)
- `tutorial_lessons` (Phase 2)

---

## 🔑 .env Template

```env
SECRET_KEY=change-this-to-random-secure-key
FLASK_APP=app.py
FLASK_ENV=development

SSH_HOST=ssh.pythonanywhere.com
SSH_USERNAME=byambaa1982
SSH_PASSWORD=your-ssh-password
DB_HOST=byambaa1982.mysql.pythonanywhere-services.com
DB_USER=byambaa1982
DB_PASSWORD=your-mysql-password
DB_NAME=byambaa1982$codemirror

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@tutorial-ecommerce.com
```

---

## 📁 Key Files to Create

1. **Configuration:**
   - `config.py` - SSH tunnel + database connection
   - `requirements.txt` - Dependencies
   - `.env` - Environment variables (SECRET!)
   - `.gitignore` - Git ignore rules

2. **Application:**
   - `app.py` - Entry point
   - `app/__init__.py` - App factory
   - `app/extensions.py` - Flask extensions
   - `app/models.py` - Database models

3. **Authentication:**
   - `app/auth/__init__.py`
   - `app/auth/routes.py` - Login, register, reset
   - `app/auth/forms.py` - WTForms
   - `app/auth/utils.py` - Email utilities

4. **Main Pages:**
   - `app/main/__init__.py`
   - `app/main/routes.py` - Home, about

5. **Templates:**
   - `app/templates/base.html`
   - `app/templates/index.html`
   - `app/templates/auth/login.html`
   - `app/templates/auth/register.html`
   - `app/templates/auth/request_reset.html`
   - `app/templates/auth/reset_password.html`

---

## 🧪 Testing Checklist

- [ ] SSH tunnel connects successfully
- [ ] Database tables created (check with `SHOW TABLES LIKE 'tutorial_%';`)
- [ ] Homepage loads at http://localhost:5000
- [ ] User registration works
- [ ] User login works
- [ ] User logout works
- [ ] Password reset request works
- [ ] Failed login locks account after 5 attempts
- [ ] Flash messages display correctly
- [ ] Mobile responsive design works

---

## 🔍 Database Connection

**Local Development:**
```
SSH Tunnel → PythonAnywhere MySQL
localhost:XXXXX → byambaa1982.mysql.pythonanywhere-services.com:3306
```

**On PythonAnywhere:**
```
Direct Connection → MySQL
byambaa1982.mysql.pythonanywhere-services.com:3306
```

---

## ⚠️ Common Mistakes to Avoid

1. **Don't use existing table names** - Use `tutorial_` prefix
2. **Don't commit .env file** - Add to .gitignore
3. **Don't skip migrations** - Always run `flask db migrate` and `flask db upgrade`
4. **Don't forget {{ form.hidden_tag() }}** - Required in all forms for CSRF
5. **Don't test on production database first** - Always test locally

---

## 📊 SQL Verification Commands

```sql
-- Show all tutorial tables
SHOW TABLES LIKE 'tutorial_%';

-- Check tutorial_users structure
DESCRIBE tutorial_users;

-- View registered users
SELECT id, email, username, is_active, created_at 
FROM tutorial_users 
ORDER BY created_at DESC;

-- Check if email exists (before registration)
SELECT email FROM tutorial_users WHERE email = 'test@example.com';

-- Count users
SELECT COUNT(*) as total_users FROM tutorial_users;
```

---

## 🎯 Phase 1 Deliverables

✅ Flask app running with SSH tunnel  
✅ MySQL database connected  
✅ User registration with validation  
✅ User login with account locking  
✅ Password reset flow  
✅ Responsive templates with Tailwind  
✅ Flash messaging system  
✅ CSRF protection  

---

## 🔜 Next: Phase 2

Once Phase 1 is complete:
1. Admin course management
2. Course catalog with filtering
3. Course detail pages
4. Search functionality

See `TUTORIAL_ECOMMERCE_PROJECT_PLAN.md` for Phase 2 details.
