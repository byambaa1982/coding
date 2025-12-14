# Content Creator Experience Improvement Plan

## Issues Identified (Based on Exercise 24 Debugging Session)

### 1. **Form Validation Errors Not Visible**
- **Problem**: When updating an exercise, validation errors were silent - no feedback to the user
- **Impact**: Content creators don't know what's wrong when form submission fails
- **Status**: ✅ Fixed - Added error display in template

### 2. **Test Case Format Confusion**
- **Problem**: Form accepts test cases as text, but unclear whether to use JSON or Python syntax
- **Current State**: 
  - Backend expected JSON: `[{"type": "assert_output", ...}]`
  - Users naturally entered Python: `[{'type': 'assert_output', ...}]`
  - Parser failed silently, resulting in 0 test cases
- **Impact**: Tests don't run, no clear error message
- **Status**: ✅ Fixed - Parser now handles both formats with ast.literal_eval fallback

### 3. **Test Execution Logic Issue**
- **Problem**: `assert_output` tests weren't capturing stdout properly
- **Root Cause**: User code ran before stdout capture was set up
- **Impact**: Print statements weren't captured, tests always failed
- **Status**: ✅ Fixed - Reordered code to capture stdout before user code runs

### 4. **No Test Case Examples in UI**
- **Problem**: Content creators must memorize complex test case formats
- **Impact**: High error rate, time wasted on syntax issues

### 5. **No Preview/Test Before Publishing**
- **Problem**: Can't test exercises without saving and running as student
- **Impact**: Multiple save/test cycles, potential broken exercises published

---

## Improvement Plan

### **Phase 1: Immediate Fixes (High Priority)** ⚡

#### 1.1 Enhanced Test Case Input UI
**Goal**: Make test case creation intuitive and error-proof

**Implementation**:
- [ ] Add dropdown to select test type (assert_function, assert_output, assert_output_contains, etc.)
- [ ] Show dynamic form fields based on selected test type
- [ ] Visual test case builder with add/remove buttons
- [ ] Real-time JSON validation with error highlighting
- [ ] Accept both JSON and Python literal formats (already done in backend)

**Example UI Structure**:
```
┌─ Test Case 1 ──────────────────────────┐
│ Type: [assert_output ▼]                │
│                                         │
│ Expected Output: [Hello, World!     ]  │
│ Description: [Print Hello, World!   ]  │
│ ☑ Case sensitive                       │
│ ☑ Strip whitespace                     │
│                                         │
│ [Remove] [Preview JSON]                │
└─────────────────────────────────────────┘
[+ Add Test Case]
```

#### 1.2 Test Case Templates
**Goal**: Quick-start with common patterns

**Implementation**:
- [ ] Add "Load Template" button with common test types:
  - Simple print output
  - Function with return value
  - Multiple test cases
  - Variable existence check
  - Output contains text
- [ ] Pre-populate with working examples
- [ ] One-click insertion

#### 1.3 Exercise Preview & Test
**Goal**: Test exercises before publishing

**Implementation**:
- [ ] Add "Test Exercise" button in edit form
- [ ] Opens modal with code editor
- [ ] Run test cases against sample code
- [ ] Show results without saving to database
- [ ] Validate that tests work with both starter code and solution code

```javascript
// New route: POST /instructor/courses/:id/exercises/preview
// Accepts: code, test_cases, language
// Returns: execution results without saving
```

---

### **Phase 2: Enhanced Content Creation (Medium Priority)** 🎯

#### 2.1 Inline Help & Documentation
- [ ] Add help icons (?) next to each field with tooltips
- [ ] Expandable "Examples" section for each test type
- [ ] Link to full documentation
- [ ] Common pitfalls warnings

#### 2.2 Test Case Validation
- [ ] Real-time validation of test case format
- [ ] Check for common errors:
  - Missing required fields
  - Invalid JSON/Python syntax
  - Mismatched function names
  - Empty expected values
- [ ] Show warnings before save

#### 2.3 Bulk Import/Export
- [ ] Export exercise as JSON for backup
- [ ] Import exercises from JSON
- [ ] Copy exercise from another course
- [ ] Duplicate exercise within course

#### 2.4 Test Case Generator
- [ ] AI-assisted test case generation
- [ ] Analyze solution code and suggest test cases
- [ ] Generate edge cases automatically
- [ ] Validate coverage (basic, edge cases, error cases)

---

### **Phase 3: Advanced Features (Lower Priority)** 🚀

#### 3.1 Exercise Wizard
- [ ] Step-by-step guided exercise creation
- [ ] Progressive disclosure of advanced options
- [ ] Built-in best practices
- [ ] Template selection at start

#### 3.2 Analytics & Insights
- [ ] Show which test cases students fail most
- [ ] Common error patterns
- [ ] Suggest test case improvements
- [ ] Difficulty calibration based on student data

#### 3.3 Collaborative Features
- [ ] Share exercises between instructors
- [ ] Exercise review workflow
- [ ] Comment on exercises
- [ ] Version history

#### 3.4 Rich Exercise Types
- [ ] Multiple file exercises
- [ ] Interactive visualizations
- [ ] Step-by-step guided exercises
- [ ] Code comparison (before/after)

---

## Technical Implementation Details

### 1. Test Case Builder Component

