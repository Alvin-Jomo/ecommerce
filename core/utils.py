from twilio.rest import Client
from django.conf import settings

def send_sms(to, message):
    # Initialize the Twilio client
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    # Send the SMS
    try:
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to
        )
        return message.sid  # Return message SID for tracking
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None
