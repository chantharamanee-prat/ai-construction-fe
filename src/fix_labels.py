#!/usr/bin/env python3
"""
Label Validation and Cleaning Script

Fixes malformed YOLO label files that cause validation errors while preserving
progress metadata comments needed for regression evaluation.
"""

import argparse
import logging
import shutil
from pathlib import Path
from typing import List, Tuple, Dict, Optional


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def is_progress_comment(line: str) -> bool:
    """Check if line is a progress metadata comment."""
    return line.strip().startswith("# progress:")


def validate_bbox_line(line: str, num_classes: int = 5) -> Tuple[bool, str]:
    """
    Validate a YOLO bounding box line.
    
    Args:
        line: Line to validate
        num_classes: Number of valid classes (0 to num_classes-1)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    parts = line.strip().split()
    
    # Must have exactly 5 values: class_id x_center y_center width height
    if len(parts) != 5:
        return False, f"Wrong number of values: {len(parts)} (expected 5)"
    
    try:
        # Parse values
        class_id = int(float(parts[0]))  # Allow float that converts to int
        x_center = float(parts[1])
        y_center = float(parts[2])
        width = float(parts[3])
        height = float(parts[4])
        
        # Validate class_id range
        if class_id < 0 or class_id >= num_classes:
            return False, f"Invalid class_id: {class_id} (valid range: 0-{num_classes-1})"
        
        # Validate coordinate ranges (should be normalized 0-1)
        coords = [x_center, y_center, width, height]
        for i, coord in enumerate(coords):
            if coord < 0 or coord > 1:
                coord_names = ["x_center", "y_center", "width", "height"]
                return False, f"Invalid {coord_names[i]}: {coord} (should be 0-1)"
        
        return True, ""
        
    except ValueError as e:
        return False, f"Cannot convert to numeric: {e}"


def clean_label_file(
    file_path: Path, 
    num_classes: int = 5, 
    dry_run: bool = False
) -> Dict[str, int]:
    """
    Clean a single label file.
    
    Args:
        file_path: Path to label file
        num_classes: Number of valid classes
        dry_run: If True, don't modify files
    
    Returns:
        Dictionary with cleaning statistics
    """
    stats = {
        "total_lines": 0,
        "valid_bbox_lines": 0,
        "progress_comments": 0,
        "malformed_lines": 0,
        "removed_lines": 0,
        "emptied_files": 0
    }
    
    if not file_path.exists():
        return stats
    
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        logging.error(f"Failed to read {file_path}: {e}")
        return stats
    
    stats["total_lines"] = len(lines)
    cleaned_lines = []
    removed_lines = []
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Preserve progress comments
        if is_progress_comment(line):
            cleaned_lines.append(line + '\n')
            stats["progress_comments"] += 1
            continue
        
        # Skip other comments
        if line.startswith('#'):
            continue
        
        # Validate bounding box lines
        is_valid, error_msg = validate_bbox_line(line, num_classes)
        
        if is_valid:
            cleaned_lines.append(line + '\n')
            stats["valid_bbox_lines"] += 1
        else:
            stats["malformed_lines"] += 1
            stats["removed_lines"] += 1
            removed_lines.append(f"Line {line_num}: {line} -> {error_msg}")
            logging.warning(f"{file_path.name} line {line_num}: {error_msg}")
    
    # Check if file needs to be emptied (has progress comments but no bounding boxes)
    if stats["valid_bbox_lines"] == 0 and stats["progress_comments"] > 0:
        stats["emptied_files"] = 1
        if dry_run:
            logging.info(f"Would empty {file_path.name} (has progress comment but no bounding boxes)")
        else:
            try:
                with open(file_path, 'w') as f:
                    f.write("")  # Empty file
                logging.info(f"Created empty label file for {file_path.name} (no bounding boxes)")
            except Exception as e:
                logging.error(f"Failed to write cleaned {file_path}: {e}")
    
    # Write cleaned file if not dry run and malformed lines were removed
    elif not dry_run and stats["removed_lines"] > 0:
        try:
            with open(file_path, 'w') as f:
                f.writelines(cleaned_lines)
            logging.info(f"Cleaned {file_path.name}: removed {stats['removed_lines']} malformed lines")
        except Exception as e:
            logging.error(f"Failed to write cleaned {file_path}: {e}")
    
    return stats


def backup_directory(source_dir: Path, backup_dir: Path) -> bool:
    """Create backup of label directory."""
    try:
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        shutil.copytree(source_dir, backup_dir)
        logging.info(f"Created backup: {backup_dir}")
        return True
    except Exception as e:
        logging.error(f"Failed to create backup: {e}")
        return False


def process_dataset_split(
    split_name: str, 
    datasets_dir: Path, 
    num_classes: int = 5, 
    dry_run: bool = False,
    create_backup: bool = True
) -> Dict[str, int]:
    """Process all label files in a dataset split."""
    split_dir = datasets_dir / split_name
    labels_dir = split_dir / "labels"
    
    if not labels_dir.exists():
        logging.warning(f"Labels directory not found: {labels_dir}")
        return {}
    
    # Create backup if requested
    if create_backup and not dry_run:
        backup_dir = split_dir / "labels_backup"
        if not backup_directory(labels_dir, backup_dir):
            logging.error(f"Backup failed for {split_name}, skipping...")
            return {}
    
    # Process all label files
    total_stats = {
        "files_processed": 0,
        "total_lines": 0,
        "valid_bbox_lines": 0,
        "progress_comments": 0,
        "malformed_lines": 0,
        "removed_lines": 0,
        "emptied_files": 0
    }
    
    label_files = list(labels_dir.glob("*.txt"))
    logging.info(f"Processing {len(label_files)} label files in {split_name}")
    
    for label_file in label_files:
        file_stats = clean_label_file(label_file, num_classes, dry_run)
        
        # Aggregate statistics
        total_stats["files_processed"] += 1
        for key in ["total_lines", "valid_bbox_lines", "progress_comments", "malformed_lines", "removed_lines", "emptied_files"]:
            total_stats[key] += file_stats[key]
    
    return total_stats


def generate_report(all_stats: Dict[str, Dict], report_path: Path, dry_run: bool) -> None:
    """Generate validation report."""
    try:
        with open(report_path, 'w') as f:
            f.write("YOLO Label Validation and Cleaning Report\n")
            f.write("=" * 50 + "\n\n")
            
            if dry_run:
                f.write("DRY RUN MODE - No files were modified\n\n")
            
            total_files = sum(stats.get("files_processed", 0) for stats in all_stats.values())
            total_removed = sum(stats.get("removed_lines", 0) for stats in all_stats.values())
            
            f.write(f"Summary:\n")
            f.write(f"- Total files processed: {total_files}\n")
            f.write(f"- Total malformed lines removed: {total_removed}\n\n")
            
            for split_name, stats in all_stats.items():
                if not stats:
                    continue
                    
                f.write(f"{split_name.upper()} Split:\n")
                f.write(f"- Files processed: {stats['files_processed']}\n")
                f.write(f"- Total lines: {stats['total_lines']}\n")
                f.write(f"- Valid bbox lines: {stats['valid_bbox_lines']}\n")
                f.write(f"- Progress comments: {stats['progress_comments']}\n")
                f.write(f"- Malformed lines: {stats['malformed_lines']}\n")
                f.write(f"- Lines removed: {stats['removed_lines']}\n")
                
                if not dry_run and stats['removed_lines'] > 0:
                    backup_dir = Path("datasets") / split_name / "labels_backup"
                    f.write(f"- Backup created: {backup_dir}\n")
                
                f.write("\n")
        
        logging.info(f"Report saved to: {report_path}")
        
    except Exception as e:
        logging.error(f"Failed to generate report: {e}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Fix malformed YOLO label files")
    parser.add_argument("--datasets-dir", type=str, default="datasets", 
                       help="Path to datasets directory")
    parser.add_argument("--splits", nargs="+", default=["train", "val", "test"],
                       help="Dataset splits to process")
    parser.add_argument("--num-classes", type=int, default=5,
                       help="Number of classes in dataset")
    parser.add_argument("--dry-run", action="store_true",
                       help="Preview changes without modifying files")
    parser.add_argument("--no-backup", action="store_true",
                       help="Skip creating backups")
    parser.add_argument("--report-dir", type=str, default="reports",
                       help="Directory to save validation report")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    datasets_dir = Path(args.datasets_dir)
    report_dir = Path(args.report_dir)
    report_dir.mkdir(exist_ok=True)
    
    if args.dry_run:
        logging.info("DRY RUN MODE - No files will be modified")
    
    # Process each split
    all_stats = {}
    for split in args.splits:
        logging.info(f"Processing {split} split...")
        stats = process_dataset_split(
            split, 
            datasets_dir, 
            args.num_classes, 
            args.dry_run,
            not args.no_backup
        )
        all_stats[split] = stats
    
    # Generate report
    report_path = report_dir / "label_validation_report.txt"
    generate_report(all_stats, report_path, args.dry_run)
    
    # Summary
    total_removed = sum(stats.get("removed_lines", 0) for stats in all_stats.values())
    total_emptied = sum(stats.get("emptied_files", 0) for stats in all_stats.values())
    
    if total_removed > 0 or total_emptied > 0:
        if args.dry_run:
            if total_removed > 0:
                logging.info(f"Would remove {total_removed} malformed lines")
            if total_emptied > 0:
                logging.info(f"Would empty {total_emptied} files (progress comments only)")
        else:
            if total_removed > 0:
                logging.info(f"Successfully removed {total_removed} malformed lines")
            if total_emptied > 0:
                logging.info(f"Successfully emptied {total_emptied} files (progress comments only)")
            logging.info("Re-run your evaluation script to verify the fixes")
    else:
        logging.info("No issues found - labels are already clean!")


if __name__ == "__main__":
    main()
