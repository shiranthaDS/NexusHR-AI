from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from app.models import TokenData, User, UserInDB

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Fake database - Replace with real database in production
# Pre-hashed passwords to avoid bcrypt issues on module load
# Passwords: admin123, manager123, employee123
fake_users_db = {
    "hr_admin": {
        "username": "hr_admin",
        "full_name": "HR Administrator",
        "email": "admin@nexushr.com",
        "hashed_password": "$2b$12$Kt8uge7MyunZtznfuxxcVuBAapqhfht.i9zI7NWFA75ZGK5.CPsp2",  # admin123
        "role": "admin",
        "disabled": False,
    },
    "hr_manager": {
        "username": "hr_manager",
        "full_name": "HR Manager",
        "email": "manager@nexushr.com",
        "hashed_password": "$2b$12$UOgP2c1/7Mgj/qNGbr3jO.WWEM1J2vwxDazWXjjx.DdSnD9NGx7oW",  # manager123
        "role": "hr_manager",
        "disabled": False,
    },
    "employee": {
        "username": "employee",
        "full_name": "John Doe",
        "email": "employee@nexushr.com",
        "hashed_password": "$2b$12$aNQVHkg5Fx7OiGZNVjLBQell2lcjFrdHyvCZrC90MYgnK3MLDZJQS",  # employee123
        "role": "employee",
        "disabled": False,
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def get_user(username: str) -> Optional[UserInDB]:
    """Get user from database"""
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Authenticate a user"""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current authenticated user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    
    return User(**user.dict())


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Verify user has admin or hr_manager role"""
    if current_user.role not in ["admin", "hr_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin or HR Manager role required."
        )
    return current_user
