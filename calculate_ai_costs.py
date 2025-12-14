"""
AI Cost Calculator and Usage Monitor for Hybrid Validation System

This script helps you:
1. Estimate monthly AI costs based on student usage
2. Track actual API usage (if integrated with database)
3. Set budget alerts
4. Compare different pricing scenarios
"""

import os
from datetime import datetime, timedelta


class AIUsageCalculator:
    """Calculate and monitor AI API costs."""
    
    # OpenAI GPT-3.5-turbo pricing (as of Dec 2024)
    GPT35_INPUT_COST = 0.0005 / 1000  # $0.50 per 1M tokens
    GPT35_OUTPUT_COST = 0.0015 / 1000  # $1.50 per 1M tokens
    
    # OpenAI GPT-4o pricing
    GPT4_INPUT_COST = 0.005 / 1000  # $5.00 per 1M tokens
    GPT4_OUTPUT_COST = 0.015 / 1000  # $15.00 per 1M tokens
    
    # Average token usage per request
    HINT_INPUT_TOKENS = 500   # Code + context + prompt
    HINT_OUTPUT_TOKENS = 100  # Short encouraging hint
    
    REVIEW_INPUT_TOKENS = 600   # Code + context + prompt
    REVIEW_OUTPUT_TOKENS = 150  # Detailed review
    
    def __init__(self, model='gpt-3.5-turbo'):
        self.model = model
        
        if 'gpt-4' in model.lower():
            self.input_cost = self.GPT4_INPUT_COST
            self.output_cost = self.GPT4_OUTPUT_COST
        else:
            self.input_cost = self.GPT35_INPUT_COST
            self.output_cost = self.GPT35_OUTPUT_COST
    
    def estimate_hint_cost(self):
        """Estimate cost per hint request."""
        input_cost = self.HINT_INPUT_TOKENS * self.input_cost
        output_cost = self.HINT_OUTPUT_TOKENS * self.output_cost
        return input_cost + output_cost
    
    def estimate_review_cost(self):
        """Estimate cost per review request."""
        input_cost = self.REVIEW_INPUT_TOKENS * self.input_cost
        output_cost = self.REVIEW_OUTPUT_TOKENS * self.output_cost
        return input_cost + output_cost
    
    def estimate_monthly_cost(self, active_students, hints_per_student=0.5, reviews_per_student=0.2):
        """
        Estimate monthly AI costs.
        
        Args:
            active_students: Number of active students per month
            hints_per_student: Average hints requested per student per month
            reviews_per_student: Average reviews requested per student per month
            
        Returns:
            Dictionary with cost breakdown
        """
        
        total_hints = active_students * hints_per_student
        total_reviews = active_students * reviews_per_student
        
        hint_cost = total_hints * self.estimate_hint_cost()
        review_cost = total_reviews * self.estimate_review_cost()
        total_cost = hint_cost + review_cost
        
        return {
            'model': self.model,
            'active_students': active_students,
            'total_hints': int(total_hints),
            'total_reviews': int(total_reviews),
            'hint_cost_per_request': self.estimate_hint_cost(),
            'review_cost_per_request': self.estimate_review_cost(),
            'monthly_hint_cost': hint_cost,
            'monthly_review_cost': review_cost,
            'total_monthly_cost': total_cost,
            'cost_per_student': total_cost / active_students if active_students > 0 else 0
        }
    
    def compare_scenarios(self, active_students):
        """Compare different usage scenarios."""
        
        scenarios = [
            {
                'name': 'Conservative (10% need help)',
                'hints_per_student': 0.3,
                'reviews_per_student': 0.1
            },
            {
                'name': 'Moderate (20% need help)',
                'hints_per_student': 0.6,
                'reviews_per_student': 0.2
            },
            {
                'name': 'Heavy (40% need help)',
                'hints_per_student': 1.2,
                'reviews_per_student': 0.4
            },
            {
                'name': 'Very Heavy (all students use)',
                'hints_per_student': 3.0,
                'reviews_per_student': 1.0
            }
        ]
        
        results = []
        for scenario in scenarios:
            cost = self.estimate_monthly_cost(
                active_students,
                scenario['hints_per_student'],
                scenario['reviews_per_student']
            )
            cost['scenario'] = scenario['name']
            results.append(cost)
        
        return results
    
    def print_cost_report(self, active_students):
        """Print a detailed cost report."""
        
        print("=" * 80)
        print("AI COST ESTIMATION REPORT")
        print("=" * 80)
        print(f"\nModel: {self.model}")
        print(f"Active Students: {active_students:,}")
        print(f"\nPer-Request Costs:")
        print(f"  - Hint: ${self.estimate_hint_cost():.6f} (~${self.estimate_hint_cost():.4f})")
        print(f"  - Review: ${self.estimate_review_cost():.6f} (~${self.estimate_review_cost():.4f})")
        
        print("\n" + "=" * 80)
        print("MONTHLY COST SCENARIOS")
        print("=" * 80)
        
        scenarios = self.compare_scenarios(active_students)
        
        for scenario in scenarios:
            print(f"\n📊 {scenario['scenario']}")
            print(f"   Hints: {scenario['total_hints']:,} requests × ${scenario['hint_cost_per_request']:.6f} = ${scenario['monthly_hint_cost']:.2f}")
            print(f"   Reviews: {scenario['total_reviews']:,} requests × ${scenario['review_cost_per_request']:.6f} = ${scenario['monthly_review_cost']:.2f}")
            print(f"   💰 Total: ${scenario['total_monthly_cost']:.2f}/month (${scenario['cost_per_student']:.3f} per student)")
        
        print("\n" + "=" * 80)
        print("COST COMPARISON: GPT-3.5 vs GPT-4")
        print("=" * 80)
        
        # Compare models
        gpt35 = AIUsageCalculator('gpt-3.5-turbo')
        gpt4 = AIUsageCalculator('gpt-4o')
        
        moderate_scenario = {
            'hints_per_student': 0.6,
            'reviews_per_student': 0.2
        }
        
        gpt35_cost = gpt35.estimate_monthly_cost(active_students, **moderate_scenario)
        gpt4_cost = gpt4.estimate_monthly_cost(active_students, **moderate_scenario)
        
        print(f"\nModerate Usage (20% students need help):")
        print(f"  GPT-3.5-turbo: ${gpt35_cost['total_monthly_cost']:.2f}/month")
        print(f"  GPT-4o: ${gpt4_cost['total_monthly_cost']:.2f}/month")
        print(f"  Difference: ${gpt4_cost['total_monthly_cost'] - gpt35_cost['total_monthly_cost']:.2f}/month ({(gpt4_cost['total_monthly_cost'] / gpt35_cost['total_monthly_cost']):.1f}x more expensive)")
        
        print("\n" + "=" * 80)
        print("BUDGET RECOMMENDATIONS")
        print("=" * 80)
        
        conservative = scenarios[0]
        moderate = scenarios[1]
        heavy = scenarios[2]
        
        print(f"\n💡 Recommended monthly budget:")
        print(f"   Minimum: ${conservative['total_monthly_cost']:.2f} (if 10% need help)")
        print(f"   Expected: ${moderate['total_monthly_cost']:.2f} (if 20% need help)")
        print(f"   Maximum: ${heavy['total_monthly_cost']:.2f} (if 40% need help)")
        
        print(f"\n⚠️ Set OpenAI billing alert at: ${heavy['total_monthly_cost'] * 1.5:.2f}")
        
        print("\n" + "=" * 80)
        print("SAVINGS vs FULL AI VALIDATION")
        print("=" * 80)
        
        # Estimate full AI validation cost
        exercises_per_student = 50  # Average exercises per month
        full_ai_cost_per_validation = 0.01  # ~$0.01 per full AI validation
        full_ai_monthly = active_students * exercises_per_student * full_ai_cost_per_validation
        
        hybrid_cost = moderate['total_monthly_cost']
        savings = full_ai_monthly - hybrid_cost
        savings_percent = (savings / full_ai_monthly) * 100
        
        print(f"\nFull AI Validation: ${full_ai_monthly:.2f}/month")
        print(f"Hybrid System: ${hybrid_cost:.2f}/month")
        print(f"💰 Savings: ${savings:.2f}/month ({savings_percent:.1f}%)")
        print(f"📈 Cost Reduction: {full_ai_monthly / hybrid_cost:.1f}x cheaper!")
        
        print("\n" + "=" * 80)


