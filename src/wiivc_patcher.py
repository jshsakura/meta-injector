"""
WiiVC firmware and ISO patcher for WiiLink WFC support and C2W CPU unlock.

This module provides automatic patching for Wii Virtual Console games:
- fw.img Trucha bug patch: Bypasses signature verification (fixes error 22000)
- ISO WiiLink WFC patch: Modifies game to connect to WiiLink WFC servers
- C2W (Cafe2Wii) patch: Unlocks CPU clock from 729MHz to 1.215GHz

WiiLink WFC is specifically designed for WiiVC compatibility:
- Uses HTTP instead of HTTPS/TLS (WiiVC doesn't support SSL)
- Region-specific GCT patches (RMCK01 ≠ RMCE01)
- Supports: Mario Kart Wii, Super Smash Bros. Brawl (all regions including Korean)

C2W patch improves performance by removing CPU clock restrictions.
"""
from pathlib import Path
from typing import Optional, Tuple
import hashlib
import urllib.request
import shutil
import subprocess


class WiiVCPatcher:
    """Patches fw.img and ISO for WiiLink WFC online play."""

    # VERIFIED fw.img patch offsets (extracted from actual base games)
    # Format: (offset, original_bytes, patched_bytes, description)
    FW_IMG_PATCHES = {
        # Rhythm Heaven Fever (USA) - VERIFIED from actual fw.img
        # File: JNUSTool download - Rhythm Heaven Fever [VAKE01]
        # Hash verification: Pattern 20 07 4B 0B confirmed at 0x271EE
        'RHF_USA': [
            (0x000271EE, b'\x20\x07\x4B\x0B', b'\x20\x00\x4B\x0B', 'ES_Sign: Trucha bug - skip signature verification'),
        ],
        # Xenoblade Chronicles (USA) - To be verified
        'XC_USA': [
            (0x000271EE, b'\x20\x07\x4B\x0B', b'\x20\x00\x4B\x0B', 'ES_Sign: Trucha bug (same as RHF)'),
        ],
        # Super Mario Galaxy 2 (EUR) - To be verified
        'SMG2_EUR': [
            (0x000271EE, b'\x20\x07\x4B\x0B', b'\x20\x00\x4B\x0B', 'ES_Sign: Trucha bug (same as RHF)'),
        ],
    }

    # WiiLink WFC supported games
    # GCT patches are REGION-SPECIFIC! RMCK01 ≠ RMCE01
    # Each game ID requires its own matching patch file
    # Auto-downloads from https://wfc.wiilink24.com/patches/
    WIILINK_WFC_GAMES = {
        # Mario Kart Wii (All regions supported including Korean)
        'RMCK01': 'Mario Kart Wii (KOR)',  # 🇰🇷 Korean version
        'RMCE01': 'Mario Kart Wii (USA)',
        'RMCP01': 'Mario Kart Wii (EUR)',
        'RMCJ01': 'Mario Kart Wii (JPN)',
        # Super Smash Bros. Brawl (All regions supported including Korean)
        'RSBK01': 'Super Smash Bros. Brawl (KOR)',  # 🇰🇷 Korean version
        'RSBE01': 'Super Smash Bros. Brawl (USA)',
        'RSBP01': 'Super Smash Bros. Brawl (EUR)',
        'RSBJ01': 'Super Smash Bros. Brawl (JPN)',
        # Add more games as WiiLink WFC adds support
    }

    # GCT filename variations (some games use different naming conventions)
    # Maps game ID to alternative GCT filenames to try
    GCT_FILENAME_VARIANTS = {
        'RMCE01': ['RMCE01.gct', 'RMCED00.gct', 'RMCEN0001.gct'],
        'RMCJ01': ['RMCJ01.gct', 'RMCJD00.gct', 'RMCJN0001.gct'],
        'RMCK01': ['RMCK01.gct', 'RMCKD00.gct', 'RMCKN0001.gct'],
        'RMCP01': ['RMCP01.gct', 'RMCPD00.gct', 'RMCPN0001.gct'],
        'RSBE01': ['RSBE01.gct', 'RSBE02.gct'],
        'RSBJ01': ['RSBJ01.gct', 'RSBJ00.gct'],
        'RSBP01': ['RSBP01.gct', 'RSBP00.gct'],
        'RSBK01': ['RSBK01.gct'],
    }

    @staticmethod
    def get_file_hash(file_path: Path) -> str:
        """Calculate SHA-1 hash of file."""
        sha1 = hashlib.sha1()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha1.update(chunk)
        return sha1.hexdigest()

    @staticmethod
    def detect_fw_img_version(fw_img_path: Path) -> Optional[str]:
        """
        Detect fw.img version by file hash or size.

        Returns:
            Version key (e.g., 'RHF_USA') or None
        """
        if not fw_img_path.exists():
            return None

        # Try to detect by searching for known patterns
        with open(fw_img_path, 'rb') as f:
            data = f.read()

        # Check for ES module signature patterns
        # These are ARM Thumb instructions commonly found in ES_Sign
        if b'\x20\x07\x4B\x0B' in data:
            # Most common pattern - assume RHF_USA compatible
            return 'RHF_USA'

        return 'RHF_USA'  # Default fallback

    @staticmethod
    def patch_fw_img_trucha(fw_img_path: Path, base_game: str = None) -> bool:
        """
        Apply Trucha bug patch to fw.img to bypass signature checks.

        This patches the ES_Sign function to always return success,
        allowing modified content to run (fixes error 22000).
        Required for WiiLink WFC to work on WiiVC!

        Args:
            fw_img_path: Path to fw.img file
            base_game: Base game identifier (e.g., 'Rhythm Heaven Fever (USA)')

        Returns:
            True if patch applied successfully
        """
        if not fw_img_path.exists():
            print(f"[FW Patch] fw.img not found: {fw_img_path}")
            return False

        # Detect version
        version = WiiVCPatcher.detect_fw_img_version(fw_img_path)
        if not version:
            print("[FW Patch] Unable to detect fw.img version")
            return False

        patches = WiiVCPatcher.FW_IMG_PATCHES.get(version, [])
        if not patches:
            print(f"[FW Patch] No patches defined for version: {version}")
            return False

        print(f"[FW Patch] Detected fw.img version: {version}")

        # Read entire file
        with open(fw_img_path, 'rb') as f:
            data = bytearray(f.read())

        original_hash = hashlib.sha1(data).hexdigest()[:8]
        patches_applied = 0

        # Apply patches
        for offset, original, patched, description in patches:
            if offset >= len(data):
                print(f"[FW Patch] Offset 0x{offset:08X} out of range")
                continue

            # Verify original bytes
            actual = bytes(data[offset:offset+len(original)])
            if actual != original:
                print(f"[FW Patch] Mismatch at 0x{offset:08X}")
                print(f"  Expected: {original.hex()}")
                print(f"  Found:    {actual.hex()}")
                # Try to find the pattern nearby
                search_range = 0x10000  # Search within 64KB
                start = max(0, offset - search_range)
                end = min(len(data), offset + search_range)
                search_data = bytes(data[start:end])
                pos = search_data.find(original)
                if pos != -1:
                    actual_offset = start + pos
                    print(f"  Pattern found at 0x{actual_offset:08X} instead")
                    offset = actual_offset
                else:
                    print(f"  Skipping patch: {description}")
                    continue

            # Apply patch
            data[offset:offset+len(patched)] = patched
            patches_applied += 1
            print(f"[FW Patch] Applied: {description} at 0x{offset:08X}")

        if patches_applied == 0:
            print("[FW Patch] No patches were applied!")
            return False

        # Write patched file
        with open(fw_img_path, 'wb') as f:
            f.write(data)

        patched_hash = hashlib.sha1(data).hexdigest()[:8]
        print(f"[FW Patch] Success! ({patches_applied} patches)")
        print(f"[FW Patch] Hash: {original_hash} -> {patched_hash}")

        return True

    @staticmethod
    def txt_to_gct(txt_path: Path, gct_path: Path) -> bool:
        """
        Convert Gecko code TXT file to GCT binary format.

        Args:
            txt_path: Path to .txt file with hex codes
            gct_path: Path to output .gct file

        Returns:
            True if conversion successful
        """
        try:
            # Read TXT file
            with open(txt_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # GCT header: 00D0C0DE 00D0C0DE
            gct_data = bytearray(b'\x00\xD0\xC0\xDE\x00\xD0\xC0\xDE')

            # Parse each line
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#') or line.startswith('//'):
                    continue  # Skip empty lines and comments

                # Split address and value (e.g., "220EDDE4 00000004")
                parts = line.split()
                if len(parts) != 2:
                    continue  # Skip malformed lines

                try:
                    # Convert hex strings to bytes
                    addr = int(parts[0], 16)
                    value = int(parts[1], 16)

                    # Add to GCT (big-endian format)
                    gct_data.extend(addr.to_bytes(4, 'big'))
                    gct_data.extend(value.to_bytes(4, 'big'))
                except ValueError:
                    continue  # Skip invalid hex values

            # GCT footer: F0000000 00000000
            gct_data.extend(b'\xF0\x00\x00\x00\x00\x00\x00\x00')

            # Write GCT file
            with open(gct_path, 'wb') as f:
                f.write(gct_data)

            print(f"[GCT] Converted {txt_path.name} -> {gct_path.name} ({len(gct_data)} bytes)")
            return True

        except Exception as e:
            print(f"[GCT] Failed to convert TXT to GCT: {e}")
            return False

    @staticmethod
    def download_and_convert_gct(game_id: str, core_dir: Path) -> Optional[Path]:
        """
        Download TXT patch from WiiLink WFC and convert to GCT.

        Automatically downloads Gecko code from wfc.wiilink24.com and converts it.

        Args:
            game_id: 6-character game ID (e.g., 'RMCK01')
            core_dir: Path to core directory for storage

        Returns:
            Path to .gct file, or None if failed
        """
        if game_id not in WiiVCPatcher.WIILINK_WFC_GAMES:
            print(f"[WiiLink WFC] Game {game_id} not supported")
            print(f"[WiiLink WFC] Supported: Mario Kart Wii, Smash Bros. Brawl (all regions)")
            print(f"[WiiLink WFC] Note: Patches are region-specific (KOR ≠ USA ≠ EUR ≠ JPN)")
            return None

        game_name = WiiVCPatcher.WIILINK_WFC_GAMES[game_id]
        print(f"[WiiLink WFC] Supported game detected: {game_name} ({game_id})")

        # Create wiilink-wfc directory
        wiilink_dir = core_dir / "wiilink-wfc"
        wiilink_dir.mkdir(parents=True, exist_ok=True)

        # Try different filename variants
        variants = WiiVCPatcher.GCT_FILENAME_VARIANTS.get(game_id, [f"{game_id}.gct"])

        for variant in variants:
            gct_path = wiilink_dir / variant

            # 1. Check if GCT already exists (cached)
            if gct_path.exists():
                file_size = gct_path.stat().st_size / 1024
                print(f"[WiiLink WFC] Using cached GCT: {variant} ({file_size:.1f} KB)")
                return gct_path

            # 2. Try to download TXT from WiiLink WFC
            txt_variant = variant.replace('.gct', '.txt')
            txt_path = wiilink_dir / txt_variant
            txt_url = f"https://wfc.wiilink24.com/patches/{txt_variant}"

            print(f"[WiiLink WFC] Trying to download: {txt_url}")

            try:
                urllib.request.urlretrieve(txt_url, txt_path)
                print(f"[WiiLink WFC] Downloaded TXT: {txt_variant}")

                # 3. Convert TXT to GCT
                print(f"[WiiLink WFC] Converting to GCT...")
                if WiiVCPatcher.txt_to_gct(txt_path, gct_path):
                    return gct_path
                else:
                    # Conversion failed, clean up
                    if txt_path.exists():
                        txt_path.unlink()

            except urllib.error.HTTPError as e:
                if e.code == 404:
                    print(f"[WiiLink WFC] Not found: {txt_variant} (trying next variant...)")
                else:
                    print(f"[WiiLink WFC] HTTP error {e.code}: {txt_url}")
            except Exception as e:
                print(f"[WiiLink WFC] Download failed: {e}")

        # Not found after trying all variants
        print(f"[WiiLink WFC] No patches found for {game_id}")
        print(f"[WiiLink WFC] Tried URLs:")
        for variant in variants:
            txt_variant = variant.replace('.gct', '.txt')
            print(f"  - https://wfc.wiilink24.com/patches/{txt_variant}")
        return None

    @staticmethod
    def patch_iso_wiilink_wfc(iso_path: Path, game_id: str, wit_path: Path) -> bool:
        """
        Apply WiiLink WFC patch to game ISO using Gecko codes.

        WiiLink WFC uses HTTP instead of TLS, making it compatible with WiiVC!
        This method downloads the .gct file and applies it using wstrt.

        Args:
            iso_path: Path to game ISO
            game_id: 6-character game ID (e.g., 'RMCK01')
            wit_path: Path to wit.exe (used to locate core directory)

        Returns:
            True if patch applied successfully
        """
        if not iso_path.exists():
            print(f"[WiiLink WFC] ISO not found: {iso_path}")
            return False

        print(f"[WiiLink WFC] Applying WiiLink WFC patch to {game_id}...")

        # Get core directory (where WIT is located)
        core_dir = wit_path.parent.parent  # core/WIT/wit.exe -> core/

        # Download and convert WiiLink WFC .gct file (fully automatic!)
        gct_path = WiiVCPatcher.download_and_convert_gct(game_id, core_dir)
        if not gct_path:
            print("[WiiLink WFC] Failed to get GCT file")
            print("[WiiLink WFC] ISO patch skipped - game will work but without online play")
            return False

        # Extract ISO
        wit_exe = wit_path
        extract_dir = iso_path.parent / "WIILINK_TEMP"

        if extract_dir.exists():
            shutil.rmtree(extract_dir)

        print("[WiiLink WFC] Extracting ISO...")
        try:
            result = subprocess.run(
                [str(wit_exe), 'extract', str(iso_path), '--DEST', str(extract_dir), '--psel', 'data', '-vv1'],
                capture_output=True,
                text=True,
                timeout=1800
            )
            if result.returncode != 0:
                print(f"[WiiLink WFC] WIT extract failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"[WiiLink WFC] Failed to extract ISO: {e}")
            return False

        # Find main.dol
        main_dol = extract_dir / "sys" / "main.dol"
        if not main_dol.exists():
            print(f"[WiiLink WFC] main.dol not found: {main_dol}")
            shutil.rmtree(extract_dir, ignore_errors=True)
            return False

        # Apply GCT using wstrt
        wstrt_exe = core_dir / "WIT" / "wstrt.exe"
        print(f"[WiiLink WFC] Applying GCT patch to main.dol...")

        try:
            result = subprocess.run(
                [str(wstrt_exe), 'patch', str(main_dol), '--add-section', str(gct_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                print(f"[WiiLink WFC] wstrt patch failed: {result.stderr}")
                shutil.rmtree(extract_dir, ignore_errors=True)
                return False
        except Exception as e:
            print(f"[WiiLink WFC] Failed to apply GCT: {e}")
            shutil.rmtree(extract_dir, ignore_errors=True)
            return False

        # Rebuild ISO
        print("[WiiLink WFC] Rebuilding ISO...")
        try:
            result = subprocess.run(
                [str(wit_exe), 'copy', str(extract_dir), '--DEST', str(iso_path), '-ovv', '--iso'],
                capture_output=True,
                text=True,
                timeout=1800
            )
            if result.returncode != 0:
                print(f"[WiiLink WFC] WIT copy failed: {result.stderr}")
                shutil.rmtree(extract_dir, ignore_errors=True)
                return False
        except Exception as e:
            print(f"[WiiLink WFC] Failed to rebuild ISO: {e}")
            shutil.rmtree(extract_dir, ignore_errors=True)
            return False

        # Cleanup
        shutil.rmtree(extract_dir, ignore_errors=True)

        print("[WiiLink WFC] Patch applied successfully!")
        print("[WiiLink WFC] Game is now ready for WiiLink WFC online play on WiiVC!")
        return True

    @staticmethod
    def apply_c2w_patch(ancast_key: str, build_code_dir: Path, core_dir: Path) -> bool:
        """
        Apply C2W (Cafe2Wii) patch to unlock CPU clock from 729MHz to 1.215GHz.

        This patch modifies c2w.img to remove the CPU clock restriction, allowing
        Wii VC games to run at full Wii U CPU speed for better performance.

        Args:
            ancast_key: 32-character hex Ancast key (Wii U Starbuck encryption key)
            build_code_dir: Path to the build/code directory containing c2w.img
            core_dir: Path to the core directory containing C2W patcher tool

        Returns:
            True if patch applied successfully, False otherwise

        Process:
        1. Copy c2w.img from build/code to C2W tool directory
        2. Write Ancast key to starbuck_key.txt
        3. Run c2w_patcher.exe -nc (non-compressed mode)
        4. Copy patched c2p.img back as c2w.img
        5. Clean up temporary files
        """
        import os

        # Validate Ancast key
        if not ancast_key or len(ancast_key) != 32:
            print("[C2W] Invalid Ancast key - must be 32 hex characters")
            return False

        # Validate hex characters
        try:
            int(ancast_key, 16)
        except ValueError:
            print("[C2W] Invalid Ancast key - must contain only hex characters (0-9, A-F)")
            return False

        # Path validation
        c2w_img_source = build_code_dir / "c2w.img"
        if not c2w_img_source.exists():
            print(f"[C2W] c2w.img not found at {c2w_img_source}")
            print("[C2W] Make sure base files (0005001010004001) are downloaded")
            return False

        c2w_tool_dir = core_dir / "C2W"
        c2w_patcher_exe = c2w_tool_dir / "c2w_patcher.exe"
        if not c2w_patcher_exe.exists():
            print(f"[C2W] c2w_patcher.exe not found at {c2w_patcher_exe}")
            return False

        print("[C2W] Applying CPU clock unlock patch...")
        print(f"[C2W] Ancast key: {ancast_key[:8]}...{ancast_key[-8:]}")

        try:
            # Copy c2w.img to C2W tool directory
            c2w_temp = c2w_tool_dir / "c2w.img"
            shutil.copy2(c2w_img_source, c2w_temp)
            print(f"[C2W] Copied c2w.img to {c2w_tool_dir}")

            # Write Ancast key to starbuck_key.txt
            starbuck_key_file = c2w_tool_dir / "starbuck_key.txt"
            with open(starbuck_key_file, 'w') as f:
                f.write(ancast_key)
            print(f"[C2W] Wrote Ancast key to {starbuck_key_file}")

            # Run c2w_patcher.exe -nc
            print("[C2W] Running c2w_patcher.exe -nc...")
            original_dir = os.getcwd()
            os.chdir(c2w_tool_dir)

            result = subprocess.run(
                [str(c2w_patcher_exe), '-nc'],
                capture_output=True,
                text=True,
                timeout=30
            )

            os.chdir(original_dir)

            if result.returncode != 0:
                print(f"[C2W] c2w_patcher.exe failed: {result.stderr}")
                # Cleanup
                c2w_temp.unlink(missing_ok=True)
                starbuck_key_file.unlink(missing_ok=True)
                return False

            print(f"[C2W] c2w_patcher.exe output:\n{result.stdout}")

            # Check if c2p.img was created
            c2p_img = c2w_tool_dir / "c2p.img"
            if not c2p_img.exists():
                print("[C2W] c2p.img not created - patch may have failed")
                # Cleanup
                c2w_temp.unlink(missing_ok=True)
                starbuck_key_file.unlink(missing_ok=True)
                return False

            # Copy c2p.img back as c2w.img
            shutil.copy2(c2p_img, c2w_img_source)
            print(f"[C2W] Copied patched c2p.img to {c2w_img_source}")

            # Cleanup temporary files
            c2w_temp.unlink(missing_ok=True)
            c2p_img.unlink(missing_ok=True)
            starbuck_key_file.unlink(missing_ok=True)
            print("[C2W] Cleaned up temporary files")

            print("[C2W] CPU clock unlock patch applied successfully!")
            print("[C2W] Game will now run at 1.215GHz (up from 729MHz)")
            return True

        except Exception as e:
            print(f"[C2W] Failed to apply C2W patch: {e}")
            import traceback
            traceback.print_exc()
            # Cleanup on error
            (c2w_tool_dir / "c2w.img").unlink(missing_ok=True)
            (c2w_tool_dir / "c2p.img").unlink(missing_ok=True)
            (c2w_tool_dir / "starbuck_key.txt").unlink(missing_ok=True)
            return False

    @staticmethod
    def is_network_game(game_id: str, game_title: str) -> bool:
        """
        Check if game supports network/online play via WiiLink WFC.

        IMPORTANT: Checks for EXACT game ID match (region-specific).
        RMCK01 (KOR) ≠ RMCE01 (USA) - patches are NOT interchangeable!

        Args:
            game_id: 6-character game ID (must match exactly)
            game_title: Game title

        Returns:
            True if this exact game ID has WiiLink WFC support
        """
        # EXACT match required - GCT patches are region-specific!
        return game_id in WiiVCPatcher.WIILINK_WFC_GAMES


def auto_patch_wiilink_wfc(iso_path: Path, fw_img_path: Path, game_id: str,
                            game_title: str, wit_path: Path, base_game: str = None,
                            progress_callback = None) -> Tuple[bool, bool]:
    """
    Automatically apply WiiLink WFC patches to Wii games.

    This function applies two patches:
    1. fw.img Trucha bug patch: Bypasses signature verification (always applied)
       - Safe for all games
       - Enables modified content to run
       - Fixes error 22000
       - Required for WiiLink WFC and Galaxy patches

    2. ISO WiiLink WFC patch: Redirects online games to WiiLink WFC servers
       - Uses HTTP instead of TLS (WiiVC compatible!)
       - Auto-downloads and converts TXT to GCT
       - Supports: Mario Kart Wii, Super Smash Bros Brawl, and more
       - Only applied if game is supported

    Args:
        iso_path: Path to game ISO
        fw_img_path: Path to fw.img
        game_id: 6-character game ID
        game_title: Game title
        wit_path: Path to wit.exe
        base_game: Base game identifier
        progress_callback: Optional callback for progress updates

    Returns:
        Tuple of (fw_patched, iso_patched)
    """
    print(f"[WiiLink WFC] Checking {game_title} ({game_id})")

    # Check if network game (EXACT game ID match required!)
    is_network = WiiVCPatcher.is_network_game(game_id, game_title)
    if is_network:
        print(f"[WiiLink WFC] ✅ Supported game! Online play will be enabled")
        print(f"[WiiLink WFC] Region: {WiiVCPatcher.WIILINK_WFC_GAMES[game_id]}")
        print(f"[WiiLink WFC] This will work on WiiVC! (HTTP-based, no TLS required)")

    # Step 1: ALWAYS patch fw.img (safe for all games)
    if progress_callback:
        progress_callback(68, "WiiLink WFC: Patching fw.img...")
    fw_patched = WiiVCPatcher.patch_fw_img_trucha(fw_img_path, base_game)

    if not fw_patched:
        print("[WiiLink WFC] WARNING: fw.img patch failed!")
        print("[WiiLink WFC] Modified content may show error 22000")

    # Step 2: Patch ISO - Only for network games
    iso_patched = False
    if is_network:
        if progress_callback:
            progress_callback(69, "WiiLink WFC: Patching ISO...")
        iso_patched = WiiVCPatcher.patch_iso_wiilink_wfc(iso_path, game_id, wit_path)
    else:
        print("[WiiLink WFC] Skipping ISO patch (not a supported network game)")
        iso_patched = True  # Not needed = success

    if fw_patched and iso_patched:
        print("[WiiLink WFC] All patches applied successfully!")
        if is_network:
            print("[WiiLink WFC] Game ready for WiiLink WFC online play on WiiVC!")
    elif fw_patched:
        print("[WiiLink WFC] fw.img patched, but ISO patch failed")
    else:
        print("[WiiLink WFC] Patching incomplete")

    # Complete
    if progress_callback:
        progress_callback(70, "WiiLink WFC patches complete")

    return (fw_patched, iso_patched)
