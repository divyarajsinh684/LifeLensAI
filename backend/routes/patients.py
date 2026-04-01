"""Patient routes — /api/patients"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import Optional
from datetime import date
from database.db import get_db
from models.user import User
from models.patient import Patient
from models.prediction import Prediction
from models.appointment import Appointment
from utils.auth import get_current_user

router = APIRouter()

class PatientUpdate(BaseModel):
    date_of_birth: Optional[date]=None; sex: Optional[str]=None; blood_group: Optional[str]=None
    phone: Optional[str]=None; address: Optional[str]=None; medical_history: Optional[str]=None
    allergies: Optional[str]=None; medications: Optional[str]=None

def _pd(p,u): return {"id":p.id,"patient_code":p.patient_code,"full_name":u.full_name,"email":u.email,"dob":str(p.date_of_birth) if p.date_of_birth else None,"sex":p.sex,"blood_group":p.blood_group,"phone":p.phone,"vitals":{"glucose":p.latest_glucose,"bmi":p.latest_bmi,"bp_sys":p.latest_bp_sys,"bp_dia":p.latest_bp_dia,"cholesterol":p.latest_cholesterol,"insulin":p.latest_insulin}}

@router.get("/me")
async def get_me(user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    r=await db.execute(select(Patient).where(Patient.user_id==user.id))
    p=r.scalar_one_or_none()
    if not p: raise HTTPException(404,"Patient profile not found")
    return _pd(p,user)

@router.put("/me")
async def update_me(body: PatientUpdate, user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    r=await db.execute(select(Patient).where(Patient.user_id==user.id))
    p=r.scalar_one_or_none()
    if not p: raise HTTPException(404,"Not found")
    for k,v in body.model_dump(exclude_none=True).items(): setattr(p,k,v)
    await db.commit(); await db.refresh(p); return _pd(p,user)

@router.get("/dashboard")
async def dashboard(user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    r=await db.execute(select(Patient).where(Patient.user_id==user.id))
    p=r.scalar_one_or_none()
    if not p: raise HTTPException(404,"Not found")
    preds=(await db.execute(select(Prediction).where(Prediction.patient_id==p.id).order_by(desc(Prediction.created_at)).limit(5))).scalars().all()
    appts=(await db.execute(select(Appointment).where(Appointment.user_id==user.id).order_by(Appointment.date).limit(3))).scalars().all()
    return {"patient":_pd(p,user),"recent_predictions":[{"disease":x.disease_type,"risk_level":x.risk_level,"risk_score":x.risk_score,"date":x.created_at.isoformat()} for x in preds],"appointments":[{"code":a.appointment_code,"specialist":a.specialist_type,"date":str(a.date),"time":a.time_slot,"status":a.status} for a in appts]}
