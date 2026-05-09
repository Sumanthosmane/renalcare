"""
RenalCare AI - FastAPI Backend
Complete backend for kidney stone analysis, tracking, and recommendations
"""

from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import pickle
import json
import uuid
import os

# Import local modules
from database import init_db, get_db, seed_diet_recommendations, Patient, KidneyScan, WaterIntake, MealLog, DietRecommendation
from image_utils import save_upload_file, analyze_image_file
from schemas import (
    PatientCreate, PatientResponse, ScanUploadRequest, ScanResponse, ScanDetailedResponse,
    WaterIntakeCreate, WaterIntakeResponse, DailyWaterSummary,
    MealLogCreate, MealLogResponse, DailyMealSummary, MealItemCreate,
    DietRecommendationRequest, DietRecommendationResponse,
    RiskPredictionRequest, RiskPredictionResponse,
    SuccessResponse, ErrorResponse, HealthSummary
)

# ============= FastAPI App Setup =============

app = FastAPI(
    title="RenalCare AI",
    description="Advanced Kidney Stone Detection and Management System",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176", "http://localhost:5177", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= Initialization =============

@app.on_event("startup")
def startup_event():
    """Initialize database on startup"""
    init_db()
    print("✓ Database initialized")
    
    # Seed diet recommendations
    db = next(get_db())
    seed_diet_recommendations(db)
    db.close()


# ============= Health Check =============

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "message": "RenalCare AI API is running",
        "version": "2.0.0",
        "status": "operational"
    }


@app.get("/api/health")
def health_check():
    """API health status"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "database": "connected",
            "image_processing": "ready",
            "ml_models": "loaded"
        }
    }


# ============= Patient Management Endpoints =============

@app.post("/api/patients", response_model=PatientResponse)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """Create a new patient"""
    # Check if patient already exists
    existing = db.query(Patient).filter(Patient.id == patient.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Patient already exists")
    
    db_patient = Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@app.get("/api/patients/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    """Get patient details"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@app.get("/api/patients/{patient_id}/health-summary", response_model=HealthSummary)
def get_health_summary(patient_id: str, db: Session = Depends(get_db)):
    """Get patient's comprehensive health summary"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get latest scan
    latest_scan = db.query(KidneyScan).filter(
        KidneyScan.patient_id == patient_id
    ).order_by(KidneyScan.created_at.desc()).first()
    
    # Get today's water intake
    today = datetime.utcnow().date()
    today_intakes = db.query(WaterIntake).filter(
        WaterIntake.patient_id == patient_id,
        func.date(WaterIntake.date) == today
    ).all()
    total_water = sum(intake.amount_ml for intake in today_intakes)
    
    # Get today's meals
    today_meals = db.query(MealLog).filter(
        MealLog.patient_id == patient_id,
        func.date(MealLog.date) == today
    ).all()
    
    # Calculate risk (mock for now - integrate real model later)
    risk_score = calculate_patient_risk(patient, db)
    
    return HealthSummary(
        patient_id=patient.id,
        name=patient.name,
        latest_scan=latest_scan,
        today_water_intake_ml=total_water,
        water_goal_ml=3000,
        today_meals_count=len(today_meals),
        risk_score=risk_score,
        risk_level=get_risk_level(risk_score),
        recommendations=get_health_recommendations(patient, latest_scan, total_water)
    )


# ============= Image Upload & Analysis Endpoints =============

@app.post("/api/analyze-scan", response_model=ScanResponse)
async def analyze_scan(
    patient_id: str,
    stone_type: str = "calcium_oxalate",
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and analyze kidney stone scan
    Returns: stone size, location, severity, confidence
    """
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    try:
        # Save uploaded file
        file_content = await file.read()
        filename = f"{patient_id}_{uuid.uuid4()}.png"
        file_path = save_upload_file(file_content, filename)
        
        # Analyze image
        analysis = analyze_image_file(file_path)
        
        if not analysis["success"]:
            raise HTTPException(status_code=400, detail=f"Analysis failed: {analysis['error']}")
        
        stone_data = analysis["analysis"]
        
        # Save scan result to database
        scan_id = f"scan_{uuid.uuid4()}"
        db_scan = KidneyScan(
            id=scan_id,
            patient_id=patient_id,
            image_path=file_path,
            stone_size_mm=stone_data["stone_size_mm"],
            stone_location=stone_data["location"],
            severity=stone_data["severity"],
            confidence=stone_data["confidence"],
            stone_type=stone_type,
            analysis_results=json.dumps(stone_data)
        )
        
        db.add(db_scan)
        db.commit()
        db.refresh(db_scan)
        
        return db_scan
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing scan: {str(e)}")


