# app/views/notification.py
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.schemas.notification import NotificationCreate, NotificationUpdate, NotificationResponse, SalesNoteNotificationRequest
from app.controllers.notification import NotificationController
from app.database import get_db

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
def read_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    resource_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all notifications with pagination and filtering"""
    return NotificationController.get_notifications(db, skip=skip, limit=limit, resource_id=resource_id)

@router.post("/", response_model=NotificationResponse, status_code=201)
def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db)
):
    """Create a new notification"""
    return NotificationController.create_notification(db, notification)

@router.get("/{notification_id}", response_model=NotificationResponse)
def read_notification(
    notification_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """Get a specific notification by ID"""
    return NotificationController.get_notification(db, notification_id)

@router.put("/{notification_id}", response_model=NotificationResponse)
def update_notification(
    notification_id: int = Path(..., gt=0),
    notification: NotificationUpdate = Body(...),
    db: Session = Depends(get_db)
):
    """Update a notification"""
    return NotificationController.update_notification(db, notification_id, notification)

@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """Delete a notification"""
    return NotificationController.delete_notification(db, notification_id)

@router.post("/{notification_id}/send")
def send_notification(
    notification_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """Send a notification"""
    return NotificationController.send_notification(db, notification_id)

@router.post("/sales-note")
def send_sales_note_notification(
    request: SalesNoteNotificationRequest,
    db: Session = Depends(get_db)
):
    """Send a notification for a sales note"""
    return NotificationController.send_sales_note_notification(db, request)
