# app/payment/routes.py
"""Payment and checkout routes."""

import json
import logging
from datetime import datetime
from decimal import Decimal
from flask import render_template, redirect, url_for, flash, request, jsonify, session, current_app
from flask_login import login_required, current_user
from sqlalchemy import and_

from app.payment import payment_bp
from app.payment.stripe_utils import (
    create_checkout_session,
    retrieve_checkout_session,
    construct_webhook_event,
    format_stripe_amount,
    create_refund
)
from app.payment.forms import CheckoutForm, CouponForm
from app.models import (
    NewTutorial, TutorialOrder, TutorialOrderItem, TutorialEnrollment,
    Coupon, Wishlist
)
from app.extensions import db

logger = logging.getLogger(__name__)


@payment_bp.route('/cart')
@login_required
def cart():
    """Display shopping cart."""
    cart_items = session.get('cart', [])
    
    # Fetch tutorial details
    tutorials = []
    subtotal = Decimal('0.00')
    
    for item in cart_items:
        tutorial = NewTutorial.query.get(item['tutorial_id'])
        if tutorial and tutorial.status == 'published':
            # Check if already enrolled
            existing_enrollment = TutorialEnrollment.query.filter_by(
                user_id=current_user.id,
                tutorial_id=tutorial.id,
                status='active'
            ).first()
            
            if not existing_enrollment:
                tutorials.append({
                    'tutorial': tutorial,
                    'quantity': item.get('quantity', 1)
                })
                subtotal += Decimal(str(tutorial.price))
    
    # Apply coupon if exists
    coupon_code = session.get('coupon_code')
    discount_amount = Decimal('0.00')
    coupon = None
    
    if coupon_code:
        coupon = Coupon.query.filter_by(code=coupon_code, is_active=True).first()
        if coupon:
            is_valid, message = coupon.is_valid(
                user_id=current_user.id,
                cart_total=float(subtotal),
                tutorial_ids=[t['tutorial'].id for t in tutorials]
            )
            if is_valid:
                discount_amount = Decimal(str(coupon.calculate_discount(float(subtotal))))
            else:
                session.pop('coupon_code', None)
                flash(message, 'warning')
                coupon = None
    
    total = subtotal - discount_amount
    
    return render_template('payment/cart.html',
                         cart_items=tutorials,
                         subtotal=subtotal,
                         discount_amount=discount_amount,
                         total=total,
                         coupon=coupon)


@payment_bp.route('/enroll-free/<int:tutorial_id>', methods=['POST'])
@login_required
def enroll_free(tutorial_id):
    """Enroll in a free course directly."""
    tutorial = NewTutorial.query.get_or_404(tutorial_id)
    
    # Verify it's a free course
    if not tutorial.is_free:
        flash('This course is not free. Please add it to cart.', 'error')
        return redirect(url_for('catalog.course_detail', slug=tutorial.slug))
    
    # Check if already enrolled
    existing_enrollment = TutorialEnrollment.query.filter_by(
        user_id=current_user.id,
        tutorial_id=tutorial_id,
        status='active'
    ).first()
    
    if existing_enrollment:
        flash('You are already enrolled in this course!', 'info')
        return redirect(url_for('account.my_courses'))
    
    # Check if tutorial is published
    if tutorial.status != 'published':
        flash('This course is not available.', 'error')
        return redirect(url_for('catalog.index'))
    
    # Create enrollment directly
    enrollment = TutorialEnrollment(
        user_id=current_user.id,
        tutorial_id=tutorial_id,
        status='active',
        enrollment_type='free'
    )
    db.session.add(enrollment)
    db.session.commit()
    
    flash(f'Successfully enrolled in "{tutorial.title}"! Start learning now.', 'success')
    return redirect(url_for('account.my_courses'))


@payment_bp.route('/add-to-cart/<int:tutorial_id>', methods=['POST'])
@login_required
def add_to_cart(tutorial_id):
    """Add course to cart."""
    tutorial = NewTutorial.query.get_or_404(tutorial_id)
    
    # Check if already enrolled
    existing_enrollment = TutorialEnrollment.query.filter_by(
        user_id=current_user.id,
        tutorial_id=tutorial_id,
        status='active'
    ).first()
    
    if existing_enrollment:
        flash('You are already enrolled in this course.', 'info')
        return redirect(url_for('catalog.course_detail', slug=tutorial.slug))
    
    # Check if tutorial is published
    if tutorial.status != 'published':
        flash('This course is not available for purchase.', 'error')
        return redirect(url_for('catalog.index'))
    
    # Add to cart
    cart = session.get('cart', [])
    
    # Check if already in cart
    if any(item['tutorial_id'] == tutorial_id for item in cart):
        flash('This course is already in your cart.', 'info')
    else:
        cart.append({
            'tutorial_id': tutorial_id,
            'quantity': 1
        })
        session['cart'] = cart
        flash(f'Added "{tutorial.title}" to cart.', 'success')
    
    return redirect(url_for('payment.cart'))


