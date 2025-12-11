# Phase 3 Migration Script
"""
This script creates the necessary database tables for Phase 3:
- Payment & Order Management
- Enrollments
- Coupons
- Wishlists
"""

# Run this with: flask db migrate -m "Phase 3: Add payment, enrollment, and order tables"
# Then: flask db upgrade

# The migration will create the following tables:
# - tutorial_enrollments
# - tutorial_orders
# - tutorial_order_items
# - tutorial_coupons
# - tutorial_wishlists
