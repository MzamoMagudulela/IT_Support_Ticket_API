from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_password_hash
from app.core.permissions import get_current_active_user, RoleChecker
from app.models.user import User, Role, Department
from app.schemas.user import UserCreate, UserUpdate, UserRead, RoleRead
from app.services.audit_service import record_audit_log

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=List[UserRead])
def get_users(
    role: Optional[str] = None,
    department_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(User).filter(User.is_active == True)
    if department_id:
        query = query.filter(User.department_id == department_id)
    if role:
        query = query.join(User.roles).filter(Role.name.ilike(f"%{role}%"))
    return query.all()

@router.get("/roles", response_model=List[RoleRead])
def get_roles(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return db.query(Role).all()

@router.get("/{user_id}", response_model=UserRead)
def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("", response_model=UserRead, dependencies=[Depends(RoleChecker(["admin", "system administrator"]))])
def create_user(
    data: UserCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter((User.email == data.email) | (User.username == data.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email or username already exists")

    new_user = User(
        email=data.email,
        username=data.username,
        full_name=data.full_name,
        hashed_password=get_password_hash(data.password),
        department_id=data.department_id,
        is_active=data.is_active
    )

    # Assign roles
    for r_name in data.role_names:
        r = db.query(Role).filter(Role.name.ilike(r_name)).first()
        if r:
            new_user.roles.append(r)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    record_audit_log(
        db, action="CREATE", entity_type="USER", entity_id=new_user.id,
        user=current_user, request=request, new_values={"username": new_user.username}
    )
    return new_user

@router.patch("/{user_id}", response_model=UserRead, dependencies=[Depends(RoleChecker(["admin", "system administrator", "it_manager"]))])
def update_user(
    user_id: int,
    data: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.full_name is not None:
        user.full_name = data.full_name
    if data.email is not None:
        user.email = data.email
    if data.department_id is not None:
        user.department_id = data.department_id
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.is_locked is not None:
        user.is_locked = data.is_locked
        if not data.is_locked:
            user.failed_login_attempts = 0
            user.locked_until = None

    if data.role_names is not None:
        user.roles.clear()
        for r_name in data.role_names:
            r = db.query(Role).filter(Role.name.ilike(r_name)).first()
            if r:
                user.roles.append(r)

    db.commit()
    db.refresh(user)
    record_audit_log(db, action="UPDATE", entity_type="USER", entity_id=user.id, user=current_user, request=request)
    return user