@payment_bp.route('/remove-from-cart/<int:tutorial_id>', methods=['POST'])
@login_required
def remove_from_cart(tutorial_id):
    """Remove course from cart."""
    cart = session.get('cart', [])
    cart = [item for item in cart if item['tutorial_id'] != tutorial_id]
    session['cart'] = cart
    
    flash('Item removed from cart.', 'success')
    return redirect(url_for('payment.cart'))


@payment_bp.route('/apply-coupon', methods=['POST'])
@login_required
def apply_coupon():
    """Apply coupon code to cart."""
    form = CouponForm()
    
    if form.validate_on_submit():
        coupon_code = form.coupon_code.data.strip().upper()
        
        # Find coupon
        coupon = Coupon.query.filter_by(code=coupon_code, is_active=True).first()
        
        if not coupon:
            flash('Invalid coupon code.', 'error')
            return redirect(url_for('payment.cart'))
        
        # Calculate cart total
        cart_items = session.get('cart', [])
        subtotal = Decimal('0.00')
        for item in cart_items:
            tutorial = NewTutorial.query.get(item['tutorial_id'])
            if tutorial:
                subtotal += Decimal(str(tutorial.price))
        
        # Validate coupon
        is_valid, message = coupon.is_valid(
            user_id=current_user.id,
            cart_total=float(subtotal)
        )
        
        if is_valid:
            session['coupon_code'] = coupon_code
            flash(f'Coupon applied! You save ${coupon.calculate_discount(float(subtotal)):.2f}', 'success')
        else:
            flash(message, 'error')
    
    return redirect(url_for('payment.cart'))


@payment_bp.route('/remove-coupon', methods=['POST'])
@login_required
def remove_coupon():
    """Remove coupon from cart."""
    session.pop('coupon_code', None)
    flash('Coupon removed.', 'info')
    return redirect(url_for('payment.cart'))


