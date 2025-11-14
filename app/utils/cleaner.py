import os
import time
from datetime import datetime, timedelta
from pathlib import Path

from ..logger import logger

def list_recent_files(directory: os.PathLike='.', age_seconds=60):
    """
    List files in the given directory that were modified within the last `age_seconds`.
    
    Parameters:
        directory (str): Path to the directory to scan (default: current directory).
        age_seconds (int): Maximum age in seconds (default: 60 for 1 minute).
    """
    now = time.time()
    cutoff = now - age_seconds

    try:
        with os.scandir(directory) as entries:
            recent_files = []
            for entry in entries:
                if entry.is_file():
                    # Get modification time
                    mtime = entry.stat().st_mtime
                    if mtime < cutoff:
                        recent_files.append(entry)
            
            return recent_files
    
    except FileNotFoundError:
        print(f"Error: Directory '{directory}' not found.")
    except PermissionError:
        print(f"Error: Permission denied to access '{directory}'.")
        
        
def delete_files(directory: os.PathLike='.', age_seconds=60):
    """
    Delete files in the given directory that were modified within the last `age_seconds`.
    
    Parameters:
        directory (str): Path to the directory to scan (default: current directory).
        age_seconds (int): Maximum age in seconds (default: 60 for 1 minute).
    """
    recent_files = list_recent_files(directory, age_seconds)
    removed = []
    errors = []
    for file in recent_files:
        _path = Path(file)
        logger.info(f"Deleting file: {_path.name}")
        try:
            _path.unlink()
            removed.append(_path.name)
        except OSError as e:
            errors.append(e)
            continue
    
    return removed, errors