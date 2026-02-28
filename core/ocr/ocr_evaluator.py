"""Evaluate OCR accuracy against your ground truth annotations."""

import json
import editdistance
from pathlib import Path
from typing import Dict, List
import pandas as pd
from collections import defaultdict

from core.ocr.ocr_engine import OcrEngine


class OcrEvaluator:
    """Calculate WER, CER against your annotated dataset."""
    
    def __init__(self, annotations_dir: Path):
        self.annotations_dir = Path(annotations_dir)
        self.results = []
    
    def load_annotation(self, annotation_file: Path) -> Dict:
        """Load your JSON annotation format."""
        with open(annotation_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def evaluate_sample(self, image_path: Path, annotation_path: Path, 
                       lang: str = 'en') -> Dict:
        """Evaluate single prescription against ground truth."""
        # Load ground truth
        annotation = self.load_annotation(annotation_path)
        ground_truth = annotation.get('ocr_text', '')
        
        # Run OCR
        engine = OcrEngine(lang=lang)
        result = engine.extract(image_path)
        
        # Calculate metrics
        cer = self.calculate_cer(ground_truth, result.text)
        wer = self.calculate_wer(ground_truth, result.text)
        
        # Calculate medication accuracy if available
        med_accuracy = None
        if 'medications' in annotation:
            med_accuracy = self._check_medications(result.text, annotation['medications'])
        
        metrics = {
            'image': str(image_path),
            'language': lang,
            'cer': cer,
            'wer': wer,
            'ocr_confidence': result.confidence,
            'ground_truth_length': len(ground_truth),
            'hypothesis_length': len(result.text),
            'medication_accuracy': med_accuracy
        }
        
        self.results.append(metrics)
        return metrics
    
    def calculate_cer(self, reference: str, hypothesis: str) -> float:
        """Character Error Rate."""
        ref = reference.replace(' ', '')
        hyp = hypothesis.replace(' ', '')
        
        if len(ref) == 0:
            return 0.0 if len(hyp) == 0 else 1.0
        
        distance = editdistance.eval(ref, hyp)
        return distance / len(ref)
    
    def calculate_wer(self, reference: str, hypothesis: str) -> float:
        """Word Error Rate."""
        ref_words = reference.split()
        hyp_words = hypothesis.split()
        
        if len(ref_words) == 0:
            return 0.0 if len(hyp_words) == 0 else 1.0
        
        distance = editdistance.eval(ref_words, hyp_words)
        return distance / len(ref_words)
    
    def _check_medications(self, ocr_text: str, ground_truth_meds: List[Dict]) -> float:
        """Check if medications were correctly extracted."""
        ocr_lower = ocr_text.lower()
        found = 0
        
        for med in ground_truth_meds:
            med_name = med.get('name', '').lower()
            if med_name and med_name in ocr_lower:
                found += 1
        
        return found / len(ground_truth_meds) if ground_truth_meds else 0.0
    
    def evaluate_dataset(self, image_dir: Path, annotation_dir: Path,
                        lang: str = 'en') -> pd.DataFrame:
        """Evaluate entire annotated dataset."""
        # Match images to annotations
        for img_path in image_dir.glob('*.jpg'):
            ann_path = annotation_dir / f"{img_path.stem}.json"
            if ann_path.exists():
                try:
                    self.evaluate_sample(img_path, ann_path, lang)
                except Exception as e:
                    print(f"Error evaluating {img_path}: {e}")
        
        return pd.DataFrame(self.results)
    
    def get_summary(self) -> Dict:
        """Get aggregate statistics."""
        if not self.results:
            return {}
        
        df = pd.DataFrame(self.results)
        return {
            'mean_cer': df['cer'].mean(),
            'mean_wer': df['wer'].mean(),
            'mean_confidence': df['ocr_confidence'].mean(),
            'samples_evaluated': len(df),
            'mean_med_accuracy': df['medication_accuracy'].mean() if 'medication_accuracy' in df else None
        }
    
    def export_report(self, output_path: Path):
        """Save detailed report."""
        df = pd.DataFrame(self.results)
        df.to_csv(output_path, index=False)
        print(f"Report saved to {output_path}")
        print(self.get_summary())