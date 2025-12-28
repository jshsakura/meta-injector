"""
WiiVC firmware patcher for Galaxy patch support.

This module provides ONLY the Trucha bug patch required for Galaxy patches:
- fw.img Trucha bug patch: Bypasses signature verification
- Required when main.dol is modified by Galaxy GCT patches
- Fixes error 22000 (signature verification failure)
"""
from pathlib import Path
from typing import Optional
import hashlib


class WiiVCPatcher:
    """Patches fw.img for Galaxy patch compatibility."""

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
        Detect fw.img version by searching for known patterns.

        Returns:
            Version key (e.g., 'RHF_USA') or None
        """
        if not fw_img_path.exists():
            return None

        # Check for ES module signature patterns
        # These are ARM Thumb instructions commonly found in ES_Sign
        with open(fw_img_path, 'rb') as f:
            data = f.read()

        if b'\x20\x07\x4B\x0B' in data:
            # Most common pattern - assume RHF_USA compatible
            return 'RHF_USA'

        return 'RHF_USA'  # Default fallback

    @staticmethod
    def patch_fw_img_trucha(fw_img_path: Path) -> bool:
        """
        Apply Trucha bug patch to fw.img to bypass signature checks.

        This patches the ES_Sign function to always return success,
        allowing modified content (Galaxy patches) to run.

        Args:
            fw_img_path: Path to fw.img file

        Returns:
            True if patch applied successfully
        """
        if not fw_img_path.exists():
            print(f"[Trucha] fw.img not found: {fw_img_path}")
            return False

        # Detect version
        version = WiiVCPatcher.detect_fw_img_version(fw_img_path)
        if not version:
            print("[Trucha] Unable to detect fw.img version")
            return False

        patches = WiiVCPatcher.FW_IMG_PATCHES.get(version, [])
        if not patches:
            print(f"[Trucha] No patches defined for version: {version}")
            return False

        print(f"[Trucha] Detected fw.img version: {version}")

        # Read entire file
        with open(fw_img_path, 'rb') as f:
            data = bytearray(f.read())

        original_hash = hashlib.sha1(data).hexdigest()[:8]
        patches_applied = 0

        # Apply patches
        for offset, original, patched, description in patches:
            if offset >= len(data):
                print(f"[Trucha] Offset 0x{offset:08X} out of range")
                continue

            # Verify original bytes
            actual = bytes(data[offset:offset+len(original)])
            if actual != original:
                print(f"[Trucha] Mismatch at 0x{offset:08X}")
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
            print(f"[Trucha] Applied: {description} at 0x{offset:08X}")

        if patches_applied == 0:
            print("[Trucha] No patches were applied!")
            return False

        # Write patched file
        with open(fw_img_path, 'wb') as f:
            f.write(data)

        patched_hash = hashlib.sha1(data).hexdigest()[:8]
        print(f"[Trucha] Success! ({patches_applied} patches)")
        print(f"[Trucha] Hash: {original_hash} -> {patched_hash}")

        return True


# Convenience singleton
patcher = WiiVCPatcher()
