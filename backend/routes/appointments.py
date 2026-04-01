"""Appointment routes — /api/appointments"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from datetime import date
from database.db import get_db
from models.user import User
from models.appointment import Appointment, AppointmentStatus, AppointmentType, SpecialistType
from utils.auth import get_current_user

router = APIRouter()

class ApptCreate(BaseModel):
    specialist_type: SpecialistType; appointment_type: AppointmentType
    date: date; time_slot: str; doctor_name: Optional[str]=None
    notes: Optional[str]=None; report_ref: Optional[str]=None

class ApptUpdate(BaseModel):
    status: Optional[AppointmentStatus]=None; doctor_name: Optional[str]=None; notes: Optional[str]=None

def _ad(a): return {"id":a.id,"code":a.appointment_code,"specialist":a.specialist_type,"type":a.appointment_type,"status":a.status,"date":str(a.date),"time":a.time_slot,"doctor":a.doctor_name,"notes":a.notes,"created_at":a.created_at.isoformat()}

@router.post("/", status_code=201)
async def create(body: ApptCreate, user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    a=Appointment(user_id=user.id,appointment_code=Appointment.generate_code(),specialist_type=body.specialist_type,appointment_type=body.appointment_type,date=body.date,time_slot=body.time_slot,doctor_name=body.doctor_name,notes=body.notes,report_ref=body.report_ref,status=AppointmentStatus.CONFIRMED)
    db.add(a); await db.commit(); await db.refresh(a); return _ad(a)

@router.get("/")
async def list_appts(user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    r=await db.execute(select(Appointment).where(Appointment.user_id==user.id).order_by(Appointment.date))
    return {"appointments":[_ad(a) for a in r.scalars().all()]}

@router.put("/{appt_id}")
async def update(appt_id: str, body: ApptUpdate, user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    r=await db.execute(select(Appointment).where(Appointment.id==appt_id,Appointment.user_id==user.id))
    a=r.scalar_one_or_none()
    if not a: raise HTTPException(404,"Not found")
    for k,v in body.model_dump(exclude_none=True).items(): setattr(a,k,v)
    await db.commit(); await db.refresh(a); return _ad(a)

@router.delete("/{appt_id}")
async def cancel(appt_id: str, user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    r=await db.execute(select(Appointment).where(Appointment.id==appt_id,Appointment.user_id==user.id))
    a=r.scalar_one_or_none()
    if not a: raise HTTPException(404,"Not found")
    a.status=AppointmentStatus.CANCELLED; await db.commit()
    return {"message":"Cancelled","code":a.appointment_code}