@app.get("/api/scans/{patient_id}", response_model=list[ScanResponse])
def get_patient_scans(patient_id: str, db: Session = Depends(get_db)):
    """Get all scans for a patient"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    scans = db.query(KidneyScan).filter(
        KidneyScan.patient_id == patient_id
    ).order_by(KidneyScan.created_at.desc()).all()
    
    return scans


@app.get("/api/scans/detail/{scan_id}", response_model=ScanDetailedResponse)
def get_scan_detail(scan_id: str, db: Session = Depends(get_db)):
    """Get detailed scan information"""
    scan = db.query(KidneyScan).filter(KidneyScan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


# ============= Water Intake Tracking Endpoints =============

@app.post("/api/water-intake", response_model=WaterIntakeResponse)
def log_water_intake(intake: WaterIntakeCreate, db: Session = Depends(get_db)):
    """Log daily water intake"""
    patient = db.query(Patient).filter(Patient.id == intake.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    intake_id = f"water_{uuid.uuid4()}"
    current_time = intake.time or datetime.utcnow().strftime("%H:%M")
    
    db_intake = WaterIntake(
        id=intake_id,
        patient_id=intake.patient_id,
        amount_ml=intake.amount_ml,
        time=current_time,
        notes=intake.notes,
        date=datetime.utcnow()
    )
    
    db.add(db_intake)
    db.commit()
    db.refresh(db_intake)
    
    return db_intake


@app.get("/api/water-intake/{patient_id}/daily", response_model=DailyWaterSummary)
def get_daily_water_summary(
    patient_id: str,
    date: str = None,
    db: Session = Depends(get_db)
):
    """Get daily water intake summary"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Parse date
    if date:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    else:
        target_date = datetime.utcnow().date()
    
    # Query intakes for the day
    intakes = db.query(WaterIntake).filter(
        WaterIntake.patient_id == patient_id,
        func.date(WaterIntake.date) == target_date
    ).all()
    
    total_intake = sum(intake.amount_ml for intake in intakes)
    goal = 3000  # Default 3L per day
    percentage = (total_intake / goal) * 100 if goal > 0 else 0
    
    return DailyWaterSummary(
        date=target_date.isoformat(),
        total_intake_ml=total_intake,
        goal_ml=goal,
        percentage=min(percentage, 100),
        intakes=intakes
    )


@app.get("/api/water-intake/{patient_id}/history")
def get_water_history(
    patient_id: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get water intake history (last N days)"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    intakes = db.query(WaterIntake).filter(
        WaterIntake.patient_id == patient_id,
        WaterIntake.date >= start_date
    ).order_by(WaterIntake.date.desc()).all()
    
    # Group by date
    history = {}
    for intake in intakes:
        date_key = intake.date.date().isoformat()
        if date_key not in history:
            history[date_key] = {"total_ml": 0, "intakes": []}
        history[date_key]["total_ml"] += intake.amount_ml
        history[date_key]["intakes"].append(intake)
    
    return {
        "patient_id": patient_id,
        "days": days,
        "data": history
    }


# ============= Meal Logging Endpoints =============

