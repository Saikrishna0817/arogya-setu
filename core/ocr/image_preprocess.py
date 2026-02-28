"""Advanced image preprocessing for Tesseract OCR optimization."""

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from typing import Union, Tuple
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """Preprocess medical prescription images for optimal Tesseract OCR."""
    
    def __init__(self, target_dpi: int = 300):
        self.target_dpi = target_dpi
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    
    def preprocess(self, image_path: Union[str, Path]) -> np.ndarray:
        """
        Full preprocessing pipeline optimized for handwritten medical text.
        
        Args:
            image_path: Path to prescription image
            
        Returns:
            Preprocessed image as numpy array (grayscale)
        """
        # Load image
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        logger.info(f"Original image shape: {img.shape}")
        
        # Step 1: Resize to target DPI if needed
        img = self._optimize_resolution(img)
        
        # Step 2: Denoise (preserve edges, remove paper texture)
        img = self._denoise(img)
        
        # Step 3: Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Step 4: Contrast enhancement (CLAHE)
        enhanced = self.clahe.apply(gray)
        
        # Step 5: Adaptive thresholding (handle uneven lighting)
        binary = self._adaptive_threshold(enhanced)
        
        # Step 6: Deskew if needed
        binary = self._deskew(binary)
        
        # Step 7: Remove lines (table borders if present)
        binary = self._remove_lines(binary)
        
        logger.info("Preprocessing complete")
        return binary
    
    def _optimize_resolution(self, img: np.ndarray) -> np.ndarray:
        """Ensure minimum resolution for Tesseract (300 DPI equivalent)."""
        height, width = img.shape[:2]
        
        # Calculate current DPI assuming standard photo
        current_dpi = min(height, width) / 3.5  # Rough estimate
        
        if current_dpi < 250:
            scale_factor = 300 / current_dpi
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            logger.info(f"Resized to {new_width}x{new_height} for better OCR")
        
        return img
    
    def _denoise(self, img: np.ndarray) -> np.ndarray:
        """Non-local means denoising - preserves text edges."""
        return cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
    
    def _adaptive_threshold(self, gray: np.ndarray) -> np.ndarray:
        """Adaptive Gaussian thresholding for uneven lighting."""
        # Invert if needed (white text on dark background)
        mean_brightness = np.mean(gray)
        if mean_brightness < 127:
            gray = cv2.bitwise_not(gray)
        
        # Adaptive threshold
        binary = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )
        return binary
    
    def _deskew(self, img: np.ndarray, max_skew: float = 10.0) -> np.ndarray:
        """Correct image rotation using projection profile."""
        coords = np.column_stack(np.where(img > 0))
        if len(coords) < 100:  # Too few pixels to determine skew
            return img
        
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        if abs(angle) < 0.5 or abs(angle) > max_skew:
            return img  # No significant skew or too extreme
        
        # Rotate
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(img, M, (w, h),
                                  flags=cv2.INTER_CUBIC,
                                  borderMode=cv2.BORDER_REPLICATE)
        logger.info(f"Deskewed by {angle:.2f} degrees")
        return rotated
    
    def _remove_lines(self, img: np.ndarray) -> np.ndarray:
        """Remove horizontal/vertical table lines while preserving text."""
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        
        # Detect lines
        horizontal_lines = cv2.morphologyEx(img, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
        vertical_lines = cv2.morphologyEx(img, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
        
        # Combine and remove
        lines = cv2.addWeighted(horizontal_lines, 0.5, vertical_lines, 0.5, 0.0)
        no_lines = cv2.subtract(img, lines)
        
        return no_lines
    
    def enhance_for_display(self, img: np.ndarray) -> Image.Image:
        """Convert preprocessed image back to PIL for Streamlit display."""
        if len(img.shape) == 2:  # Grayscale
            return Image.fromarray(img, mode='L')
        return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    
    def save_preprocessed(self, img: np.ndarray, output_path: Union[str, Path]):
        """Save preprocessed image for debugging."""
        cv2.imwrite(str(output_path), img)
        logger.info(f"Saved preprocessed image to {output_path}")


class PILPreprocessor:
    """Alternative preprocessor using PIL (simpler, faster)."""
    
    def __init__(self):
        pass
    
    def preprocess(self, image_path: Union[str, Path]) -> Image.Image:
        """Quick preprocessing using PIL."""
        img = Image.open(image_path)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)
        
        # Convert to grayscale
        img = img.convert('L')
        
        # Apply mild denoising
        img = img.filter(ImageFilter.MedianFilter(size=3))
        
        return img