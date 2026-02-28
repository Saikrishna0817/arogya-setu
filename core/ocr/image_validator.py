"""Validate that uploaded image is actually a prescription."""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageValidator:
    """Validate prescription images before processing."""
    
    # Minimum quality thresholds
    MIN_RESOLUTION = (800, 600)  # width, height
    MIN_SHARPNESS = 100.0
    MIN_CONTRAST = 20.0
    MAX_BLUR = 100.0  # Laplacian variance threshold
    
    # Prescription indicators (text patterns that suggest medical doc)
    MEDICAL_INDICATORS = [
        'dr', 'doctor', 'patient', 'prescription', 'rx', 'medication',
        'tablet', 'mg', 'ml', 'dose', 'diagnosis', 'symptoms',
        'od', 'bd', 'tds', 'sos', 'cap', 'tab'
    ]
    
    def __init__(self):
        pass
    
    def validate(self, image_path: Path) -> Dict:
        """
        Comprehensive image validation.
        
        Returns:
            Dict with validation results and recommendations
        """
        img = cv2.imread(str(image_path))
        
        if img is None:
            return {
                'valid': False,
                'error': 'Could not load image',
                'recommendations': ['Check file format', 'Try re-uploading']
            }
        
        checks = {
            'resolution': self._check_resolution(img),
            'sharpness': self._check_sharpness(img),
            'contrast': self._check_contrast(img),
            'blur': self._check_blur(img),
            'orientation': self._check_orientation(img),
            'content': {'passed': True, 'score': 1.0}  # Will be checked post-OCR
        }
        
        # Overall validation
        critical_failures = [
            checks['resolution']['passed'],
            checks['sharpness']['passed'],
            checks['blur']['passed']
        ]
        
        valid = all(critical_failures)
        
        recommendations = []
        if not checks['resolution']['passed']:
            recommendations.append("Image resolution too low - use higher quality camera")
        if not checks['sharpness']['passed']:
            recommendations.append("Image appears blurry - ensure good lighting and steady hand")
        if not checks['contrast']['passed']:
            recommendations.append("Low contrast - ensure prescription is clearly visible")
        if not checks['blur']['passed']:
            recommendations.append("Image is too blurry - retake photo")
        
        return {
            'valid': valid,
            'checks': checks,
            'recommendations': recommendations,
            'can_proceed': checks['resolution']['passed'] and checks['blur']['passed'],
            'quality_score': self._calculate_quality_score(checks)
        }
    
    def _check_resolution(self, img: np.ndarray) -> Dict:
        """Check image resolution."""
        height, width = img.shape[:2]
        passed = width >= self.MIN_RESOLUTION[0] and height >= self.MIN_RESOLUTION[1]
        
        return {
            'passed': passed,
            'width': width,
            'height': height,
            'score': min(width / self.MIN_RESOLUTION[0], height / self.MIN_RESOLUTION[1], 2.0) / 2.0
        }
    
    def _check_sharpness(self, img: np.ndarray) -> Dict:
        """Check image sharpness using Laplacian variance."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        passed = laplacian_var >= self.MIN_SHARPNESS
        
        return {
            'passed': passed,
            'variance': laplacian_var,
            'score': min(laplacian_var / self.MIN_SHARPNESS, 2.0) / 2.0
        }
    
    def _check_contrast(self, img: np.ndarray) -> Dict:
        """Check image contrast."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        contrast = gray.std()
        
        passed = contrast >= self.MIN_CONTRAST
        
        return {
            'passed': passed,
            'std_dev': contrast,
            'score': min(contrast / self.MIN_CONTRAST, 2.0) / 2.0
        }
    
    def _check_blur(self, img: np.ndarray) -> Dict:
        """Check if image is too blurry."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Lower variance = more blur
        passed = laplacian_var <= self.MAX_BLUR and laplacian_var >= 50
        
        return {
            'passed': passed,
            'blur_score': laplacian_var,
            'score': 1.0 - (laplacian_var / self.MAX_BLUR) if laplacian_var < self.MAX_BLUR else 0.0
        }
    
    def _check_orientation(self, img: np.ndarray) -> Dict:
        """Check if image needs rotation."""
        # Simple check: text should be horizontal
        # Full implementation would use text orientation detection
        return {
            'passed': True,
            'rotation_needed': False,
            'score': 1.0
        }
    
    def _calculate_quality_score(self, checks: Dict) -> float:
        """Calculate overall quality score (0-1)."""
        scores = [
            checks['resolution']['score'],
            checks['sharpness']['score'],
            checks['contrast']['score'],
            checks['blur'].get('score', 0.5)
        ]
        return sum(scores) / len(scores)
    
    def quick_check(self, image_path: Path) -> bool:
        """Fast validation for UI."""
        result = self.validate(image_path)
        return result['can_proceed']
    
    def is_prescription(self, ocr_text: str) -> Tuple[bool, float]:
        """
        Check if OCR text looks like a prescription.
        
        Returns:
            (is_prescription, confidence)
        """
        text_lower = ocr_text.lower()
        
        # Count medical indicators
        found_indicators = sum(1 for indicator in self.MEDICAL_INDICATORS 
                              if indicator in text_lower)
        
        # Calculate confidence
        confidence = min(found_indicators / 3, 1.0)  # Need at least 3 indicators
        
        is_rx = confidence > 0.3 and len(ocr_text) > 50
        
        return is_rx, confidence