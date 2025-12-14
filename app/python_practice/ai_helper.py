# app/python_practice/ai_helper.py
"""
AI-powered helper for code validation and feedback.
This is OPTIONAL - only used when students request hints or after passing tests.
"""

import os
import json
from typing import Dict, Optional
import openai  # pip install openai


def get_ai_hint(code: str, exercise_description: str, error_message: Optional[str] = None) -> Dict:
    """
    Get AI-generated hint for student struggling with exercise.
    
    Args:
        code: Student's current code
        exercise_description: What the exercise asks for
        error_message: Optional error message from failed test
        
    Returns:
        Dictionary with hint and suggestions
    """
    
    # Check if API key is configured
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return {
            'hint': 'AI hints are not configured. Please check with your instructor.',
            'available': False
        }
    
    try:
        # Use GPT-3.5 (cheaper, faster) for hints
        client = openai.OpenAI(api_key=api_key)
        
        prompt = f"""You are a helpful programming tutor. A student is working on this exercise:

Exercise: {exercise_description}

Their current code:
```python
{code}
```
"""
        
        if error_message:
            prompt += f"\nThey got this error: {error_message}"
        
        prompt += """

Provide a helpful hint (2-3 sentences) without giving away the solution:
1. Point out what they're doing right
2. Suggest what to think about next
3. Don't write the code for them

Format your response as JSON:
{
    "hint": "Your helpful hint here",
    "encouragement": "Encouraging message"
}
"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Cheaper than GPT-4
            messages=[
                {"role": "system", "content": "You are a patient programming tutor who gives hints without spoiling solutions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200  # Keep costs low
        )
        
        result = json.loads(response.choices[0].message.content)
        result['available'] = True
        result['cost_estimate'] = 0.001  # Rough estimate in USD
        
        return result
        
    except json.JSONDecodeError:
        # AI didn't return valid JSON
        return {
            'hint': response.choices[0].message.content,
            'encouragement': 'Keep trying!',
            'available': True
        }
    except Exception as e:
        return {
            'hint': f'AI hint service temporarily unavailable: {str(e)}',
            'available': False
        }


def get_ai_code_review(code: str, exercise_description: str) -> Dict:
    """
    Get AI code review after student passes all tests.
    Provides suggestions for improvement.
    
    Args:
        code: Student's working code
        exercise_description: What the exercise asked for
        
    Returns:
        Dictionary with feedback and suggestions
    """
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return {
            'feedback': 'Great job! AI code review is not configured.',
            'suggestions': [],
            'available': False
        }
    
    try:
        client = openai.OpenAI(api_key=api_key)
        
        prompt = f"""Review this Python code that passed all tests:

Exercise: {exercise_description}

Code:
```python
{code}
```

Provide brief feedback (2-3 points) on:
1. Code quality and style
2. Potential improvements
3. Python best practices

Be encouraging! The code already works.

Format as JSON:
{{
    "feedback": "Overall feedback in 1-2 sentences",
    "suggestions": ["suggestion 1", "suggestion 2"],
    "strengths": ["what they did well"]
}}
"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a code reviewer who focuses on best practices and learning."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=250
        )
        
        result = json.loads(response.choices[0].message.content)
        result['available'] = True
        
        return result
        
    except Exception as e:
        return {
            'feedback': 'Great job completing the exercise!',
            'suggestions': [],
            'available': False,
            'error': str(e)
        }


def validate_with_ai(code: str, requirements: str) -> Dict:
    """
    Validate code using AI (EXPENSIVE - use sparingly!).
    Only for special exercises where traditional tests don't work.
    
    Args:
        code: Student's code
        requirements: Exercise requirements
        
    Returns:
        Dictionary with validation result
    """
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return {
            'valid': False,
            'error': 'AI validation not configured',
            'available': False
        }
    
    try:
        client = openai.OpenAI(api_key=api_key)
        
        # WARNING: This is expensive! Use GPT-3.5 to save cost
        # GPT-4 would be more accurate but costs ~10x more
        
        prompt = f"""Validate if this Python code meets the requirements:

Requirements: {requirements}

Code:
```python
{code}
```

Respond with JSON:
{{
    "valid": true/false,
    "explanation": "Brief explanation",
    "issues": ["list of issues if invalid"]
}}
"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a strict code validator. Check if code meets requirements."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for consistency
            max_tokens=300
        )
        
        result = json.loads(response.choices[0].message.content)
        result['available'] = True
        result['method'] = 'ai'
        result['warning'] = 'AI validation is less reliable than traditional tests'
        
        return result
        
    except Exception as e:
        return {
            'valid': False,
            'error': f'AI validation failed: {str(e)}',
            'available': False
        }


# Cost tracking (optional)
def estimate_monthly_cost(students: int, exercises: int, attempts_per_exercise: float = 2.5) -> Dict:
    """
    Estimate monthly AI costs based on usage.
    
    Args:
        students: Number of active students
        exercises: Number of exercises
        attempts_per_exercise: Average attempts per exercise
    
    Returns:
        Cost breakdown dictionary
    """
    
    total_submissions = students * exercises * attempts_per_exercise
    
    # Cost estimates per submission (USD)
    costs = {
        'validation_gpt4': {
            'per_submission': 0.05,
            'total': total_submissions * 0.05,
            'use_case': 'AI validation (NOT RECOMMENDED - too expensive)'
        },
        'validation_gpt35': {
            'per_submission': 0.003,
            'total': total_submissions * 0.003,
            'use_case': 'AI validation (still expensive)'
        },
        'hints_on_demand': {
            'per_submission': 0.001,
            'requests': total_submissions * 0.2,  # Assume 20% request hints
            'total': total_submissions * 0.2 * 0.001,
            'use_case': 'Hints when students click "Get Hint" (RECOMMENDED)'
        },
        'code_review': {
            'per_submission': 0.002,
            'requests': total_submissions * 0.3,  # Assume 30% want review
            'total': total_submissions * 0.3 * 0.002,
            'use_case': 'Code review after passing (OPTIONAL)'
        },
        'traditional_tests': {
            'per_submission': 0.000,
            'total': 0.00,
            'use_case': 'Traditional tests (FREE!) (RECOMMENDED)'
        }
    }
    
    return {
        'total_submissions': total_submissions,
        'cost_breakdown': costs,
        'recommendation': 'Use traditional tests + optional AI hints'
    }


# Example usage
if __name__ == '__main__':
    # Example: Get cost estimate for a real platform
    costs = estimate_monthly_cost(
        students=500,
        exercises=30,
        attempts_per_exercise=2.5
    )
    
    print("Monthly Cost Estimate:")
    print(f"Total submissions: {costs['total_submissions']:,}")
    print("\nCost by approach:")
    
    for approach, data in costs['cost_breakdown'].items():
        print(f"\n{approach}:")
        print(f"  Use case: {data['use_case']}")
        print(f"  Monthly cost: ${data['total']:.2f}")
    
    print(f"\n💡 Recommendation: {costs['recommendation']}")
