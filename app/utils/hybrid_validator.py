# app/utils/hybrid_validator.py
"""
Hybrid Validation System for Python and SQL exercises.
Combines traditional tests (fast, free, reliable) with optional AI enhancements.
"""

import os
import json
import time
from typing import Dict, List, Any, Optional
from openai import OpenAI
from app.python_practice.executor_enhanced import execute_python_code_enhanced


class HybridValidator:
    """Unified validator for Python and SQL with optional AI enhancement."""
    
    def __init__(self):
        self.openai_client = None
        self.ai_enabled = False
        
        # Check if OpenAI is configured
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and api_key.startswith('sk-'):
            try:
                # Initialize OpenAI client (compatible with v2.x)
                self.openai_client = OpenAI(api_key=api_key)
                self.ai_enabled = True
            except Exception as e:
                print(f"⚠️ OpenAI initialization failed: {e}")
                self.ai_enabled = False
    
    def validate_python(self, code: str, test_cases: List[Dict], timeout: int = 30) -> Dict[str, Any]:
        """
        Validate Python code using traditional tests.
        
        Returns:
            Dictionary with validation results including traditional test results
        """
        start_time = time.time()
        
        # Run traditional tests (FREE, FAST, RELIABLE)
        result = execute_python_code_enhanced(code, test_cases, timeout)
        
        # Add metadata
        result['validation_method'] = 'traditional'
        result['ai_available'] = self.ai_enabled
        result['execution_time_ms'] = int((time.time() - start_time) * 1000)
        
        return result
    
    def validate_sql(self, query: str, test_cases: List[Dict], schema_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate SQL query using traditional tests.
        
        Returns:
            Dictionary with validation results
        """
        # This will be implemented when SQL executor is ready
        # For now, return a placeholder
        return {
            'status': 'error',
            'error': 'SQL validation not yet implemented',
            'test_results': [],
            'tests_passed': 0,
            'tests_failed': 0,
            'validation_method': 'traditional',
            'ai_available': self.ai_enabled
        }
    
    def get_ai_hint(self, code: str, language: str, exercise_description: str, 
                    error_message: Optional[str] = None, failed_tests: Optional[List] = None) -> Dict:
        """
        Get AI-generated hint for struggling student (ON-DEMAND, COSTS ~$0.001).
        
        Args:
            code: Student's code
            language: 'python' or 'sql'
            exercise_description: What the exercise asks for
            error_message: Error from execution
            failed_tests: List of failed test cases
            
        Returns:
            Dictionary with hint and encouragement
        """
        
        if not self.ai_enabled:
            return {
                'success': False,
                'hint': 'AI hints are not available. Please ask your instructor for help.',
                'reason': 'OpenAI API not configured'
            }
        
        try:
            # Build context from failed tests
            test_context = ""
            if failed_tests:
                test_context = f"\n\nFailed tests:\n"
                for test in failed_tests[:3]:  # Limit to 3 tests to save tokens
                    test_context += f"- {test.get('description', 'Test')}: Expected {test.get('expected')}, got {test.get('actual')}\n"
            
            prompt = f"""You are a patient programming tutor helping a student learn {language.upper()}.

Exercise: {exercise_description}

Student's current code:
```{language}
{code}
```
{test_context}
{f"Error: {error_message}" if error_message else ""}

Provide a helpful hint in 2-3 sentences that:
1. Acknowledges what they're doing right
2. Points them in the right direction without giving away the answer
3. Is encouraging and supportive

Respond in JSON format:
{{
    "hint": "your helpful hint here",
    "encouragement": "positive, encouraging message"
}}
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # Cheaper option
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful programming tutor. Give hints without revealing solutions."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200,  # Keep costs low
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            result['success'] = True
            result['cost_estimate'] = 0.001  # Rough estimate
            
            return result
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                'success': True,
                'hint': response.choices[0].message.content,
                'encouragement': 'Keep practicing!'
            }
        except Exception as e:
            return {
                'success': False,
                'hint': 'AI hint service temporarily unavailable. Try reviewing the exercise requirements.',
                'error': str(e)
            }
    
    def get_code_review(self, code: str, language: str, exercise_description: str) -> Dict:
        """
        Get AI code review after passing tests (OPTIONAL, COSTS ~$0.002).
        
        Args:
            code: Student's working code
            language: 'python' or 'sql'
            exercise_description: Exercise requirements
            
        Returns:
            Dictionary with review feedback
        """
        
        if not self.ai_enabled:
            return {
                'success': False,
                'feedback': 'Congratulations on solving the exercise!',
                'suggestions': [],
                'reason': 'OpenAI API not configured'
            }
        
        try:
            prompt = f"""Review this {language.upper()} code that successfully passed all tests.

Exercise: {exercise_description}

Code:
```{language}
{code}
```

Provide constructive feedback focusing on:
1. Code quality and readability
2. Best practices for {language}
3. Potential improvements
4. What they did well

Be encouraging - the code already works!

Respond in JSON format:
{{
    "feedback": "brief overall feedback (1-2 sentences)",
    "strengths": ["what they did well"],
    "suggestions": ["optional improvement 1", "optional improvement 2"]
}}
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a {language} expert providing code review focused on learning."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=250,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            result['success'] = True
            result['cost_estimate'] = 0.002
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'feedback': 'Great job completing this exercise!',
                'suggestions': [],
                'error': str(e)
            }
    
    def explain_error(self, error_message: str, code: str, language: str) -> str:
        """
        Get plain English explanation of error message (OPTIONAL).
        
        Args:
            error_message: Technical error message
            code: Student's code
            language: 'python' or 'sql'
            
        Returns:
            Plain English explanation
        """
        
        if not self.ai_enabled:
            return error_message  # Return original error
        
        try:
            prompt = f"""Explain this {language} error in simple terms for a beginner:

Error: {error_message}

Code context:
```{language}
{code[:500]}  # First 500 chars
```

Provide a brief, clear explanation in 1-2 sentences."""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You explain programming errors in simple, beginner-friendly language."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception:
            return error_message  # Fallback to original


# Global instance
_validator = None

def get_validator() -> HybridValidator:
    """Get singleton validator instance."""
    global _validator
    if _validator is None:
        _validator = HybridValidator()
    return _validator
