"""Load and manage prescription image datasets."""

import json
import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PrescriptionDatasetLoader:
    """Load prescription images with annotations."""
    
    def __init__(self, dataset_path: Path):
        self.dataset_path = Path(dataset_path)
        self.images = []
        self.annotations = {}
    
    def load_from_folder(self, image_format: str = 'jpg') -> List[Path]:
        """Load all prescription images from folder."""
        pattern = f'*.{image_format}'
        self.images = list(self.dataset_path.glob(pattern))
        self.images.extend(self.dataset_path.rglob(pattern))
        
        logger.info(f"Found {len(self.images)} prescription images")
        return self.images
    
    def load_annotations_json(self, annotation_file: str = 'annotations.json') -> Dict:
        """Load annotations from JSON file."""
        ann_path = self.dataset_path / annotation_file
        
        if not ann_path.exists():
            logger.warning(f"Annotation file not found: {ann_path}")
            return {}
        
        with open(ann_path, 'r', encoding='utf-8') as f:
            self.annotations = json.load(f)
        
        logger.info(f"Loaded {len(self.annotations)} annotations")
        return self.annotations
    
    def load_annotations_csv(self, annotation_file: str = 'labels.csv') -> Dict:
        """Load annotations from CSV file."""
        ann_path = self.dataset_path / annotation_file
        
        if not ann_path.exists():
            return {}
        
        annotations = {}
        with open(ann_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                img_name = row.get('image_name') or row.get('filename')
                if img_name not in annotations:
                    annotations[img_name] = {
                        'ocr_text': row.get('ocr_text', ''),
                        'medications': []
                    }
                
                annotations[img_name]['medications'].append({
                    'name': row.get('medication_name', ''),
                    'dose': row.get('dose', ''),
                    'frequency': row.get('frequency', '')
                })
        
        self.annotations = annotations
        return annotations
    
    def get_train_test_split(self, test_ratio: float = 0.2) -> Tuple[List[Path], List[Path]]:
        """Split dataset into train and test."""
        import random
        
        all_images = self.images.copy()
        random.shuffle(all_images)
        
        split_idx = int(len(all_images) * (1 - test_ratio))
        train = all_images[:split_idx]
        test = all_images[split_idx:]
        
        return train, test
    
    def verify_dataset(self) -> Dict:
        """Check dataset integrity."""
        report = {
            'total_images': len(self.images),
            'annotated_images': len(self.annotations),
            'missing_annotations': [],
            'corrupt_images': []
        }
        
        for img_path in self.images:
            if img_path.name not in self.annotations:
                report['missing_annotations'].append(img_path.name)
        
        for img_path in self.images:
            try:
                with Image.open(img_path) as img:
                    img.verify()
            except Exception as e:
                report['corrupt_images'].append((img_path.name, str(e)))
        
        return report