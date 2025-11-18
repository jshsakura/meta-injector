"""Build engine for WiiVC Injector - calls external tools."""
import os
import subprocess
import shutil
import hashlib
from pathlib import Path
from typing import Optional, Callable


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
                text=True
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

    def run_tool(self, exe_path: Path, args: str, cwd: Optional[Path] = None, hide_window: bool = True) -> bool:
        """
        Run external tool.

        Args:
            exe_path: Path to executable
            args: Command line arguments
            cwd: Working directory
            hide_window: Hide command window

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

            result = subprocess.run(
                cmd,
                shell=True,
                cwd=str(cwd) if cwd else None,
                startupinfo=startupinfo,
                capture_output=True,
                text=True
            )

            if result.stdout:
                print(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                print(f"STDERR:\n{result.stderr}")

            if result.returncode != 0:
                print(f"\n❌ Tool failed with exit code: {result.returncode}")
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

        # Define critical files (relative paths)
        critical_file_paths = [
            # vWii system files
            ("0005001010004000", "deint.txt"),
            ("0005001010004000", "font.bin"),
            ("0005001010004001", "c2w.img"),
            ("0005001010004001", "boot.bin"),
            ("0005001010004001", "dmcu.d.hex"),
            # Rhythm Heaven base files
            ("00050000101b0700", "cos.xml"),
            ("00050000101b0700", "frisbiiU.rpx"),
            ("00050000101b0700", "fw.img"),
            ("00050000101b0700", "fw.tmd"),
            ("00050000101b0700", "htk.bin"),
            ("00050000101b0700", "nn_hai_user.rpl"),
            ("00050000101b0700", "bootMovie.h264"),
            ("00050000101b0700", "bootLogoTex.tga"),
            ("00050000101b0700", "bootSound.btsnd"),
        ]

        # Check project-local cache first (most reliable)
        local_cache = self.paths.base_files_cache
        local_files = [(local_cache / title_id / filename) for title_id, filename in critical_file_paths]
        local_missing = [f for f in local_files if not f.exists()]

        if not local_missing:
            print(f"✓ Base files found in project cache: {local_cache}")
            print(f"✓ Verified {len(local_files)} files")
            self.update_progress(40, "Base files ready (cached)")
            return True

        # Check JNUSTool downloads directory
        jnustool_cache = self.paths.jnustool_downloads
        jnustool_files = [(jnustool_cache / title_id / filename) for title_id, filename in critical_file_paths]
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

        # Files to download
        downloads = [
            ("0005001010004000", None, "/code/deint.txt"),
            ("0005001010004000", None, "/code/font.bin"),
            ("0005001010004001", None, "/code/c2w.img"),
            ("0005001010004001", None, "/code/boot.bin"),
            ("0005001010004001", None, "/code/dmcu.d.hex"),
            ("00050000101b0700", title_key, "/code/cos.xml"),
            ("00050000101b0700", title_key, "/code/frisbiiU.rpx"),
            ("00050000101b0700", title_key, "/code/fw.img"),
            ("00050000101b0700", title_key, "/code/fw.tmd"),
            ("00050000101b0700", title_key, "/code/htk.bin"),
            ("00050000101b0700", title_key, "/code/nn_hai_user.rpl"),
            ("00050000101b0700", title_key, "/content/assets/shaders/cafe/banner.gsh"),
            ("00050000101b0700", title_key, "/content/assets/shaders/cafe/fade.gsh"),
            ("00050000101b0700", title_key, "/meta/bootMovie.h264"),
            ("00050000101b0700", title_key, "/meta/bootLogoTex.tga"),
            ("00050000101b0700", title_key, "/meta/bootSound.btsnd"),
        ]

        # Use jnustool.exe (IKVM compiled version)
        jnustool_exe = jnustool_dir / "jnustool.exe"
        if not jnustool_exe.exists():
            print(f"ERROR: jnustool.exe not found at {jnustool_exe}")
            return False

        # Only download missing files
        downloaded_count = 0
        for title_id, key, file_path in downloads:
            args = f"{title_id}"
            if key:
                args += f" {key}"
            args += f" -file {file_path}"

            if not self.run_tool(jnustool_exe, args, cwd=jnustool_dir):
                print(f"Failed to download {file_path}")
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
        self.update_progress(70, "Converting game to NFS format...")

        nfs_tool = self.paths.temp_tools / "EXE" / "nfs2iso2nfs.exe"
        output_dir = self.paths.temp_build / "content"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build arguments based on system type
        args = "-enc"

        if system_type == "wii":
            if options.get("disable_passthrough"):
                args += " -passthrough"
            if options.get("lr_patch"):
                args += " -lrpatch"
        elif system_type == "gcn":
            args += " -homebrew -passthrough"
        elif system_type in ["dol", "wiiware"]:
            args += " -homebrew"
            if not options.get("disable_passthrough"):
                args += " -passthrough"
            if options.get("lr_patch"):
                args += " -lrpatch"

        args += f' -iso "{iso_path}"'

        return self.run_tool(nfs_tool, args, cwd=output_dir)

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

            # Copy code files
            code_files = [
                (cache_dir / "0005001010004000" / "deint.txt", build_code / "deint.txt"),
                (cache_dir / "0005001010004000" / "font.bin", build_code / "font.bin"),
                (cache_dir / "0005001010004001" / "c2w.img", build_code / "c2w.img"),
                (cache_dir / "0005001010004001" / "boot.bin", build_code / "boot.bin"),
                (cache_dir / "0005001010004001" / "dmcu.d.hex", build_code / "dmcu.d.hex"),
                (cache_dir / "00050000101b0700" / "cos.xml", build_code / "cos.xml"),
                (cache_dir / "00050000101b0700" / "frisbiiU.rpx", build_code / "frisbiiU.rpx"),
                (cache_dir / "00050000101b0700" / "fw.img", build_code / "fw.img"),
                (cache_dir / "00050000101b0700" / "fw.tmd", build_code / "fw.tmd"),
                (cache_dir / "00050000101b0700" / "htk.bin", build_code / "htk.bin"),
                (cache_dir / "00050000101b0700" / "nn_hai_user.rpl", build_code / "nn_hai_user.rpl"),
            ]

            copied = 0
            for src, dst in code_files:
                if src.exists():
                    shutil.copy2(src, dst)
                    copied += 1
                else:
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

            print(f"✓ Copied {copied} base files from cache to build directory")
            return True

        except Exception as e:
            print(f"Error copying base files: {e}")
            import traceback
            traceback.print_exc()
            return False

    def pack_final(self, output_path: Path, common_key: str, title_name: str, title_id: str) -> bool:
        """
        Pack final WUP package using NUSPacker.

        Args:
            output_path: Output directory
            common_key: Wii U Common Key
            title_name: Game title
            title_id: Title ID

        Returns:
            True if successful
        """
        self.update_progress(85, "Encrypting and packing final package...")

        nuspacker_exe = self.paths.temp_tools / "JAR" / "nuspacker.exe"

        # Sanitize filename
        safe_name = "".join(c if c.isalnum() or c in " -_()" else "_" for c in title_name)
        final_output = output_path / f"{safe_name}_WUP-N-{title_id}"

        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)

        args = f'-in "{self.paths.temp_build}" -out "{final_output}" -encryptKeyWith {common_key}'

        if not self.run_tool(nuspacker_exe, args, cwd=self.paths.temp_root):
            print("❌ NUSPacker failed")
            return False

        # Verify output files were created
        if not final_output.exists():
            print(f"❌ Output directory not created: {final_output}")
            return False

        # Check for essential files
        output_files = list(final_output.rglob("*"))
        if len(output_files) == 0:
            print(f"❌ No files generated in output: {final_output}")
            return False

        print(f"✓ Build complete! Generated {len(output_files)} files")
        print(f"✓ Output location: {final_output}")
        self.update_progress(100, f"Build complete! Output: {final_output.name}")
        return True

    def build(self, game_path: Path, system_type: str, output_dir: Path,
              common_key: str, title_key: str,
              title_name: str, title_id: str, options: dict) -> bool:
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
            # Verify keys
            self.update_progress(0, "Verifying encryption keys...")

            if not self.verify_key(common_key):
                raise ValueError("Invalid Wii U Common Key (must be 32 hex characters)")

            if not self.verify_key(title_key):
                raise ValueError("Invalid Title Key (must be 32 hex characters)")

            # Download base files
            if not self.download_base_files(common_key, title_key):
                raise RuntimeError("Failed to download base files")

            # Copy base files to build directory
            self.update_progress(50, "Copying base files...")
            if not self.copy_base_files():
                raise RuntimeError("Failed to copy base files")

            # Convert images to TGA
            self.update_progress(60, "Converting images to TGA...")
            if not self.convert_images_to_tga():
                raise RuntimeError("Failed to convert images")

            # Convert ISO to NFS
            if not self.convert_iso_to_nfs(game_path, system_type, options):
                raise RuntimeError("Failed to convert ISO to NFS")

            # Pack final
            if not self.pack_final(output_dir, common_key, title_name, title_id):
                raise RuntimeError("Failed to pack final package")

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
