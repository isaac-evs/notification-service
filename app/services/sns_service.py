# app/services/sns_service.py
import os
import json
import boto3
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.notification import Notification, NotificationStatus

class SNSService:
    @staticmethod
    def send_email_notification(db: Session, notification_id: int):
        """
        Sends an email notification using AWS SNS.
        Updates the notification record with the status and sent timestamp.
        """
        # Get notification from database
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise ValueError(f"Notification with ID {notification_id} not found")

        try:
            # Configure AWS SNS client
            sns_client = boto3.client(
                'sns',
                region_name=os.getenv("AWS_REGION"),
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
            )

            # Prepare the message
            message = {
                "default": notification.message,
                "email": notification.message,
            }

            # Send the message
            response = sns_client.publish(
                TopicArn=os.getenv("SNS_TOPIC_ARN"),
                Message=json.dumps(message),
                Subject=notification.subject,
                MessageStructure='json',
                MessageAttributes={
                    'email': {
                        'DataType': 'String',
                        'StringValue': notification.recipient_email
                    }
                }
            )

            # Update notification status
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.now()
            db.commit()

            return {"status": "success", "message_id": response.get("MessageId")}

        except Exception as e:
            # Update notification with error
            notification.status = NotificationStatus.FAILED
            notification.error_message = str(e)
            db.commit()

            return {"status": "error", "error": str(e)}

    @staticmethod
    def send_sales_note_notification(db: Session, notification_type, sales_note_id, customer_email, pdf_url=None):
        """
        Creates and sends a notification for a sales note event.
        """
        # Prepare subject and message based on notification type
        if notification_type == "SALES_NOTE_CREATED":
            subject = "New Sales Note Created"
            message = f"A new sales note has been created for you. "
        elif notification_type == "SALES_NOTE_UPDATED":
            subject = "Sales Note Updated"
            message = f"Your sales note has been updated. "
        elif notification_type == "SALES_NOTE_PAID":
            subject = "Sales Note Marked as Paid"
            message = f"Your sales note has been marked as paid. Thank you for your payment! "
        elif notification_type == "SALES_NOTE_CANCELED":
            subject = "Sales Note Canceled"
            message = f"Your sales note has been canceled. "
        else:
            raise ValueError(f"Invalid notification type: {notification_type}")

        # Add PDF URL if provided
        if pdf_url:
            message += f"You can view your sales note here: {pdf_url}"

        # Create notification record
        notification = Notification(
            type=notification_type,
            status=NotificationStatus.PENDING,
            recipient_email=customer_email,
            subject=subject,
            message=message,
            resource_id=sales_note_id
        )

        db.add(notification)
        db.flush()

        # Send the notification
        result = SNSService.send_email_notification(db, notification.id)

        db.commit()
        db.refresh(notification)

        return notification, result
