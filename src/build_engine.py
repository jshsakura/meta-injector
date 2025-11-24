"""
WiiVC Injector Build Engine
Based on TeconMoon + UWUVCI logic for robust Wii game packaging.
"""
import os
import random
import shutil
import subprocess
from pathlib import Path
from typing import Callable, Optional
from .translations import tr


class BuildEngine:
    """
    Build engine combining TeconMoon's simplicity with UWUVCI's robustness.
    Properly handles TIK/TMD files and generates random IDs for multiple installs.
    """

    def __init__(self, paths_manager, progress_callback: Optional[Callable[[int, str], None]] = None, keep_temp_for_debug: bool = False, language: str = "en"):
        self.paths = paths_manager
        self.progress_callback = progress_callback
        self.keep_temp_for_debug = keep_temp_for_debug
        self.language = language
        self.generated_title_id = None
        self.generated_product_code = None
        self.should_stop = False

    def stop(self):
        """Request build to stop."""
        self.should_stop = True
        print("[STOP] Build cancellation requested")

    def check_stop(self):
        """Check if build should stop and raise exception if so."""
        if self.should_stop:
            raise RuntimeError("Build cancelled by user")

    def update_progress(self, percent: int, message: str):
        """Update progress callback."""
        self.check_stop()  # Check for cancellation
        if self.progress_callback:
            self.progress_callback(percent, message)

    def run_tool(self, exe_path: Path, args: str, cwd: Optional[Path] = None, timeout: int = 300) -> bool:
        """
        Run external tool (mimics TeconMoon's LaunchProgram()).

        Args:
            timeout: Timeout in seconds (default 300 = 5 minutes)
        """
        try:
            cmd = f'"{exe_path}" {args}'

            startupinfo = None
            creationflags = 0
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0  # SW_HIDE
                creationflags = subprocess.CREATE_NO_WINDOW

            print(f"\nRunning: {exe_path.name}")
            print(f"Command: {cmd}")

            result = subprocess.run(
                cmd,
                shell=True,
                cwd=str(cwd) if cwd else None,
                startupinfo=startupinfo,
                creationflags=creationflags,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout
            )

            if result.returncode != 0:
                print(f"Tool failed with code: {result.returncode}")
                if result.stderr:
                    print(f"Error: {result.stderr}")
                if result.stdout:
                    print(f"Output: {result.stdout}")
                return False

            if result.stdout:
                print(f"Output: {result.stdout[:500]}")  # Print first 500 chars
            print("Tool completed successfully\n")
            return True

        except subprocess.TimeoutExpired:
            print(f"Tool timed out after {timeout} seconds")
            return False
        except Exception as e:
            print(f"Exception running tool: {e}")
            return False

    def download_base_files(self, common_key: str, title_key: str) -> bool:
        """
        Download base files using JNUSTool (TeconMoon style - downloads individual files).
        Uses CommonApplicationData path like TeconMoon.
        """
        self.update_progress(10, tr.get("progress_checking_base_files"))

        # Use the same path as TeconMoon: %PROGRAMDATA%\JNUSToolDownloads\
        jnus_downloads = self.paths.jnustool_downloads
        jnus_downloads.mkdir(parents=True, exist_ok=True)

        # TeconMoon checks specific files with MD5 hashes
        # We'll check if key directories exist
        rhythm_heaven_folder = jnus_downloads / "Rhythm Heaven Fever [VAKE01]"
        vwii_folder = jnus_downloads / "0005001010004000"

        # Check for essential files
        essential_files = [
            vwii_folder / "code" / "deint.txt",
            vwii_folder / "code" / "font.bin",
            rhythm_heaven_folder / "code" / "cos.xml",
            rhythm_heaven_folder / "code" / "frisbiiU.rpx",
        ]

        all_exist = all(f.exists() for f in essential_files)

        if all_exist:
            print("[OK] Base files already downloaded")
            return True

        # Need to download - setup JNUSTool
        print("[DOWNLOAD] Base files not found, downloading from Nintendo...")
        self.update_progress(15, tr.get("progress_downloading_base"))

        jnustool_dir = self.paths.temp_tools / "JAR"
        config_path = jnustool_dir / "config"

        # Write config file (TeconMoon style)
        config_path.write_text(
            f"http://ccs.cdn.wup.shop.nintendo.net/ccs/download\n{common_key}\n"
        )

        jnustool_exe = jnustool_dir / "jnustool.exe"

        # TeconMoon downloads individual files, not entire titles
        # This prevents GUI popup and is faster
        files_to_download = [
            "0005001010004000 -file /code/deint.txt",
            "0005001010004000 -file /code/font.bin",
            f"00050000101b0700 {title_key} -file /code/cos.xml",
            f"00050000101b0700 {title_key} -file /code/frisbiiU.rpx",
            f"00050000101b0700 {title_key} -file /code/fw.img",
            f"00050000101b0700 {title_key} -file /code/fw.tmd",
            f"00050000101b0700 {title_key} -file /code/htk.bin",
            f"00050000101b0700 {title_key} -file /code/nn_hai_user.rpl",
            f"00050000101b0700 {title_key} -file /content/assets/shaders/cafe/banner.gsh",
            f"00050000101b0700 {title_key} -file /content/assets/shaders/cafe/fade.gsh",
            f"00050000101b0700 {title_key} -file /meta/bootMovie.h264",
            f"00050000101b0700 {title_key} -file /meta/bootLogoTex.tga",
            f"00050000101b0700 {title_key} -file /meta/bootSound.btsnd",
        ]

        total_files = len(files_to_download)
        for idx, args in enumerate(files_to_download, 1):
            print(f"[{idx}/{total_files}] Downloading file...")
            if not self.run_tool(jnustool_exe, args, cwd=jnustool_dir, timeout=120):
                config_path.unlink(missing_ok=True)
                print(f"[ERROR] Failed to download file: {args[:50]}...")
                return False

        # Move downloaded files to permanent location (TeconMoon does this)
        import shutil
        if (jnustool_dir / "Rhythm Heaven Fever [VAKE01]").exists():
            target = jnus_downloads / "Rhythm Heaven Fever [VAKE01]"
            if target.exists():
                shutil.rmtree(target)
            shutil.move(str(jnustool_dir / "Rhythm Heaven Fever [VAKE01]"), str(target))

        if (jnustool_dir / "0005001010004000").exists():
            target = jnus_downloads / "0005001010004000"
            if target.exists():
                shutil.rmtree(target)
            shutil.move(str(jnustool_dir / "0005001010004000"), str(target))

        config_path.unlink(missing_ok=True)
        print("[OK] Base files downloaded successfully")
        return True

    def copy_base_files(self) -> bool:
        """Copy base files from JNUSToolDownloads to build directory (TeconMoon style)."""
        self.update_progress(45, tr.get("progress_copying_base_files"))

        # TeconMoon uses the downloaded base directly from JNUSToolDownloads
        jnus_downloads = self.paths.jnustool_downloads
        rhythm_heaven = jnus_downloads / "Rhythm Heaven Fever [VAKE01]"

        if not rhythm_heaven.exists():
            print(f"Error: Base files not found at {rhythm_heaven}")
            print(f"Expected location: {jnus_downloads}")
            print("Please ensure base files were downloaded correctly.")
            return False

        print(f"[COPY] Copying base files from {rhythm_heaven}")
        shutil.copytree(rhythm_heaven, self.paths.temp_build, dirs_exist_ok=True)
        print("[OK] Base files copied successfully")
        return True

    def generate_random_ids(self) -> tuple:
        """
        Generate random Title ID and Product Code (UWUVCI style).
        Allows multiple versions of same game to be installed.
        """
        # Random Title ID: 00050002 + 8 hex digits
        random_id = f"{random.randint(0x3000, 0xFFFF):04X}{random.randint(0x3000, 0xFFFF):04X}"
        title_id = f"00050002{random_id}"

        # Random Product Code: 4 hex digits
        product_code = f"{random.randint(0x3000, 0xFFFF):04X}"

        print(f"Generated Title ID: {title_id}")
        print(f"Generated Product Code: {product_code}")

        return title_id, product_code

    def generate_meta_xml(self, title_name: str, iso_path: Path, drc_use: str = "1") -> bool:
        """
        Generate meta.xml (UWUVCI style - reads game code from ISO, random IDs).
        """
        self.update_progress(50, tr.get("progress_generating_meta"))

        import html
        safe_title = html.escape(title_name.strip())

        # Generate random IDs (UWUVCI style)
        title_id, product_code = self.generate_random_ids()
        self.generated_title_id = title_id
        self.generated_product_code = product_code

        # Read first 4 bytes from ISO (actual game code) - UWUVCI style
        with open(iso_path, 'rb') as f:
            game_code_bytes = f.read(4)
        game_code_hex = game_code_bytes.hex().upper()  # e.g., 5255554B for RUUK

        print(f"Read game code from ISO: {game_code_bytes.decode('ascii', errors='ignore')} ({game_code_hex})")

        # Group ID from product code
        group_id_hex = f"0000{product_code}"

        code_dir = self.paths.temp_build / "code"
        meta_dir = self.paths.temp_build / "meta"
        meta_dir.mkdir(exist_ok=True)

        # Generate app.xml
        app_xml = f"""<?xml version="1.0" encoding="utf-8"?><app type="complex" access="777"><version type="unsignedInt" length="4">16</version><os_version type="hexBinary" length="8">000500101000400A</os_version><title_id type="hexBinary" length="8">{title_id}</title_id><title_version type="hexBinary" length="2">0000</title_version><sdk_version type="unsignedInt" length="4">21204</sdk_version><app_type type="hexBinary" length="4">8000002E</app_type><group_id type="hexBinary" length="4">{group_id_hex}</group_id></app>"""
        (code_dir / "app.xml").write_text(app_xml, encoding='utf-8')

        # Generate meta.xml (UWUVCI style - reserved_flag2 from ISO game code!)
        meta_xml = f"""<?xml version="1.0" encoding="utf-8"?>
<menu type="complex" access="777">
  <version type="unsignedInt" length="4">33</version>
  <product_code type="string" length="32">WUP-N-{product_code}</product_code>
  <content_platform type="string" length="32">WUP</content_platform>
  <company_code type="string" length="8">0001</company_code>
  <mastering_date type="string" length="32"></mastering_date>
  <logo_type type="unsignedInt" length="4">0</logo_type>
  <app_launch_type type="hexBinary" length="4">00000000</app_launch_type>
  <invisible_flag type="hexBinary" length="4">00000000</invisible_flag>
  <no_managed_flag type="hexBinary" length="4">00000000</no_managed_flag>
  <no_event_log type="hexBinary" length="4">00000002</no_event_log>
  <no_icon_database type="hexBinary" length="4">00000000</no_icon_database>
  <launching_flag type="hexBinary" length="4">00000004</launching_flag>
  <install_flag type="hexBinary" length="4">00000000</install_flag>
  <closing_msg type="unsignedInt" length="4">0</closing_msg>
  <title_version type="unsignedInt" length="4">0</title_version>
  <title_id type="hexBinary" length="8">{title_id}</title_id>
  <group_id type="hexBinary" length="4">{group_id_hex}</group_id>
  <boss_id type="hexBinary" length="8">0000000000000000</boss_id>
  <os_version type="hexBinary" length="8">000500101000400A</os_version>
  <app_size type="hexBinary" length="8">0000000000000000</app_size>
  <common_save_size type="hexBinary" length="8">0000000000000000</common_save_size>
  <account_save_size type="hexBinary" length="8">0000000000000000</account_save_size>
  <common_boss_size type="hexBinary" length="8">0000000000000000</common_boss_size>
  <account_boss_size type="hexBinary" length="8">0000000000000000</account_boss_size>
  <save_no_rollback type="unsignedInt" length="4">0</save_no_rollback>
  <join_game_id type="hexBinary" length="4">00000000</join_game_id>
  <join_game_mode_mask type="hexBinary" length="8">0000000000000000</join_game_mode_mask>
  <bg_daemon_enable type="unsignedInt" length="4">0</bg_daemon_enable>
  <olv_accesskey type="unsignedInt" length="4">3921400692</olv_accesskey>
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
  <drc_use type="unsignedInt" length="4">{drc_use}</drc_use>
  <network_use type="unsignedInt" length="4">0</network_use>
  <online_account_use type="unsignedInt" length="4">0</online_account_use>
  <direct_boot type="hexBinary" length="4">00000000</direct_boot>
  <reserved_flag0 type="hexBinary" length="4">00010001</reserved_flag0>
  <reserved_flag1 type="hexBinary" length="4">00080023</reserved_flag1>
  <reserved_flag2 type="hexBinary" length="4">{game_code_hex}</reserved_flag2>
  <reserved_flag3 type="hexBinary" length="4">00000000</reserved_flag3>
  <reserved_flag4 type="hexBinary" length="4">00000000</reserved_flag4>
  <reserved_flag5 type="hexBinary" length="4">00000000</reserved_flag5>
  <reserved_flag6 type="hexBinary" length="4">00000003</reserved_flag6>
  <reserved_flag7 type="hexBinary" length="4">00000005</reserved_flag7>
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
  <shortname_ja type="string" length="512">{safe_title}</shortname_ja>
  <shortname_en type="string" length="512">{safe_title}</shortname_en>
  <shortname_fr type="string" length="512">{safe_title}</shortname_fr>
  <shortname_de type="string" length="512">{safe_title}</shortname_de>
  <shortname_it type="string" length="512">{safe_title}</shortname_it>
  <shortname_es type="string" length="512">{safe_title}</shortname_es>
  <shortname_zhs type="string" length="512">{safe_title}</shortname_zhs>
  <shortname_ko type="string" length="512">{safe_title}</shortname_ko>
  <shortname_nl type="string" length="512">{safe_title}</shortname_nl>
  <shortname_pt type="string" length="512">{safe_title}</shortname_pt>
  <shortname_ru type="string" length="512">{safe_title}</shortname_ru>
  <shortname_zht type="string" length="512">{safe_title}</shortname_zht>
  <publisher_ja type="string" length="256"></publisher_ja>
  <publisher_en type="string" length="256"></publisher_en>
  <publisher_fr type="string" length="256"></publisher_fr>
  <publisher_de type="string" length="256"></publisher_de>
  <publisher_it type="string" length="256"></publisher_it>
  <publisher_es type="string" length="256"></publisher_es>
  <publisher_zhs type="string" length="256"></publisher_zhs>
  <publisher_ko type="string" length="256"></publisher_ko>
  <publisher_nl type="string" length="256"></publisher_nl>
  <publisher_pt type="string" length="256"></publisher_pt>
  <publisher_ru type="string" length="256"></publisher_ru>
  <publisher_zht type="string" length="256"></publisher_zht>
  <add_on_unique_id0 type="hexBinary" length="4">00000000</add_on_unique_id0>
  <add_on_unique_id1 type="hexBinary" length="4">00000000</add_on_unique_id1>
  <add_on_unique_id2 type="hexBinary" length="4">00000000</add_on_unique_id2>
  <add_on_unique_id3 type="hexBinary" length="4">00000000</add_on_unique_id3>
  <add_on_unique_id4 type="hexBinary" length="4">00000000</add_on_unique_id4>
  <add_on_unique_id5 type="hexBinary" length="4">00000000</add_on_unique_id5>
  <add_on_unique_id6 type="hexBinary" length="4">00000000</add_on_unique_id6>
  <add_on_unique_id7 type="hexBinary" length="4">00000000</add_on_unique_id7>
  <add_on_unique_id8 type="hexBinary" length="4">00000000</add_on_unique_id8>
  <add_on_unique_id9 type="hexBinary" length="4">00000000</add_on_unique_id9>
  <add_on_unique_id10 type="hexBinary" length="4">00000000</add_on_unique_id10>
  <add_on_unique_id11 type="hexBinary" length="4">00000000</add_on_unique_id11>
  <add_on_unique_id12 type="hexBinary" length="4">00000000</add_on_unique_id12>
  <add_on_unique_id13 type="hexBinary" length="4">00000000</add_on_unique_id13>
  <add_on_unique_id14 type="hexBinary" length="4">00000000</add_on_unique_id14>
  <add_on_unique_id15 type="hexBinary" length="4">00000000</add_on_unique_id15>
  <add_on_unique_id16 type="hexBinary" length="4">00000000</add_on_unique_id16>
  <add_on_unique_id17 type="hexBinary" length="4">00000000</add_on_unique_id17>
  <add_on_unique_id18 type="hexBinary" length="4">00000000</add_on_unique_id18>
  <add_on_unique_id19 type="hexBinary" length="4">00000000</add_on_unique_id19>
  <add_on_unique_id20 type="hexBinary" length="4">00000000</add_on_unique_id20>
  <add_on_unique_id21 type="hexBinary" length="4">00000000</add_on_unique_id21>
  <add_on_unique_id22 type="hexBinary" length="4">00000000</add_on_unique_id22>
  <add_on_unique_id23 type="hexBinary" length="4">00000000</add_on_unique_id23>
  <add_on_unique_id24 type="hexBinary" length="4">00000000</add_on_unique_id24>
  <add_on_unique_id25 type="hexBinary" length="4">00000000</add_on_unique_id25>
  <add_on_unique_id26 type="hexBinary" length="4">00000000</add_on_unique_id26>
  <add_on_unique_id27 type="hexBinary" length="4">00000000</add_on_unique_id27>
  <add_on_unique_id28 type="hexBinary" length="4">00000000</add_on_unique_id28>
  <add_on_unique_id29 type="hexBinary" length="4">00000000</add_on_unique_id29>
  <add_on_unique_id30 type="hexBinary" length="4">00000000</add_on_unique_id30>
  <add_on_unique_id31 type="hexBinary" length="4">00000000</add_on_unique_id31>
</menu>"""

        (meta_dir / "meta.xml").write_text(meta_xml, encoding='utf-8')
        print("Generated meta.xml and app.xml")
        return True

    def convert_images_to_tga(self, icon_path: Path, banner_path: Path, drc_path: Optional[Path] = None, logo_path: Optional[Path] = None) -> bool:
        """
        Convert PNG images to TGA using png2tgacmd.exe (TeconMoon style).
        Uses temp directory to avoid overwriting source images.
        """
        self.update_progress(52, tr.get("progress_converting_images"))

        png_tool = self.paths.temp_tools / "IMG" / "png2tgacmd.exe"
        meta_dir = self.paths.temp_build / "meta"
        meta_dir.mkdir(exist_ok=True)

        # Create temporary image processing directory (UWUVCI style - don't touch source!)
        temp_img_dir = self.paths.temp_source / "IMGTEMP"
        if temp_img_dir.exists():
            shutil.rmtree(temp_img_dir)
        temp_img_dir.mkdir(exist_ok=True)

        # Icon: 128x128, 32bpp (convert to temp first, then move)
        args = f'-i "{icon_path}" -o "{temp_img_dir}" --width=128 --height=128 --tga-bpp=32 --tga-compression=none'
        if not self.run_tool(png_tool, args):
            return False

        # Banner: 1280x720, 24bpp
        args = f'-i "{banner_path}" -o "{temp_img_dir}" --width=1280 --height=720 --tga-bpp=24 --tga-compression=none'
        if not self.run_tool(png_tool, args):
            return False

        # DRC: 854x480, 24bpp (use banner if not specified)
        if drc_path is None:
            drc_path = banner_path
        args = f'-i "{drc_path}" -o "{temp_img_dir}" --width=854 --height=480 --tga-bpp=24 --tga-compression=none'
        if not self.run_tool(png_tool, args):
            return False

        # Logo: 170x42, 32bpp (optional)
        if logo_path and logo_path.exists():
            args = f'-i "{logo_path}" -o "{temp_img_dir}" --width=170 --height=42 --tga-bpp=32 --tga-compression=none'
            if not self.run_tool(png_tool, args):
                return False

        # Move converted TGA files to meta directory
        tga_files = list(temp_img_dir.glob("*.tga"))
        if not tga_files:
            print("[ERROR] No TGA files generated! Check png2tgacmd.exe")
            return False

        for tga_file in tga_files:
            dest = meta_dir / tga_file.name
            if dest.exists():
                dest.unlink()
            shutil.move(str(tga_file), str(dest))
            print(f"✓ Moved {tga_file.name} to meta/ (size: {dest.stat().st_size} bytes)")

        # Clean up temp directory
        shutil.rmtree(temp_img_dir)

        # Verify required TGA files exist
        required_tgas = ["iconTex.tga", "bootTvTex.tga", "bootDrcTex.tga"]
        for tga_name in required_tgas:
            tga_path = meta_dir / tga_name
            if not tga_path.exists():
                print(f"[ERROR] Required TGA file missing: {tga_name}")
                return False

        print("✓ Images converted to TGA successfully")
        return True

    def apply_galaxy_patch(self, extract_dir: Path, game_id: str, galaxy_variant: str) -> bool:
        """
        Apply Galaxy GCT patch to main.dol using wstrt.

        Args:
            extract_dir: Extracted game directory
            game_id: Game ID (e.g., RMGE01)
            galaxy_variant: 'allstars' or 'nvidia'

        Returns:
            True if successful
        """
        print(f"[GALAXY] Applying {galaxy_variant} patch to {game_id}...")

        # Find GCT file
        variant_name = "AllStars" if galaxy_variant == "allstars" else "Nvidia"
        gct_filename = f"{game_id}-{variant_name}.gct"
        gct_path = self.paths.project_root / "core" / "Galaxy1GamePad_v1.2" / gct_filename

        if not gct_path.exists():
            # Try without deflicker variant
            print(f"[GALAXY] GCT not found: {gct_path}")
            return False

        # Path to main.dol
        main_dol = extract_dir / "sys" / "main.dol"
        if not main_dol.exists():
            print(f"[GALAXY] main.dol not found: {main_dol}")
            return False

        # Apply patch using wstrt
        wstrt_exe = self.paths.temp_tools / "WIT" / "wstrt.exe"
        args = f'patch "{main_dol}" --add-section "{gct_path}"'

        if not self.run_tool(wstrt_exe, args):
            print("[GALAXY] Failed to apply GCT patch")
            return False

        print(f"✓ Galaxy {variant_name} patch applied successfully")
        return True

    def process_game_file(self, game_path: Path, disable_trimming: bool = False, galaxy_patch: str = None) -> Path:
        """
        Process game file (WBFS conversion, trimming) - UWUVCI style with proper WIT options.
        """
        self.update_progress(60, tr.get("progress_processing_game"))

        # Always copy/convert to pre.iso first (UWUVCI style)
        pre_iso = self.paths.temp_source / "pre.iso"

        # Convert WBFS to ISO if needed
        if str(game_path).lower().endswith('.wbfs'):
            self.update_progress(62, tr.get("progress_converting_wbfs"))
            wit_exe = self.paths.temp_tools / "WIT" / "wit.exe"
            # UWUVCI uses WIT for WBFS conversion
            args = f'copy --source "{game_path}" --dest "{pre_iso}" -I'
            if not self.run_tool(wit_exe, args):
                raise RuntimeError("WBFS conversion failed")
        else:
            # Copy ISO to pre.iso
            self.update_progress(62, tr.get("progress_copying_iso"))
            shutil.copy(game_path, pre_iso)

        wit_exe = self.paths.temp_tools / "WIT" / "wit.exe"
        extract_dir = self.paths.temp_source / "TEMP"

        if extract_dir.exists():
            shutil.rmtree(extract_dir)

        # Trim ISO if not disabled (UWUVCI style)
        if not disable_trimming:
            self.update_progress(65, tr.get("progress_trimming_iso"))

            # Extract with --psel WHOLE (UWUVCI trim mode)
            args = f'extract "{pre_iso}" --DEST "{extract_dir}" --psel WHOLE -vv1'
            if not self.run_tool(wit_exe, args):
                raise RuntimeError("WIT extract failed")

            # Apply Galaxy patch if specified
            if galaxy_patch:
                # Read game ID from extracted disc
                disc_header = extract_dir / "sys" / "boot.bin"
                if disc_header.exists():
                    with open(disc_header, 'rb') as f:
                        game_id = f.read(6).decode('ascii', errors='ignore')
                    self.apply_galaxy_patch(extract_dir, game_id, galaxy_patch)

            # Re-pack with --links --iso (UWUVCI style - preserves structure!)
            game_iso = self.paths.temp_source / "game.iso"
            args = f'copy "{extract_dir}" --DEST "{game_iso}" -ovv --links --iso'
            if not self.run_tool(wit_exe, args):
                raise RuntimeError("WIT copy failed")

            processed_path = game_iso
        else:
            # No trim: extract data only, then repack with --psel WHOLE
            self.update_progress(65, tr.get("progress_preparing_iso"))

            # Extract
            args = f'extract "{pre_iso}" --DEST "{extract_dir}" --psel data -vv1'
            if not self.run_tool(wit_exe, args):
                raise RuntimeError("WIT extract failed")

            # Apply Galaxy patch if specified
            if galaxy_patch:
                # Read game ID from extracted disc
                disc_header = extract_dir / "sys" / "boot.bin"
                if disc_header.exists():
                    with open(disc_header, 'rb') as f:
                        game_id = f.read(6).decode('ascii', errors='ignore')
                    self.apply_galaxy_patch(extract_dir, game_id, galaxy_patch)

            # Re-pack with --psel WHOLE (UWUVCI no-trim mode)
            game_iso = self.paths.temp_source / "game.iso"
            args = f'copy "{extract_dir}" --DEST "{game_iso}" -ovv --psel WHOLE --iso'
            if not self.run_tool(wit_exe, args):
                raise RuntimeError("WIT copy failed")

            processed_path = game_iso

        # Clean up
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        if pre_iso.exists():
            pre_iso.unlink()

        print(f"Game file processed: {processed_path}")
        return processed_path

    def extract_and_copy_tik_tmd(self, iso_path: Path) -> bool:
        """
        Extract TIK and TMD from ISO and copy to code folder (UWUVCI style).
        CRITICAL: Without this, WiiU shows "Corrupted Software" error!
        """
        self.update_progress(72, tr.get("progress_extracting_tik_tmd"))

        wit_exe = self.paths.temp_tools / "WIT" / "wit.exe"
        tiktmd_dir = self.paths.temp_source / "TIKTMD"

        # Clean up existing TIKTMD folder
        if tiktmd_dir.exists():
            shutil.rmtree(tiktmd_dir)

        # Extract tmd.bin and ticket.bin from ISO
        args = f'extract "{iso_path}" --psel data --files +tmd.bin --files +ticket.bin --DEST "{tiktmd_dir}" -vv1'
        if not self.run_tool(wit_exe, args):
            raise RuntimeError("Failed to extract TIK/TMD from ISO")

        code_dir = self.paths.temp_build / "code"

        # Delete existing rvlt.* files in code directory
        for rvlt_file in code_dir.glob("rvlt.*"):
            rvlt_file.unlink()
            print(f"✓ Deleted old file: {rvlt_file.name}")

        # Find and copy extracted files
        tmd_file = tiktmd_dir / "tmd.bin"
        tik_file = tiktmd_dir / "ticket.bin"

        if not tmd_file.exists():
            # Try searching in subdirectories
            tmd_files = list(tiktmd_dir.rglob("tmd.bin"))
            if tmd_files:
                tmd_file = tmd_files[0]
            else:
                raise RuntimeError("tmd.bin not found in extracted files")

        if not tik_file.exists():
            # Try searching in subdirectories
            tik_files = list(tiktmd_dir.rglob("ticket.bin"))
            if tik_files:
                tik_file = tik_files[0]
            else:
                raise RuntimeError("ticket.bin not found in extracted files")

        # Copy to code directory with correct names
        shutil.copy(tmd_file, code_dir / "rvlt.tmd")
        shutil.copy(tik_file, code_dir / "rvlt.tik")

        print(f"✓ Copied {tmd_file} -> code/rvlt.tmd")
        print(f"✓ Copied {tik_file} -> code/rvlt.tik")

        # Clean up temp directory
        shutil.rmtree(tiktmd_dir)

        print("✓ TIK and TMD extracted and copied successfully")
        return True

    def convert_iso_to_nfs(self, iso_path: Path, pad_option: str = "no_gamepad") -> bool:
        """
        Convert ISO to NFS format using nfs2iso2nfs.exe (TeconMoon style).
        """
        self.update_progress(70, tr.get("progress_converting_nfs"))

        nfs_tool = self.paths.temp_tools / "EXE" / "nfs2iso2nfs.exe"
        content_dir = self.paths.temp_build / "content"
        content_dir.mkdir(exist_ok=True)

        # Build args based on pad option (TeconMoon logic)
        args = "-enc"
        if pad_option == "no_gamepad":
            args += " -nocc"
        elif pad_option == "wiimote":
            args += " -wiimote"
        elif pad_option == "horizontal_wiimote":
            args += " -horizontal"
        elif pad_option in ("galaxy_allstars", "galaxy_nvidia"):
            # Galaxy patches use Classic Controller emulation
            args += " -instantcc"
        else:
            args += " -instantcc"

        if pad_option == "gamepad_lr":
            args += " -lrpatch"

        args += f' -iso "{iso_path}"'

        # Temporarily copy required files to content dir (TeconMoon uses JNUSToolDownloads)
        jnus_downloads = self.paths.jnustool_downloads
        temp_files_to_copy = [
            self.paths.temp_build / "code" / "fw.img",
            jnus_downloads / "0005001010004000" / "code" / "deint.txt",
            jnus_downloads / "0005001010004000" / "code" / "font.bin"
        ]

        try:
            for f in temp_files_to_copy:
                if f.exists():
                    shutil.copy(f, content_dir)

            if not self.run_tool(nfs_tool, args, cwd=content_dir):
                return False
        finally:
            # Clean up temp files
            for f in temp_files_to_copy:
                temp_file = content_dir / f.name
                if temp_file.exists():
                    temp_file.unlink()

        print("NFS conversion complete")
        return True

    def pack_final(self, output_dir: Path, common_key: str, game_id: str) -> bool:
        """
        Pack final WUP using NUSPacker (uses generated random IDs).
        """
        self.update_progress(85, tr.get("progress_packing_wup"))

        nuspacker_exe = self.paths.temp_tools / "JAR" / "nuspacker.exe"
        build_dir = self.paths.temp_build

        # Use generated IDs
        title_id = self.generated_title_id
        product_code = self.generated_product_code

        if not title_id or not product_code:
            raise RuntimeError("Title ID and Product Code not generated")

        # Use game ID as folder name (short and simple)
        final_output = output_dir / game_id

        args = f'-in "{build_dir}" -out "{final_output}" -encryptKeyWith {common_key}'

        if not self.run_tool(nuspacker_exe, args, cwd=self.paths.temp_root):
            return False

        # Verify output
        if not (final_output / "title.tmd").exists():
            print("Error: Final package incomplete")
            return False

        print(f"✓ Final package created at: {final_output}")
        print(f"  Title ID: {title_id}")
        print(f"  Product Code: WUP-N-{product_code}")
        return True

    def build(self, game_path: Path, output_dir: Path, common_key: str, title_key: str,
              title_name: str, options: dict, system_type: str = "wii") -> bool:
        """
        Main build process (UWUVCI-enhanced flow with proper TIK/TMD handling).

        Args:
            system_type: 'wii' or 'gc' (GameCube)
        """
        try:
            # Setup
            self.system_type = system_type  # Store for use in other methods
            self.update_progress(0, tr.get("progress_initializing"))
            print("\n" + "="*80)
            print(f"WiiVC Injector - Enhanced Build Process ({'GameCube' if system_type == 'gc' else 'Wii'})")
            print("="*80 + "\n")

            # Clean temp directories first (important for consecutive builds)
            # Only preserve permanent cache folders (IMAGECACHE, BASECACHE)
            if self.paths.temp_root.exists():
                print("[CLEANUP] Removing previous temp files...")
                preserve_folders = {"IMAGECACHE", "BASECACHE"}
                for item in self.paths.temp_root.iterdir():
                    if item.name not in preserve_folders:
                        if item.is_dir():
                            shutil.rmtree(item, ignore_errors=True)
                        else:
                            item.unlink(missing_ok=True)

            self.paths.create_temp_directories()
            # Ensure cache directories exist
            self.paths.images_cache.mkdir(parents=True, exist_ok=True)
            self.paths.base_cache.mkdir(parents=True, exist_ok=True)

            # Copy images from cache to temp AFTER cleanup
            print("[IMAGE] Copying images from cache...")
            cache_icon = options.get("cache_icon_path")
            cache_banner = options.get("cache_banner_path")
            cache_drc = options.get("cache_drc_path")

            if cache_icon and cache_icon.exists():
                shutil.copy2(cache_icon, self.paths.temp_icon)
                print(f"  ✓ Icon copied: {cache_icon} -> {self.paths.temp_icon}")

            if cache_banner and cache_banner.exists():
                shutil.copy2(cache_banner, self.paths.temp_banner)
                print(f"  ✓ Banner copied: {cache_banner} -> {self.paths.temp_banner}")

            if cache_drc and cache_drc.exists():
                shutil.copy2(cache_drc, self.paths.temp_drc)
                print(f"  ✓ DRC copied: {cache_drc} -> {self.paths.temp_drc}")

            # Copy core tools to temp (fresh copy for each build)
            print("[SETUP] Copying core tools...")
            shutil.copytree(self.paths.project_root / "core", self.paths.temp_tools, dirs_exist_ok=True)

            # Download base files
            if not self.download_base_files(common_key, title_key):
                raise RuntimeError("Failed to download base files")

            # Copy base files
            if not self.copy_base_files():
                raise RuntimeError("Failed to copy base files")

            # Process game FIRST (need ISO to read game code for meta.xml)
            processed_iso = self.process_game_file(
                game_path,
                options.get("disable_trimming", False),
                options.get("galaxy_patch")
            )

            # Extract game ID from ISO for output folder name
            with open(processed_iso, 'rb') as f:
                game_id = f.read(6).decode('ascii', errors='ignore')  # e.g., RUUK01

            # Add prefix based on controller option
            pad_option = options.get("pad_option", "none")
            prefix_map = {
                "no_gamepad": "NOGP_",
                "none": "GP_",
                "gamepad_lr": "GPLR_",
                "wiimote": "WM_",
                "horizontal_wiimote": "HWM_",
                "passthrough": "PT_",
                "galaxy_allstars": "GALA_",
                "galaxy_nvidia": "GALN_"
            }
            prefix = prefix_map.get(pad_option, "")
            game_id_with_prefix = f"{prefix}{game_id}"

            # Generate XML (reads game code from processed ISO, generates random IDs)
            drc_use = "65537" if options.get("pad_option", "no_gamepad") != "no_gamepad" else "1"
            if not self.generate_meta_xml(title_name, processed_iso, drc_use):
                raise RuntimeError("Failed to generate meta.xml")

            # Convert images (uses temp directory to protect source images)
            if not self.convert_images_to_tga(
                options.get("icon_path"),
                options.get("banner_path"),
                options.get("drc_path"),
                options.get("logo_path")
            ):
                raise RuntimeError("Failed to convert images")

            # CRITICAL: Extract TIK/TMD from ISO BEFORE NFS conversion
            if not self.extract_and_copy_tik_tmd(processed_iso):
                raise RuntimeError("Failed to extract TIK/TMD - game will show as corrupted!")

            # Convert to NFS
            if not self.convert_iso_to_nfs(processed_iso, options.get("pad_option", "no_gamepad")):
                raise RuntimeError("Failed to convert to NFS")

            # Pack final (uses game ID with prefix as folder name)
            if not self.pack_final(output_dir, common_key, game_id_with_prefix):
                raise RuntimeError("Failed to pack WUP")

            self.update_progress(100, tr.get("progress_build_successful"))
            print("\n" + "="*80)
            print("✓ BUILD SUCCESSFUL!")
            print("="*80)
            print(f"Title: {title_name}")
            print(f"Title ID: {self.generated_title_id}")
            print(f"Product Code: WUP-N-{self.generated_product_code}")
            print("="*80 + "\n")
            return True

        except Exception as e:
            print(f"\n" + "="*80)
            print("✗ BUILD FAILED")
            print("="*80)
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            print("="*80 + "\n")
            return False
