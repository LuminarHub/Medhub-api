from django.apps import AppConfig
import threading
import time
from django.utils import timezone
from django.db import connections
from datetime import timedelta
from django.db.utils import OperationalError


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        threading.Thread(target=start_message_scheduler, daemon=True).start()


def wait_for_db():
    """Wait until the database is ready before running the background thread."""
    while True:
        try:
            connections["default"].cursor()  # Try connecting to the DB
            return
        except OperationalError:
            print("Database not ready, waiting...")
            time.sleep(50)  # Wait 50 seconds before trying again

def start_message_scheduler():
    """Wait for the database and then start processing scheduled reminders."""
    wait_for_db()  # Ensure the database is ready before running queries
    
    from .models import Reminder, Notification
    while True:
        now = timezone.now()  # Current time for comparison
        new_time = now + timedelta(hours=5, minutes=30)
        print(f"Checking scheduled reminders at {new_time}")  # Debugging output

        reminders = Reminder.objects.filter(
            from_date__lte=now.date(),  # Only consider reminders that have started
            to_date__gte=now.date(),    # Only consider reminders that haven't ended
            time__hour=now.hour,        # Check if the current hour matches the reminder time
            time__minute=now.minute,    # Check if the current minute matches the reminder time
        )

        for reminder in reminders:
            # Check if this reminder has not been sent yet
            if reminder.time <= now.time() and reminder.from_date <= now.date() <= reminder.to_date:
                # Send the message to the user
                send_reminder_message(reminder)

                # If repeat is false, delete the reminder after sending it
                if not reminder.repeat:
                    reminder.delete()

        time.sleep(60)  # Check every minute for pending reminders


def send_reminder_message(reminder):
    """Create and send a message based on the reminder."""
    user = reminder.user
    content = reminder.message
    
    from .models import Reminder, Notification
    try:
        # Create a notification for the reminder
        Notification.objects.create(
            user=user,  # Assuming 'user' is a valid field in your model
            message=content,
        )
        print(f"Sent reminder to {user.name}: {content}")  # Debugging output
    except Exception as e:
        print(f"Error sending reminder to {user.name}: {e}")  # Log any errors
