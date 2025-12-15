from app import create_app
from app.models import Exercise

app = create_app()
ctx = app.app_context()
ctx.push()

exercises = Exercise.query.filter_by(lesson_id=6).order_by(Exercise.order_index).all()
new_exercises = [ex for ex in exercises if ex.order_index in [1, 2, 3, 4, 5]]

for ex in new_exercises:
    print(f'\n{ex.order_index}. {ex.title}')
    sol = ex.solution_code if ex.solution_code else 'None'
    print(f'   Solution Code: {sol[:100]}...')
