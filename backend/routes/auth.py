"""Auth routes — /api/auth"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timezone
from typing import Optional
import logging
from database.db import get_db
from models.user import User, UserRole
from models.patient import Patient
from utils.auth import hash_password, verify_password, create_access_token, create_refresh_token, decode_token, get_current_user

router = APIRouter()
logger = logging.getLogger("lifelens.auth")

class RegisterReq(BaseModel):
    email: EmailStr; password: str=Field(min_length=6)
    first_name: str=Field(min_length=1); last_name: str=Field(min_length=1)
    role: Optional[UserRole]=UserRole.PATIENT

class LoginReq(BaseModel):
    email: EmailStr; password: str

class RefreshReq(BaseModel):
    refresh_token: str

class ChangePwReq(BaseModel):
    current_password: str; new_password: str=Field(min_length=6)

def _resp(user,access,refresh):
    return {"access_token":access,"refresh_token":refresh,"token_type":"bearer","user":{"id":user.id,"email":user.email,"first_name":user.first_name,"last_name":user.last_name,"full_name":user.full_name,"role":user.role}}

@router.post("/register", status_code=201)
async def register(body: RegisterReq, db: AsyncSession=Depends(get_db)):
    ex = await db.execute(select(User).where(User.email==body.email.lower()))
    if ex.scalar_one_or_none(): raise HTTPException(409,"Email already registered")
    user = User(email=body.email.lower(),hashed_password=hash_password(body.password),first_name=body.first_name.strip(),last_name=body.last_name.strip(),role=body.role)
    db.add(user); await db.flush()
    if body.role==UserRole.PATIENT: db.add(Patient(user_id=user.id,patient_code=Patient.generate_code()))
    await db.commit(); await db.refresh(user)
    logger.info(f"Registered: {user.email}")
    return _resp(user,create_access_token({"sub":user.id}),create_refresh_token({"sub":user.id}))

@router.post("/login")
async def login(body: LoginReq, db: AsyncSession=Depends(get_db)):
    r = await db.execute(select(User).where(User.email==body.email.lower()))
    user: User = r.scalar_one_or_none()
    if not user or not verify_password(body.password,user.hashed_password): raise HTTPException(401,"Invalid email or password")
    if not user.is_active: raise HTTPException(403,"Account disabled")
    user.last_login=datetime.now(timezone.utc); await db.commit()
    logger.info(f"Login: {user.email}")
    return _resp(user,create_access_token({"sub":user.id}),create_refresh_token({"sub":user.id}))

@router.post("/refresh")
async def refresh(body: RefreshReq, db: AsyncSession=Depends(get_db)):
    p=decode_token(body.refresh_token)
    if p.get("type")!="refresh": raise HTTPException(401,"Invalid refresh token")
    r=await db.execute(select(User).where(User.id==p["sub"]))
    user=r.scalar_one_or_none()
    if not user: raise HTTPException(401,"User not found")
    return _resp(user,create_access_token({"sub":user.id}),create_refresh_token({"sub":user.id}))

@router.get("/me")
async def me(user: User=Depends(get_current_user)):
    return {"id":user.id,"email":user.email,"first_name":user.first_name,"last_name":user.last_name,"full_name":user.full_name,"role":user.role}

@router.put("/change-password")
async def change_pw(body: ChangePwReq, user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    if not verify_password(body.current_password,user.hashed_password): raise HTTPException(400,"Current password incorrect")
    user.hashed_password=hash_password(body.new_password); await db.commit()
    return {"message":"Password updated"}

@router.post("/logout")
async def logout(): return {"message":"Logged out"}
