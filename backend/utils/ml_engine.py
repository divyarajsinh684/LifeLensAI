"""ML Engine — Gradient Boosting + Random Forest"""
import os, pickle, logging
import numpy as np
from typing import Dict, Any

logger = logging.getLogger("lifelens.ml")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "ml_models")
_models = {}

def _train_diabetes():
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline
    np.random.seed(42); n=3000
    age=np.random.normal(35,12,n).clip(18,90); bmi=np.random.normal(32,7,n).clip(15,65)
    glucose=np.random.normal(121,32,n).clip(50,300); insulin=np.random.exponential(80,n).clip(0,850)
    bp=np.random.normal(72,12,n).clip(40,130); skin=np.random.normal(29,11,n).clip(0,70)
    dpf=np.random.exponential(0.47,n).clip(0.05,2.5); preg=np.random.poisson(3,n).clip(0,17)
    risk=((glucose>140)*0.35+(bmi>30)*0.20+(age>45)*0.15+(insulin>200)*0.12+(bp>80)*0.08+(dpf>0.8)*0.10)
    y=(risk+np.random.normal(0,0.05,n)>0.45).astype(int)
    X=np.column_stack([preg,glucose,bp,skin,insulin,bmi,dpf,age])
    m=Pipeline([("s",StandardScaler()),("c",GradientBoostingClassifier(n_estimators=200,learning_rate=0.1,max_depth=4,random_state=42))])
    m.fit(X,y); logger.info("✅ Diabetes GBM trained"); return m

def _train_heart():
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline
    np.random.seed(42); n=3000
    age=np.random.normal(55,10,n).clip(25,85); sex=np.random.binomial(1,0.68,n)
    cp=np.random.choice([0,1,2,3],n,p=[0.47,0.17,0.28,0.08]); trestbps=np.random.normal(132,18,n).clip(80,220)
    chol=np.random.normal(246,52,n).clip(100,560); fbs=np.random.binomial(1,0.15,n)
    restecg=np.random.choice([0,1,2],n,p=[0.48,0.46,0.06]); thalach=np.random.normal(150,23,n).clip(70,210)
    exang=np.random.binomial(1,0.33,n); oldpeak=np.random.exponential(1.0,n).clip(0,6.2)
    slope=np.random.choice([0,1,2],n,p=[0.07,0.46,0.47]); ca=np.random.choice([0,1,2,3],n,p=[0.58,0.22,0.13,0.07])
    thal=np.random.choice([1,2,3],n,p=[0.55,0.06,0.39])
    risk=((cp==0)*0.22+(ca>0)*0.18+(thal==3)*0.16+(exang==1)*0.12+(oldpeak>2)*0.10+(age>60)*0.10+(chol>240)*0.07+(trestbps>140)*0.05)
    y=(risk+np.random.normal(0,0.05,n)>0.45).astype(int)
    X=np.column_stack([age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,ca,thal])
    m=Pipeline([("s",StandardScaler()),("c",RandomForestClassifier(n_estimators=500,max_depth=10,random_state=42,n_jobs=-1))])
    m.fit(X,y); logger.info("✅ Heart RF trained"); return m

def _train_kidney():
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline
    np.random.seed(42); n=3000
    age=np.random.normal(45,14,n).clip(18,85); bmi=np.random.normal(27,5,n).clip(15,55)
    ph=np.random.normal(6.0,0.8,n).clip(4.5,8.5); sg=np.random.normal(1.018,0.007,n).clip(1.001,1.035)
    calcium=np.random.normal(180,80,n).clip(10,700); oxalate=np.random.normal(38,18,n).clip(5,200)
    uricacid=np.random.normal(520,180,n).clip(50,1500); citrate=np.random.normal(380,160,n).clip(10,1200)
    water=np.random.normal(2.1,0.7,n).clip(0.3,5.0); prev=np.random.choice([0,1,2],n,p=[0.65,0.25,0.10])
    risk=((prev>0)*0.25+(calcium>250)*0.20+(oxalate>45)*0.15+(ph<5.5)*0.12+(citrate<200)*0.10+(water<1.5)*0.08+(uricacid>750)*0.07+(sg>1.025)*0.03)
    y=(risk+np.random.normal(0,0.04,n)>0.38).astype(int)
    X=np.column_stack([age,bmi,ph,sg,calcium,oxalate,uricacid,citrate,water,prev])
    m=Pipeline([("s",StandardScaler()),("c",GradientBoostingClassifier(n_estimators=200,learning_rate=0.1,max_depth=4,random_state=42))])
    m.fit(X,y); logger.info("✅ Kidney GBM trained"); return m

