#!/usr/bin/env python
"""
Cleanup utility for the Malaysian Lead Generator project.

This script handles the cleanup of temporary files and directories created during
the scraping and lead generation process. It removes expired files, compresses logs,
and maintains the disk space usage within acceptable limits.
"""

import os
import sys
import time
import shutil
import logging
import argparse
import zipfile
import json
from datetime import datetime, timedelta
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("cleanup.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_CONFIG = {
    "temp_directories": [
        "cache",
        "logs",
        "output/temp",
        "scrapers/temp"
    ],
    "file_age_threshold_days": 7,
    "log_archive_threshold_days": 30,
    "max_log_size_mb": 100,
    "compress_logs": True,
    "db_backup_before_cleanup": True,
    "skip_patterns": [
        ".gitkeep",
        "README.md",
        "important_"
    ]
}

def load_config(config_path=None):
    """Load configuration from file or use defaults."""
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                logger.info(f"Loaded configuration from {config_path}")
                # Merge with defaults for any missing keys
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
    
    logger.info("Using default configuration")
    return DEFAULT_CONFIG

def should_skip_file(filename, skip_patterns):
    """Check if file should be skipped based on patterns."""
    for pattern in skip_patterns:
        if pattern in filename:
            return True
    return False

def get_file_age_days(file_path):
    """Get file age in days."""
    mtime = os.path.getmtime(file_path)
    file_datetime = datetime.fromtimestamp(mtime)
    age = datetime.now() - file_datetime
    return age.days

def backup_database(backup_dir="backups"):
    """Create a backup of the database before cleanup."""
    try:
        # Ensure backup directory exists
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"leads_db_backup_{timestamp}.db")
        
        # Copy the database file
        shutil.copy2("leads.db", backup_path)
        logger.info(f"Database backed up to {backup_path}")
        
        # Remove old backups (keep last 5)
        backups = sorted([f for f in os.listdir(backup_dir) if f.startswith("leads_db_backup_")])
        if len(backups) > 5:
            for old_backup in backups[:-5]:
                os.remove(os.path.join(backup_dir, old_backup))
                logger.info(f"Removed old backup: {old_backup}")
        
        return True
    except Exception as e:
        logger.error(f"Database backup failed: {e}")
        return False

def compress_log_directory(log_dir, archive_dir="log_archives"):
    """Compress logs older than threshold to save space."""
    if not os.path.exists(log_dir):
        logger.warning(f"Log directory not found: {log_dir}")
        return 0
    
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
    
    # Get all log files
    log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
    if not log_files:
        logger.info(f"No log files found in {log_dir}")
        return 0
    
    # Group logs by date (assuming format includes date like YYYY-MM-DD)
    log_groups = {}
    for log_file in log_files:
        try:
            # Extract date from filename or use modification time
            try:
                # Try to extract date from filename (assuming format with date)
                date_str = log_file.split('_')[0]  # Adjust based on your log naming convention
                date_obj = datetime.strptime(date_str, "%Y%m%d")
            except (IndexError, ValueError):
                # If date extraction fails, use file modification time
                mtime = os.path.getmtime(os.path.join(log_dir, log_file))
                date_obj = datetime.fromtimestamp(mtime)
            
            # Group by date
            date_key = date_obj.strftime("%Y%m%d")
            if date_key not in log_groups:
                log_groups[date_key] = []
            log_groups[date_key].append(log_file)
        except Exception as e:
            logger.warning(f"Error processing log file {log_file}: {e}")
    
    # Compress each group
    archives_created = 0
    for date_key, files in log_groups.items():
        archive_path = os.path.join(archive_dir, f"logs_{date_key}.zip")
        
        # Skip if archive already exists
        if os.path.exists(archive_path):
            continue
        
        try:
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in files:
                    file_path = os.path.join(log_dir, file)
                    zipf.write(file_path, arcname=file)
                    # Delete original after successful compression
                    os.remove(file_path)
            
            logger.info(f"Compressed {len(files)} logs to {archive_path}")
            archives_created += 1
        except Exception as e:
            logger.error(f"Error compressing logs for {date_key}: {e}")
    
    return archives_created

def cleanup_temp_files(config):
    """Clean up temporary files based on configuration."""
    logger.info("Starting cleanup process")
    
    # Backup database if configured
    if config["db_backup_before_cleanup"]:
        backup_database()
    
    files_removed = 0
    bytes_freed = 0
    errors = 0
    
    # Process each directory in the configuration
    for temp_dir in config["temp_directories"]:
        if not os.path.exists(temp_dir):
            logger.warning(f"Directory not found: {temp_dir}")
            continue
        
        logger.info(f"Processing directory: {temp_dir}")
        
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if should_skip_file(file, config["skip_patterns"]):
                    continue
                
                file_path = os.path.join(root, file)
                
                try:
                    # Check file age
                    age_days = get_file_age_days(file_path)
                    
                    if age_days >= config["file_age_threshold_days"]:
                        # Get file size before deletion
                        file_size = os.path.getsize(file_path)
                        
                        # Remove file
                        os.remove(file_path)
                        
                        files_removed += 1
                        bytes_freed += file_size
                        logger.debug(f"Removed: {file_path} (Age: {age_days} days, Size: {file_size / 1024:.1f} KB)")
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    errors += 1
    
    # Compress logs if configured
    if config["compress_logs"]:
        logger.info("Compressing old log files")
        archives = compress_log_directory("logs")
        logger.info(f"Created {archives} log archives")
    
    # Log summary
    logger.info(f"Cleanup complete: {files_removed} files removed, {bytes_freed / (1024*1024):.2f} MB freed")
    if errors > 0:
        logger.warning(f"Encountered {errors} errors during cleanup")
    
    return {
        "files_removed": files_removed,
        "bytes_freed": bytes_freed,
        "errors": errors
    }

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Cleanup temporary files for Malaysian Lead Generator")
    parser.add_argument(
        "--config", 
        help="Path to configuration file (JSON)",
        default=None
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Show what would be deleted without actually deleting"
    )
    parser.add_argument(
        "--force", 
        action="store_true",
        help="Force cleanup ignoring age thresholds"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose logging"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    # Set logging level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Load configuration
    config = load_config(args.config)
    
    # Modify config if force flag is set
    if args.force:
        logger.warning("Force mode enabled - ignoring age thresholds")
        config["file_age_threshold_days"] = 0
    
    # Execute cleanup or dry run
    if args.dry_run:
        logger.info("Dry run mode - no files will be deleted")
        # TODO: Implement dry run logic to show what would be deleted
        # For now, just print the configuration
        logger.info(f"Configuration: {json.dumps(config, indent=2)}")
    else:
        cleanup_temp_files(config) 