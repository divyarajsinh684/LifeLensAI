"""Report routes — /api/reports"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from database.db import get_db
from models.user import User
from models.patient import Patient
from models.report import Report
from models.prediction import Prediction
from utils.auth import get_current_user

router = APIRouter()

@router.get("/")
async def list_reports(user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    r=await db.execute(select(Patient).where(Patient.user_id==user.id))
    p=r.scalar_one_or_none()
    if not p: return {"reports":[]}
    reps=(await db.execute(select(Report).where(Report.patient_id==p.id).order_by(desc(Report.created_at)))).scalars().all()
    return {"reports":[{"id":r.id,"code":r.report_code,"title":r.title,"summary":r.summary,"reviewed":r.is_reviewed,"date":r.created_at.isoformat()} for r in reps]}

@router.post("/generate/{prediction_id}", status_code=201)
async def generate(prediction_id: str, user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    pred=(await db.execute(select(Prediction).where(Prediction.id==prediction_id))).scalar_one_or_none()
    if not pred: raise HTTPException(404,"Prediction not found")
    pat=(await db.execute(select(Patient).where(Patient.id==pred.patient_id))).scalar_one_or_none()
    rep=Report(patient_id=pat.id,prediction_id=pred.id,report_code=Report.generate_code(),title=f"{pred.disease_type.replace('_',' ').title()} Risk Report — {pred.risk_level.title()} Risk",summary=f"AI score: {pred.risk_score}/100 · {pred.model_name} · {pred.confidence*100:.1f}% confidence")
    db.add(rep); await db.commit(); await db.refresh(rep)
    return {"id":rep.id,"code":rep.report_code,"title":rep.title,"date":rep.created_at.isoformat()}

@router.get("/{report_id}")
async def get_report(report_id: str, user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    r=(await db.execute(select(Report).where(Report.id==report_id))).scalar_one_or_none()
    if not r: raise HTTPException(404,"Not found")
    return {"id":r.id,"code":r.report_code,"title":r.title,"summary":r.summary,"reviewed":r.is_reviewed,"date":r.created_at.isoformat()}
