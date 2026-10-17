import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/healthcare_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AppointmentModel(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, index=True)
    doctor_name = Column(String)
    appointment_date = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Healthcare Appointment Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)

class AppointmentCreate(BaseModel):
    patient_name: str
    doctor_name: str
    appointment_date: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "healthcare-appointment-api"}

@app.post("/appointments")
def create_appointment(data: AppointmentCreate, db: Session = Depends(get_db)):
    appointment = AppointmentModel(
        patient_name=data.patient_name,
        doctor_name=data.doctor_name,
        appointment_date=data.appointment_date
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return {"message": "Appointment created successfully", "appointment_id": appointment.id}

@app.get("/appointments")
def list_appointments(db: Session = Depends(get_db)):
    return db.query(AppointmentModel).all()