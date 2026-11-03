from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimeStampedModel

user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
)

role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)
)

class Department(TimeStampedModel):
    __tablename__ = "departments"

    name = Column(String(100), unique=True, nullable=False, index=True)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    manager_name = Column(String(100), nullable=True)

    users = relationship("User", back_populates="department")
    tickets = relationship("Ticket", back_populates="department")
    assets = relationship("Asset", back_populates="department")

class Role(TimeStampedModel):
    __tablename__ = "roles"

    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)

    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

class Permission(TimeStampedModel):
    __tablename__ = "permissions"

    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    module = Column(String(50), nullable=False)

    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

class User(TimeStampedModel):
    __tablename__ = "users"

    email = Column(String(120), unique=True, index=True, nullable=False)
    username = Column(String(60), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    department = relationship("Department", back_populates="users")

    roles = relationship("Role", secondary=user_roles, back_populates="users", lazy="joined")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    
    # Tickets & work
    requested_tickets = relationship("Ticket", foreign_keys="Ticket.requester_id", back_populates="requester")
    assigned_tickets = relationship("Ticket", foreign_keys="Ticket.assigned_technician_id", back_populates="assigned_technician")
    assigned_assets = relationship("Asset", back_populates="assigned_user")
    security_incidents_reported = relationship("SecurityIncident", foreign_keys="SecurityIncident.reporter_id", back_populates="reporter")
    security_incidents_assigned = relationship("SecurityIncident", foreign_keys="SecurityIncident.assigned_analyst_id", back_populates="assigned_analyst")

    @property
    def role_names(self) -> list[str]:
        return [r.name for r in self.roles]

class RefreshToken(TimeStampedModel):
    __tablename__ = "refresh_tokens"

    token_hash = Column(String(64), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    replaced_by_hash = Column(String(64), nullable=True)

    user = relationship("User", back_populates="refresh_tokens")
