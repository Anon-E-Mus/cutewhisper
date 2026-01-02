"""
Model Download Progress Tracker - Monitors and displays model download progress
"""

from pathlib import Path
import time
import threading
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)


class ModelDownloadProgress:
    """Track and display model download progress"""

    # Estimated model sizes in bytes
    MODEL_SIZES = {
        'tiny': 39 * 1024 * 1024,    # ~39MB
        'base': 74 * 1024 * 1024,    # ~74MB
        'small': 244 * 1024 * 1024,   # ~244MB
        'medium': 769 * 1024 * 1024,  # ~769MB
        'large': 1550 * 1024 * 1024,  # ~1.5GB
        'large-v1': 1550 * 1024 * 1024,
        'large-v2': 1550 * 1024 * 1024,
        'large-v3': 1550 * 1024 * 1024,
    }

    def __init__(self, model_size='base'):
        """
        Initialize progress tracker

        Args:
            model_size: Whisper model size (for size estimation)
        """
        self.monitoring = False
        self.monitor_thread = None
        self.models_dir = None
        self.pbar = None
        self.model_size = model_size
        self.estimated_size = self.MODEL_SIZES.get(model_size, self.MODEL_SIZES['base'])

    def start_monitoring(self, models_dir: str):
        """
        Start monitoring model directory for download progress

        Args:
            models_dir: Path to models directory
        """
        self.models_dir = Path(models_dir)
        self.monitoring = True

        # Start monitoring in background thread
        self.monitor_thread = threading.Thread(
            target=self._monitor_download,
            daemon=True
        )
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop monitoring and clean up progress bar"""
        self.monitoring = False
        if self.pbar:
            self.pbar.close()
            self.pbar = None

    def _monitor_download(self):
        """Monitor model directory and update progress"""
        initial_size = self._get_dir_size()

        # If directory already has content, assume model exists
        if initial_size > 1024 * 1024:  # More than 1MB
            logger.debug(f"Model directory already contains {initial_size / (1024*1024):.1f} MB")
            return

        # Initialize progress bar
        self.pbar = tqdm(
            total=100,
            unit='%',
            desc="Downloading",
            bar_format='{l_bar}{bar}| {n:.1f}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
        )

        last_update = time.time()
        last_size = initial_size

        while self.monitoring:
            current_size = self._get_dir_size()

            if current_size > initial_size:
                # Calculate progress percentage
                progress = min(100, int((current_size / self.estimated_size) * 100))

                # Update progress bar
                self.pbar.update(progress - self.pbar.n)
                last_size = current_size
                last_update = time.time()

            time.sleep(0.5)  # Check twice per second

        # Download complete
        if self.pbar:
            final_size_mb = current_size / (1024 * 1024)
            self.pbar.write(f"✓ Model ready ({final_size_mb:.1f} MB)")

    def _get_dir_size(self) -> int:
        """Calculate total size of models directory in bytes"""
        total_size = 0
        if self.models_dir.exists():
            for file_path in self.models_dir.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        return total_size
