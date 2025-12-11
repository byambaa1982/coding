# app/payment/forms.py
"""Forms for payment and checkout process."""

from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, HiddenField, SelectField
from wtforms.validators import DataRequired, Email, Optional, Length, NumberRange


class CheckoutForm(FlaskForm):
    """Form for checkout process."""
    
    # Hidden fields for cart data
    tutorial_ids = HiddenField('Tutorial IDs', validators=[DataRequired()])
    
    # Coupon code
    coupon_code = StringField('Coupon Code', validators=[Optional(), Length(max=50)])
    
    # Billing information (optional, Stripe collects this)
    billing_name = StringField('Full Name', validators=[Optional(), Length(max=200)])
    billing_email = StringField('Email', validators=[Optional(), Email()])


class CouponForm(FlaskForm):
    """Form for applying coupon codes."""
    
    coupon_code = StringField(
        'Coupon Code',
        validators=[DataRequired(), Length(min=3, max=50)],
        render_kw={'placeholder': 'Enter coupon code'}
    )


class RefundRequestForm(FlaskForm):
    """Form for requesting refunds."""
    
    order_id = HiddenField('Order ID', validators=[DataRequired()])
    reason = SelectField(
        'Refund Reason',
        choices=[
            ('changed_mind', 'Changed my mind'),
            ('technical_issues', 'Technical issues with course'),
            ('duplicate_purchase', 'Duplicate purchase'),
            ('not_as_expected', 'Course not as expected'),
            ('other', 'Other')
        ],
        validators=[DataRequired()]
    )
    notes = StringField('Additional Notes', validators=[Optional(), Length(max=500)])
