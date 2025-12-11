"""
Sample SQL Exercise Creator
Creates sample SQL exercises for testing
"""

from app import create_app
from app.extensions import db
from app.models import Exercise, NewTutorial, Lesson
import json
from slugify import slugify


def create_sample_sql_exercises():
    """Create sample SQL exercises"""
    
    app = create_app()
    
    with app.app_context():
        # Find or create a SQL tutorial - check by slug first to avoid duplicates
        sql_tutorial = NewTutorial.query.filter_by(slug='sql-practice').first()
        
        if not sql_tutorial:
            # Also check by category as fallback
            sql_tutorial = NewTutorial.query.filter_by(category='database', course_type='sql').first()
        
        if not sql_tutorial:
            print("Creating a new SQL tutorial...")
            # We need a user ID - let's get the first admin user
            from app.models import TutorialUser
            admin_user = TutorialUser.query.filter_by(is_admin=True).first()
            if not admin_user:
                admin_user = TutorialUser.query.first()
            
            if not admin_user:
                print("❌ No users found. Please create a user first.")
                return
            
            sql_tutorial = NewTutorial(
                title='SQL Practice',
                slug='sql-practice',
                description='Interactive SQL practice exercises',
                category='database',
                course_type='sql',
                difficulty_level='beginner',
                estimated_duration_hours=10,
                instructor_id=admin_user.id,
                status='published',
                is_free=True
            )
            db.session.add(sql_tutorial)
            db.session.commit()
            print(f"✓ Created SQL tutorial (ID: {sql_tutorial.id})")
        else:
            print(f"✓ Found existing SQL tutorial (ID: {sql_tutorial.id}, Title: '{sql_tutorial.title}')")
        
        # Check if exercises already exist
        existing_count = Exercise.query.filter_by(
            tutorial_id=sql_tutorial.id,
            exercise_type='sql'
        ).count()
        
        if existing_count > 0:
            print(f"Found {existing_count} existing SQL exercises.")
            response = input("Do you want to add more exercises anyway? (y/n): ")
            if response.lower() != 'y':
                print("Cancelled.")
                return
        
        # Sample SQL exercises
        exercises = [
            {
                'title': 'Select All Employees',
                'description': '''
                <p>Write a SQL query to select all columns from the <code>employees</code> table.</p>
                <p><strong>Expected Output:</strong> All employee records with all columns.</p>
                ''',
                'exercise_type': 'sql',
                'difficulty': 'easy',
                'points': 10,
                'starter_code': 'SELECT ',
                'solution_code': 'SELECT * FROM employees;',
                'hints': [
                    'Use SELECT * to select all columns',
                    'FROM clause specifies the table name',
                    'Don\'t forget the semicolon at the end'
                ],
                'expected_output': {
                    'columns': ['id', 'first_name', 'last_name', 'email', 'department', 'salary', 'hire_date', 'created_at'],
                    'row_count': 10
                }
            },
            {
                'title': 'Filter High Salaries',
                'description': '''
                <p>Write a SQL query to find all employees with a salary greater than $80,000.</p>
                <p>Select only the <code>first_name</code>, <code>last_name</code>, and <code>salary</code> columns.</p>
                <p>Order the results by salary in descending order.</p>
                ''',
                'exercise_type': 'sql',
                'difficulty': 'easy',
                'points': 15,
                'starter_code': 'SELECT first_name, last_name, salary\nFROM employees\nWHERE ',
                'solution_code': 'SELECT first_name, last_name, salary\nFROM employees\nWHERE salary > 80000\nORDER BY salary DESC;',
                'hints': [
                    'Use WHERE clause to filter rows',
                    'salary > 80000 for the condition',
                    'ORDER BY salary DESC to sort in descending order'
                ],
                'expected_output': {
                    'columns': ['first_name', 'last_name', 'salary']
                }
            },
            {
                'title': 'Count Employees by Department',
                'description': '''
                <p>Write a SQL query to count the number of employees in each department.</p>
                <p>Display the <code>department</code> name and the <code>count</code> of employees.</p>
                <p>Order the results by count in descending order.</p>
                ''',
                'exercise_type': 'sql',
                'difficulty': 'medium',
                'points': 20,
                'starter_code': 'SELECT department, COUNT(*) as employee_count\nFROM employees\n',
                'solution_code': 'SELECT department, COUNT(*) as employee_count\nFROM employees\nGROUP BY department\nORDER BY employee_count DESC;',
                'hints': [
                    'Use GROUP BY to group records by department',
                    'COUNT(*) counts all records in each group',
                    'Use an alias for the count column'
                ],
                'expected_output': {
                    'columns': ['department', 'employee_count']
                }
            },
            {
                'title': 'Average Salary by Department',
                'description': '''
                <p>Calculate the average salary for each department.</p>
                <p>Display the <code>department</code> and <code>average_salary</code> (rounded to 2 decimal places).</p>
                <p>Only include departments where the average salary is greater than $75,000.</p>
                ''',
                'exercise_type': 'sql',
                'difficulty': 'medium',
                'points': 25,
                'starter_code': 'SELECT department, ROUND(AVG(salary), 2) as average_salary\nFROM employees\n',
                'solution_code': 'SELECT department, ROUND(AVG(salary), 2) as average_salary\nFROM employees\nGROUP BY department\nHAVING AVG(salary) > 75000;',
                'hints': [
                    'AVG() function calculates the average',
                    'ROUND(value, 2) rounds to 2 decimal places',
                    'HAVING clause filters grouped results'
                ],
                'expected_output': {
                    'columns': ['department', 'average_salary']
                }
            },
            {
                'title': 'Join Employees and Projects',
                'description': '''
                <p>Write a query to find all employees and their assigned projects.</p>
                <p>Display: <code>first_name</code>, <code>last_name</code>, <code>project_name</code>, and <code>role</code>.</p>
                <p>Use the <code>employees</code>, <code>employee_projects</code>, and <code>projects</code> tables.</p>
                ''',
                'exercise_type': 'sql',
                'difficulty': 'hard',
                'points': 30,
                'starter_code': 'SELECT e.first_name, e.last_name, p.name as project_name, ep.role\nFROM employees e\n',
                'solution_code': '''SELECT e.first_name, e.last_name, p.name as project_name, ep.role
FROM employees e
INNER JOIN employee_projects ep ON e.id = ep.employee_id
INNER JOIN projects p ON ep.project_id = p.id;''',
                'hints': [
                    'Use INNER JOIN to combine tables',
                    'Join employees with employee_projects on employee_id',
                    'Then join with projects on project_id',
                    'Use table aliases (e, ep, p) for cleaner syntax'
                ],
                'expected_output': {
                    'columns': ['first_name', 'last_name', 'project_name', 'role']
                }
            },
            {
                'title': 'Recent High-Value Orders',
                'description': '''
                <p>Find all orders from 2023 with a total amount greater than $500.</p>
                <p>Display: <code>customer first_name</code>, <code>customer last_name</code>, <code>order_date</code>, and <code>total_amount</code>.</p>
                <p>Order by total_amount descending.</p>
                ''',
                'exercise_type': 'sql',
                'difficulty': 'hard',
                'points': 35,
                'starter_code': 'SELECT c.first_name, c.last_name, o.order_date, o.total_amount\nFROM orders o\n',
                'solution_code': '''SELECT c.first_name, c.last_name, o.order_date, o.total_amount
FROM orders o
INNER JOIN customers c ON o.customer_id = c.id
WHERE YEAR(o.order_date) = 2023 AND o.total_amount > 500
ORDER BY o.total_amount DESC;''',
                'hints': [
                    'Join orders with customers table',
                    'Use YEAR() function to extract year from date',
                    'Combine conditions with AND in WHERE clause',
                    'Use ORDER BY with DESC for descending order'
                ],
                'expected_output': {
                    'columns': ['first_name', 'last_name', 'order_date', 'total_amount']
                }
            },
            {
                'title': 'Product Sales Summary',
                'description': '''
                <p>Create a sales summary showing each product's total quantity sold and revenue.</p>
                <p>Display: <code>product_name</code>, <code>total_quantity</code>, and <code>total_revenue</code>.</p>
                <p>Only include products that have been ordered.</p>
                <p>Order by total_revenue descending.</p>
                ''',
                'exercise_type': 'sql',
                'difficulty': 'hard',
                'points': 40,
                'starter_code': 'SELECT p.name as product_name, \n       SUM(oi.quantity) as total_quantity,\n       SUM(oi.quantity * oi.price) as total_revenue\nFROM products p\n',
                'solution_code': '''SELECT p.name as product_name, 
       SUM(oi.quantity) as total_quantity,
       SUM(oi.quantity * oi.price) as total_revenue
FROM products p
INNER JOIN order_items oi ON p.id = oi.product_id
GROUP BY p.id, p.name
ORDER BY total_revenue DESC;''',
                'hints': [
                    'Join products with order_items table',
                    'Use SUM() to calculate totals',
                    'Multiply quantity * price for revenue',
                    'GROUP BY product to aggregate data',
                    'Order by calculated total_revenue'
                ],
                'expected_output': {
                    'columns': ['product_name', 'total_quantity', 'total_revenue']
                }
            }
        ]
        
        # Create exercises
        created_count = 0
        for idx, ex_data in enumerate(exercises, start=1):
            # Check if exercise already exists
            existing = Exercise.query.filter_by(
                tutorial_id=sql_tutorial.id,
                title=ex_data['title']
            ).first()
            
            if existing:
                print(f"Exercise '{ex_data['title']}' already exists. Skipping.")
                continue
            
            # Create slug from title
            slug = slugify(ex_data['title'])
            
            exercise = Exercise(
                tutorial_id=sql_tutorial.id,
                lesson_id=None,  # Not tied to a specific lesson
                title=ex_data['title'],
                slug=slug,
                description=ex_data['description'],
                exercise_type=ex_data['exercise_type'],
                difficulty=ex_data['difficulty'],
                points=ex_data['points'],
                starter_code=ex_data['starter_code'],
                solution_code=ex_data['solution_code'],
                hints=json.dumps(ex_data['hints']),
                expected_output=json.dumps(ex_data['expected_output']),
                order_index=idx
            )
            
            db.session.add(exercise)
            created_count += 1
            print(f"✓ Created exercise: {ex_data['title']}")
        
        db.session.commit()
        print(f"\n✅ Successfully created {created_count} SQL exercises!")


if __name__ == '__main__':
    create_sample_sql_exercises()
