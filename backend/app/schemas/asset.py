from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.models.asset import AssetType, AssetStatus, ServiceTier, ServiceStatus

class AssetBase(BaseModel):
    asset_tag: str
    serial_number: str
    manufacturer: str
    model: str
    asset_type: AssetType = AssetType.LAPTOP
    department_id: Optional[int] = None
    assigned_user_id: Optional[int] = None
    purchase_date: Optional[datetime] = None
    warranty_expiration: Optional[datetime] = None
    status: AssetStatus = AssetStatus.ACTIVE
    location: str
    specifications: Optional[str] = None

class AssetCreate(AssetBase):
    pass

class AssetUpdate(BaseModel):
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    asset_type: Optional[AssetType] = None
    department_id: Optional[int] = None
    assigned_user_id: Optional[int] = None
    warranty_expiration: Optional[datetime] = None
    status: Optional[AssetStatus] = None
    location: Optional[str] = None
    specifications: Optional[str] = None

class AssetMaintenanceCreate(BaseModel):
    scheduled_date: datetime
    maintenance_type: str
    description: str
    technician_name: Optional[str] = None
    cost: float = 0.0

class AssetRead(AssetBase):
    id: int
    department_name: Optional[str] = None
    assigned_user_name: Optional[str] = None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SoftwareLicenseCreate(BaseModel):
    name: str
    publisher: str
    license_key: str
    total_seats: int = 1
    allocated_seats: int = 0
    expiration_date: Optional[datetime] = None
    department_id: Optional[int] = None

class SoftwareLicenseRead(SoftwareLicenseCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ITServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    tier: ServiceTier = ServiceTier.BUSINESS_CRITICAL
    status: ServiceStatus = ServiceStatus.OPERATIONAL
    owner_name: Optional[str] = None

class ITServiceRead(ITServiceCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