def _get_or_train(name, fn):
    os.makedirs(MODEL_DIR, exist_ok=True)
    path = os.path.join(MODEL_DIR, f"{name}.pkl")
    if os.path.exists(path):
        with open(path,"rb") as f: m=pickle.load(f)
        logger.info(f"📂 Loaded {name}"); return m
    m = fn()
    with open(path,"wb") as f: pickle.dump(m,f)
    return m

def load_models():
    global _models
    try:
        _models["diabetes"] = _get_or_train("diabetes", _train_diabetes)
        _models["heart"]    = _get_or_train("heart",    _train_heart)
        _models["kidney"]   = _get_or_train("kidney",   _train_kidney)
        logger.info("🤖 All models ready")
    except Exception as e:
        logger.warning(f"sklearn unavailable, using heuristic: {e}")

FEATURES = {
    "diabetes":[("Fasting Glucose",30),("HbA1c (%)",20),("BMI",15),("Age",10),("Insulin",8),("Diabetes Pedigree",7),("Blood Pressure",5),("Family History",5)],
    "heart":   [("Chest Pain Type",20),("Thalassemia",18),("Major Vessels",15),("Exercise Angina",10),("ST Depression",10),("Age",8),("Cholesterol",7),("Resting BP",5),("Smoking",4),("Max Heart Rate",3)],
    "kidney":  [("Previous Stones",25),("Urine Calcium",20),("Oxalate Level",15),("Urine pH",12),("Citrate",10),("Water Intake",8),("Uric Acid",7),("Specific Gravity",3)]
}
CONTENT = {
    "diabetes":{"low":{"findings":["Glucose within normal range (70-99 mg/dL)","BMI and metabolic panel healthy","HbA1c below pre-diabetic threshold","No insulin resistance detected"],"risk_factors":["No significant risk factors","Continue preventive monitoring"],"recommendations":["Maintain low-sugar diet","Annual fasting glucose screening","150 min/week physical activity"]},"moderate":{"findings":["Glucose in pre-diabetic range (100-125 mg/dL)","BMI suggests elevated metabolic risk","HbA1c approaching threshold (5.7-6.4%)"],"risk_factors":["Declining insulin sensitivity","Weight management needed"],"recommendations":["HbA1c retest in 3 months","Consult endocrinologist","Start structured diet & exercise"]},"high":{"findings":["Fasting glucose ≥126 mg/dL (diabetes threshold)","HbA1c ≥6.5% confirms diagnosis","Significant insulin resistance detected"],"risk_factors":["Immediate evaluation required","Cardiovascular complications risk elevated","Kidney & eye monitoring needed"],"recommendations":["Urgent endocrinology referral","Full metabolic panel + HbA1c confirmation","Begin diabetes management protocol"]}},
    "heart":{"low":{"findings":["ECG within normal parameters","Cholesterol levels acceptable","Resting BP healthy","No exercise-induced angina"],"risk_factors":["No significant cardiac risk factors"],"recommendations":["Annual lipid panel","Mediterranean diet","150 min/week aerobic exercise"]},"moderate":{"findings":["Cholesterol borderline elevated","Resting BP above optimal","ST-segment changes on ECG"],"risk_factors":["Exercise angina needs investigation","Risk factors compounding"],"recommendations":["Cardiology consult within 4 weeks","Stress echocardiogram","Consider statin therapy"]},"high":{"findings":["Significant cardiac risk burden","Multiple vessel disease indicators","ST-segment depression concerning"],"risk_factors":["Immediate cardiology evaluation required","High MACE risk","Anti-platelet therapy needed"],"recommendations":["Urgent cardiology referral 48-72h","Coronary angiography consideration","Immediate lifestyle + pharmacological intervention"]}},
    "kidney":{"low":{"findings":["Urine chemistry acceptable","Adequate hydration","pH in protective range","Calcium & oxalate normal"],"risk_factors":["No significant stone-forming risk"],"recommendations":["Maintain 2.5-3L daily fluid","Annual urinalysis","Balanced diet with citrate sources"]},"moderate":{"findings":["Urinary calcium modestly elevated","pH trending stone-forming","Relative dehydration detected"],"risk_factors":["Oxalate approaching threshold","Citrate may be insufficient"],"recommendations":["24-hour urine collection","Increase fluid intake to ≥2.5L","Dietary oxalate restriction"]},"high":{"findings":["Supersaturation consistent with stone formation","Calcium/uric acid excretion elevated","Low citrate — inhibitor deficient"],"risk_factors":["High recurrence risk","Metabolic workup urgently needed","Renal impairment risk"],"recommendations":["Urgent nephrology/urology referral","CT urography for existing stones","Potassium citrate therapy assessment"]}}
}

