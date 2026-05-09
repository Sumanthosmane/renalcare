"""
RenalCare AI - API Integration Guide for Frontend

This file provides examples of how to integrate the backend API with your React frontend.
Copy the functions to your project and use them in your components.
"""

# ============ Installation ============
# 1. Install dependencies:
# pip install fastapi uvicorn sqlalchemy pydantic python-multipart
#
# 2. Start the backend:
# python main.py
#
# 3. API will be available at: http://localhost:8000
# 4. API documentation: http://localhost:8000/docs (Swagger)


# ============ Example: React Hook for Patient Setup ============

import React, { useState } from 'react';
import { createPatient, getHealthSummary } from '../api';

export function PatientSetup() {
  const [loading, setLoading] = useState(false);

  const handleCreatePatient = async () => {
    setLoading(true);
    try {
      const patient = await createPatient({
        id: 'patient_' + Date.now(),
        name: 'John Doe',
        age: 45,
        gender: 'Male',
        bmi: 27.5,
        family_history: true
      });
      console.log('Patient created:', patient);
    } catch (error) {
      console.error('Failed to create patient:', error);
    }
    setLoading(false);
  };

  return (
    <button onClick={handleCreatePatient} disabled={loading}>
      {loading ? 'Creating...' : 'Create Patient'}
    </button>
  );
}


# ============ Example: Image Upload Component ============

import React, { useState } from 'react';
import { uploadScan } from '../api';

export function ScanUploader({ patientId }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    try {
      const analysis = await uploadScan(patientId, 'calcium_oxalate', file);
      setResult({
        stoneSize: analysis.stone_size_mm,
        location: analysis.stone_location,
        severity: analysis.severity,
        confidence: (analysis.confidence * 100).toFixed(1)
      });
    } catch (error) {
      console.error('Upload failed:', error);
    }
    setLoading(false);
  };

  return (
    <div>
      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
        accept="image/*"
      />
      <button onClick={handleUpload} disabled={loading || !file}>
        {loading ? 'Analyzing...' : 'Analyze Scan'}
      </button>

      {result && (
        <div>
          <p>Stone Size: {result.stoneSize}mm</p>
          <p>Location: {result.location}</p>
          <p>Severity: {result.severity}</p>
          <p>Confidence: {result.confidence}%</p>
        </div>
      )}
    </div>
  );
}


# ============ Example: Water Intake Logger ============

import React, { useState, useEffect } from 'react';
import { logWaterIntake, getDailyWaterSummary } from '../api';

export function WaterTracker({ patientId }) {
  const [amount, setAmount] = useState('');
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadSummary = async () => {
    try {
      const data = await getDailyWaterSummary(patientId);
      setSummary(data);
    } catch (error) {
      console.error('Failed to load summary:', error);
    }
  };

  useEffect(() => {
    loadSummary();
  }, [patientId]);

  const handleLog = async () => {
    if (!amount) return;

    setLoading(true);
    try {
      await logWaterIntake({
        patient_id: patientId,
        amount_ml: parseFloat(amount),
        time: new Date().toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit'
        })
      });
      setAmount('');
      loadSummary();
    } catch (error) {
      console.error('Failed to log water:', error);
    }
    setLoading(false);
  };

  return (
    <div>
      <input
        type="number"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        placeholder="Amount (ml)"
      />
      <button onClick={handleLog} disabled={loading || !amount}>
        {loading ? 'Logging...' : 'Log Water'}
      </button>

      {summary && (
        <div>
          <p>Today: {summary.total_intake_ml}ml / {summary.goal_ml}ml</p>
          <progress
            value={summary.total_intake_ml}
            max={summary.goal_ml}
          />
          <p>Progress: {summary.percentage.toFixed(0)}%</p>
        </div>
      )}
    </div>
  );
}


# ============ Example: Meal Logger ============

import React, { useState } from 'react';
import { logMeal, getDailyMealSummary } from '../api';

