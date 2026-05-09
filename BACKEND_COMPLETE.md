# RenalCare AI - Complete Backend Documentation

## 🎯 Project Overview

RenalCare AI is an advanced kidney stone management system with:
- **Image Analysis**: U-Net based stone detection (size, location, severity)
- **Risk Prediction**: XGBoost model for recurrence risk
- **Health Tracking**: Water intake & meal logging
- **Personalized Recommendations**: Diet based on stone type

---

## 📂 Backend Architecture

```
backend/
├── main.py                    # FastAPI application (40+ endpoints)
├── database.py               # SQLAlchemy models & initialization
├── schemas.py                # Pydantic validation models
├── image_utils.py            # Image processing & stone detection
├── train_vision_model.py     # U-Net training script
├── train_risk_model.py       # XGBoost training script
├── init_db.py               # Database seeder
├── setup.py / setup.sh      # Installation scripts
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
└── models/                  # ML models (runtime created)
    ├── risk_model.pkl
    ├── risk_scaler.pkl
    └── unet_kidney_stone.pth
```

---

## 🚀 Quick Start (5 minutes)

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Initialize Database
```bash
python init_db.py
```

### Step 3: Run Backend
```bash
python main.py
```

**Backend available at:** `http://localhost:8000`  
**API Docs:** `http://localhost:8000/docs`

---

## 📡 Core API Endpoints

### 1. **Patient Management**
```
POST   /api/patients                           Create patient
GET    /api/patients/{patient_id}              Get patient info
GET    /api/patients/{patient_id}/health-summary  Health dashboard
```

### 2. **Image Analysis** ⭐
```
POST   /api/analyze-scan                       Upload & analyze scan
       Returns: stone_size_mm, location, severity, confidence
GET    /api/scans/{patient_id}                 Get all patient scans
GET    /api/scans/detail/{scan_id}             Get scan details
```

### 3. **Water Intake Tracking** 💧
```
POST   /api/water-intake                       Log water intake (ml)
GET    /api/water-intake/{patient_id}/daily    Daily summary + progress
GET    /api/water-intake/{patient_id}/history  7/14/30-day history
```

### 4. **Meal Logging** 🍽️
```
POST   /api/meals                              Add meal with food items
GET    /api/meals/{patient_id}/daily           Daily summary + sodium/oxalate
GET    /api/meals/{patient_id}/history         Meal history
```

### 5. **Diet Recommendations** 📋
```
GET    /api/diet-recommendations/{stone_type}  Get diet for stone type
       Supports: calcium_oxalate, uric_acid, struvite, cystine
GET    /api/diet-recommendations               All recommendations
POST   /api/diet-recommendations/{patient_id}  Update patient diet
```

### 6. **Risk Prediction** ⚠️
```
POST   /api/predict-risk                       Predict recurrence risk (0-1)
GET    /api/patients/{patient_id}/risk-score   Current risk score
```

---

## 🔌 Frontend Integration

### Example: Upload Scan & Get Results
```javascript
import { uploadScan } from './api.js';

const handleScanUpload = async (file) => {
  const result = await uploadScan('patient_001', 'calcium_oxalate', file);
  
  console.log('Stone Analysis:');
  console.log(`  Size: ${result.stone_size_mm}mm`);
  console.log(`  Location: ${result.stone_location}`);
  console.log(`  Severity: ${result.severity}`);
  console.log(`  Confidence: ${(result.confidence * 100).toFixed(1)}%`);
};
```

### Example: Track Water Intake
```javascript
import { logWaterIntake, getDailyWaterSummary } from './api.js';

const trackWater = async (patientId) => {
  // Log water intake
  await logWaterIntake({
    patient_id: patientId,
    amount_ml: 500,
    time: "09:30"
  });
  
  // Get daily summary
  const summary = await getDailyWaterSummary(patientId);
  console.log(`Today: ${summary.total_intake_ml}ml / ${summary.goal_ml}ml`);
  console.log(`Progress: ${summary.percentage}%`);
};
```

### Example: Log Meals
```javascript
import { logMeal, getDailyMealSummary } from './api.js';

const addMeal = async (patientId) => {
  await logMeal({
    patient_id: patientId,
    meal_type: 'lunch',
    food_items: [
      { name: 'Chicken Breast', quantity: '200g', oxalate_level: 'low' },
      { name: 'White Rice', quantity: '1 cup', oxalate_level: 'low' }
    ]
  });
  
  const summary = await getDailyMealSummary(patientId);
  console.log(`Total Sodium: ${summary.total_sodium_mg}mg`);
};
```

