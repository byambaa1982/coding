# enroll_in_mock_course.py
"""
Enroll user in the mock course for testing without payment.
This bypasses the payment system for testing purposes.
"""

from app import create_app
from app.models import TutorialUser, NewTutorial, TutorialEnrollment, TutorialOrder, TutorialOrderItem
from app.extensions import db
from datetime import datetime

app = create_app()

def enroll_user_in_mock_course(user_email=None):
    """Enroll a user in the mock course for testing."""
    
    with app.app_context():
        print("=" * 80)
        print("ENROLL USER IN MOCK COURSE (For Testing)")
        print("=" * 80)
        
        # Get the mock course
        course = NewTutorial.query.filter_by(slug='python-fundamentals-complete').first()
        
        if not course:
            print("❌ Mock course not found. Please run seed_mock_course_data.py first.")
            return
        
        print(f"\n📚 Course: {course.title}")
        print(f"   ID: {course.id}")
        print(f"   Price: ${course.price}")
        
        # Get user
        if user_email:
            user = TutorialUser.query.filter_by(email=user_email).first()
        else:
            user = TutorialUser.query.first()
        
        if not user:
            print("❌ No user found. Please register a user first.")
            return
        
        print(f"\n👤 User: {user.email}")
        print(f"   ID: {user.id}")
        
        # Check if already enrolled
        existing_enrollment = TutorialEnrollment.query.filter_by(
            user_id=user.id,
            tutorial_id=course.id
        ).first()
        
        if existing_enrollment:
            print(f"\n⚠️  User is already enrolled in this course!")
            print(f"   Enrollment ID: {existing_enrollment.id}")
            print(f"   Status: {existing_enrollment.status}")
            print(f"   Progress: {existing_enrollment.progress_percentage}%")
            
            response = input("\nDelete existing enrollment and create new one? (yes/no): ")
            if response.lower() in ['yes', 'y']:
                db.session.delete(existing_enrollment)
                db.session.commit()
                print("✅ Existing enrollment deleted.")
            else:
                print("❌ Operation cancelled.")
                return
        
        # Create order (for record keeping, marked as completed)
        order = TutorialOrder(
            user_id=user.id,
            order_number=TutorialOrder.generate_order_number(),
            status='completed',
            subtotal=0.00,  # Free for testing
            total_amount=0.00,
            currency='USD',
            payment_method='test',
            billing_name=user.full_name or user.email,
            billing_email=user.email,
            paid_at=datetime.utcnow()
        )
        db.session.add(order)
        db.session.commit()
        
        print(f"\n📝 Order created: {order.order_number}")
        
        # Create order item
        order_item = TutorialOrderItem(
            order_id=order.id,
            tutorial_id=course.id,
            tutorial_title=course.title,
            quantity=1,
            unit_price=0.00,  # Free for testing
            total_price=0.00
        )
        db.session.add(order_item)
        db.session.commit()
        
        # Create enrollment
        enrollment = TutorialEnrollment(
            user_id=user.id,
            tutorial_id=course.id,
            order_id=order.id,
            status='active',
            enrollment_type='free',  # Mark as free for testing
            progress_percentage=0.00,
            lessons_completed=0,
            exercises_completed=0
        )
        db.session.add(enrollment)
        db.session.commit()
        
        print(f"✅ Enrollment created: {enrollment.id}")
        
        print("\n" + "=" * 80)
        print("✅ SUCCESS! User enrolled in mock course")
        print("=" * 80)
        print(f"\n📊 Details:")
        print(f"   Order ID: {order.id}")
        print(f"   Order Number: {order.order_number}")
        print(f"   Enrollment ID: {enrollment.id}")
        print(f"   Status: {enrollment.status}")
        print(f"\n🎉 You can now test the learning flow!")
        print(f"\n📍 Next Steps:")
        print(f"   1. Go to: http://127.0.0.1:5000/account/my-courses")
        print(f"   2. Click 'Continue Learning' on the course")
        print(f"   3. Complete exercises and test the flow")


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("ENROLL IN MOCK COURSE FOR TESTING")
    print("=" * 80)
    
    email = input("\nEnter user email (press Enter for first user): ").strip()
    
    if not email:
        email = None
    
    enroll_user_in_mock_course(email)
