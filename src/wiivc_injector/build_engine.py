"""Build engine for WiiVC Injector - calls external tools."""
import os
import subprocess
import shutil
import hashlib
from pathlib import Path
from typing import Optional, Callable
from .translations import tr


class BuildEngine:
    """Handles the build process by calling external tools."""

    def __init__(self, paths_manager, progress_callback: Optional[Callable[[int, str], None]] = None):
        """
        Initialize build engine.

        Args:
            paths_manager: PathManager instance
            progress_callback: Function to call with (progress_percent, status_message)
        """
        self.paths = paths_manager
        self.progress_callback = progress_callback

        # Deprecated: No longer using MD5 hash validation, just format validation
        # self.COMMON_KEY_HASH = "35AC59949722793319709094FA2FB97FC"
        # self.TITLE_KEY_HASH = "F94BD88EBB7AA93867E630615F271C9F"
        # self.ANCAST_KEY_HASH = "318D1F9D98FB08E77C7FE177AA490543"

    def update_progress(self, percent: int, message: str):
        """Update progress."""
        if self.progress_callback:
            self.progress_callback(percent, message)

    def verify_key(self, key: str, expected_hash: str = None) -> bool:
        """
        Verify encryption key format (32 hex characters).

        Args:
            key: Key string to verify
            expected_hash: Deprecated, not used

        Returns:
            True if valid format
        """
        key_clean = key.upper().replace("-", "").strip()
        # Just check format: 32 hex characters
        return len(key_clean) == 32 and all(c in '0123456789ABCDEF' for c in key_clean)

    def run_java(self, args: str, cwd: Optional[Path] = None, hide_window: bool = True) -> bool:
        """
        Run Java with arguments.

        Args:
            args: Java arguments (e.g., '-jar tool.jar ...')
            cwd: Working directory
            hide_window: Hide command window

        Returns:
            True if successful
        """
        try:
            cmd = f'java {args}'

            startupinfo = None
            if hide_window and os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            print(f"\n{'='*80}")
            print(f"Running Java tool")
            print(f"Command: {cmd}")
            print(f"Working directory: {cwd}")
            print(f"{'='*80}")

            result = subprocess.run(
                cmd,
                shell=True,
                cwd=str(cwd) if cwd else None,
                startupinfo=startupinfo,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'  # Ignore decoding errors
            )

            if result.stdout:
                print(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                print(f"STDERR:\n{result.stderr}")

            if result.returncode != 0:
                print(f"\n❌ Java tool failed with exit code: {result.returncode}")
                print(f"{'='*80}\n")
                return False

            print(f"✓ Java tool completed successfully")
            print(f"{'='*80}\n")
            return True

        except Exception as e:
            print(f"\n❌ Exception running Java: {e}")
            import traceback
            traceback.print_exc()
            print(f"{'='*80}\n")
            return False

    def run_tool(self, exe_path: Path, args: str, cwd: Optional[Path] = None, hide_window: bool = True,
                 progress_start: int = None, progress_end: int = None) -> bool:
        """
        Run external tool.

        Args:
            exe_path: Path to executable
            args: Command line arguments
            cwd: Working directory
            hide_window: Hide command window
            progress_start: Starting progress percentage (optional)
            progress_end: Ending progress percentage (optional)

        Returns:
            True if successful
        """
        try:
            cmd = f'"{exe_path}" {args}'

            startupinfo = None
            if hide_window and os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            print(f"\n{'='*80}")
            print(f"Running tool: {exe_path.name}")
            print(f"Command: {cmd}")
            print(f"Working directory: {cwd}")
            print(f"{'='*80}")

            # If progress range specified, show incremental progress
            if progress_start is not None and progress_end is not None:
                import time
                import threading

                # Start process without waiting
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    cwd=str(cwd) if cwd else None,
                    startupinfo=startupinfo,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'
                )

                # Simulate progress updates while process is running
                progress_range = progress_end - progress_start
                current_progress = progress_start
                increment = max(1, progress_range // 10)  # Update 10 times

                stdout_lines = []
                stderr_lines = []

                def read_output(pipe, lines):
                    for line in iter(pipe.readline, ''):
                        if line:
                            lines.append(line)
                            print(line, end='')

                # Start threads to read output
                stdout_thread = threading.Thread(target=read_output, args=(process.stdout, stdout_lines))
                stderr_thread = threading.Thread(target=read_output, args=(process.stderr, stderr_lines))
                stdout_thread.daemon = True
                stderr_thread.daemon = True
                stdout_thread.start()
                stderr_thread.start()

                # Update progress while waiting
                while process.poll() is None:
                    if current_progress < progress_end:
                        current_progress = min(current_progress + increment, progress_end - 1)
                        self.update_progress(current_progress, tr.get("progress_processing", percent=current_progress))
                    time.sleep(0.5)  # Update every 0.5 seconds

                # Wait for threads to finish
                stdout_thread.join(timeout=1)
                stderr_thread.join(timeout=1)

                result_stdout = ''.join(stdout_lines)
                result_stderr = ''.join(stderr_lines)
                returncode = process.returncode

            else:
                # Original behavior - wait for completion
                result = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=str(cwd) if cwd else None,
                    startupinfo=startupinfo,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'
                )
                result_stdout = result.stdout
                result_stderr = result.stderr
                returncode = result.returncode

            if result_stdout:
                print(f"STDOUT:\n{result_stdout}")
            if result_stderr:
                print(f"STDERR:\n{result_stderr}")

            if returncode != 0:
                print(f"\n❌ Tool failed with exit code: {returncode}")
                print(f"{'='*80}\n")
                return False

            print(f"✓ Tool completed successfully")
            print(f"{'='*80}\n")
            return True

        except Exception as e:
            print(f"\n❌ Exception running tool {exe_path}: {e}")
            import traceback
            traceback.print_exc()
            print(f"{'='*80}\n")
            return False

    def download_base_files(self, common_key: str, title_key: str) -> bool:
        """
        Download base files using JNUSTool.

        Args:
            common_key: Wii U Common Key
            title_key: Title Key

        Returns:
            True if successful
        """
        self.update_progress(10, "Checking base files...")

        # Define critical files (title_id, jnustool_subpath, local_filename)
        # jnustool_subpath: path used by jnustool (includes code/meta folders)
        # local_filename: simplified name for local cache
        # NOTE: Excludes boot.bin, c2w.img, dmcu.d.hex, deint.txt, font.bin
        #       These files have no NUSPacker content rules and are not needed
        critical_file_paths = [
            # Rhythm Heaven base files (only these are needed)
            ("00050000101b0700", "code/cos.xml", "cos.xml"),
            ("00050000101b0700", "code/frisbiiU.rpx", "frisbiiU.rpx"),
            ("00050000101b0700", "code/fw.img", "fw.img"),
            ("00050000101b0700", "code/fw.tmd", "fw.tmd"),
            ("00050000101b0700", "code/htk.bin", "htk.bin"),
            ("00050000101b0700", "code/nn_hai_user.rpl", "nn_hai_user.rpl"),
            ("00050000101b0700", "content/assets/shaders/cafe/banner.gsh", "banner.gsh"),
            ("00050000101b0700", "content/assets/shaders/cafe/fade.gsh", "fade.gsh"),
            ("00050000101b0700", "meta/bootMovie.h264", "bootMovie.h264"),
            ("00050000101b0700", "meta/bootLogoTex.tga", "bootLogoTex.tga"),
            ("00050000101b0700", "meta/bootSound.btsnd", "bootSound.btsnd"),
        ]

        # Check project-local cache first (most reliable)
        local_cache = self.paths.base_files_cache
        local_files = [(local_cache / title_id / local_name) for title_id, jnus_path, local_name in critical_file_paths]
        local_missing = [f for f in local_files if not f.exists()]

        if not local_missing:
            print(f"✓ Base files found in project cache: {local_cache}")
            print(f"✓ Verified {len(local_files)} files")
            self.update_progress(40, "Base files ready (cached)")
            return True

        # Check JNUSTool downloads directory
        # JNUSTool saves files by game name (e.g., "Rhythm Heaven Fever [VAKE01]") not by title ID
        # But for system files, it uses the title ID
        jnustool_programdata = Path(os.environ.get('PROGRAMDATA', 'C:\\ProgramData')) / "JNUSToolDownloads"
        jnustool_jar = self.paths.temp_tools / "JAR"

        # Map title IDs to JNUSTool folder names
        jnustool_folder_map = {
            "00050000101b0700": "Rhythm Heaven Fever [VAKE01]",  # Game name folder
            "0005001010004000": "0005001010004000",  # System files use title ID
            "0005001010004001": "0005001010004001",
        }

        # Build jnustool file paths - check both ProgramData (for games) and JAR (for system)
        jnustool_files = []
        for title_id, jnus_path, local_name in critical_file_paths:
            folder_name = jnustool_folder_map.get(title_id, title_id)
            if title_id.startswith("00050010"):  # System files in JAR
                jnustool_files.append(jnustool_jar / folder_name / jnus_path)
            else:  # Game files in ProgramData
                jnustool_files.append(jnustool_programdata / folder_name / jnus_path)

        jnustool_missing = [f for f in jnustool_files if not f.exists()]

        # If files exist in JNUSTool cache but not in local cache, copy them
        if not jnustool_missing:
            print(f"✓ Found files in JNUSTool cache, copying to project cache...")
            for src, dst in zip(jnustool_files, local_files):
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
            print(f"✓ Copied {len(local_files)} files to project cache")
            self.update_progress(40, "Base files ready (cached)")
            return True

        print(f"⚠ Missing {len(jnustool_missing)} base files, downloading from Nintendo CDN...")
        self.update_progress(10, f"Downloading {len(jnustool_missing)} files...")

        # Create JNUSTool config
        jnustool_dir = self.paths.temp_tools / "JAR"
        jnustool_dir.mkdir(parents=True, exist_ok=True)  # Create directory if it doesn't exist
        config_path = jnustool_dir / "config"

        config_content = f"http://ccs.cdn.wup.shop.nintendo.net/ccs/download\n{common_key}\n"
        config_path.write_text(config_content)

        # Clear JNUSTool's ProgramData cache to force fresh downloads
        # JNUSTool checks this cache and skips downloads if files exist there
        programdata_cache = Path(os.environ.get('PROGRAMDATA', 'C:\\ProgramData')) / "JNUSToolDownloads"
        if programdata_cache.exists():
            for title_id in ["00050000101b0700", "0005001010004000", "0005001010004001"]:
                cache_dir = programdata_cache / title_id
                if cache_dir.exists():
                    print(f"  Clearing JNUSTool cache: {cache_dir}")
                    shutil.rmtree(cache_dir, ignore_errors=True)

        # Use jnustool.exe (IKVM compiled version)
        jnustool_exe = jnustool_dir / "jnustool.exe"
        if not jnustool_exe.exists():
            print(f"ERROR: jnustool.exe not found at {jnustool_exe}")
            return False

        # Download each missing file
        downloaded_count = 0
        for title_id, jnus_path, local_name in critical_file_paths:
            jnus_file = jnustool_dir / title_id / jnus_path
            if jnus_file.exists():
                continue  # Skip if already downloaded

            # Determine title key - system titles don't need key
            key = None
            if title_id == "00050000101b0700":
                key = title_key

            # Build jnustool command with -dlEncrypted to force download
            args = f"{title_id}"
            if key:
                args += f" {key}"
            args += f" -file /{jnus_path}"

            if not self.run_tool(jnustool_exe, args, cwd=jnustool_dir):
                print(f"Failed to download /{jnus_path}")
                # Continue anyway - files may already exist
            else:
                downloaded_count += 1

        # Verify download was successful
        jnustool_missing_after = [f for f in jnustool_files if not f.exists()]
        if jnustool_missing_after:
            print(f"⚠ Warning: {len(jnustool_missing_after)} files still missing after download")
            for f in jnustool_missing_after[:5]:  # Show first 5
                print(f"  - {f}")
            return False

        print(f"✓ Downloaded {downloaded_count} new files to JNUSTool cache")

        # Copy to project-local cache for faster future access
        print(f"✓ Copying to project cache: {local_cache}")
        for src, dst in zip(jnustool_files, local_files):
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        print(f"✓ Cached {len(local_files)} files in project directory")

        return True

    def convert_wbfs_to_iso(self, wbfs_path: Path) -> Path:
        """
        Convert WBFS to ISO format using wit.

        Uses direct conversion which is faster than extract+repack.

        Args:
            wbfs_path: Path to WBFS file

        Returns:
            Path to converted ISO file, or None if failed
        """
        wit_tool = self.paths.project_root / "core" / "WIT" / "wit.exe"
        output_iso = self.paths.temp_source / f"{wbfs_path.stem}.iso"

        # Direct copy: WBFS → ISO (maximum speed optimizations)
        # --iso: Force plain ISO output (fastest format)
        # --overwrite: No confirmation prompts
        # --no-sort: Skip file sorting
        # --trunc: Truncate to minimal size (faster write)
        # --psel=raw: Copy raw data without scrubbing (fastest mode)
        # -q: Quiet mode (minimal output)
        args = f'copy "{wbfs_path}" "{output_iso}" --iso --overwrite --no-sort --trunc --psel=raw -q'

        if self.run_tool(wit_tool, args):
            if output_iso.exists():
                print(f"✓ Converted WBFS to ISO: {output_iso}")
                return output_iso

        print(f"❌ Failed to convert WBFS to ISO")
        return None

    def apply_galaxy_gamepad_patch(self, game_path: Path, game_id: str, patch_type: str) -> Path:
        """
        Apply gamepad patch using GCT files.

        This patch can be applied to any Wii game, not just Super Mario Galaxy.
        It maps the game's controls to the Wii U GamePad.

        Args:
            game_path: Path to ISO/WBFS file
            game_id: Game ID (e.g., RMGE01, RMGK01, RUUK01)
            patch_type: 'allstars' or 'nvidia'

        Returns:
            Path to patched ISO file, or None if failed
        """
        # Map region code to Galaxy game ID - only region matters
        region_char = game_id[3] if len(game_id) >= 4 else 'E'
        galaxy_region_map = {
            'E': 'RMGE01',  # USA
            'P': 'RMGP01',  # EUR
            'J': 'RMGJ01',  # JPN
            'K': 'RMGK01',  # KOR
        }
        galaxy_id = galaxy_region_map.get(region_char, 'RMGE01')

        # Determine GCT file based on patch type and region
        gct_suffix = "AllStars" if patch_type == "allstars" else "Nvidia"
        gct_filename = f"{galaxy_id}-{gct_suffix}.gct"
        gct_path = self.paths.project_root / "core" / "Galaxy1GamePad_v1.2" / gct_filename

        if not gct_path.exists():
            print(f"❌ GCT file not found: {gct_path}")
            return None

        print(f"✓ Applying gamepad patch: {game_id} (region {region_char}) -> {gct_filename}")

        # Tools (both 64-bit Cygwin)
        wit_tool = self.paths.project_root / "core" / "WIT" / "wit.exe"
        wstrt_tool = self.paths.project_root / "core" / "WIT" / "wstrt.exe"

        if not wit_tool.exists():
            print(f"❌ wit.exe not found: {wit_tool}")
            return None

        if not wstrt_tool.exists():
            print(f"❌ wstrt.exe not found: {wstrt_tool}")
            return None

        # Create temp directory for extraction (clean start every time)
        extract_dir = self.paths.temp_source / "galaxy_extract"

        # Forcefully remove existing directory
        if extract_dir.exists():
            print(f"Removing existing extraction directory: {extract_dir}")
            try:
                # Try multiple times if needed (sometimes takes a moment on Windows)
                for attempt in range(3):
                    try:
                        shutil.rmtree(extract_dir, ignore_errors=False)
                        break
                    except Exception as e:
                        if attempt < 2:
                            import time
                            time.sleep(0.5)
                        else:
                            print(f"❌ Could not remove directory after 3 attempts: {e}")
                            return None
            except Exception as e:
                print(f"❌ Could not remove directory: {e}")
                return None

        extract_dir.mkdir(parents=True, exist_ok=True)

        # Verify directory is really empty
        if list(extract_dir.iterdir()):
            print(f"❌ Directory not empty after cleanup: {extract_dir}")
            return None

        print(f"✓ Clean extraction directory ready: {extract_dir}")

        # Step 1: Extract game with wit (full extraction including sys folder)
        # Use --overwrite to force extraction even if destination exists
        args = f'extract "{game_path}" "{extract_dir}" --overwrite'
        if not self.run_tool(wit_tool, args):
            print("❌ Failed to extract game with wit")
            return None

        # Step 2: Apply GCT patch to main.dol with wstrt
        # wstrt patch main.dol --add-section file.gct
        main_dol = extract_dir / "sys" / "main.dol"
        if not main_dol.exists():
            # Try alternative path (some extractions put it differently)
            main_dol = extract_dir / "DATA" / "sys" / "main.dol"
        if not main_dol.exists():
            print(f"❌ main.dol not found in {extract_dir}")
            return None

        args = f'patch "{main_dol}" --add-section="{gct_path}"'
        if not self.run_tool(wstrt_tool, args):
            print("❌ Failed to patch main.dol with wstrt")
            return None

        # Step 3: Repack to ISO with wit
        # wit copy extract_dir output.iso
        patched_iso = self.paths.temp_source / f"{game_path.stem}_patched.iso"
        args = f'copy "{extract_dir}" "{patched_iso}"'
        if not self.run_tool(wit_tool, args):
            print("❌ Failed to repack game with wit")
            return None

        if not patched_iso.exists():
            print(f"❌ Patched ISO not created: {patched_iso}")
            return None

        print(f"✓ Galaxy gamepad patch applied: {patched_iso}")

        # Cleanup extraction directory
        shutil.rmtree(extract_dir, ignore_errors=True)

        return patched_iso

    def convert_iso_to_nfs(self, iso_path: Path, system_type: str, options: dict) -> bool:
        """
        Convert ISO to NFS format.

        Args:
            iso_path: Path to ISO file
            system_type: System type (wii, gcn, dol, wiiware)
            options: Build options

        Returns:
            True if successful
        """
        # Progress: 70-85% (this step takes the longest time)
        self.update_progress(70, "Starting NFS conversion (this may take several minutes)...")

        nfs_tool = self.paths.temp_tools / "EXE" / "nfs2iso2nfs.exe"
        output_dir = self.paths.temp_build / "content"

        # Clean existing NFS files to prevent accumulation
        if output_dir.exists():
            print(f"Cleaning existing NFS files in {output_dir}")
            for nfs_file in output_dir.glob("*.nfs"):
                nfs_file.unlink()
                print(f"  Removed: {nfs_file.name}")

        output_dir.mkdir(parents=True, exist_ok=True)

        self.update_progress(40, tr.get("progress_preparing_nfs"))

        # Build arguments based on system type
        # nfs2iso2nfs options:
        # -passthrough: 게임패드 입력을 Wii 리모컨으로 변환 (게임패드 미지원 게임용)
        # -lrpatch: LR 버튼 패치 (클래식 컨트롤러 전용)
        # -horizontal: 가로 Wiimote 모드
        # force_cc_emu=True: passthrough 제거 → 게임패드로 클래식 컨트롤러 에뮬레이션
        args = "-enc"

        if system_type == "wii":
            if not options.get("force_cc_emu"):
                # 게임패드 미지원 - passthrough로 Wii 리모컨 에뮬레이션
                args += " -passthrough"
                # 가로 Wiimote 모드
                if options.get("horizontal_wiimote"):
                    args += " -horizontal"
            # force_cc_emu=True면 passthrough 없음 → 게임패드로 CC 에뮬레이션
            if options.get("lr_patch"):
                args += " -lrpatch"
        elif system_type == "gcn":
            # GameCube는 항상 homebrew + passthrough
            args += " -homebrew -passthrough"
        elif system_type in ["dol", "wiiware"]:
            args += " -homebrew"
            if not options.get("force_cc_emu"):
                args += " -passthrough"
                if options.get("horizontal_wiimote"):
                    args += " -horizontal"
            if options.get("lr_patch"):
                args += " -lrpatch"

        args += f' -iso "{iso_path}"'

        self.update_progress(42, tr.get("progress_converting_nfs"))

        # Run with progress tracking from 42% to 75% (longest operation)
        result = self.run_tool(nfs_tool, args, cwd=output_dir, progress_start=42, progress_end=75)

        if result:
            self.update_progress(75, tr.get("progress_nfs_complete"))

        return result

    def convert_images_to_tga(self) -> bool:
        """
        Convert PNG images to TGA format for meta files.

        Returns:
            True if successful
        """
        try:
            from PIL import Image

            meta_dir = self.paths.temp_build / "meta"
            meta_dir.mkdir(parents=True, exist_ok=True)

            # Convert icon if exists
            if self.paths.temp_icon.exists():
                with Image.open(self.paths.temp_icon) as img:
                    icon_tga = meta_dir / "iconTex.tga"
                    img.save(icon_tga, 'TGA')
                    print(f"✓ Converted icon to TGA: {icon_tga}")

            # Convert banner if exists
            if self.paths.temp_banner.exists():
                with Image.open(self.paths.temp_banner) as img:
                    banner_tga = meta_dir / "bootTvTex.tga"
                    img.save(banner_tga, 'TGA')
                    print(f"✓ Converted banner to TGA: {banner_tga}")

            # Convert DRC if exists
            if self.paths.temp_drc.exists():
                with Image.open(self.paths.temp_drc) as img:
                    drc_tga = meta_dir / "bootDrcTex.tga"
                    img.save(drc_tga, 'TGA')
                    print(f"✓ Converted DRC to TGA: {drc_tga}")

            # Convert logo if exists
            if self.paths.temp_logo.exists():
                with Image.open(self.paths.temp_logo) as img:
                    logo_tga = meta_dir / "bootLogoTex.tga"
                    img.save(logo_tga, 'TGA')
                    print(f"✓ Converted logo to TGA: {logo_tga}")

            return True

        except Exception as e:
            print(f"Error converting images to TGA: {e}")
            return False

    def copy_base_files(self) -> bool:
        """
        Copy base files from project cache to build directory.

        Returns:
            True if successful
        """
        try:
            # Use project-local cache (more reliable than JNUSTool cache)
            cache_dir = self.paths.base_files_cache
            build_code = self.paths.temp_build / "code"
            build_meta = self.paths.temp_build / "meta"

            build_code.mkdir(parents=True, exist_ok=True)
            build_meta.mkdir(parents=True, exist_ok=True)

            # Copy code files (matching Rhythm Heaven Fever base structure)
            code_files = [
                # Skip these files - not present in base and no NUSPacker content rules:
                # (cache_dir / "0005001010004000" / "deint.txt", build_code / "deint.txt"),
                # (cache_dir / "0005001010004000" / "font.bin", build_code / "font.bin"),
                # (cache_dir / "0005001010004001" / "c2w.img", build_code / "c2w.img"),
                # (cache_dir / "0005001010004001" / "boot.bin", build_code / "boot.bin"),
                # (cache_dir / "0005001010004001" / "dmcu.d.hex", build_code / "dmcu.d.hex"),
                (cache_dir / "00050000101b0700" / "cos.xml", build_code / "cos.xml"),
                (cache_dir / "00050000101b0700" / "frisbiiU.rpx", build_code / "frisbiiU.rpx"),
                (cache_dir / "00050000101b0700" / "fw.img", build_code / "fw.img"),
                (cache_dir / "00050000101b0700" / "fw.tmd", build_code / "fw.tmd"),
                (cache_dir / "00050000101b0700" / "htk.bin", build_code / "htk.bin"),
                (cache_dir / "00050000101b0700" / "nn_hai_user.rpl", build_code / "nn_hai_user.rpl"),
            ]

            copied = 0
            missing = []
            for src, dst in code_files:
                if src.exists():
                    shutil.copy2(src, dst)
                    copied += 1
                else:
                    missing.append(str(src))
                    print(f"⚠ Missing: {src}")

            # Copy meta files
            meta_files = [
                (cache_dir / "00050000101b0700" / "bootMovie.h264", build_meta / "bootMovie.h264"),
                (cache_dir / "00050000101b0700" / "bootLogoTex.tga", build_meta / "bootLogoTex.tga"),
                (cache_dir / "00050000101b0700" / "bootSound.btsnd", build_meta / "bootSound.btsnd"),
            ]

            for src, dst in meta_files:
                if src.exists():
                    shutil.copy2(src, dst)
                    copied += 1
                else:
                    missing.append(str(src))
                    print(f"⚠ Missing: {src}")

            # Verify minimum required files are present
            required_code_files = ["cos.xml", "frisbiiU.rpx", "fw.img", "fw.tmd", "htk.bin", "nn_hai_user.rpl"]
            for filename in required_code_files:
                if not (build_code / filename).exists():
                    print(f"❌ Critical file missing: {filename}")
                    return False

            print(f"✓ Copied {copied} base files from cache to build directory")
            if missing:
                print(f"⚠ Warning: {len(missing)} optional files were missing")
            return True

        except Exception as e:
            print(f"Error copying base files: {e}")
            import traceback
            traceback.print_exc()
            return False

    def generate_xml_files(self, title_name: str, title_id: str) -> bool:
        """
        Generate app.xml and meta.xml files for NUSPacker.

        Args:
            title_name: Game title
            title_id: Title ID (8 hex characters)

        Returns:
            True if successful
        """
        try:
            import html

            # Escape XML special characters
            safe_title = html.escape(title_name)

            # Generate app.xml
            code_dir = self.paths.temp_build / "code"
            code_dir.mkdir(parents=True, exist_ok=True)

            app_xml = f"""<?xml version="1.0" encoding="utf-8"?>
<app type="complex" access="777">
  <version type="unsignedInt" length="4">16</version>
  <os_version type="hexBinary" length="8">000500101000400A</os_version>
  <title_id type="hexBinary" length="8">{title_id}</title_id>
  <title_version type="unsignedInt" length="4">0</title_version>
  <sdk_version type="unsignedInt" length="4">21204</sdk_version>
  <app_type type="hexBinary" length="4">80000000</app_type>
  <group_id type="hexBinary" length="4">0000000F</group_id>
</app>"""

            app_xml_path = code_dir / "app.xml"
            app_xml_path.write_text(app_xml, encoding='utf-8')
            print(f"✓ Generated app.xml: {app_xml_path}")

            # Generate meta.xml
            meta_dir = self.paths.temp_build / "meta"
            meta_dir.mkdir(parents=True, exist_ok=True)

            meta_xml = f"""<?xml version="1.0" encoding="utf-8"?>
<menu type="complex" access="777">
  <version type="unsignedInt" length="4">33</version>
  <product_code type="string" length="32">WUP-N-{title_id}</product_code>
  <content_platform type="string" length="32">WUP</content_platform>
  <company_code type="string" length="8">0001</company_code>
  <mastering_date type="string" length="32"></mastering_date>
  <logo_type type="unsignedInt" length="4">0</logo_type>
  <app_launch_type type="hexBinary" length="4">00000000</app_launch_type>
  <invisible_flag type="hexBinary" length="4">00000000</invisible_flag>
  <no_managed_flag type="hexBinary" length="4">00000000</no_managed_flag>
  <no_event_log type="hexBinary" length="4">00000000</no_event_log>
  <no_icon_database type="hexBinary" length="4">00000000</no_icon_database>
  <launching_flag type="hexBinary" length="4">00000004</launching_flag>
  <install_flag type="hexBinary" length="4">00000000</install_flag>
  <closing_msg type="unsignedInt" length="4">0</closing_msg>
  <title_version type="unsignedInt" length="4">0</title_version>
  <title_id type="hexBinary" length="8">{title_id}</title_id>
  <group_id type="hexBinary" length="4">0000000F</group_id>
  <boss_id type="hexBinary" length="8">0000000000000000</boss_id>
  <os_version type="hexBinary" length="8">000500101000400A</os_version>
  <app_size type="hexBinary" length="8">0000000000000000</app_size>
  <common_save_size type="hexBinary" length="8">0000000000000000</common_save_size>
  <account_save_size type="hexBinary" length="8">0000000000000000</account_save_size>
  <common_boss_size type="hexBinary" length="8">0000000000000000</common_boss_size>
  <account_boss_size type="hexBinary" length="8">0000000000000000</account_boss_size>
  <save_no_rollback type="unsignedInt" length="4">0</save_no_rollback>
  <join_game_id type="hexBinary" length="8">0000000000000000</join_game_id>
  <join_game_mode_mask type="hexBinary" length="8">0000000000000000</join_game_mode_mask>
  <bg_daemon_enable type="unsignedInt" length="4">0</bg_daemon_enable>
  <olv_accesskey type="unsignedInt" length="4">3921440372</olv_accesskey>
  <wood_tin type="unsignedInt" length="4">0</wood_tin>
  <e_manual type="unsignedInt" length="4">0</e_manual>
  <e_manual_version type="unsignedInt" length="4">0</e_manual_version>
  <region type="hexBinary" length="4">00000002</region>
  <pc_cero type="unsignedInt" length="4">128</pc_cero>
  <pc_esrb type="unsignedInt" length="4">6</pc_esrb>
  <pc_bbfc type="unsignedInt" length="4">192</pc_bbfc>
  <pc_usk type="unsignedInt" length="4">128</pc_usk>
  <pc_pegi_gen type="unsignedInt" length="4">128</pc_pegi_gen>
  <pc_pegi_fin type="unsignedInt" length="4">192</pc_pegi_fin>
  <pc_pegi_prt type="unsignedInt" length="4">128</pc_pegi_prt>
  <pc_pegi_bbfc type="unsignedInt" length="4">128</pc_pegi_bbfc>
  <pc_cob type="unsignedInt" length="4">128</pc_cob>
  <pc_grb type="unsignedInt" length="4">128</pc_grb>
  <pc_cgsrr type="unsignedInt" length="4">128</pc_cgsrr>
  <pc_oflc type="unsignedInt" length="4">128</pc_oflc>
  <pc_reserved0 type="unsignedInt" length="4">192</pc_reserved0>
  <pc_reserved1 type="unsignedInt" length="4">192</pc_reserved1>
  <pc_reserved2 type="unsignedInt" length="4">192</pc_reserved2>
  <pc_reserved3 type="unsignedInt" length="4">192</pc_reserved3>
  <ext_dev_nunchaku type="unsignedInt" length="4">0</ext_dev_nunchaku>
  <ext_dev_classic type="unsignedInt" length="4">0</ext_dev_classic>
  <ext_dev_urcc type="unsignedInt" length="4">0</ext_dev_urcc>
  <ext_dev_board type="unsignedInt" length="4">0</ext_dev_board>
  <ext_dev_usb_keyboard type="unsignedInt" length="4">0</ext_dev_usb_keyboard>
  <ext_dev_etc type="unsignedInt" length="4">0</ext_dev_etc>
  <ext_dev_etc_name type="string" length="512"></ext_dev_etc_name>
  <eula_version type="unsignedInt" length="4">0</eula_version>
  <drc_use type="unsignedInt" length="4">1</drc_use>
  <network_use type="unsignedInt" length="4">0</network_use>
  <online_account_use type="unsignedInt" length="4">0</online_account_use>
  <direct_boot type="unsignedInt" length="4">0</direct_boot>
  <reserved_flag0 type="hexBinary" length="4">00010001</reserved_flag0>
  <reserved_flag1 type="hexBinary" length="4">00000000</reserved_flag1>
  <reserved_flag2 type="hexBinary" length="4">00000000</reserved_flag2>
  <reserved_flag3 type="hexBinary" length="4">00000000</reserved_flag3>
  <reserved_flag4 type="hexBinary" length="4">00000000</reserved_flag4>
  <reserved_flag5 type="hexBinary" length="4">00000000</reserved_flag5>
  <reserved_flag6 type="hexBinary" length="4">00010001</reserved_flag6>
  <reserved_flag7 type="hexBinary" length="4">00000000</reserved_flag7>
  <longname_ja type="string" length="512">{safe_title}</longname_ja>
  <longname_en type="string" length="512">{safe_title}</longname_en>
  <longname_fr type="string" length="512">{safe_title}</longname_fr>
  <longname_de type="string" length="512">{safe_title}</longname_de>
  <longname_it type="string" length="512">{safe_title}</longname_it>
  <longname_es type="string" length="512">{safe_title}</longname_es>
  <longname_zhs type="string" length="512">{safe_title}</longname_zhs>
  <longname_ko type="string" length="512">{safe_title}</longname_ko>
  <longname_nl type="string" length="512">{safe_title}</longname_nl>
  <longname_pt type="string" length="512">{safe_title}</longname_pt>
  <longname_ru type="string" length="512">{safe_title}</longname_ru>
  <longname_zht type="string" length="512">{safe_title}</longname_zht>
  <shortname_ja type="string" length="256">{safe_title}</shortname_ja>
  <shortname_en type="string" length="256">{safe_title}</shortname_en>
  <shortname_fr type="string" length="256">{safe_title}</shortname_fr>
  <shortname_de type="string" length="256">{safe_title}</shortname_de>
  <shortname_it type="string" length="256">{safe_title}</shortname_it>
  <shortname_es type="string" length="256">{safe_title}</shortname_es>
  <shortname_zhs type="string" length="256">{safe_title}</shortname_zhs>
  <shortname_ko type="string" length="256">{safe_title}</shortname_ko>
  <shortname_nl type="string" length="256">{safe_title}</shortname_nl>
  <shortname_pt type="string" length="256">{safe_title}</shortname_pt>
  <shortname_ru type="string" length="256">{safe_title}</shortname_ru>
  <shortname_zht type="string" length="256">{safe_title}</shortname_zht>
  <publisher_ja type="string" length="256">Nintendo</publisher_ja>
  <publisher_en type="string" length="256">Nintendo</publisher_en>
  <publisher_fr type="string" length="256">Nintendo</publisher_fr>
  <publisher_de type="string" length="256">Nintendo</publisher_de>
  <publisher_it type="string" length="256">Nintendo</publisher_it>
  <publisher_es type="string" length="256">Nintendo</publisher_es>
  <publisher_zhs type="string" length="256">Nintendo</publisher_zhs>
  <publisher_ko type="string" length="256">Nintendo</publisher_ko>
  <publisher_nl type="string" length="256">Nintendo</publisher_nl>
  <publisher_pt type="string" length="256">Nintendo</publisher_pt>
  <publisher_ru type="string" length="256">Nintendo</publisher_ru>
  <publisher_zht type="string" length="256">Nintendo</publisher_zht>
</menu>"""

            meta_xml_path = meta_dir / "meta.xml"
            meta_xml_path.write_text(meta_xml, encoding='utf-8')
            print(f"✓ Generated meta.xml: {meta_xml_path}")

            return True

        except Exception as e:
            print(f"Error generating XML files: {e}")
            import traceback
            traceback.print_exc()
            return False

    def pack_final(self, output_path: Path, common_key: str, title_name: str, title_id: str, game_id: str, options: dict = None) -> bool:
        """
        Pack final WUP package using NUSPacker.

        Args:
            output_path: Output directory
            common_key: Wii U Common Key
            title_name: Game title
            title_id: Title ID
            game_id: Game ID
            options: Build options (for folder naming)

        Returns:
            True if successful
        """
        # Pack final: 85-95% (encryption and packing)
        self.update_progress(85, "Preparing for encryption...")

        nuspacker_exe = self.paths.temp_tools / "JAR" / "nuspacker.exe"

        # Use game_id for folder name (unique identifier)
        if game_id:
            safe_name = game_id
        else:
            # Fallback: Sanitize title_name - ASCII only for compatibility
            safe_name = "".join(c if c.isascii() and (c.isalnum() or c in " -_()") else "_" for c in title_name)
            # Remove consecutive underscores
            while "__" in safe_name:
                safe_name = safe_name.replace("__", "_")
            safe_name = safe_name.strip("_")

            # If name became empty or too short, use title_id only
            if len(safe_name) < 3:
                safe_name = title_id[-8:]

        # Add controller option suffix to distinguish different builds
        option_suffix = ""
        if options:
            if options.get("galaxy_patch") == "allstars":
                option_suffix = "_GalAS"
            elif options.get("galaxy_patch") == "nvidia":
                option_suffix = "_GalNV"
            elif options.get("force_cc_emu") and options.get("lr_patch"):
                option_suffix = "_PadLR"
            elif options.get("force_cc_emu"):
                option_suffix = "_Pad"
            elif options.get("horizontal_wiimote"):
                option_suffix = "_HWii"
            # Vertical wiimote (default) gets no suffix

        final_output = output_path / f"{safe_name}{option_suffix}_WUP-N-{title_id}"

        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)

        # Verify BUILDDIR structure before packing
        build_code = self.paths.temp_build / "code"
        build_meta = self.paths.temp_build / "meta"
        build_content = self.paths.temp_build / "content"

        if not build_code.exists() or not build_meta.exists() or not build_content.exists():
            print(f"❌ Build directory structure incomplete")
            print(f"  code: {build_code.exists()}")
            print(f"  meta: {build_meta.exists()}")
            print(f"  content: {build_content.exists()}")
            return False

        # Check for critical files
        if not (build_code / "app.xml").exists():
            print(f"❌ app.xml not found in build directory")
            return False
        if not (build_meta / "meta.xml").exists():
            print(f"❌ meta.xml not found in build directory")
            return False

        # Count NFS files
        nfs_files = list(build_content.glob("*.nfs"))
        if len(nfs_files) == 0:
            print(f"❌ No NFS files found in content directory")
            return False
        print(f"✓ Build directory verified: {len(nfs_files)} NFS files ready")

        self.update_progress(87, "Encrypting and packing (this may take a while)...")

        # Run NUSPacker with special error checking
        args = f'-in "{self.paths.temp_build}" -out "{final_output}" -encryptKeyWith {common_key}'

        try:
            cmd = f'"{nuspacker_exe}" {args}'

            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            print(f"\n{'='*80}")
            print(f"Running tool: nuspacker.exe")
            print(f"Command: {cmd}")
            print(f"Working directory: {self.paths.temp_root}")
            print(f"{'='*80}")

            result = subprocess.run(
                cmd,
                shell=True,
                cwd=str(self.paths.temp_root),
                startupinfo=startupinfo,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )

            if result.stdout:
                print(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                print(f"STDERR:\n{result.stderr}")

                # Check for fatal errors in stderr (NUSPacker returns 0 even on errors)
                stderr_lower = result.stderr.lower()
                if "is not assigned to any content" in stderr_lower:
                    print(f"\n❌ NUSPacker failed: Files not assigned to content")
                    print(f"{'='*80}\n")
                    return False
                if "error" in stderr_lower and "file" in stderr_lower:
                    print(f"\n❌ NUSPacker failed with file error")
                    print(f"{'='*80}\n")
                    return False

            if result.returncode != 0:
                print(f"\n❌ NUSPacker failed with exit code: {result.returncode}")
                print(f"{'='*80}\n")
                return False

            print(f"✓ NUSPacker completed successfully")
            print(f"{'='*80}\n")

        except Exception as e:
            print(f"\n❌ Exception running NUSPacker: {e}")
            import traceback
            traceback.print_exc()
            print(f"{'='*80}\n")
            return False

        self.update_progress(90, "Verifying output files...")

        # Verify output files were created
        if not final_output.exists():
            print(f"❌ Output directory not created: {final_output}")
            print(f"   Expected location: {final_output}")
            return False

        # Check for essential files - must contain .app files and title.tmd
        output_files = list(final_output.rglob("*"))
        app_files = list(final_output.glob("*.app"))
        tmd_files = list(final_output.glob("title.tmd"))
        tik_files = list(final_output.glob("title.tik"))

        if len(output_files) == 0:
            print(f"❌ No files generated in output: {final_output}")
            return False

        # Verify critical files exist
        missing_critical = []
        if len(app_files) == 0:
            missing_critical.append(".app files")
        if len(tmd_files) == 0:
            missing_critical.append("title.tmd")
        if len(tik_files) == 0:
            missing_critical.append("title.tik")

        if missing_critical:
            print(f"❌ Package incomplete - missing: {', '.join(missing_critical)}")
            print(f"   Generated {len(output_files)} files but package structure is invalid")
            return False

        print(f"✓ Build complete! Generated {len(output_files)} files")
        print(f"  - {len(app_files)} .app files")
        print(f"  - title.tmd and title.tik present")
        print(f"✓ Output location: {final_output}")
        self.update_progress(95, f"Complete: {final_output.name}")
        return True

    def build(self, game_path: Path, system_type: str, output_dir: Path,
              common_key: str, title_key: str,
              title_name: str, title_id: str, game_id: str, options: dict) -> bool:
        """
        Main build process.

        Args:
            game_path: Path to game ISO/WBFS
            system_type: System type (wii, gcn, dol, wiiware)
            output_dir: Output directory
            common_key: Wii U Common Key
            title_key: Title Key
            title_name: Game title
            title_id: Title ID
            options: Build options dict

        Returns:
            True if successful
        """
        try:
            # Progress breakdown:
            # 0-5%: Verify keys
            # 5-45%: Download base files
            # 45-50%: Copy base files
            # 50-55%: Convert images
            # 55-60%: WBFS to ISO (if needed)
            # 60-70%: Galaxy patch (if needed)
            # 70-85%: ISO to NFS conversion
            # 85-100%: Final packing

            # Verify keys (0-3%)
            self.update_progress(0, tr.get("progress_verifying_keys"))

            if not self.verify_key(common_key):
                raise ValueError("Invalid Wii U Common Key (must be 32 hex characters)")

            if not self.verify_key(title_key):
                raise ValueError("Invalid Title Key (must be 32 hex characters)")

            self.update_progress(3, tr.get("progress_keys_verified"))

            # Clean build directory from previous runs
            if self.paths.temp_build.exists():
                print(f"Cleaning previous build directory: {self.paths.temp_build}")
                shutil.rmtree(self.paths.temp_build, ignore_errors=True)

            # Download base files (3-20%)
            if not self.download_base_files(common_key, title_key):
                raise RuntimeError("Failed to download base files")

            # Copy base files to build directory (20-25%)
            self.update_progress(20, tr.get("progress_copying_base_files"))
            if not self.copy_base_files():
                raise RuntimeError("Failed to copy base files")

            # Convert images to TGA (25-28%)
            self.update_progress(25, tr.get("progress_converting_images"))
            if not self.convert_images_to_tga():
                raise RuntimeError("Failed to convert images")

            # Convert WBFS to ISO if needed (28-32%)
            actual_game_path = game_path
            if str(game_path).lower().endswith('.wbfs'):
                self.update_progress(28, tr.get("progress_converting_wbfs"))
                iso_path = self.convert_wbfs_to_iso(game_path)
                if not iso_path:
                    raise RuntimeError("Failed to convert WBFS to ISO")
                actual_game_path = iso_path
                self.update_progress(32, tr.get("progress_wbfs_converted"))
            else:
                self.update_progress(32, tr.get("progress_using_iso"))

            # Apply Galaxy gamepad patch if requested (32-38%)
            galaxy_patch = options.get("galaxy_patch")
            if galaxy_patch:
                self.update_progress(32, tr.get("progress_applying_patch", patch_type=galaxy_patch))
                patched_path = self.apply_galaxy_gamepad_patch(actual_game_path, game_id, galaxy_patch)
                if not patched_path:
                    raise RuntimeError("Failed to apply Galaxy gamepad patch")
                actual_game_path = patched_path
                self.update_progress(38, tr.get("progress_patch_applied"))
            else:
                self.update_progress(38, tr.get("progress_skipping_patch"))

            # Convert ISO to NFS (40-75%) - LONGEST OPERATION
            # Progress is handled inside convert_iso_to_nfs with incremental updates
            if not self.convert_iso_to_nfs(actual_game_path, system_type, options):
                raise RuntimeError("Failed to convert ISO to NFS")
            # Progress already set to 75% by convert_iso_to_nfs

            # Generate XML files (app.xml and meta.xml)
            if not self.generate_xml_files(title_name, title_id):
                raise RuntimeError("Failed to generate XML files")

            # Pack final (75-100%)
            if not self.pack_final(output_dir, common_key, title_name, title_id, game_id, options):
                raise RuntimeError("Failed to pack final package")

            # Cleanup temporary files
            self.cleanup_temp_files()

            return True

        except Exception as e:
            import traceback
            error_msg = f"Build failed: {str(e)}"
            self.update_progress(0, error_msg)

            # Print detailed error to console for debugging
            print("\n" + "="*80)
            print("BUILD ERROR:")
            print("="*80)
            print(error_msg)
            print("\nFull traceback:")
            traceback.print_exc()
            print("="*80 + "\n")

            return False

    def cleanup_temp_files(self):
        """Clean up temporary files to free disk space."""
        try:
            # Clean SOURCETEMP (ISO files, extracted directories)
            if self.paths.temp_source.exists():
                print(f"Cleaning temporary source files: {self.paths.temp_source}")
                for item in self.paths.temp_source.iterdir():
                    if item.is_file():
                        item.unlink()
                        print(f"  Removed: {item.name}")
                    elif item.is_dir():
                        shutil.rmtree(item, ignore_errors=True)
                        print(f"  Removed directory: {item.name}")
        except Exception as e:
            print(f"Warning: Could not clean all temporary files: {e}")
