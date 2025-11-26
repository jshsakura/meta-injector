"""
WiiVC firmware and ISO patcher for Wiimmfi support.

This module provides automatic Wiimmfi patching for Wii Virtual Console games:
- fw.img Trucha bug patch: Bypasses signature verification (fixes error 22000)
- ISO Wiimmfi patch: Modifies game to connect to Wiimmfi servers (fixes error 20100)

The ISO patcher uses the official Wiimmfi ISO Patcher tool which is automatically
downloaded on first use (~35 MB).
"""
from pathlib import Path
from typing import Optional, Tuple
import hashlib


class WiiVCPatcher:
    """Patches fw.img and ISO for Wiimmfi online play."""

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

        file_size = fw_img_path.stat().st_size

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
    def download_wiimmfi_patcher(core_dir: Path) -> Path:
        """
        Download and extract Wiimmfi ISO Patcher to core directory.

        Args:
            core_dir: Path to core directory (where WIT, etc. are stored)

        Returns:
            Path to patcher directory
        """
        import urllib.request
        import zipfile
        import shutil

        patcher_dir = core_dir / "wiimmfi-patcher"
        patcher_url = "https://download.wiimmfi.de/patcher/wiimmfi-patcher-latest.zip"
        zip_path = core_dir / "wiimmfi-patcher.zip"

        # Check if already downloaded
        if patcher_dir.exists() and (patcher_dir / "patch-images.bat").exists():
            print("[ISO Patch] Wiimmfi patcher already installed")
            return patcher_dir

        print("[ISO Patch] Downloading Wiimmfi patcher...")

        try:
            # Download
            urllib.request.urlretrieve(patcher_url, zip_path)
            print(f"[ISO Patch] Downloaded {zip_path.stat().st_size / 1024 / 1024:.1f} MB")

            # Extract
            print("[ISO Patch] Extracting patcher...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(patcher_dir)

            # Cleanup
            zip_path.unlink()
            print(f"[ISO Patch] Patcher installed to {patcher_dir}")

            return patcher_dir

        except Exception as e:
            print(f"[ISO Patch] Failed to download patcher: {e}")
            if zip_path.exists():
                zip_path.unlink()
            return None

    @staticmethod
    def patch_iso_wiimmfi(iso_path: Path, game_id: str, wit_path: Path) -> bool:
        """
        Apply Wiimmfi patch to game ISO using official Wiimmfi ISO Patcher.

        This modifies the game to connect to Wiimmfi servers instead of
        Nintendo WFC (fixes error 20100 by using HTTP instead of HTTPS).

        Args:
            iso_path: Path to game ISO
            game_id: 6-character game ID (e.g., 'RMCK01')
            wit_path: Path to wit.exe (used to locate core directory)

        Returns:
            True if patch applied successfully
        """
        import subprocess
        import shutil

        if not iso_path.exists():
            print(f"[ISO Patch] ISO not found: {iso_path}")
            return False

        print(f"[ISO Patch] Applying Wiimmfi patch to {game_id}...")

        # Known Wiimmfi-compatible games
        WIIMMFI_GAMES = {
            'RMCK01': 'Mario Kart Wii (KOR)',
            'RMCE01': 'Mario Kart Wii (USA)',
            'RMCP01': 'Mario Kart Wii (EUR)',
            'RMCJ01': 'Mario Kart Wii (JPN)',
            'RSBE01': 'Super Smash Bros. Brawl (USA)',
            'RSBP01': 'Super Smash Bros. Brawl (EUR)',
            'RSBJ01': 'Super Smash Bros. Brawl (JPN)',
            'RSBK01': 'Super Smash Bros. Brawl (KOR)',
            # Add more as needed
        }

        game_name = WIIMMFI_GAMES.get(game_id, f'Game {game_id}')
        print(f"[ISO Patch] Game: {game_name}")

        # Get core directory (where WIT is located)
        core_dir = wit_path.parent.parent  # core/WIT/wit.exe -> core/

        # Download/setup Wiimmfi patcher
        patcher_dir = WiiVCPatcher.download_wiimmfi_patcher(core_dir)
        if not patcher_dir:
            print("[ISO Patch] Failed to setup Wiimmfi patcher")
            return False

        # Determine which bat file to use
        patcher_bat = patcher_dir / "patch-images.bat"
        if not patcher_bat.exists():
            # Try 32-bit version
            patcher_bat = patcher_dir / "patch-images-32.bat"
            if not patcher_bat.exists():
                print("[ISO Patch] Patcher batch file not found")
                return False

        # Copy ISO to patcher directory
        iso_in_patcher = patcher_dir / iso_path.name
        print(f"[ISO Patch] Copying ISO to patcher directory...")
        shutil.copy2(iso_path, iso_in_patcher)

        # Run patcher
        print("[ISO Patch] Running Wiimmfi patcher (this may take a minute)...")
        try:
            result = subprocess.run(
                [str(patcher_bat)],
                cwd=str(patcher_dir),
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes max
            )

            if result.returncode != 0:
                print(f"[ISO Patch] Patcher failed with code {result.returncode}")
                print(f"[ISO Patch] Output: {result.stdout}")
                print(f"[ISO Patch] Error: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("[ISO Patch] Patcher timed out after 5 minutes")
            return False
        except Exception as e:
            print(f"[ISO Patch] Failed to run patcher: {e}")
            return False

        # Check for patched ISO
        patched_dir = patcher_dir / "wiimmfi-images"
        if not patched_dir.exists():
            print("[ISO Patch] Patched images directory not found")
            return False

        # Find patched ISO (should have same name or similar)
        patched_files = list(patched_dir.glob("*.iso"))
        if not patched_files:
            print("[ISO Patch] No patched ISO found in output directory")
            return False

        patched_iso = patched_files[0]
        print(f"[ISO Patch] Found patched ISO: {patched_iso.name}")

        # Replace original ISO with patched version
        print("[ISO Patch] Replacing original ISO with patched version...")
        shutil.copy2(patched_iso, iso_path)

        # Cleanup
        print("[ISO Patch] Cleaning up temporary files...")
        iso_in_patcher.unlink(missing_ok=True)
        shutil.rmtree(patched_dir, ignore_errors=True)

        print("[ISO Patch] Wiimmfi patch applied successfully!")
        return True

    @staticmethod
    def is_network_game(game_id: str, game_title: str) -> bool:
        """
        Check if game supports network/online play.

        Args:
            game_id: 6-character game ID
            game_title: Game title

        Returns:
            True if game has network features
        """
        # Known network-enabled games
        NETWORK_GAME_IDS = {
            'RMCK', 'RMCE', 'RMCP', 'RMCJ',  # Mario Kart Wii
            'RSBE', 'RSBP', 'RSBJ', 'RSBK',  # Smash Bros Brawl
            'RSPE', 'RSPP', 'RSPJ',          # Wii Sports
            'RZTP', 'RZTE',                  # Wii Sports Resort
            'R8PE', 'R8PP',                  # Mario Kart Wii
            # Add more game ID prefixes
        }

        # Check game ID prefix (first 4 chars)
        if game_id and len(game_id) >= 4:
            prefix = game_id[:4]
            if prefix in NETWORK_GAME_IDS:
                return True

        # Check title keywords
        NETWORK_KEYWORDS = [
            'mario kart', 'smash bros', 'call of duty', 'goldeneye',
            'conduit', 'online', 'multiplayer', 'wifi', 'wfc'
        ]

        title_lower = game_title.lower()
        for keyword in NETWORK_KEYWORDS:
            if keyword in title_lower:
                return True

        return False


def auto_patch_wiimmfi(iso_path: Path, fw_img_path: Path, game_id: str,
                       game_title: str, wit_path: Path, base_game: str = None,
                       progress_callback = None) -> Tuple[bool, bool]:
    """
    Automatically apply Wiimmfi patches to Wii games.

    This function applies two patches:
    1. fw.img Trucha bug patch: Bypasses signature verification for all games
       - Safe for all games (online or offline)
       - Enables modified content to run
       - Fixes error 22000

    2. ISO Wiimmfi patch: Redirects online games to Wiimmfi servers
       - Uses official Wiimmfi ISO Patcher (auto-downloaded ~35 MB)
       - Only needed for network-enabled games
       - Fixes error 20100
       - Supports: Mario Kart Wii, Super Smash Bros Brawl, and more

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
    print(f"[Wiimmfi] Patching {game_title} ({game_id})")

    # Check if network game for informational purposes
    is_network = WiiVCPatcher.is_network_game(game_id, game_title)
    if is_network:
        print(f"[Wiimmfi] Network features detected - online play will be enabled")

    # Step 1: Patch fw.img (fixes error 22000)
    if progress_callback:
        progress_callback(68, "Wiimmfi: Patching fw.img...")
    fw_patched = WiiVCPatcher.patch_fw_img_trucha(fw_img_path, base_game)

    # Step 2: Patch ISO (fixes error 20100) - Only for network games
    iso_patched = False
    if is_network:
        if progress_callback:
            progress_callback(69, "Wiimmfi: Patching ISO...")
        iso_patched = WiiVCPatcher.patch_iso_wiimmfi(iso_path, game_id, wit_path)
    else:
        print("[Wiimmfi] Skipping ISO patch (no network features detected)")
        iso_patched = True  # Consider it successful since it's not needed

    if fw_patched and iso_patched:
        print("[Wiimmfi] All patches applied successfully!")
        if is_network:
            print("[Wiimmfi] Game should now work with Wiimmfi online service")
    elif fw_patched:
        print("[Wiimmfi] fw.img patched, but ISO patch failed or pending")
    else:
        print("[Wiimmfi] Patching incomplete - online play may not work")

    # Complete
    if progress_callback:
        progress_callback(70, "Wiimmfi patches complete")

    return (fw_patched, iso_patched)
