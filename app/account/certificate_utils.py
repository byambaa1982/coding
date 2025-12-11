"""
Certificate generation utilities for course completion.
Uses WeasyPrint for PDF generation.
"""

import os
from datetime import datetime
from flask import render_template, url_for

# Optional WeasyPrint import - will fail gracefully if GTK not installed
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    WEASYPRINT_AVAILABLE = False
    print(f"Warning: WeasyPrint not available: {e}")

from app.extensions import db
from app.models import Certificate, TutorialEnrollment


def generate_certificate_pdf(user, tutorial, enrollment):
    """
    Generate certificate PDF for course completion.
    
    Args:
        user: TutorialUser object
        tutorial: NewTutorial object
        enrollment: TutorialEnrollment object
    
    Returns:
        Certificate object with PDF path/URL
    """
    # Check if certificate already exists
    existing_cert = Certificate.query.filter_by(
        user_id=user.id,
        tutorial_id=tutorial.id
    ).first()
    
    if existing_cert and not existing_cert.is_revoked:
        return existing_cert
    
    # Create certificate record
    cert = Certificate(
        user_id=user.id,
        tutorial_id=tutorial.id,
        enrollment_id=enrollment.id,
        certificate_number=Certificate.generate_certificate_number(),
        verification_code=Certificate.generate_verification_code(),
        issued_to_name=user.full_name or user.username or user.email,
        tutorial_title=tutorial.title,
        instructor_name=tutorial.instructor.full_name or tutorial.instructor.username,
        completion_date=enrollment.completed_at.date() if enrollment.completed_at else datetime.utcnow().date()
    )
    
    db.session.add(cert)
    db.session.flush()  # Get cert.id
    
    # Generate PDF
    try:
        pdf_path = _create_certificate_pdf(cert, user, tutorial)
        cert.pdf_path = pdf_path
        cert.pdf_url = url_for('static', filename=f'certificates/{os.path.basename(pdf_path)}', _external=True)
        
        # Mark enrollment as certificate issued
        enrollment.certificate_issued = True
        
        db.session.commit()
        return cert
        
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Failed to generate certificate PDF: {str(e)}")


def _create_certificate_pdf(cert, user, tutorial):
    """
    Create the actual PDF file using WeasyPrint.
    
    Args:
        cert: Certificate object
        user: TutorialUser object
        tutorial: NewTutorial object
    
    Returns:
        str: Path to generated PDF file
    """
    if not WEASYPRINT_AVAILABLE:
        raise Exception("WeasyPrint is not available. Please install GTK3 runtime and WeasyPrint.")
    
    # Ensure certificates directory exists
    cert_dir = os.path.join('app', 'static', 'certificates')
    os.makedirs(cert_dir, exist_ok=True)
    
    # Generate filename
    filename = f"cert_{cert.certificate_number}.pdf"
    filepath = os.path.join(cert_dir, filename)
    
    # Render HTML template
    html_content = render_template(
        'account/certificate_template.html',
        certificate=cert,
        user=user,
        tutorial=tutorial
    )
    
    # Generate PDF from HTML
    HTML(string=html_content).write_pdf(filepath)
    
    return filepath


def verify_certificate(certificate_number=None, verification_code=None):
    """
    Verify a certificate by certificate number or verification code.
    
    Args:
        certificate_number: Certificate number (e.g., CERT-202412-12345678)
        verification_code: Verification code (e.g., ABC123XYZ456)
    
    Returns:
        tuple: (is_valid: bool, certificate: Certificate or None, message: str)
    """
    if not certificate_number and not verification_code:
        return False, None, "Please provide either certificate number or verification code"
    
    # Query certificate
    query = Certificate.query
    if certificate_number:
        query = query.filter_by(certificate_number=certificate_number)
    if verification_code:
        query = query.filter_by(verification_code=verification_code)
    
    cert = query.first()
    
    if not cert:
        return False, None, "Certificate not found"
    
    if cert.is_revoked:
        return False, cert, f"Certificate has been revoked. Reason: {cert.revoked_reason}"
    
    return True, cert, "Certificate is valid and authentic"


def revoke_certificate(certificate_id, reason):
    """
    Revoke a certificate.
    
    Args:
        certificate_id: Certificate ID
        reason: Reason for revocation
    
    Returns:
        bool: Success status
    """
    cert = Certificate.query.get(certificate_id)
    if not cert:
        return False
    
    cert.is_revoked = True
    cert.revoked_reason = reason
    db.session.commit()
    
    return True


def get_user_certificates(user_id):
    """
    Get all certificates for a user.
    
    Args:
        user_id: User ID
    
    Returns:
        list: List of Certificate objects
    """
    return Certificate.query.filter_by(
        user_id=user_id,
        is_revoked=False
    ).order_by(Certificate.created_at.desc()).all()


def should_issue_certificate(enrollment):
    """
    Check if a certificate should be issued for an enrollment.
    
    Args:
        enrollment: TutorialEnrollment object
    
    Returns:
        bool: True if certificate should be issued
    """
    # Check if already issued
    if enrollment.certificate_issued:
        return False
    
    # Check if course is completed
    if not enrollment.is_completed:
        return False
    
    # Check if already has certificate
    existing = Certificate.query.filter_by(
        user_id=enrollment.user_id,
        tutorial_id=enrollment.tutorial_id,
        is_revoked=False
    ).first()
    
    return existing is None