### Example: Get Risk Score
```javascript
import { predictRisk } from './api.js';

const assessRisk = async (patientId, patient) => {
  const riskData = await predictRisk({
    patient_id: patientId,
    age: patient.age,
    gender: patient.gender,
    family_history: patient.family_history,
    previous_stones: 1,
    treatment_compliance: 85
  });
  
  console.log(`Risk Score: ${(riskData.risk_score * 100).toFixed(1)}%`);
  console.log(`Risk Level: ${riskData.risk_level}`);
  riskData.recommendations.forEach(rec => console.log(`  • ${rec}`));
};
```

---

## 🤖 Machine Learning Models

### Vision Model (U-Net)
- **Purpose**: Stone detection in medical images
- **Input**: Medical scan image (PNG, JPG, DICOM)
- **Output**: 
  - `stone_size_mm`: Detected size
  - `location`: Left/Right/Center + Upper/Lower
  - `severity`: mild/moderate/severe
  - `confidence`: 0-1 confidence score

**Training:**
```bash
python train_vision_model.py
```

### Risk Model (XGBoost)
- **Purpose**: Predict kidney stone recurrence risk
- **Input Features**:
  - Age, BMI, Hydration Score, Diet Score
  - Family History, Previous Stones, Stone Type
  - Treatment Compliance, Daily Sodium Intake
- **Output**: Risk probability (0-1)

**Training:**
```bash
python train_risk_model.py
```

---

## 🗄️ Database Schema

### Patients Table
```
id (PK)           | String    | Unique patient ID
name              | String    | Patient name
age               | Integer   | Age in years
gender            | String    | Male/Female
bmi               | Float     | Body Mass Index
family_history    | Boolean   | Family history of stones
created_at        | DateTime  | Creation timestamp
```

### KidneyScans Table
```
id (PK)                | String    | Unique scan ID
patient_id (FK)        | String    | Reference to patient
image_path             | String    | Path to uploaded image
stone_size_mm          | Float     | Detected stone size
stone_location         | String    | Location in kidneys/ureter
severity               | String    | mild/moderate/severe/none
confidence             | Float     | Detection confidence (0-1)
stone_type             | String    | calcium_oxalate, etc.
analysis_results       | Text(JSON)| Detailed analysis data
created_at             | DateTime  | Analysis timestamp
```

### WaterIntakes Table
```
id (PK)        | String    | Unique intake ID
patient_id (FK)| String    | Reference to patient
date           | DateTime  | Date of intake
amount_ml      | Float     | Water amount in milliliters
time           | String    | Time of intake (HH:MM)
notes          | String    | Optional notes
created_at     | DateTime  | Log timestamp
```

### MealLogs Table
```
id (PK)        | String    | Unique meal ID
patient_id (FK)| String    | Reference to patient
date           | DateTime  | Date of meal
meal_type      | String    | breakfast/lunch/dinner/snack
food_items     | Text(JSON)| Array of food items
oxalate_level  | String    | low/medium/high
sodium_mg      | Float     | Total sodium in mg
notes          | String    | Optional notes
created_at     | DateTime  | Log timestamp
```

### DietRecommendations Table
```
id (PK)                    | String        | Unique ID
stone_type (UNIQUE)        | String        | Stone type
restricted_foods           | Text(JSON)    | Foods to avoid
recommended_foods          | Text(JSON)    | Foods to eat
daily_fluid_intake_ml      | Integer       | Daily water goal
daily_sodium_limit_mg      | Integer       | Sodium limit
tips                       | Text(JSON)    | Diet tips
```

---

## 🔐 Configuration

Edit `.env` to customize:
```
# Database
DATABASE_URL=sqlite:///./renal_care.db

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# File Upload
MAX_UPLOAD_SIZE_MB=50
UPLOAD_DIRECTORY=./uploads

# ML Models
RISK_MODEL_PATH=./models/risk_model.pkl
VISION_MODEL_PATH=./models/unet_kidney_stone.pth
```

---

## 📊 Data Flow

