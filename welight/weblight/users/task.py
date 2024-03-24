from celery import shared_task
from twilio.rest import Client
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

@shared_task()
def send_otp(phone_number, otp):
    try:
        twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = twilio_client.messages.create(
            body=f"Your OTP is: {otp}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
    except Exception:
        print("exception raised...")
        import traceback
        traceback.print_exc()
        print(f"===================== OTP for {phone_number}: {otp} ==================")
        return False
    
@shared_task()
def send_email(email, reset_link):
    try:
        email = EmailMultiAlternatives(
            subject = 'Password Reset',
            body= f"Click the following link to reset your password: {reset_link}",
            to=[email],
        )
        print('\033[91m'+'subject: ' + '\033[92m', 'Password Reset',)
        print(f"Click the following link to reset your password: {reset_link}")
        email.send()
        return True
    except Exception:
        return False