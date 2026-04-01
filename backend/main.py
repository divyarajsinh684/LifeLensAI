"""LifeLens AI — FastAPI Main Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import uvicorn, logging, os, time
from fastapi import Request

from database.db import init_db
from routes import auth, predict, patients, reports, appointments

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("lifelens")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 LifeLens AI starting...")
    await init_db()
    from utils.ml_engine import load_models
    load_models()
    logger.info("✅ Ready!")
    yield

app = FastAPI(title="LifeLens AI", version="2.0.0", lifespan=lifespan, docs_url="/api/docs", redoc_url="/api/redoc")

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth.router,         prefix="/api/auth",         tags=["Auth"])
app.include_router(predict.router,      prefix="/api/predict",      tags=["Predictions"])
app.include_router(patients.router,     prefix="/api/patients",     tags=["Patients"])
app.include_router(reports.router,      prefix="/api/reports",      tags=["Reports"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["Appointments"])

frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve():
    idx = os.path.join(frontend_dir, "index.html")
    if os.path.exists(idx):
        return HTMLResponse(open(idx).read())
    return HTMLResponse("<h1>LifeLens AI running — <a href='/api/docs'>API Docs</a></h1>")

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "LifeLens AI", "version": "2.0.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host=os.getenv("HOST","0.0.0.0"), port=int(os.getenv("PORT",8000)), reload=True)
