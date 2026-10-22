import os
import urllib.request
import json
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, func
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
    patient_phone = Column(String)
    patient_email = Column(String)
    doctor_name = Column(String)
    appointment_date = Column(String)
    payment_status = Column(String, default="Paid")
    prescription = Column(String, nullable=True, default="")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Healthcare Appointment Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

class AppointmentCreate(BaseModel):
    patient_name: str
    patient_phone: str
    patient_email: str
    doctor_name: str
    appointment_date: str

class AppointmentResponse(AppointmentCreate):
    id: int
    prescription: Optional[str] = ""
    payment_status: str = "Paid"
    
    class Config:
        from_attributes = True

class PrescriptionUpdate(BaseModel):
    prescription: str

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
        patient_phone=data.patient_phone, 
        patient_email=data.patient_email,
        doctor_name=data.doctor_name,
        appointment_date=data.appointment_date,
        payment_status="Paid",
        prescription=""
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    lambda_url = "https://h3xonabeb37s5xcup7oxwyobwy0skbyp.lambda-url.ap-southeast-2.on.aws/"  
    
    payload = json.dumps({
        "patient_name": data.patient_name,
        "patient_phone": data.patient_phone,
        "patient_email": data.patient_email,
        "doctor_name": data.doctor_name,
        "appointment_date": data.appointment_date
    }).encode('utf-8')

    try:
        req = urllib.request.Request(lambda_url, data=payload, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        print(f"AWS Lambda trigger failed: {e}")

    return {"message": "Appointment created successfully", "appointment_id": appointment.id}

@app.get("/appointments")
def list_appointments(db: Session = Depends(get_db)):
    return db.query(AppointmentModel).all()

@app.get("/appointments/doctor/{doctor_name}", response_model=List[AppointmentResponse])
def get_doctor_appointments(doctor_name: str, db: Session = Depends(get_db)):
    appointments = db.query(AppointmentModel).filter(AppointmentModel.doctor_name == doctor_name).all()
    return appointments

@app.put("/appointments/{appointment_id}/prescription")
def update_prescription(appointment_id: int, data: PrescriptionUpdate, db: Session = Depends(get_db)):
    appointment = db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appointment.prescription = data.prescription
    db.commit()
    
    return {"message": "Prescription saved successfully", "prescription": appointment.prescription}

class TriageRequest(BaseModel):
    symptoms: str

@app.post("/triage")
def symptom_triage(data: TriageRequest):
    symptoms = data.symptoms.lower()
    
    if any(word in symptoms for word in ["headache", "migraine", "dizziness", "vision", "brain"]):
        specialist = "Neurologist"
    elif any(word in symptoms for word in ["chest", "heart", "palpitations", "breath"]):
        specialist = "Cardiologist"
    elif any(word in symptoms for word in ["bone", "joint", "back", "knee", "fracture", "muscle"]):
        specialist = "Orthopedist"
    elif any(word in symptoms for word in ["skin", "rash", "acne", "itch"]):
        specialist = "Dermatologist"
    elif any(word in symptoms for word in ["stomach", "pain", "nausea", "vomit", "digestion"]):
        specialist = "Gastroenterologist"
    else:
        specialist = "General Physician"
        
    doctor_mapping = {
        "Neurologist": "Dr. Smith (Neurology)",
        "Cardiologist": "Dr. Davis (Cardiology)",
        "Orthopedist": "Dr. Jones (Orthopedics)",
        "Dermatologist": "Dr. Lee (Dermatology)",
        "Gastroenterologist": "Dr. Gupta (Gastro)",
        "General Physician": "Dr. Adams (General)"
    }
    
    return {
        "specialty": specialist, 
        "assigned_doctor": doctor_mapping.get(specialist)
    }
@app.get("/admin/stats")
def get_admin_stats(db: Session = Depends(get_db)):
    total_appointments = db.query(AppointmentModel).count()
    total_revenue = total_appointments * 500 
    
    doctor_stats = db.query(
        AppointmentModel.doctor_name, 
        func.count(AppointmentModel.id)
    ).group_by(AppointmentModel.doctor_name).all()
    
    return {
        "total_appointments": total_appointments,
        "total_revenue": total_revenue,
        "doctor_load": [{"doctor": doc, "count": count} for doc, count in doctor_stats]
    }