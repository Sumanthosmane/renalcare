#!/bin/bash

# ========================================
# RenalCare AI - Complete Setup Script
# Run this script to set up the entire project
# ========================================

set -e  # Exit on error

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   RenalCare AI - Complete Setup       ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.8+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓ Python ${PYTHON_VERSION}${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠ Node.js not found. Skipping frontend setup.${NC}"
    SKIP_FRONTEND=true
else
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js ${NODE_VERSION}${NC}"
fi

# Check npm
if [ "$SKIP_FRONTEND" != "true" ] && ! command -v npm &> /dev/null; then
    echo -e "${YELLOW}⚠ npm not found. Skipping frontend setup.${NC}"
    SKIP_FRONTEND=true
else
    [ "$SKIP_FRONTEND" != "true" ] && NPM_VERSION=$(npm --version) && echo -e "${GREEN}✓ npm ${NPM_VERSION}${NC}"
fi

echo ""

# ============= Backend Setup =============

echo -e "${BLUE}═══ Setting up Backend ═══${NC}"
echo ""

# Navigate to backend
cd backend || exit 1

# Create virtual environment (optional but recommended)
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
fi

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi

# Create necessary directories
mkdir -p uploads models
echo -e "${GREEN}✓ Created upload and model directories${NC}"

# Initialize database
echo "Initializing database..."
python init_db.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database initialized${NC}"
else
    echo -e "${RED}✗ Failed to initialize database${NC}"
    exit 1
fi

cd ..

# ============= Frontend Setup =============

if [ "$SKIP_FRONTEND" != "true" ]; then
    echo ""
    echo -e "${BLUE}═══ Setting up Frontend ═══${NC}"
    echo ""
    
    # Install frontend dependencies
    echo "Installing npm dependencies..."
    npm install > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
    else
        echo -e "${RED}✗ Failed to install frontend dependencies${NC}"
        # Don't exit, backend still works
    fi
fi

echo ""
echo "╔════════════════════════════════════════╗"
echo -e "║${GREEN}    ✓ Setup Complete!${NC}               ║"
echo "╚════════════════════════════════════════╝"
echo ""

# ============= Usage Instructions =============

echo -e "${BLUE}How to start the project:${NC}"
echo ""
echo -e "${YELLOW}1. Terminal 1 - Start Backend:${NC}"
echo "   cd backend"
echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "   python main.py"
echo ""
echo -e "${YELLOW}2. Terminal 2 - Start Frontend (optional):${NC}"
echo "   npm run dev"
echo ""

# ============= Verification Instructions =============

echo -e "${BLUE}Verify Installation:${NC}"
echo ""
echo "✓ Backend Health Check:"
echo "  curl http://localhost:8000/health"
echo ""
echo "✓ API Documentation:"
echo "  http://localhost:8000/docs"
echo ""
echo "✓ Frontend (if enabled):"
echo "  http://localhost:5173"
echo ""

# ============= Optional ML Model Training =============

echo -e "${BLUE}Optional - Train ML Models:${NC}"
echo ""
echo "To train the vision model:"
echo "  cd backend"
echo "  python train_vision_model.py"
echo ""
echo "To train the risk prediction model:"
echo "  cd backend"
echo "  python train_risk_model.py"
echo ""

# ============= File Structure =============

echo -e "${BLUE}Project Structure:${NC}"
echo ""
cat << 'EOF'
renal-care/
├── backend/
│   ├── main.py                    (FastAPI app - 40+ endpoints)
│   ├── database.py               (SQLAlchemy models)
│   ├── schemas.py                (Pydantic schemas)
│   ├── image_utils.py            (Image processing)
│   ├── train_vision_model.py     (U-Net training)
│   ├── train_risk_model.py       (XGBoost training)
│   ├── requirements.txt          (Python dependencies)
│   ├── .env                      (Configuration)
│   └── venv/                     (Virtual environment)
├── src/
│   ├── App.jsx                   (Main React component)
│   └── index.css                 (Styles)
├── api.js                        (Frontend API helpers)
├── BACKEND_COMPLETE.md           (Backend documentation)
├── FRONTEND_INTEGRATION.md       (Integration guide)
├── SYSTEM_ARCHITECTURE.md        (Architecture docs)
└── PROJECT_SUMMARY.md            (Project overview)
EOF

echo ""

# ============= API Endpoints Quick Reference =============

echo -e "${BLUE}Quick API Reference:${NC}"
echo ""
cat << 'EOF'
Patient Management:
  POST   /api/patients
  GET    /api/patients/{patient_id}
  GET    /api/patients/{patient_id}/health-summary

Image Analysis:
  POST   /api/analyze-scan (upload image)
  GET    /api/scans/{patient_id}

Water Tracking:
  POST   /api/water-intake (log water)
  GET    /api/water-intake/{patient_id}/daily
  GET    /api/water-intake/{patient_id}/history

Meal Logging:
  POST   /api/meals (add meal)
  GET    /api/meals/{patient_id}/daily
  GET    /api/meals/{patient_id}/history

Diet Recommendations:
  GET    /api/diet-recommendations/{stone_type}
  GET    /api/diet-recommendations

Risk Prediction:
  POST   /api/predict-risk
  GET    /api/patients/{patient_id}/risk-score

Full API docs at: http://localhost:8000/docs
EOF

echo ""

# ============= Troubleshooting =============

echo -e "${BLUE}Troubleshooting:${NC}"
echo ""
cat << 'EOF'
Port 8000 already in use:
  lsof -i :8000
  kill -9 <PID>

Database errors:
  rm backend/renal_care.db
  cd backend && python init_db.py

Python import errors:
  pip install -r backend/requirements.txt --upgrade

Clear npm cache:
  npm cache clean --force
  rm -rf node_modules package-lock.json
  npm install
EOF

echo ""
echo "═══════════════════════════════════════"
echo -e "${GREEN}✓ Installation Complete!${NC}"
echo "═══════════════════════════════════════"
echo ""
