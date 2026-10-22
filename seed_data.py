from main import SessionLocal, AppointmentModel

def seed_database():
    db = SessionLocal()
    try:
        # 1. Clear existing database rows
        db.query(AppointmentModel).delete()
        db.commit()
        print("Existing database cleared.")

        # 2. Generate meaningful mock data
        sample_data = [
            AppointmentModel(patient_name="Rohan Joshi", patient_phone="9876543210", patient_email="rohan@example.com", doctor_name="Dr. Smith (Neurology)", appointment_date="2026-10-24 10:00", payment_status="Paid", prescription="Ibuprofen 400mg, rest for 2 days."),
            AppointmentModel(patient_name="Priya Deshmukh", patient_phone="9876543211", patient_email="priya@example.com", doctor_name="Dr. Davis (Cardiology)", appointment_date="2026-10-24 11:30", payment_status="Paid", prescription=""),
            AppointmentModel(patient_name="Amit Patil", patient_phone="9876543212", patient_email="amit@example.com", doctor_name="Dr. Jones (Orthopedics)", appointment_date="2026-10-25 09:15", payment_status="Pending", prescription="Physiotherapy recommended for 2 weeks."),
            AppointmentModel(patient_name="Sneha Iyer", patient_phone="9876543213", patient_email="sneha@example.com", doctor_name="Dr. Lee (Dermatology)", appointment_date="2026-10-25 14:00", payment_status="Paid", prescription="Topical steroid cream applied 2x daily."),
            AppointmentModel(patient_name="Vikram Singh", patient_phone="9876543214", patient_email="vikram@example.com", doctor_name="Dr. Gupta (Gastro)", appointment_date="2026-10-26 16:45", payment_status="Paid", prescription=""),
            AppointmentModel(patient_name="Anjali Sharma", patient_phone="9876543215", patient_email="anjali@example.com", doctor_name="Dr. Smith (Neurology)", appointment_date="2026-10-27 10:30", payment_status="Paid", prescription="")
        ]

        # 3. Insert and commit
        db.add_all(sample_data)
        db.commit()
        print(f"Successfully seeded {len(sample_data)} realistic hospital records.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()