"""Build engine for WiiVC Injector - calls external tools."""
import os
import subprocess
import shutil
import shlex
from pathlib import Path
from typing import Optional, Callable
from .translations import tr
from .translations import tr


class BuildEngine:
    """Handles the build process by calling external tools."""

    def __init__(self, paths_manager, progress_callback: Optional[Callable[[int, str], None]] = None, keep_temp_for_debug: bool = False, language: str = "en"):
        self.paths = paths_manager
        self.progress_callback = progress_callback
        self.keep_temp_for_debug = keep_temp_for_debug
        tr.set_language(language)

    def update_progress(self, percent: int, message: str):
        if self.progress_callback:
            self.progress_callback(percent, message)

    def verify_key(self, key: str) -> bool:
        key_clean = key.upper().replace("-", "").strip()
        return len(key_clean) == 32 and all(c in '0123456789ABCDEF' for c in key_clean)

    def run_tool(self, exe_path: Path, args: str, cwd: Optional[Path] = None, hide_window: bool = True) -> bool:
        try:
            cmd_list = [str(exe_path)] + shlex.split(args)
            startupinfo = None
            creation_flags = 0
            if hide_window and os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                creation_flags = 0x08000000

            print(f"\n{'='*80}")
            print(f"Running tool: {exe_path.name}")
            print(f"Command: {' '.join(cmd_list)}")
            print(f"Working directory: {cwd}")
            print(f"{ '='*80}")

            process = subprocess.Popen(
                cmd_list,
                shell=False,
                cwd=str(cwd) if cwd else None,
                startupinfo=startupinfo,
                creationflags=creation_flags,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            result_stdout, result_stderr = process.communicate()
            returncode = process.returncode

            if result_stdout:
                print(f"STDOUT:\n{result_stdout.strip()}")
            if result_stderr:
                print(f"STDERR:\n{result_stderr.strip()}")

            if returncode != 0:
                print(f"\n❌ Tool failed with exit code: {returncode}")
                if "System.IO.IOException" in result_stderr and "nuspacker.exe" in exe_path.name.lower():
                    print("⚠ Ignoring non-fatal cleanup error from NUSPacker.")
                    return True
                return False

            print(f"✓ Tool completed successfully")
            print(f"{ '='*80}\n")
            return True

        except Exception as e:
            print(f"\n❌ Exception running tool {exe_path.name}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def download_base_files(self, common_key: str, title_key: str) -> bool:
        self.update_progress(10, tr.get("progress_checking_base_files"))

        critical_file_map = {
            "cos.xml": "00050000101b0700", "frisbiiU.rpx": "00050000101b0700",
            "fw.img": "00050000101b0700", "fw.tmd": "00050000101b0700", "htk.bin": "00050000101b0700",
            "nn_hai_user.rpl": "00050000101b0700", "banner.gsh": "00050000101b0700",
            "fade.gsh": "00050000101b0700", "bootMovie.h264": "00050000101b0700",
            "bootLogoTex.tga": "00050000101b0700", "bootSound.btsnd": "00050000101b0700",
            "deint.txt": "0005001010004000", "font.bin": "0005001010004000"
        }

        project_cache = self.paths.base_files_cache
        missing_files = [f for f, t in critical_file_map.items() if not (project_cache / t / f).exists()]

        if not missing_files:
            print(f"✓ Base files found in project cache: {project_cache}")
            self.update_progress(40, "Base files ready (cached)")
            return True

        print(f"⚠ Missing {len(missing_files)} base files, downloading from Nintendo CDN...")
        self.update_progress(10, f"Downloading {len(missing_files)} files...")

        jnustool_exe = self.paths.temp_tools / "JAR" / "jnustool.exe"
        download_cache = self.paths.temp_downloads
        download_cache.mkdir(parents=True, exist_ok=True)
        (download_cache / "config").write_text(f"http://ccs.cdn.wup.shop.nintendo.net/ccs/download\n{common_key}\n")

        for filename in missing_files:
            title_id = critical_file_map[filename]
            key = title_key if title_id == "00050000101b0700" else None
            
            # JNUSTool needs to look for the full path, so we find it.
            # This is a bit of a hack because we don't have the full paths easily available.
            # We assume a standard structure.
            path_prefix = "code/" if not filename.endswith(('.gsh', '.h264', '.tga', '.btsnd')) else "meta/"
            if filename.endswith(('.gsh')): path_prefix = "content/assets/shaders/cafe/"
            
            jnus_path = f"/{path_prefix}{filename}"

            args = f"{title_id} -file {jnus_path}"
            if key:
                args = f"{title_id} {key} -file {jnus_path}"
            
            if not self.run_tool(jnustool_exe, args, cwd=download_cache):
                print(f"❌ Failed to download {jnus_path}")
                return False
            
            # After download, move to project cache
            src = download_cache / title_id / filename
            dst = project_cache / title_id / filename
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(src, dst)
        
        print(f"✓ Download complete and project cache populated.")
        return True

    def copy_base_files(self) -> bool:
        """Copy base files from cache to BUILDDIR, placing them in the correct subdirectories."""
        try:
            print("Copying base files from cache to build directory...")
            project_cache = self.paths.base_files_cache
            build_dir = self.paths.temp_build

            file_map = [
                ("00050000101b0700", "cos.xml", "code/cos.xml"),
                ("00050000101b0700", "frisbiiU.rpx", "code/frisbiiU.rpx"),
                ("00050000101b0700", "fw.img", "code/fw.img"),
                ("00050000101b0700", "fw.tmd", "code/fw.tmd"),
                ("00050000101b0700", "htk.bin", "code/htk.bin"),
                ("00050000101b0700", "nn_hai_user.rpl", "code/nn_hai_user.rpl"),
                ("00050000101b0700", "banner.gsh", "content/assets/shaders/cafe/banner.gsh"),
                ("00050000101b0700", "fade.gsh", "content/assets/shaders/cafe/fade.gsh"),
                ("00050000101b0700", "bootMovie.h264", "meta/bootMovie.h264"),
                ("00050000101b0700", "bootLogoTex.tga", "meta/bootLogoTex.tga"),
                ("00050000101b0700", "bootSound.btsnd", "meta/bootSound.btsnd"),
                ("0005001010004000", "deint.txt", "content/deint.txt"),
                ("0005001010004000", "font.bin", "content/font.bin"),
            ]
            
            missing_files = []
            for title_id, filename, dest_subpath in file_map:
                src = project_cache / title_id / filename
                if not src.exists():
                    missing_files.append(str(src))
                    continue
                dst = build_dir / dest_subpath
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

            if missing_files:
                print(f"❌ Critical files missing from cache: {missing_files}")
                return False

            print(f"✓ Copied {len(file_map)} base files to build directory.")
            return True
        except Exception as e:
            print(f"❌ Error copying base files: {e}")
            return False

    def convert_wbfs_to_iso(self, wbfs_path: Path) -> Path:
        """
        Convert WBFS to an ISO for processing using the original wbfs_file.exe tool.
        """
        wbfs_tool = self.paths.temp_tools / "EXE" / "wbfs_file.exe"
        final_iso = self.paths.temp_source / "game.iso"
        
        self.update_progress(15, "Converting WBFS to ISO...")
        
        # Arguments for wbfs_file.exe are: "INPUT" convert "OUTPUT"
        args = f'"{wbfs_path}" convert "{final_iso}"'
        if not self.run_tool(wbfs_tool, args):
            raise RuntimeError("Failed to convert WBFS to ISO using wbfs_file.exe.")

        if final_iso.exists():
            iso_size_mb = final_iso.stat().st_size / (1024 * 1024)
            print(f"✓ Converted WBFS to ISO: {final_iso} ({iso_size_mb:.2f} MB)")
            return final_iso
        raise RuntimeError("Failed to create final ISO from WBFS.")

    def convert_iso_to_nfs(self, iso_path: Path, system_type: str, options: dict) -> bool:
        """Convert ISO to NFS format."""
        self.update_progress(70, "Starting NFS conversion...")
        nfs_tool = self.paths.temp_tools / "EXE" / "nfs2iso2nfs.exe"
        build_content_dir = self.paths.temp_build / "content"
        build_content_dir.mkdir(parents=True, exist_ok=True)

        fw_img_src = self.paths.temp_build / "code" / "fw.img"
        fw_img_dst = build_content_dir / "fw.img"
        if not fw_img_src.exists():
            print("❌ fw.img not found in build/code, cannot proceed.")
            return False
            
        shutil.copy2(fw_img_src, fw_img_dst)

        try:
            args = "-enc"
            if system_type == "wii":
                if options.get("no_gamepad_emu"): args += " -nocc"
                elif options.get("wiimote_mode"):
                    args += " -wiimote"
                    if options.get("horizontal_wiimote"): args += " -horizontal"
                elif options.get("passthrough_mode"): args += " -passthrough"
                else: args += " -instantcc"
                if options.get("lr_patch"): args += " -lrpatch"
            elif system_type == "gcn": args += " -homebrew -passthrough"
            
            args += f' -iso "{iso_path}"'
            if not self.run_tool(nfs_tool, args, cwd=build_content_dir):
                return False
        finally:
            if fw_img_dst.exists(): fw_img_dst.unlink()

        self.update_progress(75, "NFS conversion complete.")
        return True

    def generate_xml_files(self, title_name: str, title_id: str, game_id: str) -> bool:
        """Generate app.xml and meta.xml from the definitive template."""
        try:
            import html
            safe_title = html.escape(title_name.strip())
            code_dir = self.paths.temp_build / "code"
            meta_dir = self.paths.temp_build / "meta"
            code_dir.mkdir(parents=True, exist_ok=True)
            meta_dir.mkdir(parents=True, exist_ok=True)

            if len(game_id) == 4 and game_id.isascii() and game_id.isalnum():
                group_id_hex = game_id.encode('ascii').hex().upper()
            else:
                group_id_hex = title_id[-8:] 

            app_xml = f"""<?xml version="1.0" encoding="utf-8"?>
<app type="complex" access="777">
  <version type="unsignedInt" length="4">16</version>
  <os_version type="hexBinary" length="8">000500101000400A</os_version>
  <title_id type="hexBinary" length="8">{title_id}</title_id>
  <title_version type="hexBinary" length="2">0000</title_version>
  <sdk_version type="unsignedInt" length="4">21204</sdk_version>
  <app_type type="hexBinary" length="4">8000002E</app_type>
  <group_id type="hexBinary" length="4">0000000F</group_id>
</app>"""
            (code_dir / "app.xml").write_text(app_xml, encoding='utf-8-sig')

            add_on_tags = '\n  '.join([f'<add_on_unique_id{i} type="hexBinary" length="4">00000000</add_on_unique_id{i}>' for i in range(32)])

            meta_xml = f"""<?xml version="1.0" encoding="utf-8"?>
<menu type="complex" access="777">
  <version type="unsignedInt" length="4">33</version>
  <product_code type="string" length="32">WUP-N-{game_id}</product_code>
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
  <drc_use type="unsignedInt" length="4">1</drc_use>
  <network_use type="unsignedInt" length="4">0</network_use>
  <online_account_use type="unsignedInt" length="4">0</online_account_use>
  <direct_boot type="unsignedInt" length="4">0</direct_boot>
  <reserved_flag0 type="hexBinary" length="4">00010001</reserved_flag0>
  <reserved_flag1 type="hexBinary" length="4">00080023</reserved_flag1>
  <reserved_flag2 type="hexBinary" length="4">{group_id_hex}</reserved_flag2>
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
  {add_on_tags}
</menu>"""
            (meta_dir / "meta.xml").write_text(meta_xml, encoding='utf-8-sig')
            
            print(f"✓ Generated app.xml and meta.xml")
            return True
        except Exception as e:
            print(f"❌ Error generating XML files: {e}")
            return False

    def pack_final(self, output_path: Path, common_key: str, title_id: str, game_id: str, options: dict = None) -> bool:
        """Pack final WUP package using NUSPacker."""
        print(f"\n{'='*80}")
        print(f"[PACK_FINAL] Starting NUSPacker packaging...")
        nuspacker_exe = self.paths.temp_tools / "JAR" / "nuspacker.exe"
        build_dir = self.paths.temp_build

        safe_name = game_id or "".join(c for c in title_id if c.isalnum() or c in " -_() ").strip()
        final_output = output_path / f"{safe_name}_WUP-N-{title_id}"
        if final_output.exists(): shutil.rmtree(final_output)
        output_path.mkdir(parents=True, exist_ok=True)
        
        args = f'-in "{build_dir}" -out "{final_output}" -encryptKeyWith {common_key}'
        if not self.run_tool(nuspacker_exe, args, cwd=self.paths.temp_root):
            if not (final_output / "title.tmd").exists():
                print(f"❌ NUSPacker failed to create essential files.")
                return False

        self.update_progress(90, tr.get("progress_verifying_output"))
        if not (final_output / "title.tmd").exists():
            print(f"❌ Final package incomplete.")
            return False

        print(f"✓ Build complete! Output: {final_output.name}")
        self.update_progress(95, f"Complete: {final_output.name}")
        return True

    def trim_iso(self, iso_path: Path) -> Path:
        """Extracts the data partition and rebuilds a minimal ISO to save space."""
        self.update_progress(35, tr.get("progress_trimming_iso"))
        wit_tool = self.paths.temp_tools / "WIT" / "wit.exe"
        
        extract_dir = self.paths.temp_source / "ISOEXTRACT"
        trimmed_iso_path = self.paths.temp_source / "game_trimmed.iso"

        try:
            # 1. Extract the data partition from the original ISO
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            
            # This extracts just the game files, discarding empty space and update partitions.
            extract_args = f'extract "{iso_path}" --dest "{extract_dir}" --psel data,-update'
            if not self.run_tool(wit_tool, extract_args):
                print("WARN: Failed to extract data for trimming. Will use original ISO. This may result in a large file size.")
                return iso_path # Fallback to the original ISO

            # 2. Rebuild a new, smaller ISO from the extracted files
            if trimmed_iso_path.exists():
                trimmed_iso_path.unlink()

            copy_args = f'copy "{extract_dir}" --dest "{trimmed_iso_path}" --iso'
            if not self.run_tool(wit_tool, copy_args):
                print("WARN: Failed to rebuild trimmed ISO. Will use original ISO. This may result in a large file size.")
                return iso_path # Fallback

            iso_size_mb = trimmed_iso_path.stat().st_size / (1024 * 1024)
            print(f"✓ ISO successfully trimmed to {iso_size_mb:.2f} MB")
            return trimmed_iso_path

        except Exception as e:
            print(f"ERROR: An exception occurred during ISO trimming: {e}")
            # Fallback to using the original ISO if trimming fails
            return iso_path
        finally:
            if extract_dir.exists():
                shutil.rmtree(extract_dir)

    def extract_rvlt_files(self, iso_path: Path) -> bool:
        """Extracts tmd.bin and ticket.bin from the Wii ISO, renaming them to rvlt.tmd and rvlt.tik."""
        self.update_progress(30, "Extracting Wii metadata (TMD and Ticket)...")
        wit_tool = self.paths.temp_tools / "WIT" / "wit.exe"
        code_dir = self.paths.temp_build / "code"
        extract_dir = self.paths.temp_source  # Extract directly into the source temp directory

        tmd_path = extract_dir / "tmd.bin"
        tik_path = extract_dir / "ticket.bin"

        # Clean up from previous runs just in case
        if tmd_path.exists(): tmd_path.unlink()
        if tik_path.exists(): tik_path.unlink()
        
        try:
            code_dir.mkdir(parents=True, exist_ok=True)

            # Extract to the root of the source temp directory. WIT shouldn't complain about this.
            args = f'extract "{iso_path}" --dest "{extract_dir}" --files +tmd.bin +ticket.bin -1'

            if not self.run_tool(wit_tool, args):
                print("WARN: wit.exe could not extract tmd.bin or ticket.bin. This may be okay for homebrew/custom ISOs.")
                return True

            if tmd_path.exists():
                shutil.move(tmd_path, code_dir / "rvlt.tmd")
                print("✓ Found and processed rvlt.tmd")
            
            if tik_path.exists():
                shutil.move(tik_path, code_dir / "rvlt.tik")
                print("✓ Found and processed rvlt.tik")
            
            return True

        except Exception as e:
            print(f"ERROR: An exception occurred during RVLT file extraction: {e}")
            return True # Not a fatal error
        finally:
            # Clean up originals if they still exist for some reason
            if tmd_path.exists():
                tmd_path.unlink()
            if tik_path.exists():
                tik_path.unlink()

    def build(self, game_path: Path, system_type: str, output_dir: Path,
              common_key: str, title_key: str,
              title_name: str, title_id: str, game_id: str, options: dict) -> bool:
        """Main build process."""
        try:
            if self.keep_temp_for_debug:
                print("--- DEBUG MODE: Temporary files will be kept. ---")
                self.paths.create_temp_directories() # Ensure directories exist even in debug mode
            else:
                print("Cleaning previous temporary files...")
                if self.paths.temp_root.exists(): # Check if temp_root exists
                    shutil.rmtree(self.paths.temp_root) # Delete it if it exists
                self.paths.create_temp_directories() # Recreate them after potential deletion

            self.update_progress(0, tr.get("progress_verifying_keys"))
            if not self.verify_key(common_key) or not self.verify_key(title_key):
                raise ValueError("Invalid Key format")
            
            print("Copying tools to temporary directory...")
            shutil.copytree(self.paths.project_root / "core", self.paths.temp_tools, dirs_exist_ok=True)

            # --- Title ID Modification based on options ---
            # This is critical to ensure different injects don't conflict
            if options.get("force_43"): title_id = title_id[:14] + "43"
            
            if not self.download_base_files(common_key, title_key):
                raise RuntimeError("Failed to download base files")

            self.update_progress(20, "Copying base files...")
            if not self.copy_base_files():
                raise RuntimeError("Failed to copy base files")

            self.update_progress(25, "Converting images...")
            if not self.convert_images_to_tga():
                raise RuntimeError("Failed to convert images")

            actual_game_path = game_path
            if str(game_path).lower().endswith(('.wbfs', '.nkit.iso')):
                iso_path = self.convert_wbfs_to_iso(game_path)
                actual_game_path = iso_path

            # If the game is a Wii game, trim the ISO to save space.
            # This replicates the logic from the original Teconmoon's Injector.
            if not options.get("disable_trimming", False) and system_type == "wii":
                actual_game_path = self.trim_iso(actual_game_path)
            
            if not self.extract_rvlt_files(actual_game_path):
                 print("Continuing build without rvlt files...")

            self.update_progress(40, "Converting game to NFS format...")
            if not self.convert_iso_to_nfs(actual_game_path, system_type, options):
                raise RuntimeError("Failed to convert ISO to NFS")

            self.update_progress(80, "Generating metadata files...")
            if not self.generate_xml_files(title_name, title_id, game_id):
                raise RuntimeError("Failed to generate XML files")

            self.update_progress(85, "Packing final installable package...")
            if not self.pack_final(output_dir, common_key, title_id, game_id, options):
                raise RuntimeError("Failed to pack final package")

            print(f"\n✓✓✓ BUILD SUCCESSFUL ✓✓✓")
            if self.keep_temp_for_debug:
                print(f"✓ Temporary files kept for inspection in {self.paths.temp_root}")
            else:
                self.cleanup_temp_files()
            return True

        except Exception as e:
            import traceback
            error_msg = f"Build failed: {str(e)}"
            self.update_progress(0, error_msg)
            print(f"\n{'='*80}\nBUILD ERROR:\n{'='*80}\n{error_msg}\n\nFull traceback:\n")
            traceback.print_exc()
            print("="*80 + "\n")
            return False
        
    def convert_images_to_tga(self) -> bool:
        """Convert PNG images to TGA format for meta files."""
        try:
            from PIL import Image
            meta_dir = self.paths.temp_build / "meta"
            meta_dir.mkdir(parents=True, exist_ok=True)
            for img_path, tga_name in [
                (self.paths.temp_icon, "iconTex.tga"),
                (self.paths.temp_banner, "bootTvTex.tga"),
                (self.paths.temp_drc, "bootDrcTex.tga"),
                (self.paths.temp_logo, "bootLogoTex.tga"),
            ]:
                if img_path.exists():
                    with Image.open(img_path) as img:
                        img.save(meta_dir / tga_name, 'TGA')
            return True
        except Exception as e:
            print(f"Error converting images to TGA: {e}")
            return False
        
    def cleanup_temp_files(self):
        """Clean up all temporary files."""
        if not self.keep_temp_for_debug:
            print("Cleaning up all temporary files...")
            shutil.rmtree(self.paths.temp_root, ignore_errors=True)
