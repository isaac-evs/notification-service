# app/schemas/notification.py
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.models.notification import NotificationType, NotificationStatus

class NotificationBase(BaseModel):
    type: NotificationType
    recipient_email: EmailStr
    subject: str
    message: str
    resource_id: Optional[int] = None

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    status: Optional[NotificationStatus] = None
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None

class NotificationResponse(NotificationBase):
    id: int
    status: NotificationStatus
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class SalesNoteNotificationRequest(BaseModel):
    sales_note_id: int
    customer_email: EmailStr
    pdf_url: Optional[str] = None
