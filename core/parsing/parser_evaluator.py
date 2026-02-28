"""Evaluate parser accuracy against annotations."""

import json
from pathlib import Path
from typing import Dict, List
import pandas as pd
from dataclasses import asdict

from core.parsing.prescription_parser import PrescriptionParser


class ParserEvaluator:
    """Calculate parsing accuracy metrics."""
    
    def __init__(self):
        self.results = []
    
    def evaluate_sample(self, annotation_path: Path) -> Dict:
        """Evaluate single annotated prescription."""
        with open(annotation_path, 'r', encoding='utf-8') as f:
            annotation = json.load(f)
        
        ground_truth = annotation.get('medications', [])
        ocr_text = annotation.get('ocr_text', '')
        
        # Parse
        parser = PrescriptionParser()
        parsed = parser.parse(ocr_text)
        
        # Compare medications
        tp = 0  # True positives
        fp = 0  # False positives
        fn = 0  # False negatives
        
        parsed_meds = {m.name.lower(): m for m in parsed.medications}
        gt_meds = {m['name'].lower(): m for m in ground_truth}
        
        for name in parsed_meds:
            if name in gt_meds:
                tp += 1
                # Check fields
                parsed_med = parsed_meds[name]
                gt_med = gt_meds[name]
                
                field_accuracy = self._compare_fields(parsed_med, gt_med)
            else:
                fp += 1
        
        fn = len(gt_meds) - tp
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        result = {
            'file': annotation_path.name,
            'true_positives': tp,
            'false_positives': fp,
            'false_negatives': fn,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'medication_count_gt': len(ground_truth),
            'medication_count_parsed': len(parsed.medications)
        }
        
        self.results.append(result)
        return result
    
    def _compare_fields(self, parsed, ground_truth: Dict) -> Dict:
        """Compare individual fields."""
        accuracy = {}
        
        # Strength
        if 'strength_mg' in ground_truth:
            gt_val = ground_truth['strength_mg']
            parsed_val = parsed.strength_value
            accuracy['strength'] = (gt_val == parsed_val) if parsed_val else False
        
        # Frequency
        if 'frequency' in ground_truth:
            accuracy['frequency'] = (ground_truth['frequency'].upper() == 
                                   (parsed.frequency or '').upper())
        
        # Duration
        if 'duration_days' in ground_truth:
            gt_days = ground_truth['duration_days']
            parsed_days = parsed.duration_days
            accuracy['duration'] = (gt_days == parsed_days) if parsed_days else False
        
        return accuracy
    
    def evaluate_dataset(self, annotation_dir: Path) -> pd.DataFrame:
        """Evaluate all annotations in directory."""
        for ann_file in annotation_dir.glob('*.json'):
            try:
                self.evaluate_sample(ann_file)
            except Exception as e:
                print(f"Error evaluating {ann_file}: {e}")
        
        return pd.DataFrame(self.results)
    
    def get_summary(self) -> Dict:
        """Aggregate metrics."""
        if not self.results:
            return {}
        
        df = pd.DataFrame(self.results)
        return {
            'mean_precision': df['precision'].mean(),
            'mean_recall': df['recall'].mean(),
            'mean_f1': df['f1_score'].mean(),
            'total_samples': len(df)
        }