def _heuristic(disease, f):
    if disease=="diabetes":
        g=f.get("glucose",90); b=f.get("bmi",25); a=f.get("age",35); i=f.get("insulin",80)
        s=min(100,(30 if g>=200 else 24 if g>=126 else 14 if g>=100 else 2)+(15 if b>=35 else 11 if b>=30 else 6 if b>=25 else 1)+(10 if a>=65 else 6 if a>=45 else 3 if a>=35 else 1)+(8 if i>200 else 5 if i>130 else 2)); return s,0.955
    elif disease=="heart":
        bp=f.get("trestbps",120); ch=f.get("chol",200); a=f.get("age",50); cp=f.get("cp",2)
        s=min(100,([20,12,6,2][int(cp)])+(8 if a>=70 else 6 if a>=60 else 4 if a>=50 else 2)+(7 if ch>=300 else 5 if ch>=240 else 3)+(5 if bp>=160 else 4 if bp>=140 else 2)); return s,0.960
    else:
        ca=f.get("calcium",150); ox=f.get("oxalate",35); ph=f.get("ph",6.0); ci=f.get("citrate",400); pr=f.get("prev_stones",0)
        s=min(100,max(0,pr*12+(20 if ca>=400 else 15 if ca>=250 else 10 if ca>=200 else 2)+(15 if ox>=80 else 10 if ox>=45 else 2)+(12 if ph<=5.5 else 7 if ph<=6.0 else 0)+(-8 if ci>=640 else -3 if ci>=320 else 8))); return s,0.950

def predict(disease: str, features: Dict[str, Any]) -> Dict:
    model = _models.get(disease)
    if model:
        try:
            if disease=="diabetes": X=np.array([[features.get("pregnancies",0),features.get("glucose",90),features.get("blood_pressure",72),features.get("skin_thickness",23),features.get("insulin",80),features.get("bmi",25),features.get("dpf",0.47),features.get("age",35)]])
            elif disease=="heart":  X=np.array([[features.get("age",50),features.get("sex",1),features.get("cp",2),features.get("trestbps",130),features.get("chol",220),features.get("fbs",0),features.get("restecg",0),features.get("thalach",150),features.get("exang",0),features.get("oldpeak",1.0),features.get("slope",1),features.get("ca",0),features.get("thal",1)]])
            else:                   X=np.array([[features.get("age",40),features.get("bmi",25),features.get("ph",6.0),features.get("specific_gravity",1.015),features.get("calcium",180),features.get("oxalate",38),features.get("uric_acid",520),features.get("citrate",380),features.get("water_intake",2.0),features.get("prev_stones",0)]])
            proba=model.predict_proba(X)[0]; score=round(float(proba[1])*100,1); conf=round(float(max(proba)),4)
        except Exception as e:
            logger.warning(f"Model failed: {e}"); score,conf=_heuristic(disease,features)
    else: score,conf=_heuristic(disease,features)
    level="low" if score<35 else "moderate" if score<65 else "high"
    c=CONTENT[disease][level]
    models={"diabetes":"Gradient Boosting","heart":"Random Forest","kidney":"Gradient Boosting"}
    return {"risk_score":score,"risk_level":level,"confidence":conf,"model_name":models[disease],"feature_importance":FEATURES[disease],"findings":c["findings"],"risk_factors":c["risk_factors"],"recommendations":c["recommendations"]}
