from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.models import Token, User
from app.auth import authenticate_user, create_access_token, get_current_active_user
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint - Returns JWT access token
    
    Default users:
    - username: hr_admin, password: admin123 (Admin)
    - username: hr_manager, password: manager123 (HR Manager)
    - username: employee, password: employee123 (Employee)
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current authenticated user information"""
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    Logout endpoint
    Note: With JWT, actual logout is handled client-side by removing the token
    """
    return {
        "status": "success",
        "message": f"User {current_user.username} logged out successfully"
    }
