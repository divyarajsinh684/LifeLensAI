"""Prediction routes — /api/predict"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel, Field
from typing import Optional
import logging
from database.db import get_db
from models.user import User
from models.patient import Patient
from models.prediction import Prediction, DiseaseType, RiskLevel
from utils.auth import get_current_user
from utils.ml_engine import predict

router = APIRouter()
logger = logging.getLogger("lifelens.predict")

class DiabetesIn(BaseModel):
    pregnancies: Optional[float]=Field(0,ge=0,le=20); glucose: float=Field(...,ge=50,le=500)
    blood_pressure: Optional[float]=Field(72,ge=30,le=180); skin_thickness: Optional[float]=Field(23,ge=0,le=100)
    insulin: Optional[float]=Field(80,ge=0,le=900); bmi: float=Field(...,ge=10,le=70)
    dpf: Optional[float]=Field(0.47,ge=0,le=2.5); age: float=Field(...,ge=1,le=120)
    hba1c: Optional[float]=Field(5.5,ge=4,le=14); family_history: Optional[int]=Field(0,ge=0,le=2)

class HeartIn(BaseModel):
    age: float=Field(...,ge=18,le=110); sex: int=Field(...,ge=0,le=1); cp: int=Field(...,ge=0,le=3)
    trestbps: float=Field(...,ge=80,le=250); chol: float=Field(...,ge=100,le=600)
    fbs: Optional[int]=Field(0,ge=0,le=1); restecg: Optional[int]=Field(0,ge=0,le=2)
    thalach: float=Field(...,ge=60,le=250); exang: Optional[int]=Field(0,ge=0,le=1)
    oldpeak: Optional[float]=Field(0,ge=0,le=6.2); slope: Optional[int]=Field(1,ge=0,le=2)
    ca: Optional[int]=Field(0,ge=0,le=3); thal: Optional[int]=Field(1,ge=1,le=3)
    smoking: Optional[int]=Field(0,ge=0,le=2)

class KidneyIn(BaseModel):
    age: float=Field(...,ge=1,le=120); bmi: Optional[float]=Field(25,ge=10,le=70)
    ph: float=Field(...,ge=4.5,le=8.5); specific_gravity: Optional[float]=Field(1.015,ge=1.001,le=1.035)
    calcium: float=Field(...,ge=0,le=1000); oxalate: float=Field(...,ge=0,le=300)
    uric_acid: Optional[float]=Field(500,ge=0,le=2000); citrate: Optional[float]=Field(380,ge=0,le=2000)
    water_intake: Optional[float]=Field(2.0,ge=0.3,le=6.0); prev_stones: Optional[int]=Field(0,ge=0,le=10)
    creatinine: Optional[float]=Field(1.0,ge=0.1,le=20); family_history: Optional[int]=Field(0,ge=0,le=1)

class QuickIn(BaseModel):
    glucose: float=Field(...,ge=50,le=500); blood_pressure: float=Field(...,ge=30,le=200)
    bmi: float=Field(...,ge=10,le=70); insulin: float=Field(...,ge=0,le=900); age: float=Field(...,ge=1,le=120)

async def _pat(db,uid):
    r=await db.execute(select(Patient).where(Patient.user_id==uid)); return r.scalar_one_or_none()

async def _save(db,pid,disease,result,features):
    p=Prediction(patient_id=pid,disease_type=DiseaseType(disease),risk_level=RiskLevel(result["risk_level"]),risk_score=result["risk_score"],confidence=result["confidence"],model_name=result["model_name"],input_features=features,feature_importance={k:v for k,v in result["feature_importance"]},findings=result["findings"],risk_factors=result["risk_factors"],recommendations=result["recommendations"])
    db.add(p); await db.commit(); await db.refresh(p); return p

@router.post("/diabetes")
async def pred_diabetes(body: DiabetesIn, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)):
    f=body.model_dump(); r=predict("diabetes",f)
    p=await _pat(db,user.id)
    if p:
        await _save(db,p.id,"diabetes",r,f)
        p.latest_glucose=body.glucose; p.latest_bmi=body.bmi; p.latest_bp_dia=body.blood_pressure; await db.commit()
    return {"disease":"diabetes","user":user.email,**r}

@router.post("/heart")
async def pred_heart(body: HeartIn, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)):
    f=body.model_dump(); r=predict("heart",f)
    p=await _pat(db,user.id)
    if p:
        await _save(db,p.id,"heart_disease",r,f)
        p.latest_cholesterol=body.chol; p.latest_bp_sys=body.trestbps; await db.commit()
    return {"disease":"heart_disease","user":user.email,**r}

@router.post("/kidney")
async def pred_kidney(body: KidneyIn, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)):
    f=body.model_dump(); r=predict("kidney",f)
    p=await _pat(db,user.id)
    if p: await _save(db,p.id,"kidney_stones",r,f); await db.commit()
    return {"disease":"kidney_stones","user":user.email,**r}

@router.post("/quick-check")
async def quick(body: QuickIn, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)):
    d=predict("diabetes",{"glucose":body.glucose,"bmi":body.bmi,"blood_pressure":body.blood_pressure,"insulin":body.insulin,"age":body.age})
    h=predict("heart",{"age":body.age,"trestbps":body.blood_pressure,"chol":200,"sex":1,"cp":2,"thalach":max(60,220-body.age)})
    k=predict("kidney",{"age":body.age,"bmi":body.bmi,"calcium":180,"oxalate":38,"ph":6.0})
    return {"diabetes":{"risk_score":d["risk_score"],"risk_level":d["risk_level"]},"heart_disease":{"risk_score":h["risk_score"],"risk_level":h["risk_level"]},"kidney_stones":{"risk_score":k["risk_score"],"risk_level":k["risk_level"]},"overall_score":round((d["risk_score"]+h["risk_score"]+k["risk_score"])/3,1)}

@router.get("/history")
async def history(limit: int=20, db: AsyncSession=Depends(get_db), user: User=Depends(get_current_user)):
    p=await _pat(db,user.id)
    if not p: return {"predictions":[],"total":0}
    r=await db.execute(select(Prediction).where(Prediction.patient_id==p.id).order_by(desc(Prediction.created_at)).limit(limit))
    preds=r.scalars().all()
    return {"predictions":[{"id":str(x.id),"disease":x.disease_type,"risk_level":x.risk_level,"risk_score":x.risk_score,"date":x.created_at.isoformat(),"recommendations":x.recommendations} for x in preds],"total":len(preds)}
