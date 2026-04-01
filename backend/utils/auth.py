"""JWT Auth + Password Hashing"""
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
from database.db import get_db
from models.user import User

SECRET_KEY = os.getenv("SECRET_KEY", "lifelens-dev-secret-key-32-characters-min")
ALGORITHM  = os.getenv("ALGORITHM", "HS256")
ACCESS_EXP = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
REFRESH_EXP= int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer  = HTTPBearer()

def hash_password(plain): return pwd_ctx.hash(plain)
def verify_password(plain, hashed): return pwd_ctx.verify(plain, hashed)

def create_access_token(data):
    p = {**data, "exp": datetime.now(timezone.utc)+timedelta(minutes=ACCESS_EXP), "type":"access"}
    return jwt.encode(p, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data):
    p = {**data, "exp": datetime.now(timezone.utc)+timedelta(days=REFRESH_EXP), "type":"refresh"}
    return jwt.encode(p, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token):
    try: return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError: raise HTTPException(401, "Invalid or expired token")

async def get_current_user(creds: HTTPAuthorizationCredentials=Depends(bearer), db: AsyncSession=Depends(get_db)) -> User:
    payload = decode_token(creds.credentials)
    uid = payload.get("sub")
    if not uid: raise HTTPException(401, "Invalid token")
    r = await db.execute(select(User).where(User.id==uid))
    user = r.scalar_one_or_none()
    if not user or not user.is_active: raise HTTPException(401, "User not found")
    return user
