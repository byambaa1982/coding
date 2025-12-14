# System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Exercise QA Testing Suite                        │
│                         (db_tester/)                                │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
            ┌───────▼──────┐ ┌───▼────┐ ┌─────▼─────┐
            │   CLI Tools  │ │  Core  │ │ Reporting │
            └──────────────┘ └────────┘ └───────────┘
                    │             │             │
        ┌───────────┼─────────┐   │   ┌─────────┼─────────┐
        │           │         │   │   │         │         │
    ┌───▼───┐   ┌──▼──┐  ┌───▼───▼───▼───┐  ┌──▼───┐ ┌───▼────┐
    │ .bat  │   │ .sh │  │test_python_   │  │ JSON │ │  HTML  │
    │script │   │script│  │exercises.py   │  │Report│ │ Report │
    └───────┘   └─────┘  └───────┬───────┘  └──────┘ └────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
            ┌───────▼──────┐ ┌───▼────────┐ ┌──▼────────┐
            │test_validator│ │batch_tester│ │html_report│
            │    .py       │ │    .py     │ │   .py     │
            └──────────────┘ └────────────┘ └───────────┘
                    │             │             │
                    └─────────────┼─────────────┘
                                  │
                        ┌─────────▼─────────┐
                        │  test_config.py   │
                        │  (Configuration)  │
                        └─────────┬─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
            ┌───────▼──────┐ ┌───▼───────┐ ┌───▼──────┐
            │   Database   │ │  Executor │ │Validator │
            │   (Models)   │ │           │ │          │
            └──────────────┘ └───────────┘ └──────────┘
                    │             │             │
                    └─────────────┼─────────────┘
                                  │
                        ┌─────────▼─────────┐
                        │   Flask App       │
                        │ (app/models.py)   │
                        │ (app/python_      │
                        │  practice/)       │
                        └───────────────────┘
```

## Component Interaction Flow

### 1. Single Exercise Test Flow
```
User Command
    │
    ▼
test_validator.py
    │
    ├─► Load Exercise from Database
    │
    ├─► Validate Code Syntax
    │   └─► validators.validate_python_code()
    │
    ├─► Parse Test Cases (JSON)
    │
    ├─► Execute Code
    │   └─► executor.execute_python_code()
    │
    ├─► Compare Results
    │
    └─► Return Result
        └─► Print to Console
```

### 2. Course/Lesson Test Flow
```
User Command
    │
    ▼
test_python_exercises.py
    │
    ├─► ExerciseTester.__init__()
    │
    ├─► get_exercises()
    │   └─► Query Database (course_id, lesson_id)
    │
    ├─► For Each Exercise:
    │   ├─► validate_exercise()
    │   │   ├─► Validate Code
    │   │   ├─► Parse Test Cases
    │   │   ├─► Execute Code
    │   │   └─► Collect Results
    │   │
    │   └─► Print Progress
    │
    ├─► Generate Summary Statistics
    │
    ├─► Print Summary
    │
    └─► Save Reports
        ├─► JSON (detailed_results.json)
        └─► HTML (optional)
```

### 3. Batch Test Flow
```
User Command
    │
    ▼
batch_tester.py
    │
    ├─► BatchTester.__init__()
    │
    ├─► Mode Selection:
    │   ├─► list: List all courses
    │   ├─► specific: Test selected courses
    │   └─► all: Test all courses
    │
    ├─► For Each Course/Lesson:
    │   └─► test_course_lesson()
    │       └─► ExerciseTester.run_tests()
    │
    ├─► Generate Batch Summary
    │   └─► Aggregate all results
    │
    ├─► Print Batch Summary
    │
    └─► Save Batch Report
```

## Data Flow

```
┌──────────────┐
│   Database   │
└──────┬───────┘
       │
       │ (SQL Query)
       │
┌──────▼───────────────────────────────┐
│        Exercise Object               │
│  - id, title, slug                   │
│  - solution_code                     │
│  - test_cases (JSON)                 │
│  - difficulty                        │
└──────┬───────────────────────────────┘
       │
       │ (Validate)
       │
┌──────▼───────────────────────────────┐
│    Validation Results                │
│  - is_valid: bool                    │
│  - errors: list                      │
└──────┬───────────────────────────────┘
       │
       │ (Execute)
       │
┌──────▼───────────────────────────────┐
│    Execution Results                 │
│  - status: passed/failed/error       │
│  - tests_passed: int                 │
│  - tests_failed: int                 │
│  - execution_time_ms: int            │
│  - test_results: list                │
│  - errors: list                      │
└──────┬───────────────────────────────┘
       │
       │ (Aggregate)
       │
┌──────▼───────────────────────────────┐
│    Test Summary                      │
│  - total_exercises: int              │
│  - passed_exercises: int             │
│  - failed_exercises: int             │
│  - success_rate: float               │
│  - total_tests: int                  │
│  - execution_time_ms: int            │
└──────┬───────────────────────────────┘
       │
       │ (Generate)
       │
┌──────▼───────────────────────────────┐
│        Reports                       │
│  - JSON Report (detailed)            │
│  - HTML Report (visual)              │
│  - Console Output                    │
└──────────────────────────────────────┘
```

## Module Dependencies

```
test_python_exercises.py
    ├── app (Flask application)
    │   ├── create_app()
    │   ├── db (SQLAlchemy)
    │   └── models
    │       ├── Exercise
    │       ├── Lesson
    │       └── NewTutorial
    │
    └── app.python_practice
        ├── validators.validate_python_code()
        └── executor.execute_python_code()

test_validator.py
    ├── app.python_practice.validators
    └── app.python_practice.executor

batch_tester.py
    ├── test_python_exercises.ExerciseTester
    └── app (for database queries)

html_report.py
    └── (Pure Python, no external dependencies)

test_config.py
    └── (Configuration only)
```

## User Interaction Paths

### Path 1: Quick Test (Default)
```
User → run_tests.bat → test_python_exercises.py → Results
```

### Path 2: Specific Exercise
```
User → Command Line → test_validator.py → Single Result
```

### Path 3: Batch Testing
```
User → batch_tester.py → Multiple Testers → Aggregated Results
```

### Path 4: Programmatic
```
Developer → import ExerciseTester → API Call → Custom Processing
```

### Path 5: Examples
```
User → examples.py → Interactive Menu → Selected Example
```

## File Relationships

```
__init__.py
    └── Exports: ExerciseTester, ExerciseValidator, BatchTester

test_python_exercises.py
    └── Uses: ExerciseValidator (indirectly via executor/validators)

test_validator.py
    └── Uses: validators, executor from app.python_practice

batch_tester.py
    └── Uses: test_python_exercises.ExerciseTester

html_report.py
    └── Uses: Results from any tester

examples.py
    └── Uses: All of the above

run_tests.bat/sh
    └── Executes: All Python scripts

test_config.py
    └── Used by: All modules (configuration)
```

## External Dependencies

```
┌─────────────────────────────────────┐
│     Flask Application               │
├─────────────────────────────────────┤
│ app/                                │
│  ├── __init__.py (create_app)      │
│  ├── models.py                      │
│  │   ├── Exercise                   │
│  │   ├── Lesson                     │
│  │   └── NewTutorial                │
│  │                                   │
│  └── python_practice/               │
│      ├── validators.py              │
│      │   └── validate_python_code() │
│      └── executor.py                │
│          └── execute_python_code()  │
└─────────────────────────────────────┘
```

---

This architecture provides:
- ✅ Clear separation of concerns
- ✅ Modular design
- ✅ Easy to extend
- ✅ Multiple entry points
- ✅ Comprehensive reporting
- ✅ Professional quality
