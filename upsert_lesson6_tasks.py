"""
Upsert Lesson 6 Tasks to Database
==================================
This script parses the markdown file containing lesson tasks and upserts them
into the Exercise table, matching them to Course 5 and Lesson 6.
"""

import re
import json
from datetime import datetime
from app import create_app
from app.models import Exercise, NewTutorial, Lesson
from app.extensions import db


class TaskParser:
    """Parse tasks from markdown file."""
    
    def __init__(self, markdown_file):
        self.markdown_file = markdown_file
        self.tasks = []
    
    def parse(self):
        """Parse the markdown file and extract tasks."""
        with open(self.markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split content by task sections
        task_sections = re.split(r'\n---\n\n(?=## Task \d+:)', content)
        
        for section in task_sections:
            if not section.strip() or not section.startswith('## Task'):
                continue
            
            # Extract task number and title
            title_match = re.search(r'## Task (\d+): (.+?)$', section, re.MULTILINE)
            if not title_match:
                continue
            
            task_num = int(title_match.group(1))
            title = title_match.group(2).strip()
            
            # Extract objective
            objective_match = re.search(r'\*\*Objective:\*\* (.+?)$', section, re.MULTILINE)
            objective = objective_match.group(1).strip() if objective_match else ""
            
            # Extract instructions (between **Instructions:** and **Expected or **Difficulty)
            instructions_match = re.search(r'\*\*Instructions:\*\*\n(.*?)(?=\n\*\*(?:Expected|Difficulty))', section, re.DOTALL)
            instructions = instructions_match.group(1).strip() if instructions_match else ""
            
            # Extract difficulty
            difficulty_match = re.search(r'\*\*Difficulty:\*\* (Easy|Medium|Hard)', section, re.IGNORECASE)
            difficulty = difficulty_match.group(1).lower() if difficulty_match else 'easy'
            
            # Extract time
            time_match = re.search(r'\*\*Estimated Time:\*\* (\d+)', section)
            estimated_minutes = int(time_match.group(1)) if time_match else 15
            
            # Extract expected output/deliverable section
            expected_output = ""
            output_match = re.search(r'\*\*Expected (?:Output|Deliverable)[^:]*:\*\*[^\n]*\n(.*?)(?=\n\*\*Difficulty)', section, re.DOTALL)
            if output_match:
                expected_output = output_match.group(1).strip()
            
            # Build full description
            description = f"{objective}\n\n{instructions}"
            if expected_output:
                description += f"\n\n{expected_output}"
            
            # Calculate points based on difficulty
            points_map = {'easy': 10, 'medium': 15, 'hard': 20}
            points = points_map.get(difficulty, 10)
            
            task = {
                'order_index': task_num,
                'title': title,
                'description': description,
                'objective': objective,
                'difficulty': difficulty,
                'estimated_minutes': estimated_minutes,
                'points': points
            }
            
            self.tasks.append(task)
        
        return self.tasks


class TaskUpserter:
    """Upsert tasks into the database."""
    
    def __init__(self, app, course_id=5, lesson_id=6):
        self.app = app
        self.course_id = course_id
        self.lesson_id = lesson_id
    
    def validate_course_and_lesson(self):
        """Check if course and lesson exist."""
        tutorial = NewTutorial.query.get(self.course_id)
        if not tutorial:
            raise ValueError(f"Tutorial with ID {self.course_id} not found")
        
        lesson = Lesson.query.get(self.lesson_id)
        if not lesson:
            raise ValueError(f"Lesson with ID {self.lesson_id} not found")
        
        if lesson.tutorial_id != self.course_id:
            raise ValueError(f"Lesson {self.lesson_id} does not belong to Tutorial {self.course_id}")
        
        return tutorial, lesson
    
    def generate_slug(self, title, order_index):
        """Generate a URL-friendly slug from title."""
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower())
        slug = slug.strip('-')
        return f"lesson6-task{order_index}-{slug}"
    
    def upsert_task(self, task_data):
        """Insert or update a single task."""
        slug = self.generate_slug(task_data['title'], task_data['order_index'])
        
        # Try to find existing exercise by slug or by lesson_id + order_index
        exercise = Exercise.query.filter_by(slug=slug).first()
        
        if not exercise:
            # Try to find by lesson_id and order_index
            exercise = Exercise.query.filter_by(
                lesson_id=self.lesson_id,
                order_index=task_data['order_index']
            ).first()
        
        if exercise:
            # Update existing exercise
            exercise.title = task_data['title']
            exercise.description = task_data['description']
            exercise.difficulty = task_data['difficulty']
            exercise.points = task_data['points']
            exercise.slug = slug
            exercise.updated_at = datetime.utcnow()
            action = 'updated'
        else:
            # Create new exercise
            exercise = Exercise(
                tutorial_id=self.course_id,
                lesson_id=self.lesson_id,
                title=task_data['title'],
                slug=slug,
                description=task_data['description'],
                exercise_type='python',
                difficulty=task_data['difficulty'],
                order_index=task_data['order_index'],
                points=task_data['points'],
                starter_code='# Write your solution here\n',
                solution_code='# Solution will be provided by instructor\n',
                test_cases=json.dumps([]),
                hints=json.dumps([])
            )
            db.session.add(exercise)
            action = 'created'
        
        db.session.commit()
        return exercise, action
    
    def upsert_all(self, tasks):
        """Upsert all tasks."""
        results = []
        
        try:
            tutorial, lesson = self.validate_course_and_lesson()
            print(f"✓ Validated Tutorial: {tutorial.title}")
            print(f"✓ Validated Lesson: {lesson.title}")
            print(f"\nUpserting {len(tasks)} tasks...\n")
            
            for task in tasks:
                try:
                    exercise, action = self.upsert_task(task)
                    results.append({
                        'exercise_id': exercise.id,
                        'title': exercise.title,
                        'action': action,
                        'success': True,
                        'error': None
                    })
                    print(f"✓ Task {task['order_index']}: {exercise.title} ({action})")
                except Exception as e:
                    results.append({
                        'exercise_id': None,
                        'title': task['title'],
                        'action': 'failed',
                        'success': False,
                        'error': str(e)
                    })
                    print(f"✗ Task {task['order_index']}: {task['title']} (FAILED: {str(e)})")
                    db.session.rollback()
            
            return results
            
        except Exception as e:
            print(f"✗ Validation failed: {str(e)}")
            return []