@app.post("/api/meals", response_model=MealLogResponse)
def log_meal(meal: MealLogCreate, db: Session = Depends(get_db)):
    """Log a meal"""
    patient = db.query(Patient).filter(Patient.id == meal.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Calculate oxalate level and sodium
    oxalate_levels = [item.oxalate_level for item in meal.food_items]
    if "high" in oxalate_levels:
        final_oxalate = "high"
    elif "medium" in oxalate_levels:
        final_oxalate = "medium"
    else:
        final_oxalate = "low"
    
    # Mock sodium calculation (in real scenario, use nutritional database)
    base_sodium = {"breakfast": 800, "lunch": 1200, "dinner": 1200, "snack": 400}
    sodium_mg = base_sodium.get(meal.meal_type, 500)
    
    meal_id = f"meal_{uuid.uuid4()}"
    
    db_meal = MealLog(
        id=meal_id,
        patient_id=meal.patient_id,
        date=datetime.utcnow(),
        meal_type=meal.meal_type,
        food_items=json.dumps([item.dict() for item in meal.food_items]),
        oxalate_level=final_oxalate,
        sodium_mg=sodium_mg,
        notes=meal.notes
    )
    
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    
    return db_meal


@app.get("/api/meals/{patient_id}/daily", response_model=DailyMealSummary)
def get_daily_meals(
    patient_id: str,
    date: str = None,
    db: Session = Depends(get_db)
):
    """Get daily meal summary"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Parse date
    if date:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    else:
        target_date = datetime.utcnow().date()
    
    # Query meals for the day
    meals = db.query(MealLog).filter(
        MealLog.patient_id == patient_id,
        func.date(MealLog.date) == target_date
    ).all()
    
    # Calculate totals
    total_sodium = sum(meal.sodium_mg for meal in meals)
    high_oxalate_items = []
    
    for meal in meals:
        if meal.oxalate_level == "high":
            food_items = json.loads(meal.food_items)
            high_oxalate_items.extend([item["name"] for item in food_items if item.get("oxalate_level") == "high"])
    
    # Get recommendations based on latest scan
    recommendations = get_meal_recommendations(patient_id, db)
    
    return DailyMealSummary(
        date=target_date.isoformat(),
        meals=meals,
        total_sodium_mg=total_sodium,
        high_oxalate_items=list(set(high_oxalate_items)),
        recommendations=recommendations
    )


@app.get("/api/meals/{patient_id}/history")
def get_meal_history(
    patient_id: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get meal history (last N days)"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    meals = db.query(MealLog).filter(
        MealLog.patient_id == patient_id,
        MealLog.date >= start_date
    ).order_by(MealLog.date.desc()).all()
    
    return {
        "patient_id": patient_id,
        "days": days,
        "total_meals": len(meals),
        "meals": meals
    }


# ============= Diet Recommendations Endpoints =============

@app.get("/api/diet-recommendations/{stone_type}", response_model=DietRecommendationResponse)
def get_diet_recommendations(stone_type: str, db: Session = Depends(get_db)):
    """Get diet recommendations based on stone type"""
    rec = db.query(DietRecommendation).filter(
        DietRecommendation.stone_type == stone_type
    ).first()
    
    if not rec:
        raise HTTPException(status_code=404, detail="Stone type not found")
    
    return DietRecommendationResponse(
        stone_type=rec.stone_type,
        restricted_foods=json.loads(rec.restricted_foods),
        recommended_foods=json.loads(rec.recommended_foods),
        daily_fluid_intake_ml=rec.daily_fluid_intake_ml,
        daily_sodium_limit_mg=rec.daily_sodium_limit_mg,
        tips=json.loads(rec.tips)
    )


@app.get("/api/diet-recommendations")
def get_all_diet_recommendations(db: Session = Depends(get_db)):
    """Get all available diet recommendations"""
    recs = db.query(DietRecommendation).all()
    
    result = []
    for rec in recs:
        result.append({
            "stone_type": rec.stone_type,
            "restricted_foods": json.loads(rec.restricted_foods),
            "recommended_foods": json.loads(rec.recommended_foods),
            "daily_fluid_intake_ml": rec.daily_fluid_intake_ml,
            "daily_sodium_limit_mg": rec.daily_sodium_limit_mg,
            "tips": json.loads(rec.tips)
        })
    
    return result


@app.post("/api/diet-recommendations/{patient_id}")
def update_patient_diet(
    patient_id: str,
    stone_type: str,
    db: Session = Depends(get_db)
):
    """Update patient's diet recommendations based on latest scan"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    rec = db.query(DietRecommendation).filter(
        DietRecommendation.stone_type == stone_type
    ).first()
    
    if not rec:
        raise HTTPException(status_code=404, detail="Stone type not found")
    
    return {
        "patient_id": patient_id,
        "stone_type": stone_type,
        "diet_recommendations": {
            "restricted_foods": json.loads(rec.restricted_foods),
            "recommended_foods": json.loads(rec.recommended_foods),
            "daily_fluid_intake_ml": rec.daily_fluid_intake_ml,
            "daily_sodium_limit_mg": rec.daily_sodium_limit_mg,
            "tips": json.loads(rec.tips)
        }
    }


# ============= Risk Prediction Endpoints =============

