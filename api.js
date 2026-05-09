"""
RenalCare AI - Frontend API Integration
Helper functions and utilities for frontend to communicate with backend
"""

const API_BASE_URL = "http://localhost:8000/api";

// ============= Patient Management =============

export const createPatient = async (patientData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/patients`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(patientData),
    });
    return await response.json();
  } catch (error) {
    console.error("Error creating patient:", error);
    throw error;
  }
};

export const getPatient = async (patientId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/patients/${patientId}`);
    return await response.json();
  } catch (error) {
    console.error("Error fetching patient:", error);
    throw error;
  }
};

export const getHealthSummary = async (patientId) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/patients/${patientId}/health-summary`
    );
    return await response.json();
  } catch (error) {
    console.error("Error fetching health summary:", error);
    throw error;
  }
};

// ============= Image Analysis =============

export const uploadScan = async (patientId, stoneType, file) => {
  try {
    const formData = new FormData();
    formData.append("patient_id", patientId);
    formData.append("stone_type", stoneType);
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/analyze-scan`, {
      method: "POST",
      body: formData,
    });
    return await response.json();
  } catch (error) {
    console.error("Error uploading scan:", error);
    throw error;
  }
};

export const getPatientScans = async (patientId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/scans/${patientId}`);
    return await response.json();
  } catch (error) {
    console.error("Error fetching scans:", error);
    throw error;
  }
};

export const getScanDetail = async (scanId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/scans/detail/${scanId}`);
    return await response.json();
  } catch (error) {
    console.error("Error fetching scan detail:", error);
    throw error;
  }
};

// ============= Water Intake =============

export const logWaterIntake = async (intakeData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/water-intake`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(intakeData),
    });
    return await response.json();
  } catch (error) {
    console.error("Error logging water intake:", error);
    throw error;
  }
};

export const getDailyWaterSummary = async (patientId, date = null) => {
  try {
    const url = date
      ? `${API_BASE_URL}/water-intake/${patientId}/daily?date=${date}`
      : `${API_BASE_URL}/water-intake/${patientId}/daily`;
    const response = await fetch(url);
    return await response.json();
  } catch (error) {
    console.error("Error fetching water summary:", error);
    throw error;
  }
};

export const getWaterHistory = async (patientId, days = 7) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/water-intake/${patientId}/history?days=${days}`
    );
    return await response.json();
  } catch (error) {
    console.error("Error fetching water history:", error);
    throw error;
  }
};

// ============= Meals =============

export const logMeal = async (mealData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/meals`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(mealData),
    });
    return await response.json();
  } catch (error) {
    console.error("Error logging meal:", error);
    throw error;
  }
};

export const getDailyMealSummary = async (patientId, date = null) => {
  try {
    const url = date
      ? `${API_BASE_URL}/meals/${patientId}/daily?date=${date}`
      : `${API_BASE_URL}/meals/${patientId}/daily`;
    const response = await fetch(url);
    return await response.json();
  } catch (error) {
    console.error("Error fetching meal summary:", error);
    throw error;
  }
};

export const getMealHistory = async (patientId, days = 7) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/meals/${patientId}/history?days=${days}`
    );
    return await response.json();
  } catch (error) {
    console.error("Error fetching meal history:", error);
    throw error;
  }
};

// ============= Diet Recommendations =============

export const getDietRecommendations = async (stoneType) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/diet-recommendations/${stoneType}`
    );
    return await response.json();
  } catch (error) {
    console.error("Error fetching diet recommendations:", error);
    throw error;
  }
};

export const getAllDietRecommendations = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/diet-recommendations`);
    return await response.json();
  } catch (error) {
    console.error("Error fetching all recommendations:", error);
    throw error;
  }
};

export const updatePatientDiet = async (patientId, stoneType) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/diet-recommendations/${patientId}?stone_type=${stoneType}`,
      { method: "POST" }
    );
    return await response.json();
  } catch (error) {
    console.error("Error updating diet:", error);
    throw error;
  }
};

// ============= Risk Prediction =============

export const predictRisk = async (riskData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/predict-risk`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(riskData),
    });
    return await response.json();
  } catch (error) {
    console.error("Error predicting risk:", error);
    throw error;
  }
};

export const getPatientRiskScore = async (patientId) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/patients/${patientId}/risk-score`
    );
    return await response.json();
  } catch (error) {
    console.error("Error fetching risk score:", error);
    throw error;
  }
};

// ============= Health Check =============

export const checkApiHealth = async () => {
  try {
    const response = await fetch(`${API_BASE_URL.replace("/api", "")}/health`);
    return await response.json();
  } catch (error) {
    console.error("Error checking API health:", error);
    return { status: "unavailable" };
  }
};
