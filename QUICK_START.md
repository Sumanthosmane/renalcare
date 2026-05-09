# 🎯 RenalCare AI - Quick Start Guide

## ✅ Status
- ✅ Backend running on `http://localhost:8000`
- ✅ Frontend running on `http://localhost:5175`
- ✅ Database initialized with demo patient
- ✅ Components ready to test

---

## 🚀 Open Your App

**Visit:** http://localhost:5175

You'll see the **RenalCare AI Dashboard** with a sidebar navigation.

---

## 📸 Feature 1: Upload & Analyze Kidney Scans

### How it works:
1. Click **"AI Scan Analysis"** in the sidebar
2. Drag & drop any image file (JPG/PNG) or click to browse
3. System analyzes the image and returns:
   - **Stone Size** (in millimeters)
   - **Location** (Left/Right/Center kidney)
   - **Severity** (Mild/Moderate/Severe)
   - **Confidence** (percentage accuracy)

### What's happening behind the scenes:
- Image sent to backend `/api/analyze-scan` endpoint
- Backend uses OpenCV + custom algorithm to detect stones
- Results stored in SQLite database
- Analysis displayed in real-time

### Try it:
- Use any medical image or test image
- Upload multiple scans to build history
- System learns from each analysis

---

## 💧 Feature 2: Track Water Intake

### How it works:
1. Click **"Hydration Tracker"** in the sidebar
2. Log water intake by:
   - **Quick buttons**: 250ml, 500ml, 750ml, 1000ml
   - **Custom input**: Use +/- buttons for exact amounts
   - **Time**: Automatically set to current time (editable)
   - **Notes**: Optional (e.g., "with meal", "after workout")
3. See real-time progress to daily goal (2500ml)
4. View today's complete history

### What's happening behind the scenes:
- Each intake logged to backend `/api/water-intake` endpoint
- Data stored with timestamp in SQLite database
- Progress bar updates in real-time
- Health status shown (Low/Moderate/High hydration)

### Try it:
- Log 250ml 3 times
- See progress bar reach 750ml (30% of goal)
- Log total 2500ml to hit daily goal
- View full history at bottom

---

## 🔌 Backend API Reference

### Image Upload
```bash
curl -X POST http://localhost:8000/api/analyze-scan \
  -F "file=@scan.jpg" \
  -F "patient_id=patient_demo_001"
```

**Response:**
```json
{
  "stone_size_mm": 6.5,
  "stone_location": "Right Upper",
  "severity": "Moderate",
  "confidence": 0.943
}
```

### Log Water Intake
```bash
curl -X POST http://localhost:8000/api/water-intake \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient_demo_001",
    "amount_ml": 250,
    "time": "14:30",
    "notes": "with lunch"
  }'
```

### Get Daily Summary
```bash
curl http://localhost:8000/api/water-intake/patient_demo_001/daily
```

**Response:**
```json
{
  "patient_id": "patient_demo_001",
  "date": "2024-05-08",
  "total_intake_ml": 1500,
  "goal_ml": 2500,
  "intakes": [
    {
      "id": 1,
      "amount_ml": 250,
      "time": "08:00",
      "notes": "morning"
    }
  ]
}
```

---

## 📊 Interactive API Docs

**Swagger UI:** http://localhost:8000/docs

Click on any endpoint to:
- See full documentation
- Test endpoints live
- View request/response schemas

---

## 📁 Project Structure

```
/renal-care/
├── src/
│   ├── components/
│   │   ├── ImageUploadComponent.jsx    ← Image upload form
│   │   └── WaterIntakeComponent.jsx    ← Water logging form
│   ├── api.js                           ← API helper functions
│   ├── App.jsx                          ← Main app with navigation
│   └── main.jsx                         ← React entry point
├── backend/
│   ├── main.py                          ← FastAPI server (running)
│   ├── database.py                      ← SQLAlchemy models
│   ├── schemas.py                       ← Pydantic validators
│   ├── image_utils.py                   ← Image processing
│   ├── requirements.txt                 ← Python dependencies
│   ├── renal_care.db                    ← SQLite database
│   └── models/                          ← ML models (future)
└── index.html                           ← HTML entry point
```