def main():
    """Main execution function."""
    import os
    
    # Setup
    markdown_file = os.path.join(
        os.path.dirname(__file__),
        'contents',
        'lesson6_variables_datatypes_tasks.md'
    )
    
    if not os.path.exists(markdown_file):
        print(f"Error: File not found: {markdown_file}")
        return
    
    # Create app context
    app = create_app()
    
    with app.app_context():
        print("="*80)
        print("LESSON 6 TASKS UPSERTER")
        print("="*80)
        print(f"Source file: {markdown_file}")
        print()
        
        # Parse tasks
        parser = TaskParser(markdown_file)
        tasks = parser.parse()
        
        if not tasks:
            print("✗ No tasks found in markdown file")
            return
        
        print(f"✓ Parsed {len(tasks)} tasks from markdown\n")
        
        # Upsert tasks
        upserter = TaskUpserter(app, course_id=5, lesson_id=6)
        results = upserter.upsert_all(tasks)
        
        # Print summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        created = [r for r in successful if r['action'] == 'created']
        updated = [r for r in successful if r['action'] == 'updated']
        
        print(f"Total tasks: {len(results)}")
        print(f"✓ Created: {len(created)}")
        print(f"✓ Updated: {len(updated)}")
        print(f"✗ Failed: {len(failed)}")
        
        if failed:
            print("\nFailed tasks:")
            for f in failed:
                print(f"  - {f['title']}: {f['error']}")


if __name__ == '__main__':
    main()