@app.post("/api/predict-risk", response_model=RiskPredictionResponse)
def predict_risk(request: RiskPredictionRequest, db: Session = Depends(get_db)):
    """Predict kidney stone recurrence risk"""
    patient = db.query(Patient).filter(Patient.id == request.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Simple risk calculation (integrate XGBoost model here)
    risk_score = calculate_risk_score(
        age=request.age,
        family_history=request.family_history,
        previous_stones=request.previous_stones,
        compliance=request.treatment_compliance
    )
    
    risk_level = get_risk_level(risk_score)
    
    return RiskPredictionResponse(
        patient_id=request.patient_id,
        risk_score=risk_score,
        risk_level=risk_level,
        recommendations=get_risk_recommendations(risk_score),
        last_updated=datetime.utcnow()
    )


@app.get("/api/patients/{patient_id}/risk-score")
def get_patient_risk_score(patient_id: str, db: Session = Depends(get_db)):
    """Get current risk score for a patient"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    risk_score = calculate_patient_risk(patient, db)
    
    return {
        "patient_id": patient_id,
        "risk_score": risk_score,
        "risk_level": get_risk_level(risk_score),
        "timestamp": datetime.utcnow()
    }


# ============= Helper Functions =============

def calculate_risk_score(age: int, family_history: bool, previous_stones: int, compliance: float) -> float:
    """Calculate risk score based on patient factors"""
    score = 0.0
    
    # Age factor
    if age > 60:
        score += 0.15
    elif age > 40:
        score += 0.10
    
    # Family history
    if family_history:
        score += 0.20
    
    # Previous stones
    score += (previous_stones / 10) * 0.30
    
    # Treatment compliance
    score += (1 - compliance / 100) * 0.25
    
    # Add baseline risk
    score += 0.10
    
    return min(score, 1.0)


def calculate_patient_risk(patient: Patient, db: Session) -> float:
    """Calculate overall risk for a patient"""
    # Get latest scan
    latest_scan = db.query(KidneyScan).filter(
        KidneyScan.patient_id == patient.id
    ).order_by(KidneyScan.created_at.desc()).first()
    
    stone_count = db.query(func.count(KidneyScan.id)).filter(
        KidneyScan.patient_id == patient.id
    ).scalar()
    
    risk = calculate_risk_score(
        age=patient.age,
        family_history=patient.family_history,
        previous_stones=int(stone_count),
        compliance=75.0  # Default compliance
    )
    
    return risk


def get_risk_level(risk_score: float) -> str:
    """Get risk level label"""
    if risk_score < 0.33:
        return "Low"
    elif risk_score < 0.66:
        return "Moderate"
    else:
        return "High"


def get_risk_recommendations(risk_score: float) -> list:
    """Get recommendations based on risk score"""
    recommendations = [
        "Maintain daily hydration of 2.5-3 liters",
        "Follow recommended diet for your stone type",
        "Reduce sodium intake below 2000mg per day",
    ]
    
    if risk_score > 0.66:
        recommendations.extend([
            "Schedule monthly urologist follow-ups",
            "Consider preventive medication consultation",
            "Monitor for stone symptoms closely"
        ])
    elif risk_score > 0.33:
        recommendations.extend([
            "Schedule quarterly urologist check-ups",
            "Maintain detailed meal and water intake logs"
        ])
    else:
        recommendations.extend([
            "Continue regular annual check-ups",
            "Maintain current healthy lifestyle"
        ])
    
    return recommendations


def get_health_recommendations(patient: Patient, latest_scan, total_water: float) -> list:
    """Get personalized health recommendations"""
    recommendations = []
    
    if latest_scan:
        if latest_scan.severity == "severe":
            recommendations.append("⚠️ Severe stone detected - consult urologist immediately")
        elif latest_scan.severity == "moderate":
            recommendations.append("Consider medical intervention for stone management")
    
    if total_water < 2500:
        recommendations.append("💧 Increase water intake - aim for 3 liters per day")
    
    recommendations.append("🥗 Follow your personalized diet recommendations")
    recommendations.append("📊 Track your meals and water intake daily")
    
    return recommendations


def get_meal_recommendations(patient_id: str, db: Session) -> list:
    """Get meal recommendations based on patient's stone type"""
    latest_scan = db.query(KidneyScan).filter(
        KidneyScan.patient_id == patient_id
    ).order_by(KidneyScan.created_at.desc()).first()
    
    recommendations = [
        "Stay hydrated with 3+ liters of water daily",
        "Monitor sodium intake - keep below 2000mg",
        "Avoid processed foods"
    ]
    
    if latest_scan:
        if latest_scan.stone_type == "calcium_oxalate":
            recommendations.extend([
                "Limit oxalate-rich foods like spinach and nuts",
                "Maintain adequate calcium intake"
            ])
        elif latest_scan.stone_type == "uric_acid":
            recommendations.extend([
                "Reduce purine-rich foods (red meat, seafood)",
                "Avoid alcohol and sugary drinks"
            ])
    
    return recommendations


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
