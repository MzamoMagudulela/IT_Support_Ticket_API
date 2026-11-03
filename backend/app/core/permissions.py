from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if not payload:
        raise credentials_exception
    
    token_type = payload.get("type")
    if token_type != "access":
        raise credentials_exception
        
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
        
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user account")
    if current_user.is_locked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is locked due to security policy")
    return current_user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = [r.lower() for r in allowed_roles]

    def __call__(self, user: User = Depends(get_current_active_user)) -> User:
        user_role_names = [role.name.lower() for role in user.roles]
        # Admin always has bypass access
        if any(r in user_role_names for r in ["admin", "system administrator", "system_admin"]):
            return user

        for allowed in self.allowed_roles:
            norm_allowed = allowed.replace("_", " ").lower().strip()
            allowed_words = set(norm_allowed.split())
            for u_role in user_role_names:
                norm_user = u_role.replace("_", " ").lower().strip()
                user_words = set(norm_user.split())
                if allowed_words.issubset(user_words) or norm_allowed in norm_user:
                    return user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Operation not permitted. Required roles: {', '.join(self.allowed_roles)}"
        )

def check_ticket_access(ticket, current_user: User) -> bool:
    """Resource-level authorization: Employees can only view/modify their own tickets."""
    user_roles = [r.name.lower() for r in current_user.roles]
    privileged_roles = ["admin", "system administrator", "system_admin", "it_manager", "it operations manager", "technician", "it support technician", "auditor"]
    
    if any(r in user_roles for r in privileged_roles):
        return True
    
    if ticket.requester_id == current_user.id:
        return True
        
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied: You do not have permission to access tickets created by other employees."
    )
