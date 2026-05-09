"""
RenalCare AI - Image Processing Utilities
Image analysis and stone detection functions
"""

import cv2
import numpy as np
from PIL import Image
import io
from typing import Tuple, Dict
import os


def load_image(image_path: str) -> np.ndarray:
    """Load image from file path"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    return image


def preprocess_image(image: np.ndarray) -> np.ndarray:
    """Preprocess image for analysis"""
    # Normalize image
    image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    image = clahe.apply(image)
    
    return image


def detect_kidney_stones(image: np.ndarray) -> Dict:
    """
    Detect kidney stones in medical image
    
    Returns:
        Dict with: stone_size_mm, location, severity, confidence, contours
    """
    # Preprocess
    processed = preprocess_image(image)
    
    # Apply threshold
    _, binary = cv2.threshold(processed, 127, 255, cv2.THRESH_BINARY)
    
    # Morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) == 0:
        return {
            "stone_size_mm": 0,
            "location": "No stones detected",
            "severity": "none",
            "confidence": 0.0,
            "num_stones": 0
        }
    
    # Analyze contours
    stone_areas = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 100:  # Filter small noise
            stone_areas.append(area)
    
    if not stone_areas:
        return {
            "stone_size_mm": 0,
            "location": "No significant stones detected",
            "severity": "none",
            "confidence": 0.0,
            "num_stones": 0
        }
    
    # Calculate stone size (simplified: assume ~0.1mm per pixel)
    largest_stone_area = max(stone_areas)
    stone_size_mm = np.sqrt(largest_stone_area) * 0.08  # Rough conversion to mm
    
    # Determine location (based on position in image)
    height, width = image.shape
    for contour in contours:
        area = cv2.contourArea(contour)
        if area == largest_stone_area:
            M = cv2.moments(contour)
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            
            # Determine location based on position
            if cx < width / 3:
                location = "Left"
            elif cx > 2 * width / 3:
                location = "Right"
            else:
                location = "Center"
            
            if cy < height / 3:
                location += " Upper"
            elif cy > 2 * height / 3:
                location += " Lower"
            break
    
    # Determine severity based on size
    if stone_size_mm < 5:
        severity = "mild"
        confidence = 0.75
    elif stone_size_mm < 10:
        severity = "moderate"
        confidence = 0.85
    else:
        severity = "severe"
        confidence = 0.90
    
    return {
        "stone_size_mm": round(stone_size_mm, 2),
        "location": location,
        "severity": severity,
        "confidence": min(confidence, 0.98),
        "num_stones": len(stone_areas)
    }


def save_upload_file(upload_file_bytes: bytes, filename: str) -> str:
    """Save uploaded file to disk"""
    upload_dir = "./uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, filename)
    
    with open(file_path, 'wb') as f:
        f.write(upload_file_bytes)
    
    return file_path


def analyze_image_file(file_path: str) -> Dict:
    """
    Analyze uploaded medical image
    
    Returns comprehensive analysis with stone detection results
    """
    try:
        image = load_image(file_path)
        stone_analysis = detect_kidney_stones(image)
        
        return {
            "success": True,
            "analysis": stone_analysis
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
