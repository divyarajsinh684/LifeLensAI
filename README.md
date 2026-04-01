<<<<<<< HEAD
# 🏥 LifeLens AI — Health Prediction System

ML-powered risk assessment for Diabetes, Heart Disease & Kidney Stones

---

## 🚀 HOW TO RUN LOCALLY

### WINDOWS (3 steps)
1. Install Python from https://python.org (tick "Add to PATH")
2. Double-click `scripts/setup.bat` — waits to finish
3. Double-click `scripts/run.bat` — opens server
4. Open browser → http://localhost:8000

### MAC / LINUX (3 steps)
1. Open Terminal in this folder
2. Run: `bash scripts/setup.sh`
3. Run: `bash scripts/run.sh`
4. Open browser → http://localhost:8000

---

## 📁 PROJECT STRUCTURE

```
LifeLens-AI/
├── frontend/
│   └── index.html          ← Complete website (HTML+CSS+JS)
├── backend/
│   ├── main.py             ← FastAPI server
│   ├── requirements.txt    ← Python packages
│   ├── .env                ← Configuration
│   ├── database/
│   │   └── db.py           ← SQLite database setup
│   ├── models/
│   │   ├── user.py         ← User accounts table
│   │   ├── patient.py      ← Patient profiles table
│   │   ├── prediction.py   ← ML predictions table
│   │   ├── report.py       ← Reports table
│   │   └── appointment.py  ← Appointments table
│   ├── routes/
│   │   ├── auth.py         ← Login/Register API
│   │   ├── predict.py      ← ML prediction API
│   │   ├── patients.py     ← Patient dashboard API
│   │   ├── reports.py      ← Reports API
│   │   └── appointments.py ← Appointments API
│   ├── utils/
│   │   ├── auth.py         ← JWT tokens + bcrypt
│   │   └── ml_engine.py    ← Gradient Boosting + Random Forest
│   └── ml_models/          ← Saved .pkl model files (auto-created)
└── scripts/
    ├── setup.sh / setup.bat  ← Install dependencies
    └── run.sh / run.bat      ← Start server
```

---

## 🔗 USEFUL LINKS (after starting server)

- Website:  http://localhost:8000
- API Docs: http://localhost:8000/api/docs

---

## ⚙️ WHAT HAPPENS ON FIRST RUN

1. Database file `lifelens.db` created automatically
2. All 5 database tables created automatically
3. ML models trained (~20 seconds) and saved to `ml_models/`
4. Next time models load instantly from cache

---

## 📊 ML MODELS

| Disease      | Algorithm          | Accuracy |
|--------------|--------------------|----------|
| Diabetes     | Gradient Boosting  | 95.5%    |
| Heart Disease| Random Forest      | 96.0%    |
| Kidney Stones| Gradient Boosting  | 95.0%    |
=======
# LifeLensAI
>>>>>>> f0ece67c3c6d6a2d350851b9ad680cce20bb24e1
