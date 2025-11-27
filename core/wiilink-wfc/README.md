# WiiLink WFC GCT Files

This directory contains Gecko Code Table (.gct) files for WiiLink WFC online play support.

## 🤖 Automatic Download & Conversion

**GCT files are downloaded and converted AUTOMATICALLY (for supported games only)!**

When you build a supported game, the injector will:
1. 🔍 Detect the game ID from your ISO (e.g., RMCK01)
2. ✅ Check if game is supported (Mario Kart Wii, Smash Bros. Brawl)
3. 📥 Download the region-specific TXT patch from `wfc.wiilink24.com/patches/`
4. 🔄 Convert TXT to GCT binary format
5. 💾 Cache the GCT in this directory
6. ✅ Apply the patch to your game

**⚠️ IMPORTANT: GCT patches are region-specific!**
- Korean game (RMCK01) = Korean patch (RMCKD00.gct)
- USA game (RMCE01) = USA patch (RMCED00.gct)
- **Wrong region patch = Game crash or doesn't work!**

**You don't need to do anything!** The process is fully automatic for supported games.

---

## 📥 Manual Download (Optional)

If automatic download fails, you can manually download GCT files from the WiiLink WFC website.

### Method 1: Direct Browser Download (Recommended)

1. Visit the game page on WiiLink WFC:
   - **Mario Kart Wii**: https://wfc.wiilink24.com/online/mariokartwii
   - **Super Smash Bros. Brawl**: https://wfc.wiilink24.com/online/smashbrosxwii

2. Find your game's region code:
   - Open your ISO in a hex editor and read the first 6 bytes (e.g., `RMCE01`)
   - Or check the ISO filename

3. Click the "Download GCT" button for your region

4. Save the `.gct` file to this directory with the **exact filename**:
   ```
   core/wiilink-wfc/RMCE01.gct
   core/wiilink-wfc/RMCK01.gct
   core/wiilink-wfc/RSBE01.gct
   etc...
   ```

### Method 2: Use WiiLink WFC Patcher

1. Download the official patcher: https://wfc.wiilink24.com/setup
2. Extract the `.gct` files from the patcher output
3. Copy them to this directory

## 📝 Supported Games

**⚠️ CRITICAL: Each region requires its own specific patch!**
- Using the wrong region's patch will cause crashes or malfunction
- Korean ISO (RMCK01) must use Korean patch (RMCKD00.gct)
- Cannot mix regions (e.g., USA patch on Korean game = doesn't work)

### Mario Kart Wii (All Regions Supported)
| Game ID | Region | Auto-Download | Manual Download |
|---------|--------|---------------|-----------------|
| **RMCK01** | **🇰🇷 Korea** | ✅ Auto | [Download](https://wfc.wiilink24.com/online/mariokartwii) |
| RMCE01 | 🇺🇸 USA | ✅ Auto | [Download](https://wfc.wiilink24.com/online/mariokartwii) |
| RMCJ01 | 🇯🇵 Japan | ✅ Auto | [Download](https://wfc.wiilink24.com/online/mariokartwii) |
| RMCP01 | 🇪🇺 Europe | ✅ Auto | [Download](https://wfc.wiilink24.com/online/mariokartwii) |

### Super Smash Bros. Brawl (All Regions Supported)
| Game ID | Region | Auto-Download | Manual Download |
|---------|--------|---------------|-----------------|
| **RSBK01** | **🇰🇷 Korea** | ✅ Auto | [Download](https://wfc.wiilink24.com/online/smashbrosxwii) |
| RSBE01 | 🇺🇸 USA | ✅ Auto | [Download](https://wfc.wiilink24.com/online/smashbrosxwii) |
| RSBJ01 | 🇯🇵 Japan | ✅ Auto | [Download](https://wfc.wiilink24.com/online/smashbrosxwii) |
| RSBP01 | 🇪🇺 Europe | ✅ Auto | [Download](https://wfc.wiilink24.com/online/smashbrosxwii) |

## ⚠️ Important Notes

1. **Game ID matching**: The GCT filename MUST match your game's ID exactly
2. **Region-specific**: Korean game (RMCK01) requires Korean patch - cannot use USA/EUR/JPN patches
3. **File placement**: Place files directly in `core/wiilink-wfc/`, not in subfolders
4. **Updates**: Check WiiLink WFC website regularly for new game support

## 🔒 Why WiiLink WFC Works on WiiVC (But Wiimmfi Doesn't)

| Service | Protocol | WiiVC Support | Reason |
|---------|----------|---------------|--------|
| **WiiLink WFC** | HTTP | ✅ **Works!** | Designed for WiiVC (no SSL required) |
| **Wiimmfi** | HTTPS/TLS | ❌ **Broken** | WiiVC doesn't support SSL/TLS |

**WiiLink WFC is permanently HTTP-based by design** - it won't "break later" because SSL/TLS support is intentionally not used to maintain WiiVC compatibility.

## 🔗 Resources

- WiiLink WFC Website: https://wfc.wiilink24.com
- Installation Guide: https://wfc.wiilink24.com/setup
- GitHub: https://github.com/WiiLink24/wfc-patcher-wii

## 📂 Directory Structure

```
core/wiilink-wfc/
├── README.md (this file)
├── RMCED00.gct (auto-generated from TXT)
├── RMCED00.txt (auto-downloaded)
├── RMCKD00.gct (auto-generated from TXT)
├── RMCKD00.txt (auto-downloaded)
└── ... (cached files after first build)
```

## 🔧 Technical Details

### TXT to GCT Conversion

The injector automatically converts Gecko code TXT files to GCT binary format:

**TXT Format** (human-readable):
```
220EDDE4 00000004
060EDFF8 00000028
...
```

**GCT Format** (binary):
```
00D0C0DE 00D0C0DE  ← Header
220EDDE4 00000004  ← Code data
...
F0000000 00000000  ← Footer
```

### Filename Variants

The injector tries multiple filename variants automatically:
- `RMCE01.gct` → tries `RMCE01.gct`, `RMCED00.gct`, `RMCEN0001.gct`
- `RSBE01.gct` → tries `RSBE01.gct`, `RSBE02.gct`

### Caching

Downloaded and converted files are cached in this directory. Subsequent builds will reuse cached files, saving time and bandwidth.

---

**Last Updated**: 2025-11-26