@payment_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Process checkout and create Stripe session."""
    cart_items = session.get('cart', [])
    
    if not cart_items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('catalog.index'))
    
    # Fetch tutorial details
    tutorials = []
    for item in cart_items:
        tutorial = NewTutorial.query.get(item['tutorial_id'])
        if tutorial and tutorial.status == 'published':
            # Check if already enrolled
            existing_enrollment = TutorialEnrollment.query.filter_by(
                user_id=current_user.id,
                tutorial_id=tutorial.id,
                status='active'
            ).first()
            
            if not existing_enrollment:
                tutorials.append({
                    'tutorial': tutorial,
                    'quantity': item.get('quantity', 1)
                })
    
    if not tutorials:
        flash('No valid items in cart.', 'warning')
        return redirect(url_for('payment.cart'))
    
    try:
        # Get coupon if applied
        coupon_code = session.get('coupon_code')
        
        # Create Stripe checkout session
        success_url = url_for('payment.checkout_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}'
        cancel_url = url_for('payment.checkout_cancel', _external=True)
        
        stripe_session = create_checkout_session(
            user=current_user,
            cart_items=tutorials,
            success_url=success_url,
            cancel_url=cancel_url,
            coupon_code=coupon_code
        )
        
        # Create pending order in database
        order = create_pending_order(
            user=current_user,
            tutorials=tutorials,
            stripe_session_id=stripe_session['session_id'],
            stripe_customer_id=stripe_session['customer_id'],
            coupon_code=coupon_code
        )
        
        # Store order ID in session for later
        session['pending_order_id'] = order.id
        
        # Redirect to Stripe checkout
        return redirect(stripe_session['checkout_url'])
        
    except Exception as e:
        logger.error(f"Checkout error: {str(e)}")
        flash('An error occurred during checkout. Please try again.', 'error')
        return redirect(url_for('payment.cart'))


def create_pending_order(user, tutorials, stripe_session_id, stripe_customer_id, coupon_code=None):
    """Create a pending order in database."""
    subtotal = Decimal('0.00')
    
    # Calculate subtotal
    for item in tutorials:
        tutorial = item['tutorial']
        subtotal += Decimal(str(tutorial.price)) * item['quantity']
    
    # Apply discount if coupon exists
    discount_amount = Decimal('0.00')
    coupon_discount_percentage = None
    
    if coupon_code:
        coupon = Coupon.query.filter_by(code=coupon_code, is_active=True).first()
        if coupon:
            is_valid, _ = coupon.is_valid(user_id=user.id, cart_total=float(subtotal))
            if is_valid:
                discount_amount = Decimal(str(coupon.calculate_discount(float(subtotal))))
                if coupon.discount_type == 'percentage':
                    coupon_discount_percentage = coupon.discount_value
    
    total = subtotal - discount_amount
    
    # Create order
    order = TutorialOrder(
        user_id=user.id,
        order_number=TutorialOrder.generate_order_number(),
        status='pending',
        subtotal=subtotal,
        discount_amount=discount_amount,
        tax_amount=Decimal('0.00'),
        total_amount=total,
        coupon_code=coupon_code,
        coupon_discount_percentage=coupon_discount_percentage,
        stripe_checkout_session_id=stripe_session_id,
        stripe_customer_id=stripe_customer_id,
        billing_name=user.full_name,
        billing_email=user.email
    )
    
    db.session.add(order)
    db.session.flush()  # Get order ID
    
    # Create order items
    for item in tutorials:
        tutorial = item['tutorial']
        quantity = item['quantity']
        
        order_item = TutorialOrderItem(
            order_id=order.id,
            tutorial_id=tutorial.id,
            tutorial_title=tutorial.title,
            quantity=quantity,
            unit_price=Decimal(str(tutorial.price)),
            total_price=Decimal(str(tutorial.price)) * quantity
        )
        db.session.add(order_item)
    
    db.session.commit()
    logger.info(f"Created pending order {order.order_number} for user {user.id}")
    
    return order


@payment_bp.route('/checkout/success')
@login_required
def checkout_success():
    """Handle successful payment."""
    session_id = request.args.get('session_id')
    
    if not session_id:
        flash('Invalid payment session.', 'error')
        return redirect(url_for('catalog.index'))
    
    try:
        # Retrieve Stripe session
        stripe_session = retrieve_checkout_session(session_id)
        
        # Find order
        order = TutorialOrder.query.filter_by(
            stripe_checkout_session_id=session_id
        ).first()
        
        if not order:
            flash('Order not found.', 'error')
            return redirect(url_for('catalog.index'))
        
        # Check if already processed
        if order.status == 'completed':
            flash('This order has already been processed.', 'info')
            return redirect(url_for('payment.order_confirmation', order_id=order.id))
        
        # Update order with payment info
        order.status = 'completed'
        # Extract payment intent ID (could be string or object)
        payment_intent_id = stripe_session.payment_intent
        if hasattr(payment_intent_id, 'id'):
            payment_intent_id = payment_intent_id.id
        order.stripe_payment_intent_id = payment_intent_id
        order.paid_at = datetime.utcnow()
        
        # Get receipt URL if available
        if payment_intent_id:
            try:
                from app.payment.stripe_utils import retrieve_payment_intent
                payment_intent = retrieve_payment_intent(payment_intent_id)
                if hasattr(payment_intent.charges, 'data') and payment_intent.charges.data:
                    order.receipt_url = payment_intent.charges.data[0].receipt_url
            except Exception as e:
                logger.warning(f"Could not retrieve receipt URL: {str(e)}")
        
        # Create enrollments for purchased courses
        for order_item in order.items:
            # Check if enrollment already exists
            existing_enrollment = TutorialEnrollment.query.filter_by(
                user_id=order.user_id,
                tutorial_id=order_item.tutorial_id
            ).first()
            
            if not existing_enrollment:
                enrollment = TutorialEnrollment(
                    user_id=order.user_id,
                    tutorial_id=order_item.tutorial_id,
                    order_id=order.id,
                    status='active',
                    enrollment_type='paid'
                )
                db.session.add(enrollment)
                
                # Update tutorial enrollment count
                tutorial = order_item.tutorial
                tutorial.enrollment_count += 1
                
                # Remove from wishlist if exists
                wishlist_item = Wishlist.query.filter_by(
                    user_id=order.user_id,
                    tutorial_id=order_item.tutorial_id
                ).first()
                if wishlist_item:
                    db.session.delete(wishlist_item)
        
        # Update coupon usage if applicable
        if order.coupon_code:
            coupon = Coupon.query.filter_by(code=order.coupon_code).first()
            if coupon:
                coupon.times_used += 1
        
        db.session.commit()
        
        # Clear cart and session data
        session.pop('cart', None)
        session.pop('coupon_code', None)
        session.pop('pending_order_id', None)
        
        logger.info(f"Completed order {order.order_number} for user {order.user_id}")
        
        flash('Payment successful! You now have access to your courses.', 'success')
        return redirect(url_for('account.my_courses'))
        
    except Exception as e:
        logger.error(f"Error processing successful payment: {str(e)}")
        flash('An error occurred while processing your payment. Please contact support.', 'error')
        return redirect(url_for('catalog.index'))


@payment_bp.route('/checkout/cancel')
@login_required
def checkout_cancel():
    """Handle cancelled payment."""
    flash('Payment was cancelled. Your cart items have been saved.', 'info')
    return redirect(url_for('payment.cart'))


@payment_bp.route('/order/<int:order_id>')
@login_required
def order_confirmation(order_id):
    """Display order confirmation."""
    order = TutorialOrder.query.get_or_404(order_id)
    
    # Verify user owns this order
    if order.user_id != current_user.id and not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('catalog.index'))
    
    return render_template('payment/order_confirmation.html', order=order)


@payment_bp.route('/orders')
@login_required
def order_history():
    """Display user's order history."""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    orders = TutorialOrder.query.filter_by(user_id=current_user.id)\
        .order_by(TutorialOrder.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('payment/order_history.html', orders=orders)


