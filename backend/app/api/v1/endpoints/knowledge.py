from datetime import datetime, timezone
import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from app.core.database import get_db
from app.core.permissions import get_current_active_user, RoleChecker
from app.models.user import User
from app.models.knowledge import KnowledgeArticle, KnowledgeFeedback, ArticleStatus
from app.schemas.knowledge import (
    KnowledgeArticleCreate, KnowledgeArticleUpdate, KnowledgeArticleRead, KnowledgeFeedbackCreate
)
from app.services.audit_service import record_audit_log

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[\s_-]+', '-', text)[:200]

def format_article(a: KnowledgeArticle) -> KnowledgeArticleRead:
    return KnowledgeArticleRead(
        id=a.id,
        title=a.title,
        slug=a.slug,
        content=a.content,
        category=a.category,
        tags=a.tags,
        status=a.status,
        author_id=a.author_id,
        author_name=a.author.full_name if a.author else None,
        approved_by_name=a.approved_by.full_name if a.approved_by else None,
        published_at=a.published_at,
        view_count=a.view_count,
        helpful_count=a.helpful_count,
        not_helpful_count=a.not_helpful_count,
        created_at=a.created_at,
        updated_at=a.updated_at
    )

@router.get("", response_model=List[KnowledgeArticleRead])
def get_articles(
    search: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(KnowledgeArticle)
    user_roles = [r.name.lower() for r in current_user.roles]
    is_employee = "employee" in user_roles and not any(
        r in user_roles for r in ["admin", "system administrator", "it_manager", "technician"]
    )
    # Employees only see PUBLISHED articles
    if is_employee:
        query = query.filter(KnowledgeArticle.status == ArticleStatus.PUBLISHED.value)
    elif status:
        query = query.filter(KnowledgeArticle.status == status.upper())

    if category:
        query = query.filter(KnowledgeArticle.category.ilike(category))
    if search:
        s = f"%{search}%"
        query = query.filter(or_(KnowledgeArticle.title.ilike(s), KnowledgeArticle.content.ilike(s), KnowledgeArticle.tags.ilike(s)))

    articles = query.order_by(desc(KnowledgeArticle.created_at)).all()
    return [format_article(a) for a in articles]

@router.get("/{article_id}", response_model=KnowledgeArticleRead)
def get_article_detail(
    article_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    a = db.query(KnowledgeArticle).filter(KnowledgeArticle.id == article_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Article not found")

    # Increment view count
    a.view_count += 1
    db.commit()
    db.refresh(a)
    return format_article(a)

@router.post("", response_model=KnowledgeArticleRead, dependencies=[Depends(RoleChecker(["admin", "system administrator", "it_manager", "technician"]))])
def create_article(
    data: KnowledgeArticleCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    base_slug = slugify(data.title)
    slug = f"{base_slug}-{int(datetime.now(timezone.utc).timestamp()) % 10000}"

    art = KnowledgeArticle(
        title=data.title,
        slug=slug,
        content=data.content,
        category=data.category,
        tags=data.tags,
        author_id=current_user.id,
        status=ArticleStatus.PUBLISHED.value, # Ready for use
        published_at=datetime.now(timezone.utc)
    )
    db.add(art)
    db.commit()
    db.refresh(art)

    record_audit_log(db, action="CREATE", entity_type="KNOWLEDGE_ARTICLE", entity_id=art.id, user=current_user, request=request)
    return format_article(art)

@router.post("/{article_id}/feedback")
def submit_article_feedback(
    article_id: int,
    data: KnowledgeFeedbackCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    a = db.query(KnowledgeArticle).filter(KnowledgeArticle.id == article_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Article not found")

    fb = KnowledgeFeedback(
        article_id=a.id,
        user_id=current_user.id,
        is_helpful=data.is_helpful,
        feedback_text=data.feedback_text
    )
    db.add(fb)

    if data.is_helpful:
        a.helpful_count += 1
    else:
        a.not_helpful_count += 1

    db.commit()
    return {"message": "Thank you for your feedback!"}
