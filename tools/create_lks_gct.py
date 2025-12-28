
import sys
import os
import re

def create_gct(game_id, code_text):
    print(f"Creating GCT for {game_id}...")
    
    codes = []
    lines = code_text.strip().split('\n')
    for line in lines:
        line = line.strip()
        parts = line.split()
        for part in parts:
            if re.match(r'^[0-9A-Fa-f]{8}$', part):
                codes.append(part)
    
    if not codes:
        print("No valid codes found!")
        return False
        
    print(f"Found {len(codes)} code words ({len(codes)*4} bytes)")
    
    header = bytes.fromhex("00D0C0DE00D0C0DE")
    footer = bytes.fromhex("F000000000000000")
    
    body = bytearray()
    for code in codes:
        body.extend(bytes.fromhex(code))
        
    final_data = header + body + footer
    
    # Save to core/CCPatches
    output_dir = os.path.join(os.path.dirname(__file__), "..", "core", "CCPatches")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, f"{game_id}.gct")
    output_path = os.path.abspath(output_path)
    
    with open(output_path, 'wb') as f:
        f.write(final_data)
        
    print(f"Successfully wrote {output_path}")
    print(f"Total size: {len(final_data)} bytes")
    return True

# --- Wii Fit Plus (USA) ---
# Unfinished Classic Controller Support
# USA: RFPE01
wiifit_usa = """
C2137004 00000019
2C040002 408200B8
71090800 41820008
60C68000 71090001
41820008 60C60008
71094000 41820008
60C60004 71090002
41820008 60C60001
71098000 41820008
60C60002 71090010
41820008 60C60800
71090040 41820008
60C60400 71090008
41820008 60C60100
71090020 41820008
60C60200 71092000
41820008 60C60800
71090200 41820008
60C60800 71090080
41820008 60C60800
71090004 41820008
60C60800 71090400
41820008 60C60010
71091000 41820008
60C61000 70C99FFF
60000000 00000000
C2137FF8 00000029
90010024 2C040000
4082013C 8803005C
2C000002 40820130
48000021 801529F0
3FAAAAAB 3C75C28F
00000000 00000000
3DCCCCCD 3F800000
7CA802A6 90A1000C
5727083C 38E7000C
C0030074 FC000210
C0230078 FC200A10
C083006C FC802210
C0A30070 FCA02A10
FC00082A FC84282A
FC00202A C0450014
FC001040 4180000C
38C0012C 48000014
7CC53AAE 28060000
408100B4 38C6FFFF
7CC53B2E 38C00002
98C3005E 81850000
7D8803A6 4E800021
2C030001 7FE3FB78
80A1000C C0450004
40820008 EC4200B2
C0650008 C0030020
C0230074 C083006C
FC21202A FC211024
48000039 D0030020
C0030024 C0230078
FC200850 C0830070
FC802050 FC21202A
48000019 D0030024
80010024 7C0803A6
38210020 4E800020
FC0100FA C0250018
FC000800 4180000C
FC000890 48000014
FC200850 FC000800
41810008 FC000890
4E800020 00000000
"""

# Create Wii Fit Plus patch
create_gct("RFPE01", wiifit_usa)
