from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.security import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, hash_token
)
from app.core.permissions import get_current_active_user
from app.models.user import User, RefreshToken
from app.schemas.user import TokenResponse, TokenRefreshRequest, UserRead, PasswordChange
from app.services.audit_service import record_audit_log

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        (User.username == form_data.username) | (User.email == form_data.username)
    ).first()

    now = datetime.now(timezone.utc)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    # Check account lockout
    if user.is_locked:
        if user.locked_until and user.locked_until.replace(tzinfo=timezone.utc) > now:
            minutes_left = int((user.locked_until.replace(tzinfo=timezone.utc) - now).total_seconds() / 60) + 1
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account locked due to multiple failed login attempts. Try again in {minutes_left} minutes."
            )
        else:
            # Unlock after timeout
            user.is_locked = False
            user.failed_login_attempts = 0
            user.locked_until = None
            db.commit()

    if not verify_password(form_data.password, user.hashed_password):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            user.is_locked = True
            user.locked_until = now + timedelta(minutes=settings.LOCKOUT_DURATION_MINUTES)
            db.commit()
            record_audit_log(
                db, action="ACCOUNT_LOCKED", entity_type="USER", entity_id=user.id,
                user=user, request=request,
                new_values={"failed_attempts": user.failed_login_attempts}
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account locked for {settings.LOCKOUT_DURATION_MINUTES} minutes due to {settings.MAX_LOGIN_ATTEMPTS} consecutive failed attempts."
            )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Incorrect username or password. {settings.MAX_LOGIN_ATTEMPTS - user.failed_login_attempts} attempts remaining."
        )

    # Login successful, reset failed attempts
    user.failed_login_attempts = 0
    user.is_locked = False
    user.locked_until = None
    
    role_names = user.role_names
    access_token = create_access_token(subject=user.username, roles=role_names, user_id=user.id)
    raw_refresh_token, token_hash, expires_at = create_refresh_token(subject=user.username, user_id=user.id)

    # Store refresh token
    refresh_record = RefreshToken(
        token_hash=token_hash,
        user_id=user.id,
        expires_at=expires_at,
        revoked=False
    )
    db.add(refresh_record)
    db.commit()

    record_audit_log(db, action="LOGIN_SUCCESS", entity_type="USER", entity_id=user.id, user=user, request=request)

    return {
        "access_token": access_token,
        "refresh_token": raw_refresh_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/refresh", response_model=dict)
def refresh_token(
    payload: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    token_hash = hash_token(payload.refresh_token)
    refresh_record = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

    now = datetime.now(timezone.utc)
    if not refresh_record or refresh_record.revoked or refresh_record.expires_at.replace(tzinfo=timezone.utc) < now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    user = refresh_record.user
    if not user.is_active or user.is_locked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive or locked"
        )

    # Secure rotation: Revoke current refresh token and issue a new one
    refresh_record.revoked = True
    
    new_raw_refresh, new_token_hash, new_expires_at = create_refresh_token(subject=user.username, user_id=user.id)
    refresh_record.replaced_by_hash = new_token_hash

    new_record = RefreshToken(
        token_hash=new_token_hash,
        user_id=user.id,
        expires_at=new_expires_at,
        revoked=False
    )
    db.add(new_record)
    
    new_access_token = create_access_token(subject=user.username, roles=user.role_names, user_id=user.id)
    db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_raw_refresh,
        "token_type": "bearer"
    }

@router.post("/logout")
def logout(
    payload: TokenRefreshRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    token_hash = hash_token(payload.refresh_token)
    record = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if record:
        record.revoked = True
        db.commit()
    record_audit_log(db, action="LOGOUT", entity_type="USER", entity_id=current_user.id, user=current_user)
    return {"message": "Successfully logged out and session revoked."}

@router.get("/me", response_model=UserRead)
def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.post("/change-password")
def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    
    current_user.hashed_password = get_password_hash(data.new_password)
    # Revoke all active refresh tokens on password change
    db.query(RefreshToken).filter(RefreshToken.user_id == current_user.id).update({"revoked": True})
    db.commit()
    return {"message": "Password changed successfully. Please log in again."}
