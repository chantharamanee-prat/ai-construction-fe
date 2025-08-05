import csv
from pathlib import Path
from collections import defaultdict
import numpy as np
from typing import Dict, List, Tuple

def analyze_dataset_distribution() -> None:
    """Analyze class and progress distribution across dataset splits.
    
    Outputs results to reports/dataset_distribution.csv
    """
    # Setup paths
    dataset_root = Path('datasets')
    splits = ['train', 'val', 'test']
    report_path = Path('reports/dataset_distribution.csv')
    report_path.parent.mkdir(exist_ok=True)
    
    # Initialize data structures
    class_counts: Dict[str, Dict[str, int]] = {split: defaultdict(int) for split in splits}
    progress_stats: Dict[str, Dict[str, float]] = {split: {} for split in splits}
    
    # Process each split
    for split in splits:
        label_dir = dataset_root / split / 'labels'
        progress_values = []
        
        # Count classes and collect progress values
        for label_file in label_dir.glob('*.txt'):
            with open(label_file) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('# progress:'):  # Progress metadata
                        progress = float(line.split(':')[1].strip())
                        progress_values.append(progress)
                    elif line:  # Class label
                        class_id = line.split()[0]
                        class_counts[split][class_id] += 1
        
        # Calculate progress statistics
        if progress_values:
            progress_stats[split] = {
                'mean': np.mean(progress_values),
                'std': np.std(progress_values),
                'min': np.min(progress_values),
                'max': np.max(progress_values),
                'count': len(progress_values)
            }
    
    # Write results to CSV
    with open(report_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write class distribution
        writer.writerow(['Split', 'Class', 'Count'])
        for split in splits:
            for class_id, count in class_counts[split].items():
                writer.writerow([split, class_id, count])
        
        # Write progress distribution
        writer.writerow([])
        writer.writerow(['Split', 'Mean Progress', 'Std Dev', 'Min', 'Max', 'Count'])
        for split in splits:
            stats = progress_stats[split]
            writer.writerow([
                split,
                stats.get('mean', 0),
                stats.get('std', 0),
                stats.get('min', 0),
                stats.get('max', 0),
                stats.get('count', 0)
            ])

if __name__ == '__main__':
    analyze_dataset_distribution()
