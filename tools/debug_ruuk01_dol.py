
import os
import sys
from pathlib import Path

def find_pattern_in_dol():
    # Construct path to temp build main.dol
    temp_dir = os.environ.get('TEMP', 'C:\\Users\\WIN11\\AppData\\Local\\Temp')
    dol_path = Path(temp_dir) / "MetaInjector" / "BUILDDIR" / "content" / "sys" / "main.dol"
    
    print(f"Looking for main.dol at: {dol_path}")
    
    if not dol_path.exists():
        print("Error: main.dol not found in temp directory. Please run a build first!")
        return

    with open(dol_path, 'rb') as f:
        data = f.read()
    
    print(f"Read {len(data)} bytes from main.dol")
    
    # Signatures for GetExtType (based on standardized GetExtTypePatcher patterns)
    # These are heuristic patterns often found near WPAD_GetProbeInfo
    
    # Pattern 1: Typical WPAD_GetProbeInfo prologue or check
    # We are looking for something that checks the "extension type" (usually 0, 1, 2, 255)
    # and we want to FORCE it to return 0 (Core) or 1 (Nunchuk) or 2 (Classic)?
    # For Controller Emulation, we usually want the game to think "Nunchuk is connected" (Type 1)
    # so that the game accepts input, and then we remap CC to Nunchuk.
    
    # Search for "li r3, 255" (38 60 00 FF) ? Or "li r3, 0" ?
    
    # Let's search for the "Correction" pattern that user mentioned?
    # No, we need to find the LOCATION to apply the correction.
    
    # Let's dump strings to see if we see "WPAD" functions
    import re
    strings = re.findall(b'[a-zA-Z0-9_]{5,}', data)
    wpad_strings = [s for s in strings if b'WPAD' in s]
    print(f"Found {len(wpad_strings)} WPAD-related strings:")
    for s in wpad_strings[:10]:
        print(f" - {s.decode('utf-8', errors='ignore')}")

    # Heuristic for GetExtTypePatcher failure
    # If the patcher fails, the pattern is missing.
    # We might need to find a generic "bl" (branch link) to the WPAD library.
    
    pass

if __name__ == "__main__":
    find_pattern_in_dol()
