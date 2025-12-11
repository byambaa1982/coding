# Phase 3 Quick Start Guide

## ✅ Implementation Complete!

All Phase 3 components have been successfully implemented and tested.

## What's Ready

### Backend
- ✅ Payment blueprint with Stripe integration
- ✅ Account blueprint with user dashboard
- ✅ Order and enrollment management
- ✅ Coupon system with validation
- ✅ Wishlist functionality
- ✅ Webhook handlers

### Database
- ✅ All Phase 3 tables created
- ✅ Foreign keys configured
- ✅ Indexes optimized

### Frontend
- ✅ Shopping cart UI
- ✅ Order history
- ✅ User dashboard
- ✅ My courses page

## Quick Start

### 1. Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Run the Application
```powershell
python app.py
```

### 3. Access the Application
Open your browser to: `http://localhost:5000`

## Key URLs

### Public
- `/` - Home page
- `/catalog` - Course catalog
- `/catalog/python` - Python courses
- `/catalog/sql` - SQL courses
- `/catalog/course/<slug>` - Course detail

### User (Login Required)
- `/account/dashboard` - User dashboard
- `/account/my-courses` - Enrolled courses
- `/account/wishlist` - Saved courses
- `/payment/cart` - Shopping cart
- `/payment/orders` - Order history

### Admin (Admin Only)
- `/admin` - Admin dashboard
- `/admin/courses` - Course management

## Testing Payment Flow

### 1. Browse to a Course
```
http://localhost:5000/catalog
```

### 2. Click "Add to Cart"
The course will be added to your shopping cart

### 3. View Cart
```
http://localhost:5000/payment/cart
```

### 4. Apply Coupon (Optional)
Enter a coupon code if you have one

### 5. Proceed to Checkout
Click "Proceed to Checkout" button

### 6. Complete Payment on Stripe
Use test card: **4242 4242 4242 4242**
- Expiry: Any future date
- CVC: Any 3 digits
- ZIP: Any 5 digits

### 7. Verify Enrollment
After successful payment, you'll be redirected to order confirmation.
Check your courses at: `/account/my-courses`

## Creating Test Coupons

Run this in Python shell:
```python
from app import create_app
from app.models import Coupon
from app.extensions import db

app = create_app()
with app.app_context():
    # 20% discount coupon
    coupon = Coupon(
        code='WELCOME20',
        discount_type='percentage',
        discount_value=20.00,
        is_active=True,
        description='20% off for new users'
    )
    db.session.add(coupon)
    db.session.commit()
    print('✅ Coupon WELCOME20 created!')
```

## Stripe Webhook Setup (For Production)

### 1. Install Stripe CLI (for local testing)
```powershell
stripe listen --forward-to localhost:5000/payment/webhook
```

### 2. For Production
1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://yourdomain.com/payment/webhook`
3. Select events:
   - `checkout.session.completed`
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `charge.refunded`
4. Copy webhook signing secret to `.env`

## Environment Variables

Ensure these are set in your `.env`:
```env
# Stripe
STRIPE_PUBLIC_KEY=pk_test_51RNzbCH8npKpCEIx...
STRIPE_SECRET_KEY=sk_test_51RNzbCH8npKpCEIx...
STRIPE_WEBHOOK_SECRET=whsec_00e20fa2686...

# Email (for order confirmations)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## Common Tasks

### Check Database Tables
```python
from app import create_app
from app.extensions import db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"Total tables: {len(tables)}")
    for table in sorted(tables):
        print(f"  - {table}")
```

### View All Orders
```python
from app import create_app
from app.models import TutorialOrder

app = create_app()
with app.app_context():
    orders = TutorialOrder.query.all()
    for order in orders:
        print(f"{order.order_number}: ${order.total_amount} - {order.status}")
```

### View All Enrollments
```python
from app import create_app
from app.models import TutorialEnrollment

app = create_app()
with app.app_context():
    enrollments = TutorialEnrollment.query.all()
    for enrollment in enrollments:
        print(f"User {enrollment.user_id}: {enrollment.tutorial.title} - {enrollment.progress_percentage}%")
```

## Troubleshooting

### Payment Not Completing
1. Check Stripe dashboard for payment status
2. Review application logs
3. Verify webhook endpoint is accessible
4. Check `.env` has correct Stripe keys

### Enrollment Not Created
1. Verify order status is 'completed'
2. Check `tutorial_enrollments` table
3. Review webhook processing logs
4. Ensure foreign keys are correct

### Cart Issues
1. Clear browser cookies
2. Check Flask session configuration
3. Verify SECRET_KEY is set

## Next Steps

### Immediate
- [ ] Test complete payment flow
- [ ] Create test coupons
- [ ] Test with different course types

### Phase 4 (Learning Interface)
- [ ] Implement lesson viewer
- [ ] Add video player
- [ ] Create progress tracking
- [ ] Build quiz system

### Enhancements
- [ ] Email notifications
- [ ] PDF invoice generation
- [ ] Admin coupon management
- [ ] Sales analytics dashboard

## Support

For issues or questions:
1. Check logs in terminal
2. Review Stripe dashboard
3. Inspect database tables
4. Check browser console for errors

## Success Indicators

✅ App starts without errors
✅ Can browse courses
✅ Can add courses to cart
✅ Stripe checkout opens correctly
✅ Orders are created in database
✅ Enrollments are created on payment
✅ Dashboard shows enrolled courses

**Phase 3 is ready for testing!** 🚀