**Frontend** (`app/templates/instructor/components/test_case_builder.html`):
```html
<div id="test-case-builder">
    <div class="test-cases-list">
        <!-- Dynamic test case forms -->
    </div>
    <button onclick="addTestCase()">+ Add Test Case</button>
    <button onclick="loadTemplate()">📋 Load Template</button>
    <button onclick="previewJSON()">👁️ Preview JSON</button>
</div>

<script>
function addTestCase(type = 'assert_function') {
    // Add new test case form dynamically
}

function renderTestCaseForm(testCase, index) {
    // Render form based on test type
}

function generateJSON() {
    // Convert form data to JSON
}

function validateTestCases() {
    // Validate all test cases
}
</script>
```

**Backend** (`app/instructor/forms.py`):
```python
class TestCaseBuilderField(Field):
    """Custom field for test case builder."""
    
    def process_formdata(self, valuelist):
        if valuelist:
            # Accept both JSON string and Python literal
            try:
                self.data = json.loads(valuelist[0])
            except json.JSONDecodeError:
                try:
                    import ast
                    self.data = ast.literal_eval(valuelist[0])
                except:
                    raise ValueError('Invalid test case format')
```

### 2. Exercise Preview Route

**Route** (`app/instructor/routes.py`):
```python
@instructor_bp.route('/exercises/preview', methods=['POST'])
@login_required
@instructor_required
def preview_exercise():
    """Preview exercise execution without saving."""
    data = request.get_json()
    
    code = data.get('code', '')
    test_cases = data.get('test_cases', [])
    language = data.get('language', 'python')
    
    # Validate inputs
    if not code or not test_cases:
        return jsonify({'error': 'Code and test cases required'}), 400
    
    # Execute code
    if language == 'python':
        result = execute_python_code(code, test_cases, timeout=30)
    else:
        result = execute_sql_code(code, test_cases)
    
    return jsonify(result)
```

### 3. Test Case Templates

**Data** (`app/instructor/test_case_templates.py`):
```python
TEST_CASE_TEMPLATES = {
    'python': {
        'simple_output': {
            'name': 'Simple Print Output',
            'description': 'Test a print statement',
            'test_cases': [
                {
                    'type': 'assert_output',
                    'expected': 'Hello, World!',
                    'description': 'Check printed output',
                    'case_sensitive': False,
                    'strip_whitespace': True
                }
            ]
        },
        'function_return': {
            'name': 'Function Return Value',
            'description': 'Test a function that returns a value',
            'test_cases': [
                {
                    'type': 'assert_function',
                    'function_name': 'add',
                    'input': [2, 3],
                    'expected': 5,
                    'description': 'Add 2 + 3'
                }
            ]
        },
        'multiple_tests': {
            'name': 'Multiple Test Cases',
            'description': 'Test function with multiple inputs',
            'test_cases': [
                {
                    'type': 'assert_function',
                    'function_name': 'square',
                    'input': [5],
                    'expected': 25,
                    'description': 'Square of 5'
                },
                {
                    'type': 'assert_function',
                    'function_name': 'square',
                    'input': [0],
                    'expected': 0,
                    'description': 'Square of 0 (edge case)'
                },
                {
                    'type': 'assert_function',
                    'function_name': 'square',
                    'input': [-3],
                    'expected': 9,
                    'description': 'Square of negative number'
                }
            ]
        }
    }
}
```

---

## Quick Wins (Can Implement Now)

### 1. Add Help Text to Test Cases Field
```html
<div class="help-text">
    <strong>Format:</strong> JSON array of test case objects<br>
    <strong>Both formats accepted:</strong>
    <ul>
        <li>JSON: <code>[{"type": "assert_output", "expected": "Hello"}]</code></li>
        <li>Python: <code>[{'type': 'assert_output', 'expected': 'Hello'}]</code></li>
    </ul>
    <a href="/docs/test-cases" target="_blank">View Examples →</a>
</div>
```

### 2. Add Test Case Validator Button
```html
<button type="button" onclick="validateTestCases()">✓ Validate Test Cases</button>
```

### 3. Create Test Case Documentation Page
- Route: `/instructor/docs/test-cases`
- Content: All test types with examples
- Copy-paste ready examples

---

## Success Metrics

After implementing these improvements, measure:

1. **Error Rate Reduction**
   - % of exercises with invalid test cases (should decrease to < 5%)
   - Average time to create an exercise (should decrease by 50%)

2. **User Satisfaction**
   - Survey instructors on ease of use (target: 4.5+/5)
   - Support tickets related to test cases (should decrease by 80%)

3. **Content Quality**
   - % of exercises with comprehensive test coverage
   - Student success rate on first attempt

---

## Priority Recommendation

### **Week 1: Critical Fixes** (Already Complete ✅)
- [x] Form validation error display
- [x] Test case parser (JSON + Python)
- [x] Stdout capture fix

### **Week 2: Quick Wins**
- [ ] Add inline help text and examples
- [ ] Test case validation button
- [ ] Create documentation page
- [ ] Template dropdown with 3-5 common patterns

### **Week 3-4: Test Case Builder**
- [ ] Visual test case builder component
- [ ] Dynamic form based on test type
- [ ] Preview functionality

### **Week 5-6: Advanced Features**
- [ ] Exercise preview/test
- [ ] Bulk import/export
- [ ] AI-assisted test generation

---

## Notes

- All improvements should be backward compatible
- Maintain support for both JSON and Python literal formats
- Focus on reducing cognitive load for content creators
- Provide multiple ways to accomplish the same task (templates, builder, manual entry)
- Always validate and provide clear error messages
