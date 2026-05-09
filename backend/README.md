# RenalCare AI - Backend Setup Guide

## 📋 Project Structure

```
backend/
├── main.py                 # FastAPI application with all endpoints
├── database.py            # SQLAlchemy models and database setup
├── schemas.py             # Pydantic request/response models
├── image_utils.py         # Image processing utilities
├── train_vision_model.py  # U-Net training script
├── train_risk_model.py    # XGBoost risk model training
├── init_db.py             # Database initialization
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration
└── models/               # Saved trained models (created at runtime)
    ├── risk_model.pkl
    ├── risk_scaler.pkl
    └── unet_kidney_stone.pth
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python init_db.py
```

### 3. Train ML Models (Optional)
```bash
# Train vision model for stone detection
python train_vision_model.py

# Train risk prediction model
python train_risk_model.py
```

### 4. Run FastAPI Server
```bash
python main.py
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs` (Swagger UI)

## 📡 Main API Endpoints

### Patient Management
- `POST /api/patients` - Create new patient
- `GET /api/patients/{patient_id}` - Get patient details
- `GET /api/patients/{patient_id}/health-summary` - Get health overview

### Image Analysis
- `POST /api/analyze-scan` - Upload and analyze kidney stone scan
  - Returns: stone_size_mm, location, severity, confidence
- `GET /api/scans/{patient_id}` - Get all scans for patient
- `GET /api/scans/detail/{scan_id}` - Get detailed scan info

### Water Intake Tracking
- `POST /api/water-intake` - Log water intake
- `GET /api/water-intake/{patient_id}/daily` - Get daily summary
- `GET /api/water-intake/{patient_id}/history` - Get weekly/monthly history

### Meal Logging
- `POST /api/meals` - Add meal entry
- `GET /api/meals/{patient_id}/daily` - Get daily meal summary
- `GET /api/meals/{patient_id}/history` - Get meal history

### Diet Recommendations
- `GET /api/diet-recommendations/{stone_type}` - Get recommendations by stone type
- `GET /api/diet-recommendations` - Get all available recommendations
- `POST /api/diet-recommendations/{patient_id}` - Update patient's diet

### Risk Prediction
- `POST /api/predict-risk` - Predict recurrence risk
- `GET /api/patients/{patient_id}/risk-score` - Get patient's risk score

## 🔗 Frontend Integration

The backend is configured to accept requests from:
- `http://localhost:5173` (Vite default)
- `http://localhost:3000` (React default)
- `http://localhost:8000` (Backend)

### Example API Calls

**Create Patient:**
```bash
curl -X POST http://localhost:8000/api/patients \
  -H "Content-Type: application/json" \
  -d '{
    "id": "patient_001",
    "name": "Jane Smith",
    "age": 35,
    "gender": "Female",
    "bmi": 26.5,
    "family_history": true
  }'
```

**Upload and Analyze Scan:**
```bash
curl -X POST http://localhost:8000/api/analyze-scan \
  -F "patient_id=patient_001" \
  -F "stone_type=calcium_oxalate" \
  -F "file=@scan_image.png"
```

**Log Water Intake:**
```bash
curl -X POST http://localhost:8000/api/water-intake \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient_001",
    "amount_ml": 500,
    "time": "08:30",
    "notes": "Morning water intake"
  }'
```

**Add Meal:**
```bash
curl -X POST http://localhost:8000/api/meals \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient_001",
    "meal_type": "lunch",
    "food_items": [
      {"name": "Chicken Breast", "quantity": "200g", "oxalate_level": "low"},
      {"name": "Rice", "quantity": "1 cup", "oxalate_level": "low"}
    ]
  }'
```

**Get Diet Recommendations:**
```bash
curl http://localhost:8000/api/diet-recommendations/calcium_oxalate
```

**Predict Risk:**
```bash
curl -X POST http://localhost:8000/api/predict-risk \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient_001",
    "age": 35,
    "gender": "Female",
    "family_history": true,
    "previous_stones": 1,
    "treatment_compliance": 85
  }'
```

## 🗄️ Database Schema

### Patients
- id (PK)
- name, age, gender, bmi
- family_history, created_at

### KidneyScans
- id (PK), patient_id (FK)
- stone_size_mm, stone_location, severity, confidence
- stone_type, image_path, analysis_results, created_at

### WaterIntakes
- id (PK), patient_id (FK)
- amount_ml, time, date, notes, created_at

### MealLogs
- id (PK), patient_id (FK)
- meal_type (breakfast/lunch/dinner/snack)
- food_items (JSON), oxalate_level, sodium_mg, notes, created_at

### DietRecommendations
- id (PK), stone_type (unique)
- restricted_foods, recommended_foods
- daily_fluid_intake_ml, daily_sodium_limit_mg, tips

## 🤖 ML Integration

### Vision Model (U-Net)
- Path: `./models/unet_kidney_stone.pth`
- Detects: stone_size_mm, location, severity, confidence
- Currently: Mock implementation (replaces detected values)

### Risk Model (XGBoost)
- Path: `./models/risk_model.pkl`
- Predicts: recurrence risk score (0-1)
- Features: age, BMI, hydration, diet, family history, compliance

## 🔧 Environment Variables

Edit `.env` to configure:
```
DATABASE_URL=sqlite:///./renal_care.db
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
MAX_UPLOAD_SIZE_MB=50
```

## 📝 Notes

- Database uses SQLite by default (configurable in .env)
- Images are stored in `./uploads/` directory
- ML models are optional (mock endpoints work without them)
- CORS is configured to allow frontend requests
- All endpoints return structured JSON responses

## 🐛 Troubleshooting

**Port 8000 already in use:**
```bash
lsof -i :8000
kill -9 <PID>
```

**Database errors:**
```bash
rm renal_care.db  # Delete old database
python init_db.py # Reinitialize
```

**Import errors:**
```bash
pip install -r requirements.txt --upgrade
```
