from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import enum
from app.models.base import TimeStampedModel

class ArticleStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"

class KnowledgeArticle(TimeStampedModel):
    __tablename__ = "knowledge_articles"

    title = Column(String(200), nullable=False, index=True)
    slug = Column(String(220), unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(80), nullable=False, index=True) # Hardware, Software, Network, Security, Onboarding
    tags = Column(String(255), nullable=True) # comma-separated
    
    author_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    approved_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(30), default=ArticleStatus.DRAFT.value, nullable=False, index=True)
    published_at = Column(DateTime, nullable=True)
    
    view_count = Column(Integer, default=0, nullable=False)
    helpful_count = Column(Integer, default=0, nullable=False)
    not_helpful_count = Column(Integer, default=0, nullable=False)

    author = relationship("User", foreign_keys=[author_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    feedback = relationship("KnowledgeFeedback", back_populates="article", cascade="all, delete-orphan")

class KnowledgeFeedback(TimeStampedModel):
    __tablename__ = "knowledge_feedback"

    article_id = Column(Integer, ForeignKey("knowledge_articles.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_helpful = Column(Boolean, nullable=False)
    feedback_text = Column(Text, nullable=True)

    article = relationship("KnowledgeArticle", back_populates="feedback")
    user = relationship("User")
