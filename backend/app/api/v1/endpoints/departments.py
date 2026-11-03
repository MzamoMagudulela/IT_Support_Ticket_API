from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.permissions import get_current_active_user, RoleChecker
from app.models.user import Department, User
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentRead
from app.services.audit_service import record_audit_log

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.get("", response_model=List[DepartmentRead])
def get_departments(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return db.query(Department).all()

@router.post("", response_model=DepartmentRead, dependencies=[Depends(RoleChecker(["admin", "system administrator"]))])
def create_department(
    data: DepartmentCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    dept = Department(
        name=data.name,
        code=data.code.upper(),
        description=data.description,
        manager_name=data.manager_name
    )
    db.add(dept)
    db.commit()
    db.refresh(dept)
    record_audit_log(db, action="CREATE", entity_type="DEPARTMENT", entity_id=dept.id, user=current_user, request=request)
    return dept

@router.patch("/{department_id}", response_model=DepartmentRead, dependencies=[Depends(RoleChecker(["admin", "system administrator"]))])
def update_department(
    department_id: int,
    data: DepartmentUpdate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    dept = db.query(Department).filter(Department.id == department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    
    if data.name is not None:
        dept.name = data.name
    if data.code is not None:
        dept.code = data.code.upper()
    if data.description is not None:
        dept.description = data.description
    if data.manager_name is not None:
        dept.manager_name = data.manager_name

    db.commit()
    db.refresh(dept)
    record_audit_log(db, action="UPDATE", entity_type="DEPARTMENT", entity_id=dept.id, user=current_user, request=request)
    return dept
