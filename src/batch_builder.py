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
        self.selected_cc_patch: Optional[dict] = None  # User selected CC patch override
        self.has_output_conflict = False  # Mark if output path conflicts with another job


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
        self.current_engine = None  # Track current BuildEngine for cancellation

    def stop(self):
        """Stop batch processing."""
        self.should_stop = True
        # Also stop the current build engine if running
        if self.current_engine:
            self.current_engine.stop()

    def run(self):
        """Process all jobs in queue."""
        success_count = 0
        total = len(self.jobs)

        for idx, job in enumerate(self.jobs):
            if self.should_stop:
                break

            # Skip jobs with output path conflicts
            if job.has_output_conflict:
                print(f"[SKIP] Skipping {job.title_name} due to output path conflict")
                job.status = "skipped"
                self.job_finished.emit(idx, False, "Skipped (output path conflict)")
                continue

            # Emit job started
            self.job_started.emit(idx, job.title_name)
            job.status = "processing"

            # Download icons if needed (skip if already downloaded by batch_window)
            if self.auto_icons and not (job.icon_path and job.icon_path.exists()):
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

            # Process images to cache BEFORE BuildEngine (so they survive cleanup)
            print(f"[IMAGE] Processing images to cache for {job.title_name}")

            # Get game ID for cache folder
            game_id = job.game_info.get('game_id', 'unknown')

            # Determine badge type (Galaxy, GCT patches)
            badge_type = None
            if job.pad_option == "galaxy_allstars" or "allstars" in (job.pad_option or ""):
                badge_type = "galaxy_allstars"
            elif job.pad_option == "galaxy_nvidia" or "nvidia" in (job.pad_option or ""):
                badge_type = "galaxy_nvidia"
            elif job.pad_option == "cc_patch" or (job.pad_option and job.pad_option.startswith("gct_")):
                badge_type = "gct"

            # Cache paths for this game
            cache_icon = None
            cache_banner = None
            cache_drc = None

            if job.icon_path and job.icon_path.exists():
                # Different cache filenames based on badge type
                cache_suffix = ""
                if badge_type == "galaxy_allstars":
                    cache_suffix = "_allstars"
                elif badge_type == "galaxy_nvidia":
                    cache_suffix = "_nvidia"
                elif badge_type == "gct":
                    cache_suffix = "_gct"

                cache_filename = f"icon{cache_suffix}.png" if cache_suffix else "icon.png"
                cache_icon = paths.images_cache / game_id / cache_filename

                cache_icon.parent.mkdir(parents=True, exist_ok=True)

                # Always process if badge is set, or if not already in cache
                should_process = (badge_type is not None) or (job.icon_path.resolve() != cache_icon.resolve())

                if should_process:
                    print(f"  Icon: {job.icon_path} -> {cache_icon}")
                    if badge_type:
                        print(f"  Adding {badge_type} badge to icon")
                    image_processor.process_icon(job.icon_path, cache_icon, badge_type=badge_type)
                    if cache_icon.exists():
                        print(f"  ✓ Icon cached: {cache_icon.stat().st_size} bytes")
                    else:
                        print(f"  ✗ Icon processing failed!")
                        cache_icon = None
                else:
                    print(f"  [CACHE] Icon already cached: {cache_icon}")
            else:
                print(f"  ✗ Icon not found: {job.icon_path}")

            if job.banner_path and job.banner_path.exists():
                cache_banner = paths.images_cache / game_id / "banner.png"
                cache_banner.parent.mkdir(parents=True, exist_ok=True)

                # Only process if not already in cache
                if job.banner_path.resolve() != cache_banner.resolve():
                    print(f"  Banner: {job.banner_path} -> {cache_banner}")
                    image_processor.process_banner(job.banner_path, cache_banner)
                    if cache_banner.exists():
                        print(f"  ✓ Banner cached: {cache_banner.stat().st_size} bytes")
                    else:
                        print(f"  ✗ Banner processing failed!")
                        cache_banner = None
                else:
                    print(f"  [CACHE] Banner already cached: {cache_banner}")
            else:
                print(f"  ✗ Banner not found: {job.banner_path}")

            # Use separate DRC if available, otherwise generate from banner
            if job.drc_path and job.drc_path.exists():
                cache_drc = paths.images_cache / game_id / "drc.png"
                cache_drc.parent.mkdir(parents=True, exist_ok=True)

                # Only process if not already in cache
                if job.drc_path.resolve() != cache_drc.resolve():
                    print(f"  DRC: {job.drc_path} -> {cache_drc}")
                    image_processor.process_drc(job.drc_path, cache_drc)
                else:
                    print(f"  [CACHE] DRC already cached: {cache_drc}")
            elif job.banner_path and job.banner_path.exists():
                cache_drc = paths.images_cache / game_id / "drc.png"
                cache_drc.parent.mkdir(parents=True, exist_ok=True)

                # Only process if source is different
                if job.banner_path.resolve() != cache_drc.resolve():
                    print(f"  DRC: {job.banner_path} -> {cache_drc}")
                    image_processor.process_drc(job.banner_path, cache_drc)
                else:
                    print(f"  [CACHE] DRC already cached: {cache_drc}")

            if cache_drc and cache_drc.exists():
                print(f"  ✓ DRC cached: {cache_drc.stat().st_size} bytes")
            else:
                print(f"  ✗ DRC processing failed!")
                cache_drc = None

            # Create BuildEngine (it will clean temp directories)
            engine = BuildEngine(paths, progress_callback, keep_temp_for_debug=self.keep_temp_for_debug, language=tr.current_language)
            self.current_engine = engine  # Track for cancellation

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
                # Cache image paths (BuildEngine will copy from cache to temp)
                "cache_icon_path": cache_icon,
                "cache_banner_path": cache_banner,
                "cache_drc_path": cache_drc,
                # Temp image paths (for BuildEngine to use)
                "icon_path": paths.temp_icon,
                "banner_path": paths.temp_banner,
                "drc_path": paths.temp_drc,
                # Controller option for folder naming
                "pad_option": job.pad_option,
            }

            # Apply selected profile
            print(f"\n[DEBUG] job.pad_option = '{job.pad_option}'")
            
            # Check for generic/user-selected patch override
            if job.selected_cc_patch:
                patch_info = job.selected_cc_patch
                print(f"  [CONTROLLER] {job.title_name}: Forced Patch -> {patch_info['display_name']}")
                options["force_cc_patch"] = patch_info['path']
                # If it's a generic patch (custom GCT), we usually still want the base InstantCC + the patch
                # So we don't set 'no_gamepad_emu' unless the patch specifically says so (rare)
                # But we might need 'options["galaxy_patch"] = "cc_patch"?
                # Actually BuildEngine should handle 'force_cc_patch' by just using that GCT file.
                
            elif job.pad_option == "no_gamepad":
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
            elif job.pad_option == "cc_patch":
                # CC Patch: Classic Controller 패치 (GCT Injection)
                options["galaxy_patch"] = "cc_patch"
                print(f"  [CONTROLLER] {job.title_name}: Classic Controller 패치")
            elif job.pad_option.startswith("gct_"):
                # Generic GCT patch type (dynamic patches)
                options["galaxy_patch"] = job.pad_option[4:]  # Remove 'gct_' prefix
                print(f"  [CONTROLLER] {job.title_name}: GCT 패치 ({job.pad_option})")
            else:
                print(f"  [CONTROLLER] {job.title_name}: 알 수 없는 옵션 '{job.pad_option}', 기본값 사용")

            # Select appropriate title key based on host game
            title_key = self.title_keys.get(job.host_game, '')
            if not title_key:
                # Fallback: use any available key
                title_key = next((key for key in self.title_keys.values() if key), '')

            # DEBUG: Check options being passed to build
            print(f"\n[DEBUG] Options dict being passed to build(): {options}")
            print(f"[DEBUG] galaxy_patch value: {options.get('galaxy_patch')}")
            print(f"[DEBUG] pad_option value: {options.get('pad_option')}\n")

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
