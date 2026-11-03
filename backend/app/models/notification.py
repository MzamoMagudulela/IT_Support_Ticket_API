from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel

class Notification(TimeStampedModel):
    __tablename__ = "notifications"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String(255), nullable=True)
    notification_type = Column(String(50), default="INFO", nullable=False) # INFO, WARNING, SUCCESS, ALERT
    is_read = Column(Boolean, default=False, nullable=False, index=True)

    user = relationship("User")
