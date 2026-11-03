from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from app.core.database import get_db
from app.core.permissions import get_current_active_user, RoleChecker
from app.models.user import User
from app.models.asset import (
    Asset, AssetAssignment, AssetMaintenance, SoftwareLicense,
    ITService, ConfigurationItem, CIRelationship, AssetStatus, AssetType
)
from app.schemas.asset import (
    AssetCreate, AssetUpdate, AssetRead, AssetMaintenanceCreate,
    SoftwareLicenseCreate, SoftwareLicenseRead, ITServiceCreate, ITServiceRead
)
from app.services.audit_service import record_audit_log

router = APIRouter(prefix="/assets", tags=["Assets & CMDB"])

def format_asset_read(a: Asset) -> AssetRead:
    return AssetRead(
        id=a.id,
        asset_tag=a.asset_tag,
        serial_number=a.serial_number,
        manufacturer=a.manufacturer,
        model=a.model,
        asset_type=AssetType(a.asset_type),
        department_id=a.department_id,
        department_name=a.department.name if a.department else None,
        assigned_user_id=a.assigned_user_id,
        assigned_user_name=a.assigned_user.full_name if a.assigned_user else None,
        purchase_date=a.purchase_date,
        warranty_expiration=a.warranty_expiration,
        status=AssetStatus(a.status),
        location=a.location,
        specifications=a.specifications,
        is_deleted=a.is_deleted,
        created_at=a.created_at,
        updated_at=a.updated_at
    )

@router.get("", response_model=List[AssetRead])
def get_assets(
    status: Optional[str] = None,
    asset_type: Optional[str] = None,
    department_id: Optional[int] = None,
    assigned_to_me: Optional[bool] = False,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(Asset).filter(Asset.is_deleted == False)

    user_roles = [r.name.lower() for r in current_user.roles]
    is_employee_only = "employee" in user_roles and not any(
        r in user_roles for r in ["admin", "system administrator", "it_manager", "technician", "auditor"]
    )
    if is_employee_only or assigned_to_me:
        query = query.filter(Asset.assigned_user_id == current_user.id)

    if status:
        query = query.filter(Asset.status == status.upper())
    if asset_type:
        query = query.filter(Asset.asset_type == asset_type.upper())
    if department_id:
        query = query.filter(Asset.department_id == department_id)
    if search:
        s = f"%{search}%"
        query = query.filter(or_(Asset.asset_tag.ilike(s), Asset.serial_number.ilike(s), Asset.model.ilike(s), Asset.manufacturer.ilike(s)))

    assets = query.order_by(desc(Asset.created_at)).all()
    return [format_asset_read(a) for a in assets]

@router.get("/{asset_id}", response_model=AssetRead)
def get_asset_by_id(
    asset_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.is_deleted == False).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return format_asset_read(asset)

@router.post("", response_model=AssetRead, dependencies=[Depends(RoleChecker(["admin", "system administrator", "it_manager", "technician"]))])
def create_asset(
    data: AssetCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    existing = db.query(Asset).filter((Asset.asset_tag == data.asset_tag) | (Asset.serial_number == data.serial_number)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Asset with this tag or serial number already exists")

    asset = Asset(
        asset_tag=data.asset_tag,
        serial_number=data.serial_number,
        manufacturer=data.manufacturer,
        model=data.model,
        asset_type=data.asset_type.value,
        department_id=data.department_id,
        assigned_user_id=data.assigned_user_id,
        purchase_date=data.purchase_date,
        warranty_expiration=data.warranty_expiration,
        status=data.status.value,
        location=data.location,
        specifications=data.specifications
    )
    db.add(asset)
    db.flush()

    if data.assigned_user_id:
        assignment = AssetAssignment(
            asset_id=asset.id,
            user_id=data.assigned_user_id,
            notes="Initial asset assignment"
        )
        db.add(assignment)

    db.commit()
    db.refresh(asset)

    record_audit_log(db, action="CREATE", entity_type="ASSET", entity_id=asset.id, user=current_user, request=request, new_values={"tag": asset.asset_tag})
    return format_asset_read(asset)

@router.patch("/{asset_id}", response_model=AssetRead, dependencies=[Depends(RoleChecker(["admin", "system administrator", "it_manager", "technician"]))])
def update_asset(
    asset_id: int,
    data: AssetUpdate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.is_deleted == False).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    old_user_id = asset.assigned_user_id
    if data.manufacturer is not None:
        asset.manufacturer = data.manufacturer
    if data.model is not None:
        asset.model = data.model
    if data.asset_type is not None:
        asset.asset_type = data.asset_type.value
    if data.department_id is not None:
        asset.department_id = data.department_id
    if data.warranty_expiration is not None:
        asset.warranty_expiration = data.warranty_expiration
    if data.status is not None:
        asset.status = data.status.value
    if data.location is not None:
        asset.location = data.location
    if data.specifications is not None:
        asset.specifications = data.specifications

    # Handle transfer/assignment change
    if data.assigned_user_id is not None and data.assigned_user_id != old_user_id:
        asset.assigned_user_id = data.assigned_user_id
        assignment = AssetAssignment(
            asset_id=asset.id,
            user_id=data.assigned_user_id,
            notes="Transferred/Reassigned"
        )
        db.add(assignment)

    db.commit()
    db.refresh(asset)
    record_audit_log(db, action="UPDATE", entity_type="ASSET", entity_id=asset.id, user=current_user, request=request)
    return format_asset_read(asset)

@router.post("/{asset_id}/maintenance", dependencies=[Depends(RoleChecker(["admin", "system administrator", "it_manager", "technician"]))])
def add_maintenance_record(
    asset_id: int,
    data: AssetMaintenanceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    m = AssetMaintenance(
        asset_id=asset.id,
        scheduled_date=data.scheduled_date,
        maintenance_type=data.maintenance_type,
        description=data.description,
        technician_name=data.technician_name or current_user.full_name,
        cost=data.cost,
        status="SCHEDULED"
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

# Software Licenses
@router.get("/licenses/list", response_model=List[SoftwareLicenseRead])
def list_licenses(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return db.query(SoftwareLicense).all()

@router.post("/licenses/create", response_model=SoftwareLicenseRead, dependencies=[Depends(RoleChecker(["admin", "it_manager"]))])
def create_software_license(data: SoftwareLicenseCreate, db: Session = Depends(get_db)):
    lic = SoftwareLicense(**data.model_dump())
    db.add(lic)
    db.commit()
    db.refresh(lic)
    return lic

# IT Services & CMDB Topology
@router.get("/services/list", response_model=List[ITServiceRead])
def list_services(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return db.query(ITService).all()

@router.post("/services/create", response_model=ITServiceRead, dependencies=[Depends(RoleChecker(["admin", "it_manager"]))])
def create_it_service(data: ITServiceCreate, db: Session = Depends(get_db)):
    srv = ITService(**data.model_dump())
    db.add(srv)
    db.commit()
    db.refresh(srv)
    return srv

@router.get("/cmdb/topology")
def get_cmdb_topology(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Returns nodes and edges for CMDB topology graph visualization"""
    cis = db.query(ConfigurationItem).all()
    rels = db.query(CIRelationship).all()
    
    nodes = [{"id": str(ci.id), "label": ci.name, "type": ci.ci_type, "status": ci.status, "ip": ci.ip_address} for ci in cis]
    edges = [{"source": str(r.source_ci_id), "target": str(r.target_ci_id), "type": r.relationship_type} for r in rels]
    return {"nodes": nodes, "edges": edges}