@payment_bp.route('/invoice/<int:order_id>')
@login_required
def download_invoice(order_id):
    """Generate and download invoice PDF."""
    order = TutorialOrder.query.get_or_404(order_id)
    
    # Verify user owns this order
    if order.user_id != current_user.id and not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('catalog.index'))
    
    # TODO: Implement PDF generation
    flash('Invoice download will be available soon.', 'info')
    return redirect(url_for('payment.order_confirmation', order_id=order_id))


@payment_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events."""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = construct_webhook_event(payload, sig_header)
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    
    # Handle different event types
    event_type = event['type']
    
    if event_type == 'checkout.session.completed':
        handle_checkout_completed(event['data']['object'])
    elif event_type == 'payment_intent.succeeded':
        handle_payment_succeeded(event['data']['object'])
    elif event_type == 'payment_intent.payment_failed':
        handle_payment_failed(event['data']['object'])
    elif event_type == 'charge.refunded':
        handle_charge_refunded(event['data']['object'])
    
    return jsonify({'status': 'success'}), 200


def handle_checkout_completed(session):
    """Handle completed checkout session."""
    try:
        order = TutorialOrder.query.filter_by(
            stripe_checkout_session_id=session['id']
        ).first()
        
        if order and order.status == 'pending':
            logger.info(f"Processing webhook for order {order.order_number}")
            # Payment confirmation will be handled in checkout_success route
            # This is a backup in case user doesn't complete the redirect
            
    except Exception as e:
        logger.error(f"Error handling checkout completed: {str(e)}")


def handle_payment_succeeded(payment_intent):
    """Handle successful payment intent."""
    logger.info(f"Payment succeeded: {payment_intent['id']}")


def handle_payment_failed(payment_intent):
    """Handle failed payment intent."""
    try:
        order = TutorialOrder.query.filter_by(
            stripe_payment_intent_id=payment_intent['id']
        ).first()
        
        if order:
            order.status = 'failed'
            db.session.commit()
            logger.warning(f"Payment failed for order {order.order_number}")
            
    except Exception as e:
        logger.error(f"Error handling payment failed: {str(e)}")


def handle_charge_refunded(charge):
    """Handle refunded charge."""
    try:
        payment_intent_id = charge.get('payment_intent')
        
        if payment_intent_id:
            order = TutorialOrder.query.filter_by(
                stripe_payment_intent_id=payment_intent_id
            ).first()
            
            if order:
                order.status = 'refunded'
                order.refunded_at = datetime.utcnow()
                
                # Revoke enrollments
                for enrollment in order.enrollments:
                    enrollment.status = 'refunded'
                
                db.session.commit()
                logger.info(f"Refunded order {order.order_number}")
                
    except Exception as e:
        logger.error(f"Error handling charge refunded: {str(e)}")


@payment_bp.route('/pricing')
def pricing():
    """Display pricing page with all courses."""
    python_courses = NewTutorial.query.filter_by(
        course_type='python',
        status='published'
    ).order_by(NewTutorial.difficulty_level).all()
    
    sql_courses = NewTutorial.query.filter_by(
        course_type='sql',
        status='published'
    ).order_by(NewTutorial.difficulty_level).all()
    
    return render_template('payment/pricing.html',
                         python_courses=python_courses,
                         sql_courses=sql_courses)
