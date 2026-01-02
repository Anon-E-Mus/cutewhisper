"""
Temp File Cleanup Utilities - Manages temporary audio files
"""

from pathlib import Path
import time
import logging

logger = logging.getLogger(__name__)


def cleanup_old_temp_files(temp_dir="temp", max_age_hours=24):
    """
    Remove temp files older than max_age_hours

    Called at startup to clean up any orphaned files from crashes

    Args:
        temp_dir: Path to temp directory
        max_age_hours: Maximum age in hours before files are deleted

    Returns:
        Number of files cleaned up
    """
    temp_path = Path(temp_dir)
    if not temp_path.exists():
        logger.debug(f"Temp directory does not exist: {temp_dir}")
        return 0

    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    cleaned = 0
    total_freed_bytes = 0

    for file_path in temp_path.glob("*.wav"):
        try:
            file_age = current_time - file_path.stat().st_mtime
            if file_age > max_age_seconds:
                file_size = file_path.stat().st_size
                file_path.unlink()
                cleaned += 1
                total_freed_bytes += file_size
                logger.debug(f"Removed old temp file: {file_path.name} ({file_size / 1024:.1f} KB)")
        except Exception as e:
            logger.warning(f"Could not remove {file_path}: {e}")

    if cleaned > 0:
        freed_mb = total_freed_bytes / (1024 * 1024)
        logger.info(f"Cleaned up {cleaned} old temp file(s), freed {freed_mb:.2f} MB")
    else:
        logger.debug("No old temp files to clean")

    return cleaned


def cleanup_all_temp_files(temp_dir="temp"):
    """
    Remove all temp files

    Called on uninstall or explicit cleanup request

    Args:
        temp_dir: Path to temp directory

    Returns:
        Number of files cleaned up
    """
    temp_path = Path(temp_dir)
    if not temp_path.exists():
        return 0

    cleaned = 0
    total_freed_bytes = 0

    for file_path in temp_path.glob("*"):
        try:
            if file_path.is_file():
                file_size = file_path.stat().st_size
                file_path.unlink()
                cleaned += 1
                total_freed_bytes += file_size
                logger.debug(f"Removed temp file: {file_path.name}")
        except Exception as e:
            logger.warning(f"Could not remove {file_path}: {e}")

    if cleaned > 0:
        freed_mb = total_freed_bytes / (1024 * 1024)
        logger.info(f"Cleaned up {cleaned} temp file(s), freed {freed_mb:.2f} MB")

    return cleaned


def get_temp_dir_size(temp_dir="temp") -> int:
    """
    Calculate total size of temp directory in bytes

    Args:
        temp_dir: Path to temp directory

    Returns:
        Size in bytes
    """
    temp_path = Path(temp_dir)
    if not temp_path.exists():
        return 0

    total_size = 0
    for file_path in temp_path.glob("*"):
        if file_path.is_file():
            total_size += file_path.stat().st_size

    return total_size
