"""
BEST PRACTICES FOR TEST CASE DESIGN
====================================

Different test types for different scenarios:

1. FUNCTION-BASED TESTING (Best for most cases)
   - Tests return values, not print statements
   - User can name variables anything
   - Most reliable and flexible
   
2. OUTPUT-BASED TESTING (For print exercises)
   - Use flexible matching (case-insensitive, contains, regex)
   - Good for beginner exercises
   
3. VARIABLE/STATE TESTING
   - Check if variables exist with correct values
   - Good for teaching variable assignment

Examples below show the JSON structure for each test type.
"""

# ============================================================================
# EXAMPLE 1: Function-based testing (RECOMMENDED)
# ============================================================================
# Exercise: "Create a function that returns the second item from a list"

function_test_example = [
    {
        "type": "assert_function",
        "description": "Test with animal names",
        "function_name": "get_second",  # Function name to test
        "input": [["cat", "dog", "bird"]],  # Arguments to pass
        "expected": "dog"
    },
    {
        "type": "assert_function",
        "description": "Test with numbers",
        "function_name": "get_second",
        "input": [[1, 2, 3, 4, 5]],
        "expected": 2
    },
    {
        "type": "assert_function",
        "description": "Test with different animals",
        "function_name": "get_second",
        "input": [["elephant", "lion", "zebra"]],
        "expected": "lion"
    }
]

# ============================================================================
# EXAMPLE 2: Flexible output testing (for print exercises)
# ============================================================================
# Exercise: "Print 'hello' in any case"

output_test_example = [
    {
        "type": "assert_output",
        "description": "Should print hello",
        "expected": "hello\n",
        "case_sensitive": False  # Accepts Hello, HELLO, hello
    },
    {
        "type": "assert_output_contains",
        "description": "Output should contain 'hello'",
        "expected": "hello",
        "case_sensitive": False
    },
    {
        "type": "assert_output_regex",
        "description": "Should match hello pattern",
        "pattern": r"^hello!?$",  # Accepts "hello" or "hello!"
        "flags": "IGNORECASE"
    }
]

# ============================================================================
# EXAMPLE 3: Variable testing (check if variable exists with value)
# ============================================================================
# Exercise: "Create a list of 3 animals and store in variable 'animals'"

variable_test_example = [
    {
        "type": "assert_variable_exists",
        "description": "Variable 'animals' should exist",
        "variable_name": "animals"
    },
    {
        "type": "assert_variable_type",
        "description": "Variable 'animals' should be a list",
        "variable_name": "animals",
        "expected_type": "list"
    },
    {
        "type": "assert_variable_length",
        "description": "List should have exactly 3 items",
        "variable_name": "animals",
        "expected_length": 3
    },
    {
        "type": "assert_custom",
        "description": "Second animal should be accessible",
        "code": "len(animals) >= 2 and isinstance(animals[1], str)"
    }
]

# ============================================================================
# EXAMPLE 4: Multiple acceptable answers
# ============================================================================
# Exercise: "Create a greeting message"

multiple_answers_example = [
    {
        "type": "assert_function",
        "description": "Should return a greeting",
        "function_name": "greet",
        "input": ["Alice"],
        "expected_any_of": [  # Accept any of these
            "Hello, Alice!",
            "Hi, Alice!",
            "Hey, Alice!"
        ]
    },
    {
        "type": "assert_output_pattern",
        "description": "Output should contain a number between 1-10",
        "validator": "lambda x: any(str(i) in x for i in range(1, 11))"
    }
]

# ============================================================================
# EXAMPLE 5: Custom validation logic
# ============================================================================
# Exercise: "Create any list of animals and print the second one"

custom_validation_example = [
    {
        "type": "assert_custom",
        "description": "Should define a list with at least 2 items",
        "code": """
# Check if any variable is a list with length >= 2
import __main__
has_valid_list = any(
    isinstance(getattr(__main__, var), list) and len(getattr(__main__, var)) >= 2
    for var in dir(__main__) if not var.startswith('_')
)
has_valid_list
"""
    },
    {
        "type": "assert_output_custom",
        "description": "Output should contain one word (the animal name)",
        "validator": "lambda output: len(output.strip().split()) == 1"
    }
]

# ============================================================================
# RECOMMENDED APPROACH FOR YOUR USE CASES
# ============================================================================

# For: "User can print 'Hi' or 'hi'"
case_insensitive_test = [
    {
        "type": "assert_output",
        "description": "Should print hi (case insensitive)",
        "expected": "hi",
        "case_sensitive": False,
        "strip_whitespace": True
    }
]

# For: "Create list of 3 animals and print second"
animal_list_test = [
    {
        "type": "assert_function",
        "description": "Function should return second item",
        "function_name": "get_second_animal",
        "input": [["cat", "dog", "bird"]],
        "expected": "dog"
    },
    {
        "type": "assert_function", 
        "description": "Should work with any list",
        "function_name": "get_second_animal",
        "input": [["apple", "banana", "cherry"]],
        "expected": "banana"
    }
]

# If they must use print (not recommended):
animal_print_test = [
    {
        "type": "assert_variable_exists",
        "description": "Should create a list of animals",
        "variable_name": "animals",
        "hint": "Create a variable called 'animals'"
    },
    {
        "type": "assert_variable_length",
        "description": "List should have 3 animals",
        "variable_name": "animals",
        "expected_length": 3
    },
    {
        "type": "assert_output_custom",
        "description": "Should print the second animal",
        "validator": "lambda output: output.strip() == animals[1] if 'animals' in globals() else False"
    }
]

print("Test case design guide created!")
print("\nKEY RECOMMENDATIONS:")
print("1. Use function-based testing whenever possible")
print("2. Use flexible matching for output (case_insensitive, contains, regex)")
print("3. Test behavior, not specific values (test that list[1] works, not that it equals 'dog')")
print("4. Provide multiple test cases with different inputs")
print("5. Use custom validators for complex logic")
