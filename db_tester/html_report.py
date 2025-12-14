"""
HTML Report Generator
=====================
Generates HTML reports for test results with visual formatting.
"""

import os
from datetime import datetime
from typing import Dict, List, Any


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exercise Test Report - {course_title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 8px 8px 0 0;
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .header p {{
            opacity: 0.9;
            font-size: 14px;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #fafafa;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        
        .stat-card.success {{
            border-left-color: #10b981;
        }}
        
        .stat-card.failure {{
            border-left-color: #ef4444;
        }}
        
        .stat-card h3 {{
            font-size: 12px;
            text-transform: uppercase;
            color: #6b7280;
            margin-bottom: 8px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }}
        
        .stat-card .value {{
            font-size: 32px;
            font-weight: bold;
            color: #1f2937;
        }}
        
        .stat-card .subtext {{
            font-size: 14px;
            color: #6b7280;
            margin-top: 4px;
        }}
        
        .results {{
            padding: 30px;
        }}
        
        .results h2 {{
            font-size: 20px;
            margin-bottom: 20px;
            color: #1f2937;
        }}
        
        .exercise-card {{
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            margin-bottom: 16px;
            overflow: hidden;
            transition: box-shadow 0.2s;
        }}
        
        .exercise-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        
        .exercise-header {{
            padding: 16px 20px;
            background: #f9fafb;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .exercise-header h3 {{
            font-size: 16px;
            color: #1f2937;
            font-weight: 600;
        }}
        
        .status-badge {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .status-badge.passed {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .status-badge.failed {{
            background: #fee2e2;
            color: #991b1b;
        }}
        
        .exercise-details {{
            padding: 16px 20px;
        }}
        
        .detail-row {{
            display: flex;
            padding: 8px 0;
            border-bottom: 1px solid #f3f4f6;
        }}
        
        .detail-row:last-child {{
            border-bottom: none;
        }}
        
        .detail-label {{
            flex: 0 0 150px;
            font-weight: 600;
            color: #6b7280;
            font-size: 14px;
        }}
        
        .detail-value {{
            flex: 1;
            color: #1f2937;
            font-size: 14px;
        }}
        
        .error-box {{
            background: #fef2f2;
            border: 1px solid #fecaca;
            border-radius: 4px;
            padding: 12px;
            margin-top: 12px;
        }}
        
        .error-box h4 {{
            color: #991b1b;
            font-size: 14px;
            margin-bottom: 8px;
        }}
        
        .error-box ul {{
            list-style: none;
            padding-left: 0;
        }}
        
        .error-box li {{
            color: #7f1d1d;
            font-size: 13px;
            padding: 4px 0;
            padding-left: 20px;
            position: relative;
        }}
        
        .error-box li:before {{
            content: "•";
            position: absolute;
            left: 8px;
        }}
        
        .test-details {{
            margin-top: 16px;
            background: #f9fafb;
            border-radius: 4px;
            overflow: hidden;
        }}
        
        .test-details summary {{
            padding: 12px;
            cursor: pointer;
            font-weight: 600;
            color: #4b5563;
            font-size: 14px;
            user-select: none;
        }}
        
        .test-details summary:hover {{
            background: #f3f4f6;
        }}
        
        .test-case {{
            padding: 12px;
            border-top: 1px solid #e5e7eb;
            font-size: 13px;
        }}
        
        .test-case-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }}
        
        .test-case-title {{
            font-weight: 600;
            color: #1f2937;
        }}
        
        .test-case-result {{
            font-size: 12px;
            padding: 2px 8px;
            border-radius: 4px;
        }}
        
        .test-case-result.pass {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .test-case-result.fail {{
            background: #fee2e2;
            color: #991b1b;
        }}
        
        .test-info {{
            color: #6b7280;
            font-size: 12px;
            margin-top: 4px;
        }}
        
        .footer {{
            padding: 20px 30px;
            background: #f9fafb;
            border-top: 1px solid #e5e7eb;
            text-align: center;
            color: #6b7280;
            font-size: 12px;
        }}
        
        .progress-bar {{
            height: 8px;
            background: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 8px;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #10b981 0%, #059669 100%);
            transition: width 0.3s ease;
        }}
        
        .progress-fill.low {{
            background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%);
        }}
        
        .progress-fill.medium {{
            background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Exercise Test Report</h1>
            <p><strong>Course:</strong> {course_title}</p>
            <p><strong>Lesson:</strong> {lesson_title}</p>
            <p><strong>Test Date:</strong> {test_date}</p>
        </div>
        
        <div class="summary">
            <div class="stat-card">
                <h3>Total Exercises</h3>
                <div class="value">{total_exercises}</div>
            </div>
            
            <div class="stat-card success">
                <h3>Passed</h3>
                <div class="value">{passed_exercises}</div>
                <div class="subtext">{success_rate}% success rate</div>
            </div>
            
            <div class="stat-card failure">
                <h3>Failed</h3>
                <div class="value">{failed_exercises}</div>
            </div>
            
            <div class="stat-card">
                <h3>Total Tests</h3>
                <div class="value">{total_tests}</div>
                <div class="subtext">{tests_passed} passed, {tests_failed} failed</div>
            </div>
            
            <div class="stat-card">
                <h3>Execution Time</h3>
                <div class="value">{avg_time}ms</div>
                <div class="subtext">Average per exercise</div>
            </div>
        </div>
        
        <div class="results">
            <h2>Detailed Results</h2>
            {exercise_results}
        </div>
        
        <div class="footer">
            <p>Generated by Python Exercise QA Testing System</p>
            <p>© {year} - All Rights Reserved</p>
        </div>
    </div>
</body>
</html>
"""


def generate_html_report(results: List[Dict], summary: Dict[str, Any], 
                        output_path: str):
    """
    Generate HTML report from test results.
    
    Args:
        results: List of individual test results
        summary: Summary statistics
        output_path: Path to save HTML file
    """
    # Generate exercise results HTML
    exercise_html = []
    
    for result in results:
        status_class = 'passed' if result['validation_passed'] else 'failed'
        status_text = 'PASSED' if result['validation_passed'] else 'FAILED'
        
        # Calculate progress
        if result['total_tests'] > 0:
            progress = (result['tests_passed'] / result['total_tests']) * 100
            if progress >= 80:
                progress_class = ''
            elif progress >= 50:
                progress_class = 'medium'
            else:
                progress_class = 'low'
        else:
            progress = 0
            progress_class = 'low'
        
        # Build test details
        test_details_html = ''
        if result.get('test_details'):
            test_cases_html = []
            for test in result['test_details']:
                test_passed = test.get('passed', False)
                test_class = 'pass' if test_passed else 'fail'
                test_result_text = 'PASS' if test_passed else 'FAIL'
                
                test_html = f"""
                <div class="test-case">
                    <div class="test-case-header">
                        <span class="test-case-title">{test.get('description', 'Test')}</span>
                        <span class="test-case-result {test_class}">{test_result_text}</span>
                    </div>
                    <div class="test-info">
                        Expected: {test.get('expected', 'N/A')} | 
                        Actual: {test.get('actual', 'N/A')}
                        {f" | Error: {test.get('error')}" if test.get('error') else ''}
                    </div>
                </div>
                """
                test_cases_html.append(test_html)
            
            test_details_html = f"""
            <details class="test-details">
                <summary>View {len(result['test_details'])} Test Cases</summary>
                {''.join(test_cases_html)}
            </details>
            """
        
        # Build errors section
        errors_html = ''
        if result['errors']:
            error_items = ''.join([f'<li>{error}</li>' for error in result['errors']])
            errors_html = f"""
            <div class="error-box">
                <h4>Errors</h4>
                <ul>{error_items}</ul>
            </div>
            """
        
        exercise_html.append(f"""
        <div class="exercise-card">
            <div class="exercise-header">
                <h3>{result['exercise_title']}</h3>
                <span class="status-badge {status_class}">{status_text}</span>
            </div>
            <div class="exercise-details">
                <div class="detail-row">
                    <span class="detail-label">Exercise ID:</span>
                    <span class="detail-value">{result['exercise_id']}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Difficulty:</span>
                    <span class="detail-value">{result['difficulty']}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Tests Passed:</span>
                    <span class="detail-value">{result['tests_passed']} / {result['total_tests']}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Success Rate:</span>
                    <span class="detail-value">
                        {progress:.1f}%
                        <div class="progress-bar">
                            <div class="progress-fill {progress_class}" style="width: {progress}%"></div>
                        </div>
                    </span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Execution Time:</span>
                    <span class="detail-value">{result['execution_time_ms']}ms</span>
                </div>
                {errors_html}
                {test_details_html}
            </div>
        </div>
        """)
    
    # Fill in template
    html = HTML_TEMPLATE.format(
        course_title=summary['course_title'],
        lesson_title=summary['lesson_title'],
        test_date=summary['test_date'],
        total_exercises=summary['total_exercises'],
        passed_exercises=summary['passed_exercises'],
        failed_exercises=summary['failed_exercises'],
        success_rate=f"{summary['success_rate']:.1f}",
        total_tests=summary['total_test_cases'],
        tests_passed=summary['total_tests_passed'],
        tests_failed=summary['total_tests_failed'],
        avg_time=int(summary['avg_execution_time_ms']),
        exercise_results=''.join(exercise_html),
        year=datetime.now().year
    )
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"📊 HTML report saved to: {output_path}")


if __name__ == '__main__':
    # Example usage
    print("HTML Report Generator")
    print("Import this module and use generate_html_report() function")