```
User Frontend              Backend API              Database
    │                           │                      │
    ├─ Upload Scan ───────────> /api/analyze-scan      │
    │                      Process & analyze           │
    │                           ├─────────────────────> Store result
    │                           │                      │
    │ <───── Stone Analysis ────┤ <───── Query result ──┤
    │   (size, location,        │                      │
    │    severity, confidence)  │                      │
    │                           │                      │
    ├─ Log Water ──────────────> /api/water-intake     │
    │                           ├─────────────────────> Store intake
    │                           │                      │
    │ <───── Daily Summary ─────┤ <───── Query intake ──┤
    │   (total, progress %)     │                      │
    │                           │                      │
    ├─ Add Meal ───────────────> /api/meals            │
    │                           ├─────────────────────> Store meal
    │                           │                      │
    │ <───── Meal Summary ──────┤ <───── Query meals ───┤
    │   (sodium, oxalate)       │                      │
    │                           │                      │
    ├─ Get Diet ───────────────> /api/diet-recommendations
    │                           ├─────────────────────> Query diet rec
    │                           │                      │
    │ <───── Recommendations ───┤ <───────────────────┤
    │   (foods, tips)           │                      │
    │                           │                      │
    ├─ Predict Risk ───────────> /api/predict-risk     │
    │                      Calculate score             │
    │ <───── Risk Score ─────────┤                      │
    │   (0-1, recommendations)   │                      │
```

---

## 🔧 Advanced Features

### Automatic Recommendations
- Based on latest scan stone type
- Water intake tracking with daily goals
- Meal analysis for sodium/oxalate levels
- Risk score trending

### Data Persistence
- SQLite database (configurable to PostgreSQL)
- Automatic backups recommended
- Data relationships maintained

### Error Handling
- Comprehensive error messages
- Validation on all inputs
- Graceful failure modes

---

## 📋 API Response Examples

### Scan Upload Response
```json
{
  "id": "scan_123",
  "patient_id": "patient_001",
  "stone_size_mm": 6.5,
  "stone_location": "Right Upper",
  "severity": "moderate",
  "confidence": 0.85,
  "stone_type": "calcium_oxalate",
  "created_at": "2024-05-08T10:30:00"
}
```

### Water Intake Summary Response
```json
{
  "date": "2024-05-08",
  "total_intake_ml": 2500,
  "goal_ml": 3000,
  "percentage": 83.33,
  "intakes": [
    {"id": "w1", "amount_ml": 500, "time": "08:30"},
    {"id": "w2", "amount_ml": 750, "time": "12:00"},
    {"id": "w3", "amount_ml": 500, "time": "15:30"},
    {"id": "w4", "amount_ml": 750, "time": "19:00"}
  ]
}
```

### Diet Recommendations Response
```json
{
  "stone_type": "calcium_oxalate",
  "restricted_foods": ["spinach", "beets", "nuts", "chocolate"],
  "recommended_foods": ["chicken", "rice", "apples", "pasta"],
  "daily_fluid_intake_ml": 3000,
  "daily_sodium_limit_mg": 2000,
  "tips": [
    "Drink plenty of water",
    "Limit oxalate-rich foods",
    "Avoid excess sodium"
  ]
}
```

### Risk Prediction Response
```json
{
  "patient_id": "patient_001",
  "risk_score": 0.34,
  "risk_level": "Moderate",
  "recommendations": [
    "Schedule quarterly urologist check-ups",
    "Maintain detailed meal and water intake logs",
    "Follow recommended diet for stone type"
  ],
  "last_updated": "2024-05-08T10:30:00"
}
```

---

## 🐛 Troubleshooting

### Port 8000 Already in Use
```bash
lsof -i :8000        # Find process
kill -9 <PID>        # Kill process
```

### Database Connection Error
```bash
rm renal_care.db     # Delete old database
python init_db.py    # Reinitialize
```

### Module Import Error
```bash
pip install -r requirements.txt --upgrade
python -m pip cache purge
```

### CORS Issues
Add frontend URL to `.env`:
```
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 📚 Additional Resources

- **API Documentation**: `http://localhost:8000/docs`
- **Frontend Integration**: `FRONTEND_INTEGRATION.md`
- **Backend README**: `backend/README.md`
- **Database Queries**: See `database.py` models

---

## ✅ Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Backend dependencies installed
- [ ] Database initialized
- [ ] Backend running on 8000
- [ ] API docs accessible at `/docs`
- [ ] Frontend can communicate with backend
- [ ] Sample patient created
- [ ] Image analysis working
- [ ] Water tracking functional
- [ ] Meal logging functional
- [ ] Diet recommendations displaying
- [ ] Risk score calculating

---

## 🚀 Production Deployment

For production:
1. Change DATABASE_URL to PostgreSQL
2. Set ENVIRONMENT=production
3. Use SECRET_KEY from environment
4. Enable HTTPS/SSL
5. Set up proper CORS origins
6. Use production ASGI server (Gunicorn)

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

---

**Version:** 2.0.0  
**Last Updated:** May 8, 2024  
**Status:** Production Ready ✅
