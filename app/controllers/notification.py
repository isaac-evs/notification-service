# app/controllers/notification.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

from app.models.notification import Notification, NotificationType, NotificationStatus
from app.schemas.notification import NotificationCreate, NotificationUpdate, SalesNoteNotificationRequest
from app.services.sns_service import SNSService

class NotificationController:
    @staticmethod
    def get_notifications(db: Session, skip: int = 0, limit: int = 100, resource_id: int = None):
        query = db.query(Notification)
        if resource_id:
            query = query.filter(Notification.resource_id == resource_id)
        return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_notification(db: Session, notification_id: int):
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if notification is None:
            raise HTTPException(status_code=404, detail="Notification not found")
        return notification

    @staticmethod
    def create_notification(db: Session, notification: NotificationCreate):
        db_notification = Notification(
            type=notification.type,
            status=NotificationStatus.PENDING,
            recipient_email=notification.recipient_email,
            subject=notification.subject,
            message=notification.message,
            resource_id=notification.resource_id
        )
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        return db_notification

    @staticmethod
    def update_notification(db: Session, notification_id: int, notification: NotificationUpdate):
        db_notification = NotificationController.get_notification(db, notification_id)

        # Update notification data
        update_data = notification.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_notification, key, value)

        db.commit()
        db.refresh(db_notification)
        return db_notification

    @staticmethod
    def delete_notification(db: Session, notification_id: int):
        db_notification = NotificationController.get_notification(db, notification_id)
        db.delete(db_notification)
        db.commit()
        return {"message": "Notification deleted successfully"}

    @staticmethod
    def send_notification(db: Session, notification_id: int):
        notification = NotificationController.get_notification(db, notification_id)

        # Check if notification is already sent
        if notification.status == NotificationStatus.SENT:
            raise HTTPException(status_code=400, detail="Notification already sent")

        # Send notification using SNS service
        result = SNSService.send_email_notification(db, notification_id)

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=f"Failed to send notification: {result['error']}")

        return {"message": "Notification sent successfully", "message_id": result.get("message_id")}

    @staticmethod
    def send_sales_note_notification(db: Session, request: SalesNoteNotificationRequest):
        # Verify sales note exists
        sales_note = db.execute(f"SELECT id, status FROM sales_notes WHERE id = {request.sales_note_id}").fetchone()
        if not sales_note:
            raise HTTPException(status_code=404, detail="Sales note not found")

        # Determine notification type based on sales note status
        notification_type = NotificationType.SALES_NOTE_CREATED
        if sales_note["status"] == "paid":
            notification_type = NotificationType.SALES_NOTE_PAID
        elif sales_note["status"] == "canceled":
            notification_type = NotificationType.SALES_NOTE_CANCELED

        # Send notification
        notification, result = SNSService.send_sales_note_notification(
            db,
            notification_type,
            request.sales_note_id,
            request.customer_email,
            request.pdf_url
        )

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=f"Failed to send notification: {result['error']}")

        return {
            "message": "Sales note notification sent successfully",
            "notification_id": notification.id,
            "message_id": result.get("message_id")
        }
