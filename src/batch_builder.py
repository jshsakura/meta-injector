"""Batch build system for multiple game files."""
from pathlib import Path
from typing import List, Dict, Optional
from PyQt5.QtCore import QThread, pyqtSignal
from .build_engine import BuildEngine
from .translations import tr
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
        self.drc_path: Optional[Path] = None
        self.gamepad_compatibility = ""  # Gamepad support info from DB
        self.host_game = ""  # Host game name from DB
        self.pad_option = "wiimote"  # wiimote, horizontal_wiimote, or gamepad


class BatchBuilder(QThread):
    """Background thread for batch building multiple games."""

    # Signals
    progress_updated = pyqtSignal(int, int, str)  # current_index, total, message
    job_started = pyqtSignal(int, str)  # index, game_name
    job_finished = pyqtSignal(int, bool, str)  # index, success, message
    all_finished = pyqtSignal(int, int)  # success_count, total_count

    def __init__(self, jobs: List[BatchBuildJob], common_key: str, title_keys: Dict[str, str],
                 output_dir: Path, auto_icons: bool = True, keep_temp_for_debug: bool = False):
        super().__init__()
        self.jobs = jobs
        self.common_key = common_key
        self.title_keys = title_keys  # Dict mapping host game name to title key
        self.output_dir = output_dir
        self.auto_icons = auto_icons
        self.keep_temp_for_debug = keep_temp_for_debug
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
                # Calculate overall progress: job progress + previous jobs
                # Each job is worth (100/total)%, current job contributes (percent * 100/total)%
                overall_percent = int((idx * 100 / total) + (percent / total))
                self.progress_updated.emit(overall_percent, 100, f"[{idx+1}/{total}] {message}")

            # Process images if available
            if job.icon_path and job.icon_path.exists():
                image_processor.process_icon(job.icon_path, paths.temp_icon)
            if job.banner_path and job.banner_path.exists():
                image_processor.process_banner(job.banner_path, paths.temp_banner)
            # Use separate DRC if available, otherwise generate from banner
            if job.drc_path and job.drc_path.exists():
                image_processor.process_drc(job.drc_path, paths.temp_drc)
            elif job.banner_path and job.banner_path.exists():
                image_processor.process_drc(job.banner_path, paths.temp_drc)

            engine = BuildEngine(paths, progress_callback, keep_temp_for_debug=self.keep_temp_for_debug, language=tr.current_language)

            # Controller Profile Selection (7 Profiles)
            # Profile 1 - no_gamepad: 미적용 (Wii 리모컨만) → -nocc
            # Profile 2 - none: 기본 게임패드 (CC 에뮬레이션) → -instantcc
            # Profile 3 - gamepad_lr: 게임패드 + LR 패치 → -instantcc -lrpatch
            # Profile 4 - wiimote: Wii 리모컨 모드 → -wiimote
            # Profile 5 - horizontal_wiimote: 가로 Wii 리모컨 → -wiimote -horizontal
            # Profile 6 - passthrough: Passthrough (Homebrew/Nintendont) → -passthrough
            # Profile 7 - galaxy: Galaxy 패치 → -instantcc + GCT
            options = {
                "no_gamepad_emu": False,    # Profile 1: -nocc
                "wiimote_mode": False,      # Profile 4/5: -wiimote
                "passthrough_mode": False,  # Profile 6: -passthrough
                "horizontal_wiimote": False,  # Profile 5: -horizontal
                "lr_patch": False,          # Profile 3: -lrpatch
            }

            # Apply selected profile
            if job.pad_option == "no_gamepad":
                # Profile 1: 미적용 (No GamePad)
                options["no_gamepad_emu"] = True
                print(f"  [CONTROLLER] {job.title_name}: 미적용 (Wii 리모컨만)")
            elif job.pad_option == "none":
                # Profile 2: 기본 게임패드 (Classic Controller Emulation)
                # 옵션 없음 (기본값이 -instantcc)
                print(f"  [CONTROLLER] {job.title_name}: 게임패드 (CC 에뮬레이션)")
            elif job.pad_option == "gamepad_lr":
                # Profile 3: 게임패드 + LR (Analog Trigger Patch)
                options["lr_patch"] = True
                print(f"  [CONTROLLER] {job.title_name}: 게임패드 + LR 패치")
            elif job.pad_option == "wiimote":
                # Profile 4: Wii 리모컨 모드 (Vertical Wiimote Emulation)
                options["wiimote_mode"] = True
                print(f"  [CONTROLLER] {job.title_name}: Wii 리모컨 모드 (세로)")
            elif job.pad_option == "horizontal_wiimote":
                # Profile 5: 가로 Wii 리모컨 (Horizontal Wiimote Emulation)
                options["wiimote_mode"] = True
                options["horizontal_wiimote"] = True
                print(f"  [CONTROLLER] {job.title_name}: Wii 리모컨 모드 (가로)")
            elif job.pad_option == "passthrough":
                # Profile 6: Passthrough (Homebrew/Nintendont Native)
                options["passthrough_mode"] = True
                print(f"  [CONTROLLER] {job.title_name}: Passthrough (홈브루 전용)")
            elif job.pad_option == "galaxy_allstars":
                # Profile 7: Galaxy AllStars 패치 (Complex Instruction Set Injection)
                options["galaxy_patch"] = "allstars"
                print(f"  [CONTROLLER] {job.title_name}: Galaxy AllStars 패치")
            elif job.pad_option == "galaxy_nvidia":
                # Profile 7: Galaxy Nvidia 패치 (Complex Instruction Set Injection)
                options["galaxy_patch"] = "nvidia"
                print(f"  [CONTROLLER] {job.title_name}: Galaxy Nvidia 패치")
            else:
                print(f"  [CONTROLLER] {job.title_name}: 알 수 없는 옵션 '{job.pad_option}', 기본값 사용")

            # Select appropriate title key based on host game
            title_key = self.title_keys.get(job.host_game, '')
            if not title_key:
                # Fallback: use any available key
                title_key = next((key for key in self.title_keys.values() if key), '')

            success = engine.build(
                game_path=job.game_path,
                output_dir=self.output_dir,
                common_key=self.common_key,
                title_key=title_key,
                title_name=job.title_name,
                options=options,
                system_type=job.game_info.get('system', 'wii')
            )

            return success

        except Exception as e:
            job.error_message = str(e)
            return False
