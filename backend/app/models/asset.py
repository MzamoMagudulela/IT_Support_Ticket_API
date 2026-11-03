from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
import enum
from app.models.base import TimeStampedModel

class AssetType(str, enum.Enum):
    LAPTOP = "LAPTOP"
    DESKTOP = "DESKTOP"
    SERVER = "SERVER"
    PRINTER = "PRINTER"
    ROUTER = "ROUTER"
    SWITCH = "SWITCH"
    MOBILE = "MOBILE"
    SOFTWARE_LICENSE = "SOFTWARE_LICENSE"
    CLOUD_SERVICE = "CLOUD_SERVICE"
    NETWORK_INFRASTRUCTURE = "NETWORK_INFRASTRUCTURE"

class AssetStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    IN_STOCK = "IN_STOCK"
    UNDER_MAINTENANCE = "UNDER_MAINTENANCE"
    RETIRED = "RETIRED"
    LOST = "LOST"

class ServiceTier(str, enum.Enum):
    MISSION_CRITICAL = "MISSION_CRITICAL"
    BUSINESS_CRITICAL = "BUSINESS_CRITICAL"
    STANDARD = "STANDARD"

class ServiceStatus(str, enum.Enum):
    OPERATIONAL = "OPERATIONAL"
    DEGRADED = "DEGRADED"
    OUTAGE = "OUTAGE"
    MAINTENANCE = "MAINTENANCE"

class ITService(TimeStampedModel):
    __tablename__ = "services"

    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    tier = Column(String(30), default=ServiceTier.BUSINESS_CRITICAL.value, nullable=False)
    status = Column(String(30), default=ServiceStatus.OPERATIONAL.value, nullable=False)
    owner_name = Column(String(100), nullable=True)

class Asset(TimeStampedModel):
    __tablename__ = "assets"

    asset_tag = Column(String(50), unique=True, index=True, nullable=False)
    serial_number = Column(String(100), unique=True, index=True, nullable=False)
    manufacturer = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    asset_type = Column(String(40), default=AssetType.LAPTOP.value, nullable=False, index=True)
    
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    purchase_date = Column(DateTime, nullable=True)
    warranty_expiration = Column(DateTime, nullable=True, index=True)
    status = Column(String(30), default=AssetStatus.ACTIVE.value, nullable=False, index=True)
    location = Column(String(150), nullable=False)
    specifications = Column(Text, nullable=True) # JSON or descriptive specs
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    department = relationship("Department", back_populates="assets")
    assigned_user = relationship("User", back_populates="assigned_assets")
    tickets = relationship("Ticket", back_populates="related_asset")
    assignments = relationship("AssetAssignment", back_populates="asset", cascade="all, delete-orphan", order_by="AssetAssignment.created_at.desc()")
    maintenance_records = relationship("AssetMaintenance", back_populates="asset", cascade="all, delete-orphan", order_by="AssetMaintenance.created_at.desc()")
    configuration_item = relationship("ConfigurationItem", back_populates="asset", uselist=False)

class AssetAssignment(TimeStampedModel):
    __tablename__ = "asset_assignments"

    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    return_date = Column(DateTime, nullable=True)
    notes = Column(String(255), nullable=True)

    asset = relationship("Asset", back_populates="assignments")
    user = relationship("User")

class AssetMaintenance(TimeStampedModel):
    __tablename__ = "asset_maintenance"

    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    scheduled_date = Column(DateTime, nullable=False)
    completed_date = Column(DateTime, nullable=True)
    maintenance_type = Column(String(50), nullable=False) # Routine, Repair, Upgrade, Inspection
    description = Column(Text, nullable=False)
    technician_name = Column(String(100), nullable=True)
    cost = Column(Float, default=0.0, nullable=False)
    status = Column(String(30), default="SCHEDULED", nullable=False) # SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED

    asset = relationship("Asset", back_populates="maintenance_records")

class SoftwareLicense(TimeStampedModel):
    __tablename__ = "software_licenses"

    name = Column(String(120), nullable=False, index=True)
    publisher = Column(String(100), nullable=False)
    license_key = Column(String(150), nullable=False)
    total_seats = Column(Integer, default=1, nullable=False)
    allocated_seats = Column(Integer, default=0, nullable=False)
    expiration_date = Column(DateTime, nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)

    department = relationship("Department")

class ConfigurationItem(TimeStampedModel):
    __tablename__ = "configuration_items"

    name = Column(String(120), unique=True, index=True, nullable=False)
    ci_type = Column(String(50), nullable=False) # Server, Database, Load Balancer, VPC
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="SET NULL"), nullable=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="SET NULL"), nullable=True)
    ip_address = Column(String(45), nullable=True)
    fqdn = Column(String(150), nullable=True)
    status = Column(String(30), default="ACTIVE", nullable=False)

    asset = relationship("Asset", back_populates="configuration_item")
    service = relationship("ITService")
    dependencies = relationship(
        "CIRelationship",
        foreign_keys="CIRelationship.source_ci_id",
        backref="source_ci",
        cascade="all, delete-orphan"
    )

class CIRelationship(TimeStampedModel):
    __tablename__ = "ci_relationships"

    source_ci_id = Column(Integer, ForeignKey("configuration_items.id", ondelete="CASCADE"), nullable=False)
    target_ci_id = Column(Integer, ForeignKey("configuration_items.id", ondelete="CASCADE"), nullable=False)
    relationship_type = Column(String(50), default="DEPENDS_ON", nullable=False) # DEPENDS_ON, HOSTS, CONNECTS_TO, BACKUP_FOR

    target_ci = relationship("ConfigurationItem", foreign_keys=[target_ci_id])
