"""
RenalCare AI - Database Initialization Script
Run this script to initialize the database with sample data
"""

from database import SessionLocal, init_db, seed_diet_recommendations, Patient
import uuid
from datetime import datetime

def init_sample_data():
    """Initialize database with sample patient data"""
    init_db()
    
    db = SessionLocal()
    
    try:
        # Seed diet recommendations
        seed_diet_recommendations(db)
        
        # Create sample patient
        sample_patient = Patient(
            id="patient_demo_001",
            name="John Doe",
            age=45,
            gender="Male",
            bmi=27.5,
            family_history=True,
            created_at=datetime.utcnow()
        )
        
        db.add(sample_patient)
        db.commit()
        
        print("✓ Database initialized with sample data")
        print(f"✓ Sample patient created: {sample_patient.id}")
        print("✓ Diet recommendations seeded")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_sample_data()