---

## 🧪 Testing Checklist

### Frontend Components
- [ ] Click "AI Scan Analysis" tab
- [ ] Drag & drop an image
- [ ] See image preview
- [ ] Click "Analyze Scan"
- [ ] See results (stone size, location, severity, confidence)
- [ ] Click "Hydration Tracker" tab
- [ ] Log 250ml water
- [ ] See progress bar update
- [ ] Log 500ml more
- [ ] See history with both entries

### Backend Connectivity
- [ ] Visit http://localhost:8000/docs
- [ ] Click POST /api/analyze-scan
- [ ] Upload test image
- [ ] See 200 response with analysis
- [ ] Click GET /api/water-intake/daily
- [ ] See 200 response with summary

### Database
- [ ] Check backend logs show "Database initialized"
- [ ] See "Diet recommendations seeded"
- [ ] All 40+ endpoints functional

---

## ⚡ Common Tasks

### Run both servers (fastest way)
```bash
# Terminal 1: Backend
cd backend
python3 main.py

# Terminal 2: Frontend (from project root)
npm run dev
```

### Reset database
```bash
cd backend
python3 init_db.py
```

### View database contents
```bash
cd backend
sqlite3 renal_care.db
sqlite> SELECT * FROM patients;
sqlite> SELECT * FROM water_intakes;
```

### View backend API docs
```
http://localhost:8000/docs
```

### View frontend in production mode
```bash
npm run build
npm run preview
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Cannot upload scan" | Ensure backend is running: `python3 main.py` |
| "Failed to fetch" | Check both servers running on correct ports |
| "Import error" | Run `npm install` to ensure dependencies installed |
| "Database error" | Run `python3 init_db.py` to reinitialize |
| Port already in use | Kill process: `lsof -ti:8000 \| xargs kill -9` |

---

## 📱 Features at a Glance

| Feature | Status | Endpoint |
|---------|--------|----------|
| Upload scans | ✅ Working | POST /api/analyze-scan |
| Log water intake | ✅ Working | POST /api/water-intake |
| Get daily summary | ✅ Working | GET /api/water-intake/daily |
| Diet recommendations | ✅ Implemented | GET /api/diet-recommendations |
| Risk prediction | ✅ Implemented | POST /api/predict-risk |
| Health dashboard | ✅ Implemented | GET /api/patients/{id}/health-summary |

---

## 🎓 Next Steps

### To add more features:
1. Create new component in `src/components/`
2. Add API helper in `src/api.js`
3. Add backend endpoint in `backend/main.py`
4. Wire up in `src/App.jsx` navigation

### To train ML models:
1. Update dataset paths in `backend/train_vision_model.py`
2. Update data generation in `backend/train_risk_model.py`
3. Run: `python3 train_vision_model.py`
4. Run: `python3 train_risk_model.py`

### To deploy:
1. See `BACKEND_COMPLETE.md` for production setup
2. Use PostgreSQL instead of SQLite
3. Deploy backend on Heroku/Railway/AWS
4. Deploy frontend on Vercel/Netlify

---

## 📞 Support

**For API issues:**
- Check `http://localhost:8000/docs` for live API documentation
- Review backend logs in terminal
- Check database with sqlite3

**For frontend issues:**
- Check browser console (F12)
- Review network tab for failed requests
- Check `src/api.js` for correct endpoint URLs

**For component issues:**
- Verify imports in component files
- Check backend is responding
- Test endpoint in Swagger UI first

---

## 🎊 You're All Set!

### Quick start (copy-paste):
```bash
# Terminal 1
cd /Users/puneethosmane/sumant/fresh\ pro/renal-care/backend
python3 main.py

# Terminal 2 (from project root)
npm run dev
```

Then visit **http://localhost:5175** and test the features!

**Have fun tracking kidney health! 💧🏥**