def main():
    """Run cost analysis."""
    
    print("\n🚀 HYBRID VALIDATION SYSTEM - COST CALCULATOR\n")
    
    # Get current configuration
    model = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
    print(f"Current model from .env: {model}\n")
    
    # Prompt for student count
    try:
        student_count = int(input("Enter number of active students per month (default 500): ") or 500)
    except ValueError:
        student_count = 500
        print(f"Using default: {student_count} students\n")
    
    # Create calculator
    calculator = AIUsageCalculator(model)
    
    # Print detailed report
    calculator.print_cost_report(student_count)
    
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("\n1. Review your .env file:")
    print("   - Check OPENAI_API_KEY is set")
    print("   - Confirm AI_MODEL setting (gpt-3.5-turbo recommended)")
    
    print("\n2. Set up billing alerts in OpenAI dashboard:")
    print(f"   - Soft limit: ${calculator.estimate_monthly_cost(student_count, 0.6, 0.2)['total_monthly_cost'] * 1.2:.2f}")
    print(f"   - Hard limit: ${calculator.estimate_monthly_cost(student_count, 1.2, 0.4)['total_monthly_cost'] * 1.5:.2f}")
    
    print("\n3. Monitor actual usage:")
    print("   - Track hint/review requests in database")
    print("   - Compare actual vs estimated costs")
    print("   - Adjust student behavior if needed")
    
    print("\n4. Optimize if costs too high:")
    print("   - Use GPT-3.5 instead of GPT-4")
    print("   - Add rate limiting (max 3 hints/minute)")
    print("   - Make AI features opt-in only")
    print("   - Reduce max_tokens in prompts")
    
    print("\n✅ Done! Your hybrid system combines:")
    print("   • Traditional validation (FREE, unlimited)")
    print("   • AI enhancement (cheap, on-demand)")
    print("   • Best of both worlds!")
    print("\n")


if __name__ == '__main__':
    main()
