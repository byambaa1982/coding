"""Check test_cases in database for exercise 24."""
from app import create_app
from app.models import Exercise
import json

app = create_app()
ctx = app.app_context()
ctx.push()

ex = Exercise.query.get(24)
print('Exercise ID:', ex.id)
print('Title:', ex.title)
print('\nRaw test_cases string:')
print(repr(ex.test_cases))
print('\nTrying to parse as JSON:')
try:
    parsed = json.loads(ex.test_cases)
    print('✓ Parsed successfully!')
    print('Number of test cases:', len(parsed))
    print('Test cases:', json.dumps(parsed, indent=2))
except Exception as e:
    print('✗ Parse error:', type(e).__name__, '-', e)
    print('\nThe test_cases string is not valid JSON.')
    print('Attempting to fix by replacing single quotes with double quotes...')
    try:
        # Try using ast.literal_eval for Python syntax
        import ast
        parsed_ast = ast.literal_eval(ex.test_cases)
        print('✓ Parsed as Python literal!')
        print('Test cases:', parsed_ast)
        
        # Convert to proper JSON
        json_str = json.dumps(parsed_ast)
        print('\nProper JSON format:')
        print(json_str)
    except Exception as e2:
        print('✗ Also failed with ast.literal_eval:', e2)
