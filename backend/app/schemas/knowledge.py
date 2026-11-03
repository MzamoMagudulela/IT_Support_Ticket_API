from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.knowledge import ArticleStatus

class KnowledgeArticleBase(BaseModel):
    title: str
    content: str
    category: str
    tags: Optional[str] = None

class KnowledgeArticleCreate(KnowledgeArticleBase):
    pass

class KnowledgeArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    status: Optional[ArticleStatus] = None

class KnowledgeFeedbackCreate(BaseModel):
    is_helpful: bool
    feedback_text: Optional[str] = None

class KnowledgeArticleRead(KnowledgeArticleBase):
    id: int
    slug: str
    status: str
    author_id: int
    author_name: Optional[str] = None
    approved_by_name: Optional[str] = None
    published_at: Optional[datetime] = None
    view_count: int
    helpful_count: int
    not_helpful_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
