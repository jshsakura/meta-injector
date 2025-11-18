"""Batch build system for multiple game files."""
from pathlib import Path
from typing import List, Dict, Optional
from PyQt5.QtCore import QThread, pyqtSignal
from .build_engine import BuildEngine
from .paths import paths
from .image_utils import image_processor
import requests


class BatchBuildJob:
    """Single build job in batch queue."""

    def __init__(self, game_path: Path, game_info: dict = None):
        self.game_path = game_path
        self.game_info = game_info
        self.status = "pending"  # pending, processing, completed, failed
        self.error_message = ""
        self.title_name = ""
        self.title_id = ""
        self.icon_path: Optional[Path] = None
        self.banner_path: Optional[Path] = None
        self.gamepad_compatibility = ""  # Gamepad support info from DB
        self.host_game = ""  # Host game name from DB


class BatchBuilder(QThread):
    """Background thread for batch building multiple games."""

    # Signals
    progress_updated = pyqtSignal(int, int, str)  # current_index, total, message
    job_started = pyqtSignal(int, str)  # index, game_name
    job_finished = pyqtSignal(int, bool, str)  # index, success, message
    all_finished = pyqtSignal(int, int)  # success_count, total_count

    def __init__(self, jobs: List[BatchBuildJob], common_key: str, title_keys: Dict[str, str],
                 output_dir: Path, auto_icons: bool = True):
        super().__init__()
        self.jobs = jobs
        self.common_key = common_key
        self.title_keys = title_keys  # Dict mapping host game name to title key
        self.output_dir = output_dir
        self.auto_icons = auto_icons
        self.should_stop = False

    def stop(self):
        """Stop batch processing."""
        self.should_stop = True

    def run(self):
        """Process all jobs in queue."""
        success_count = 0
        total = len(self.jobs)

        for idx, job in enumerate(self.jobs):
            if self.should_stop:
                break

            # Emit job started
            self.job_started.emit(idx, job.title_name)
            job.status = "processing"

            # Download icons if needed
            if self.auto_icons:
                self.download_icons(job, job.game_info.get('game_id', ''))

            # Build
            success = self.build_job(job, idx, total)

            if success:
                success_count += 1
                job.status = "completed"
                self.job_finished.emit(idx, True, "Build completed")
            else:
                job.status = "failed"
                self.job_finished.emit(idx, False, job.error_message)

        self.all_finished.emit(success_count, total)

    def download_icons(self, job: BatchBuildJob, game_id: str):
        """Download icon and banner for game."""
        cucholix_id = game_id[:4] if len(game_id) >= 4 else game_id

        # Try different ID variations
        id_variations = [
            game_id[:4],  # RMGE
            game_id,      # RMGE01
        ]

        for try_id in id_variations:
            icon_url = f"https://raw.githubusercontent.com/UWUVCI-PRIME/UWUVCI-IMAGES/master/wii/{try_id}/iconTex.png"
            banner_url = f"https://raw.githubusercontent.com/UWUVCI-PRIME/UWUVCI-IMAGES/master/wii/{try_id}/bootTvTex.png"

            try:
                # Download icon
                icon_response = requests.get(icon_url, timeout=5)
                if icon_response.status_code == 200:
                    icon_path = paths.temp_source / f"icon_{game_id}.png"
                    icon_path.write_bytes(icon_response.content)
                    job.icon_path = icon_path

                    # Download banner
                    banner_response = requests.get(banner_url, timeout=5)
                    if banner_response.status_code == 200:
                        banner_path = paths.temp_source / f"banner_{game_id}.png"
                        banner_path.write_bytes(banner_response.content)
                        job.banner_path = banner_path

                    break  # Found icons, stop trying
            except:
                continue

    def build_job(self, job: BatchBuildJob, idx: int, total: int) -> bool:
        """Build single job."""
        try:
            def progress_callback(percent, message):
                self.progress_updated.emit(idx + 1, total, f"[{idx+1}/{total}] {message}")

            # Process images if available
            if job.icon_path and job.icon_path.exists():
                image_processor.process_icon(job.icon_path, paths.temp_icon)
            if job.banner_path and job.banner_path.exists():
                image_processor.process_banner(job.banner_path, paths.temp_banner)
                image_processor.process_drc(job.banner_path, paths.temp_drc)

            engine = BuildEngine(paths, progress_callback)

            # Set options based on gamepad compatibility from DB
            options = {
                "disable_passthrough": False,
                "lr_patch": False,
            }

            # Check gamepad compatibility and set options accordingly
            gamepad_compat = job.gamepad_compatibility.lower()
            if 'gamepad works' in gamepad_compat or 'works' in gamepad_compat:
                # Enable gamepad support
                options["disable_passthrough"] = True
            elif 'classic controller' in gamepad_compat or 'lr patch' in gamepad_compat:
                # Enable LR patch for classic controller only games
                options["lr_patch"] = True

            # Select appropriate title key based on host game
            title_key = self.title_keys.get(job.host_game, '')
            if not title_key:
                # Fallback: use any available key
                title_key = next((key for key in self.title_keys.values() if key), '')

            success = engine.build(
                game_path=job.game_path,
                system_type=job.game_info.get('system', 'wii'),
                output_dir=self.output_dir,
                common_key=self.common_key,
                title_key=title_key,
                title_name=job.title_name,
                title_id=job.title_id,
                options=options
            )

            return success

        except Exception as e:
            job.error_message = str(e)
            return False