export function MealLogger({ patientId }) {
  const [mealType, setMealType] = useState('breakfast');
  const [foods, setFoods] = useState('');
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState(null);

  const handleAddMeal = async () => {
    if (!foods) return;

    setLoading(true);
    try {
      const foodItems = foods.split(',').map((food) => ({
        name: food.trim(),
        quantity: '1 serving',
        oxalate_level: 'medium'
      }));

      await logMeal({
        patient_id: patientId,
        meal_type: mealType,
        food_items: foodItems
      });

      setFoods('');
      const data = await getDailyMealSummary(patientId);
      setSummary(data);
    } catch (error) {
      console.error('Failed to log meal:', error);
    }
    setLoading(false);
  };

  return (
    <div>
      <select value={mealType} onChange={(e) => setMealType(e.target.value)}>
        <option>breakfast</option>
        <option>lunch</option>
        <option>dinner</option>
        <option>snack</option>
      </select>

      <textarea
        value={foods}
        onChange={(e) => setFoods(e.target.value)}
        placeholder="Foods (comma-separated)"
      />

      <button onClick={handleAddMeal} disabled={loading || !foods}>
        {loading ? 'Adding...' : 'Add Meal'}
      </button>

      {summary && (
        <div>
          <p>Total Sodium: {summary.total_sodium_mg}mg</p>
          {summary.high_oxalate_items.length > 0 && (
            <p>⚠️ High Oxalate: {summary.high_oxalate_items.join(', ')}</p>
          )}
        </div>
      )}
    </div>
  );
}


# ============ Example: Risk Prediction ============

import React, { useState, useEffect } from 'react';
import { predictRisk, getPatientRiskScore } from '../api';

export function RiskAssessment({ patientId, patient }) {
  const [risk, setRisk] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadRisk = async () => {
    setLoading(true);
    try {
      const result = await predictRisk({
        patient_id: patientId,
        age: patient.age,
        gender: patient.gender,
        family_history: patient.family_history,
        previous_stones: 0,
        treatment_compliance: 85
      });
      setRisk(result);
    } catch (error) {
      console.error('Failed to predict risk:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadRisk();
  }, [patientId]);

  if (loading) return <div>Loading risk assessment...</div>;

  return (
    <div>
      <h3>Recurrence Risk</h3>
      {risk && (
        <div>
          <p>Risk Score: {(risk.risk_score * 100).toFixed(1)}%</p>
          <p>Risk Level: {risk.risk_level}</p>
          <h4>Recommendations:</h4>
          <ul>
            {risk.recommendations.map((rec, i) => (
              <li key={i}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}


# ============ Full Page Example ============

import React, { useState } from 'react';
import PatientSetup from './PatientSetup';
import ScanUploader from './ScanUploader';
import WaterTracker from './WaterTracker';
import MealLogger from './MealLogger';
import RiskAssessment from './RiskAssessment';

export default function RenalCareDashboard() {
  const [patientId, setPatientId] = useState(null);
  const [patient, setPatient] = useState(null);

  const handlePatientCreated = (p) => {
    setPatient(p);
    setPatientId(p.id);
  };

  if (!patientId) {
    return <PatientSetup onCreated={handlePatientCreated} />;
  }

  return (
    <div className="dashboard">
      <h1>RenalCare AI - Dashboard</h1>
      <p>Patient: {patient?.name}</p>

      <section>
        <h2>📋 Scan Analysis</h2>
        <ScanUploader patientId={patientId} />
      </section>

      <section>
        <h2>💧 Water Intake</h2>
        <WaterTracker patientId={patientId} />
      </section>

      <section>
        <h2>🍽️ Meal Logger</h2>
        <MealLogger patientId={patientId} />
      </section>

      <section>
        <h2>⚠️ Risk Assessment</h2>
        <RiskAssessment patientId={patientId} patient={patient} />
      </section>
    </div>
  );
}
