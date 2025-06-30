# dwc_pos/app/services/email_service.py

import logging
from typing import NoReturn

logger = logging.getLogger(__name__)

async def send_email_verification_link(recipient_email: str, verification_link: str) -> None:
    """
    Simulates sending an email with an account activation link.
    In a real application, this would use an email sending library (e.g., aiosmtplib, SendGrid, Mailgun).
    """
    logger.info(f"Simulating sending account activation email to: {recipient_email}")
    logger.info(f"Activation Link: {verification_link}")
    # Here you would integrate with your actual email service provider
    # Example:
    # try:
    #     await real_email_service.send(
    #         to_email=recipient_email,
    #         subject="Activate Your DWC POS Account",
    #         body=f"Click here to activate your account: {verification_link}"
    #     )
    #     logger.info(f"Successfully sent activation email to {recipient_email}")
    # except Exception as e:
    #     logger.error(f"Failed to send activation email to {recipient_email}: {e}")
    pass # No actual sending for now

async def send_email_verification_code(recipient_email: str, verification_code: str) -> None:
    """
    Simulates sending an email with a 6-digit verification code for login.
    """
    logger.info(f"Simulating sending login verification code email to: {recipient_email}")
    logger.info(f"Verification Code: {verification_code}")
    # Here you would integrate with your actual email service provider
    # Example:
    # try:
    #     await real_email_service.send(
    #         to_email=recipient_email,
    #         subject="Your DWC POS Login Verification Code",
    #         body=f"Your verification code is: {verification_code}"
    #     )
    #     logger.info(f"Successfully sent login code email to {recipient_email}")
    # except Exception as e:
    #     logger.error(f"Failed to send login code email to {recipient_email}: {e}")
    pass # No actual sending for now