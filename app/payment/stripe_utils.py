# app/payment/stripe_utils.py
"""Stripe integration utilities."""

import stripe
import logging
from flask import current_app, url_for
from decimal import Decimal

logger = logging.getLogger(__name__)


def init_stripe():
    """Initialize Stripe with secret key."""
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']


def create_checkout_session(user, cart_items, success_url=None, cancel_url=None, coupon_code=None):
    """
    Create a Stripe Checkout session for purchasing courses.
    
    Args:
        user: TutorialUser object
        cart_items: List of dicts with 'tutorial' and 'quantity' keys
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect if payment is cancelled
        coupon_code: Optional coupon code to apply
        
    Returns:
        dict: Session data with checkout URL and session ID
    """
    try:
        init_stripe()
        
        # Build line items for Stripe
        line_items = []
        for item in cart_items:
            tutorial = item['tutorial']
            quantity = item.get('quantity', 1)
            
            line_items.append({
                'price_data': {
                    'currency': tutorial.currency.lower(),
                    'unit_amount': int(float(tutorial.price) * 100),  # Convert to cents
                    'product_data': {
                        'name': tutorial.title,
                        'description': tutorial.short_description or tutorial.description[:200],
                        'images': [tutorial.thumbnail_url] if tutorial.thumbnail_url else [],
                        'metadata': {
                            'tutorial_id': tutorial.id,
                            'tutorial_uuid': tutorial.uuid,
                            'course_type': tutorial.course_type
                        }
                    },
                },
                'quantity': quantity,
            })
        
        # Create or retrieve Stripe customer
        customer_id = get_or_create_stripe_customer(user)
        
        # Prepare session parameters
        session_params = {
            'payment_method_types': ['card'],
            'line_items': line_items,
            'mode': 'payment',
            'customer': customer_id,
            'customer_email': user.email if not customer_id else None,
            'success_url': success_url or url_for('payment.checkout_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            'cancel_url': cancel_url or url_for('payment.checkout_cancel', _external=True),
            'metadata': {
                'user_id': user.id,
                'user_uuid': user.uuid,
                'coupon_code': coupon_code or ''
            },
            'allow_promotion_codes': True,
        }
        
        # Apply coupon if provided
        if coupon_code:
            # Note: For production, you'd create Stripe coupons and apply them here
            # For now, we'll handle discounts in our order processing
            session_params['metadata']['coupon_code'] = coupon_code
        
        # Create the checkout session
        session = stripe.checkout.Session.create(**session_params)
        
        logger.info(f"Created Stripe checkout session {session.id} for user {user.id}")
        
        return {
            'checkout_url': session.url,
            'session_id': session.id,
            'customer_id': customer_id
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout session: {str(e)}")
        raise Exception(f"Payment system error: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        raise


def get_or_create_stripe_customer(user):
    """
    Get existing Stripe customer ID or create a new customer.
    
    Args:
        user: TutorialUser object
        
    Returns:
        str: Stripe customer ID
    """
    try:
        init_stripe()
        
        # Search for existing customer by email
        customers = stripe.Customer.list(email=user.email, limit=1)
        
        if customers.data:
            customer = customers.data[0]
            logger.info(f"Found existing Stripe customer {customer.id} for user {user.id}")
            return customer.id
        
        # Create new customer
        customer = stripe.Customer.create(
            email=user.email,
            name=user.full_name or user.username,
            metadata={
                'user_id': user.id,
                'user_uuid': user.uuid
            }
        )
        
        logger.info(f"Created new Stripe customer {customer.id} for user {user.id}")
        return customer.id
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error managing customer: {str(e)}")
        return None


def retrieve_checkout_session(session_id):
    """
    Retrieve a Stripe Checkout session.
    
    Args:
        session_id: Stripe session ID
        
    Returns:
        stripe.checkout.Session object
    """
    try:
        init_stripe()
        session = stripe.checkout.Session.retrieve(
            session_id,
            expand=['line_items', 'customer', 'payment_intent']
        )
        return session
    except stripe.error.StripeError as e:
        logger.error(f"Error retrieving checkout session {session_id}: {str(e)}")
        raise


def retrieve_payment_intent(payment_intent_id):
    """
    Retrieve a Stripe Payment Intent.
    
    Args:
        payment_intent_id: Stripe payment intent ID
        
    Returns:
        stripe.PaymentIntent object
    """
    try:
        init_stripe()
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return payment_intent
    except stripe.error.StripeError as e:
        logger.error(f"Error retrieving payment intent {payment_intent_id}: {str(e)}")
        raise


def create_refund(payment_intent_id, amount=None, reason=None):
    """
    Create a refund for a payment.
    
    Args:
        payment_intent_id: Stripe payment intent ID
        amount: Amount to refund in cents (None for full refund)
        reason: Reason for refund ('duplicate', 'fraudulent', 'requested_by_customer')
        
    Returns:
        stripe.Refund object
    """
    try:
        init_stripe()
        
        refund_params = {
            'payment_intent': payment_intent_id,
            'reason': reason or 'requested_by_customer'
        }
        
        if amount:
            refund_params['amount'] = amount
        
        refund = stripe.Refund.create(**refund_params)
        logger.info(f"Created refund {refund.id} for payment intent {payment_intent_id}")
        
        return refund
        
    except stripe.error.StripeError as e:
        logger.error(f"Error creating refund: {str(e)}")
        raise


def construct_webhook_event(payload, signature):
    """
    Construct and verify a Stripe webhook event.
    
    Args:
        payload: Request body bytes
        signature: Stripe signature header
        
    Returns:
        stripe.Event object
    """
    try:
        webhook_secret = current_app.config['STRIPE_WEBHOOK_SECRET']
        event = stripe.Webhook.construct_event(
            payload, signature, webhook_secret
        )
        return event
    except ValueError as e:
        logger.error(f"Invalid webhook payload: {str(e)}")
        raise
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid webhook signature: {str(e)}")
        raise


def format_stripe_amount(amount_cents, currency='USD'):
    """
    Format Stripe amount (in cents) to decimal.
    
    Args:
        amount_cents: Amount in cents
        currency: Currency code
        
    Returns:
        Decimal: Amount in standard units
    """
    return Decimal(amount_cents) / 100


def create_stripe_coupon(code, discount_type, discount_value, duration='once', max_redemptions=None):
    """
    Create a Stripe coupon.
    
    Args:
        code: Coupon code
        discount_type: 'percentage' or 'fixed'
        discount_value: Discount value (percentage or amount in cents)
        duration: 'once', 'repeating', or 'forever'
        max_redemptions: Maximum number of redemptions
        
    Returns:
        stripe.Coupon object
    """
    try:
        init_stripe()
        
        coupon_params = {
            'id': code,
            'duration': duration,
        }
        
        if discount_type == 'percentage':
            coupon_params['percent_off'] = float(discount_value)
        else:  # fixed
            coupon_params['amount_off'] = int(float(discount_value) * 100)
            coupon_params['currency'] = 'usd'
        
        if max_redemptions:
            coupon_params['max_redemptions'] = max_redemptions
        
        coupon = stripe.Coupon.create(**coupon_params)
        logger.info(f"Created Stripe coupon {code}")
        
        return coupon
        
    except stripe.error.StripeError as e:
        logger.error(f"Error creating Stripe coupon: {str(e)}")
        raise


def get_customer_invoices(customer_id, limit=10):
    """
    Get invoices for a Stripe customer.
    
    Args:
        customer_id: Stripe customer ID
        limit: Maximum number of invoices to retrieve
        
    Returns:
        list: List of stripe.Invoice objects
    """
    try:
        init_stripe()
        invoices = stripe.Invoice.list(customer=customer_id, limit=limit)
        return invoices.data
    except stripe.error.StripeError as e:
        logger.error(f"Error retrieving customer invoices: {str(e)}")
        return []
