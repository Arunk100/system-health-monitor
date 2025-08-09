from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
from models import Machine
from schemas import Report, MachineOut
from routes import router

app = FastAPI()
app.include_router(router)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_methods=["*"],
	allow_headers=["*"],
)

@app.on_event("startup")
def startup():
	Base.metadata.create_all(bind=engine)
