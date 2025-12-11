# Phase 6 Quick Start Guide - SQL Practice Environment

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Dependencies

```powershell
pip install mysql-connector-python==8.2.0
```

### Step 2: Build SQL Sandbox Docker Image

```powershell
cd sandbox\sql
docker build -t sql_sandbox:latest .
cd ..\..
```

### Step 3: Run Database Migration

```powershell
python migrate_phase6.py
```

### Step 4: Add Sample SQL Exercises (Optional)

```powershell
python add_sample_sql_exercises.py
```

### Step 5: Start the Application

```powershell
python app.py
```

## 🎯 Feature Access

### SQL Practice Editor
**URL:** `http://localhost:5000/sql-practice/editor`

**Features:**
- Write and execute SQL queries
- Browse database schema
- Preview table data
- Reset database

**Sample Query:**
```sql
SELECT first_name, last_name, salary 
FROM employees 
WHERE salary > 80000 
ORDER BY salary DESC;
```

### SQL Challenges
**URL:** `http://localhost:5000/sql-practice/challenges`

**Features:**
- View all SQL exercises
- Filter by difficulty (Easy, Medium, Hard)
- Track completed challenges
- Earn points

### Database Schema Viewer
**URL:** `http://localhost:5000/sql-practice/schema-viewer`

**Features:**
- View all tables and columns
- See data types and constraints
- Understand table relationships

## 📊 Sample Database Tables

The sandbox includes these pre-populated tables:

### 1. Employees
- 10 employee records
- Fields: id, first_name, last_name, email, department, salary, hire_date

### 2. Departments
- 5 departments
- Fields: id, name, location, manager_id, budget

### 3. Projects
- 5 active projects
- Fields: id, name, description, department_id, start_date, end_date, status

### 4. Employee_Projects (Many-to-Many)
- Employee-Project assignments
- Fields: employee_id, project_id, role, assigned_date

### 5. Customers
- 5 customer records
- Fields: id, first_name, last_name, email, phone, city, country

### 6. Products
- 10 products
- Fields: id, name, description, category, price, stock_quantity

### 7. Orders
- 5 orders
- Fields: id, customer_id, order_date, total_amount, status

### 8. Order_Items
- Order line items
- Fields: id, order_id, product_id, quantity, price

## 🎓 Try These Sample Queries

### Easy Queries

**1. List all employees:**
```sql
SELECT * FROM employees;
```

**2. Find employees in Engineering:**
```sql
SELECT first_name, last_name, salary 
FROM employees 
WHERE department = 'Engineering';
```

**3. Count employees:**
```sql
SELECT COUNT(*) as total_employees FROM employees;
```

### Medium Queries

**4. Average salary by department:**
```sql
SELECT department, ROUND(AVG(salary), 2) as avg_salary
FROM employees
GROUP BY department
ORDER BY avg_salary DESC;
```

**5. Employees hired after 2020:**
```sql
SELECT first_name, last_name, hire_date
FROM employees
WHERE YEAR(hire_date) >= 2020
ORDER BY hire_date;
```

### Hard Queries

**6. Employee project assignments:**
```sql
SELECT 
    e.first_name, 
    e.last_name, 
    p.name as project_name,
    ep.role
FROM employees e
INNER JOIN employee_projects ep ON e.id = ep.employee_id
INNER JOIN projects p ON ep.project_id = p.id;
```

**7. Order totals with customer info:**
```sql
SELECT 
    c.first_name,
    c.last_name,
    o.order_date,
    o.total_amount,
    o.status
FROM orders o
INNER JOIN customers c ON o.customer_id = c.id
ORDER BY o.total_amount DESC;
```

## 🔍 Troubleshooting

### Issue: Docker image build fails
**Solution:** Ensure Docker Desktop is running
```powershell
docker ps  # Should list running containers
```

### Issue: MySQL container won't start
**Solution:** Check port 3306 availability
```powershell
netstat -an | findstr 3306
```

### Issue: Query execution timeout
**Solution:** Queries are limited to 30 seconds. Simplify complex queries.

### Issue: Container cleanup not working
**Solution:** Manually remove old containers
```powershell
docker ps -a | findstr sql_sandbox
docker rm -f <container_id>
```

### Issue: Schema not loading
**Solution:** Reset the sandbox
- Click "Reset Database" button in editor
- Or restart container manually

## 📝 Exercise Completion Tips

1. **Read the Description Carefully:** Understand what's being asked
2. **Start with Starter Code:** Use provided templates
3. **Test Before Submitting:** Use "Test Query" button
4. **Use Hints:** Click "Show Hints" if stuck
5. **Check Schema:** Review table structures
6. **Validate Results:** Ensure column names and order match

## 🎯 Points System

- **Easy Exercises:** 10-15 points
- **Medium Exercises:** 20-25 points
- **Hard Exercises:** 30-40 points

## 🔐 Security Notes

### Allowed Operations:
- ✅ SELECT queries
- ✅ Aggregate functions (COUNT, AVG, SUM, etc.)
- ✅ JOINs (INNER, LEFT, RIGHT)
- ✅ GROUP BY, ORDER BY
- ✅ HAVING clauses

### Blocked Operations:
- ❌ DROP (tables, databases)
- ❌ TRUNCATE
- ❌ ALTER (schema changes)
- ❌ CREATE (new tables)
- ❌ GRANT, REVOKE (permissions)

### DML Operations (Exercise-Specific):
- INSERT, UPDATE, DELETE (only when explicitly allowed)

## 🎉 What's Next?

After completing Phase 6, you can:

1. **Complete SQL Exercises:** Practice with 7 sample exercises
2. **Explore Advanced Queries:** Try complex JOINs and subqueries
3. **Create Your Own Exercises:** Use admin panel to add exercises
4. **Move to Phase 7:** User Dashboard & Analytics

## 💡 Pro Tips

1. **Use Table Aliases:** Makes queries cleaner
   ```sql
   SELECT e.name, d.name 
   FROM employees e 
   JOIN departments d ON e.dept_id = d.id
   ```

2. **Format Your Queries:** Use proper indentation
   ```sql
   SELECT 
       first_name,
       last_name,
       salary
   FROM employees
   WHERE salary > 80000
   ORDER BY salary DESC;
   ```

3. **Preview Tables First:** Click table names in schema browser
4. **Save Common Queries:** Copy successful queries to a notepad
5. **Learn from Solutions:** Review solution code after completion

## 📚 Learning Resources

- **SQL Tutorial:** Complete in-course lessons
- **W3Schools SQL:** https://www.w3schools.com/sql/
- **MySQL Documentation:** https://dev.mysql.com/doc/
- **SQL Practice:** Use the editor to experiment freely

## ✅ Completion Checklist

Before moving to Phase 7, ensure:

- [ ] Docker image built successfully
- [ ] Migration completed without errors
- [ ] Can access SQL editor
- [ ] Can execute queries and see results
- [ ] Schema browser loads tables
- [ ] Database reset works
- [ ] Can access SQL challenges page
- [ ] Sample exercises are available
- [ ] Exercise submission works
- [ ] Feedback displays correctly

---

**Need Help?** Check the full implementation guide in `PHASE6_IMPLEMENTATION_COMPLETE.md`

**Ready for more?** Proceed to Phase 7: User Dashboard & Analytics
