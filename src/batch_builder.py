"""Batch build system for multiple game files."""
import shutil
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

        # ═══════════════════════════════════════════════════════════════════════════
        # IMAGE MANAGEMENT SYSTEM
        # ═══════════════════════════════════════════════════════════════════════════
        # Each image type (icon, banner, drc) has:
        # 1. *_path: Current image path to use for build
        # 2. *_source: Where the image comes from ("auto", "user", "default")
        # 3. auto_*_path: Cached path of auto-downloaded image (for restore)
        # 4. user_*_path: Original path of user-selected image
        #
        # When user selects custom image:
        #   - user_*_path = user's file path
        #   - *_source = "user"
        #   - *_path = user's file path (will be processed to cache)
        #
        # When restoring to auto:
        #   - *_source = "auto"
        #   - *_path = auto_*_path (cached auto image)
        # ═══════════════════════════════════════════════════════════════════════════

        # Current image paths (used for build)
        self.icon_path: Optional[Path] = None
        self.banner_path: Optional[Path] = None
        self.drc_path: Optional[Path] = None

        # Image source type: "auto" | "user" | "default"
        self.icon_source = "auto"
        self.banner_source = "auto"
        self.drc_source = "auto"  # "auto" means generated from banner

        # Auto-downloaded image paths (for restore to auto)
        self.auto_icon_path: Optional[Path] = None
        self.auto_banner_path: Optional[Path] = None
        self.auto_drc_path: Optional[Path] = None

        # User-selected original image paths
        self.user_icon_path: Optional[Path] = None
        self.user_banner_path: Optional[Path] = None
        self.user_drc_path: Optional[Path] = None

        # Flags to force reprocessing
        self.icon_edited = False
        self.banner_edited = False
        self.drc_edited = False

        self.gamepad_compatibility = ""  # Gamepad support info from DB
        self.host_game = ""  # Host game name from DB
        self.pad_option = "wiimote"  # wiimote, horizontal_wiimote, or gamepad
        self.selected_cc_patch: Optional[dict] = None  # User selected CC patch override
        self.has_output_conflict = False  # Mark if output path conflicts with another job
        self.no_trim = False  # Don't trim ISO (fixes save issues for some games like Super Paper Mario)

    def set_user_icon(self, path: Path):
        """Set user-selected icon image."""
        self.user_icon_path = path
        self.icon_path = path
        self.icon_source = "user"
        self.icon_edited = True

    def set_user_banner(self, path: Path):
        """Set user-selected banner image."""
        self.user_banner_path = path
        self.banner_path = path
        self.banner_source = "user"
        self.banner_edited = True

    def set_user_drc(self, path: Path):
        """Set user-selected DRC (GamePad) image."""
        self.user_drc_path = path
        self.drc_path = path
        self.drc_source = "user"
        self.drc_edited = True

    def restore_auto_icon(self):
        """Restore icon to auto-downloaded image."""
        if self.auto_icon_path and self.auto_icon_path.exists():
            self.icon_path = self.auto_icon_path
            self.icon_source = "auto"
            self.icon_edited = True  # Force reprocessing to apply badge
            return True
        return False

    def restore_auto_banner(self):
        """Restore banner to auto-downloaded image."""
        if self.auto_banner_path and self.auto_banner_path.exists():
            self.banner_path = self.auto_banner_path
            self.banner_source = "auto"
            self.banner_edited = True
            return True
        return False

    def restore_auto_drc(self):
        """Restore DRC to auto-generated image (from banner)."""
        if self.auto_drc_path and self.auto_drc_path.exists():
            self.drc_path = self.auto_drc_path
            self.drc_source = "auto"
            self.drc_edited = True
            return True
        return False

    def has_auto_images(self) -> bool:
        """Check if auto-downloaded images exist."""
        return bool(self.auto_icon_path and self.auto_icon_path.exists())


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

        # Log build start
        paths.append_build_log(f"=== Batch Build Started: {total} jobs ===\n")

        for idx, job in enumerate(self.jobs):
            if self.should_stop:
                paths.append_build_log("\n[STOPPED] Build stopped by user\n")
                break

            # Skip jobs with output path conflicts
            if job.has_output_conflict:
                print(f"[SKIP] Skipping {job.title_name} due to output path conflict")
                paths.append_build_log(f"\n[{idx+1}/{total}] {job.title_name}\n  Status: SKIPPED (output path conflict)\n")
                job.status = "skipped"
                self.job_finished.emit(idx, False, "Skipped (output path conflict)")
                continue

            # Log job start
            game_id = job.game_info.get('game_id', 'unknown') if job.game_info else 'unknown'
            paths.append_build_log(f"\n[{idx+1}/{total}] {job.title_name} ({game_id})")
            paths.append_build_log(f"  File: {job.game_path}")
            paths.append_build_log(f"  Pad Option: {job.pad_option}")

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
                paths.append_build_log(f"  Status: SUCCESS")
                self.job_finished.emit(idx, True, "Build completed")
            else:
                job.status = "failed"
                paths.append_build_log(f"  Status: FAILED")
                paths.append_build_log(f"  Error: {job.error_message}")
                self.job_finished.emit(idx, False, job.error_message)

        # Log build summary
        failed_count = total - success_count
        paths.append_build_log(f"\n=== Build Summary ===")
        paths.append_build_log(f"  Success: {success_count}/{total}")
        paths.append_build_log(f"  Failed: {failed_count}/{total}")
        paths.append_build_log(f"=== End of Build Log ===\n")

        self.all_finished.emit(success_count, total)

    def download_icons(self, job: BatchBuildJob, game_id: str):
        """Download icon and banner for game to permanent cache."""
        # Use permanent cache directory (not temp - survives across builds)
        cache_dir = paths.images_cache / game_id
        cache_dir.mkdir(parents=True, exist_ok=True)

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
                    icon_path = cache_dir / "icon.png"
                    icon_path.write_bytes(icon_response.content)
                    job.icon_path = icon_path
                    job.auto_icon_path = icon_path
                    job.icon_source = "auto"

                    # Download banner
                    banner_response = requests.get(banner_url, timeout=5)
                    if banner_response.status_code == 200:
                        banner_path = cache_dir / "banner.png"
                        banner_path.write_bytes(banner_response.content)
                        job.banner_path = banner_path
                        job.auto_banner_path = banner_path
                        job.banner_source = "auto"

                        # DRC from banner
                        job.drc_path = banner_path
                        job.auto_drc_path = banner_path
                        job.drc_source = "auto"

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

            # ═══════════════════════════════════════════════════════════════════════════
            # IMAGE CACHING SYSTEM
            # ═══════════════════════════════════════════════════════════════════════════
            # Images are processed once and cached to survive BuildEngine cleanup.
            #
            # ICON CACHING STRATEGY:
            # - Icons get gamepad badges (Galaxy/GCT) burned into the image
            # - Each badge type uses a separate cache file:
            #   * icon.png          (no badge)
            #   * icon_allstars.png (Galaxy AllStars badge)
            #   * icon_nvidia.png   (Galaxy Nvidia badge)
            #   * icon_gct.png      (GCT patch badge)
            # - Icons are ONLY reprocessed when:
            #   1. Cache doesn't exist yet
            #   2. Source image path changed (user selected different image)
            #   3. Source image modified (newer timestamp)
            #   4. User explicitly edited it (icon_edited flag)
            # - This ensures user-selected icons are PRESERVED across builds
            #
            # BANNER/DRC CACHING STRATEGY:
            # - Banners and DRC images have no badges
            # - Always use banner.png and drc.png
            # - Only reprocessed when source changes or user edits
            # - User-selected banners are PRESERVED across builds
            # ═══════════════════════════════════════════════════════════════════════════

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

                # Determine source icon path based on source type
                cache_dir = paths.images_cache / game_id
                source_icon_path = job.icon_path

                # For user images, use the original user path
                if job.icon_source == "user" and job.user_icon_path and job.user_icon_path.exists():
                    source_icon_path = job.user_icon_path
                    print(f"  [USER] Using user-selected icon: {source_icon_path}")
                elif job.icon_path.parent == cache_dir:
                    # Icon is already cached, use base icon.png as source
                    base_icon = cache_dir / "icon.png"
                    if base_icon.exists():
                        source_icon_path = base_icon
                        print(f"  [CACHE] Using base icon as source: {base_icon}")

                # Process if: different path, source is newer, OR user edited the image
                is_different_path = source_icon_path.resolve() != cache_icon.resolve()
                is_source_newer = cache_icon.exists() and source_icon_path.stat().st_mtime > cache_icon.stat().st_mtime
                user_edited = getattr(job, 'icon_edited', False)
                cache_not_exists = not cache_icon.exists()
                should_process = is_different_path or is_source_newer or user_edited or cache_not_exists

                if should_process:
                    print(f"  Icon: {source_icon_path} -> {cache_icon}")
                    if badge_type:
                        print(f"  Adding {badge_type} badge to icon")
                    if user_edited:
                        print(f"  (User edited)")
                    success = image_processor.process_icon(source_icon_path, cache_icon, badge_type=badge_type)
                    if success and cache_icon.exists():
                        print(f"  ✓ Icon cached: {cache_icon.stat().st_size} bytes")
                        # Reset edited flag after processing
                        job.icon_edited = False
                    else:
                        # Fallback: copy original file directly to cache
                        print(f"  [FALLBACK] Icon processing failed, copying original...")
                        try:
                            shutil.copy2(source_icon_path, cache_icon)
                            print(f"  ✓ Icon copied directly: {cache_icon}")
                        except Exception as e:
                            print(f"  ✗ Icon copy failed: {e}")
                            cache_icon = None
                else:
                    print(f"  [CACHE] Icon already cached: {cache_icon}")
            else:
                print(f"  ✗ Icon not found: {job.icon_path}")

            if job.banner_path and job.banner_path.exists():
                cache_banner = paths.images_cache / game_id / "banner.png"
                cache_banner.parent.mkdir(parents=True, exist_ok=True)

                # Determine source banner path based on source type
                source_banner_path = job.banner_path
                if job.banner_source == "user" and job.user_banner_path and job.user_banner_path.exists():
                    source_banner_path = job.user_banner_path
                    print(f"  [USER] Using user-selected banner: {source_banner_path}")

                # Process if: different path, source is newer, user edited, OR cache doesn't exist
                is_different_path = source_banner_path.resolve() != cache_banner.resolve()
                is_source_newer = cache_banner.exists() and source_banner_path.stat().st_mtime > cache_banner.stat().st_mtime
                user_edited = getattr(job, 'banner_edited', False)
                cache_not_exists = not cache_banner.exists()
                should_process_banner = is_different_path or is_source_newer or user_edited or cache_not_exists

                if should_process_banner:
                    if user_edited:
                        print(f"  Banner: {source_banner_path} (User edited)")
                    elif is_source_newer and not is_different_path:
                        print(f"  Banner: {source_banner_path} (source newer than cache)")
                    else:
                        print(f"  Banner: {source_banner_path} -> {cache_banner}")
                    success = image_processor.process_banner(source_banner_path, cache_banner)
                    if success and cache_banner.exists():
                        print(f"  ✓ Banner cached: {cache_banner.stat().st_size} bytes")
                        job.banner_edited = False
                    else:
                        # Fallback: copy original file directly to cache
                        print(f"  [FALLBACK] Banner processing failed, copying original...")
                        try:
                            shutil.copy2(source_banner_path, cache_banner)
                            print(f"  ✓ Banner copied directly: {cache_banner}")
                        except Exception as e:
                            print(f"  ✗ Banner copy failed: {e}")
                            cache_banner = None
                else:
                    print(f"  [CACHE] Banner already cached: {cache_banner}")
            else:
                print(f"  ✗ Banner not found: {job.banner_path}")

            # Use separate DRC if available, otherwise generate from banner
            cache_drc = paths.images_cache / game_id / "drc.png"
            cache_drc.parent.mkdir(parents=True, exist_ok=True)

            # Determine source DRC path based on source type
            source_drc_path = None
            if job.drc_source == "user" and job.user_drc_path and job.user_drc_path.exists():
                source_drc_path = job.user_drc_path
                print(f"  [USER] Using user-selected DRC: {source_drc_path}")
            elif job.drc_path and job.drc_path.exists():
                source_drc_path = job.drc_path
            elif job.banner_path and job.banner_path.exists():
                # Generate DRC from banner
                source_drc_path = job.banner_path
                print(f"  [AUTO] Generating DRC from banner")

            if source_drc_path:
                user_edited = getattr(job, 'drc_edited', False)
                is_different_path = source_drc_path.resolve() != cache_drc.resolve()
                cache_not_exists = not cache_drc.exists()
                should_process_drc = is_different_path or user_edited or cache_not_exists

                if should_process_drc:
                    print(f"  DRC: {source_drc_path} -> {cache_drc}")
                    success = image_processor.process_drc(source_drc_path, cache_drc)
                    if success and cache_drc.exists():
                        print(f"  ✓ DRC cached: {cache_drc.stat().st_size} bytes")
                        job.drc_edited = False
                    else:
                        # Fallback: copy original file directly to cache
                        print(f"  [FALLBACK] DRC processing failed, copying original...")
                        try:
                            shutil.copy2(source_drc_path, cache_drc)
                            print(f"  ✓ DRC copied directly: {cache_drc}")
                        except Exception as e:
                            print(f"  ✗ DRC copy failed: {e}")
                            cache_drc = None
                else:
                    print(f"  [CACHE] DRC already cached: {cache_drc}")
            else:
                print(f"  ✗ No DRC source available")
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
                # Don't trim option (fixes save issues for some games)
                "disable_trimming": job.no_trim,
            }

            # Apply selected profile
            print(f"\n[DEBUG] job.pad_option = '{job.pad_option}'")
            
            # Check for generic/user-selected patch override
            if job.selected_cc_patch:
                patch_info = job.selected_cc_patch
                print(f"  [CONTROLLER] {job.title_name}: Forced Patch -> {patch_info['display_name']}")
                options["force_cc_patch"] = patch_info['path']
                # Pass requires_getexttype flag from patch metadata
                options["requires_getexttype"] = patch_info.get('requires_getexttype', False)
                print(f"  [CONTROLLER] GetExtTypePatcher: {'Required' if options['requires_getexttype'] else 'Not Required'}")
                
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
            import traceback
            error_trace = traceback.format_exc()
            job.error_message = str(e)
            paths.append_build_log(f"  Exception: {e}")
            paths.append_build_log(f"  Traceback:\n{error_trace}")
            return False
