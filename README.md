# 🎮 WiiU Expedition VC Injector

Enhanced Wii Virtual Console injector for WiiU, combining the simplicity of TeconMoon with the robustness of UWUVCI.

## ✨ Features

- ✅ **No Corrupted Software Error**: Proper TIK/TMD handling
- ✅ **Multiple Versions**: Random ID generation allows installing multiple versions of the same game
- ✅ **Accurate Metadata**: Reads game code directly from ISO
- ✅ **Safe Processing**: Uses temporary folders to protect source files
- ✅ **Wii Game Support**: WBFS, ISO, NKIT formats
- ✅ **Flexible Trimming**: Option to trim or keep full ISO

## 📋 Requirements

- Python 3.8+
- PyQt5
- Wii U Common Key
- Rhythm Heaven Fever Title Key (for base files)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Injector

```bash
python run.py
```

### 3. Configure

- Set your Wii U Common Key
- Set Rhythm Heaven Fever Title Key
- Base files will be automatically downloaded to `%PROGRAMDATA%\JNUSToolDownloads\`

### 4. Build

1. Select your Wii game (ISO/WBFS)
2. Choose icon and banner images
3. Enter game title
4. Click "Build"

## 📁 Project Structure

```
WiiU-Expedition-VC-Injector/
├── src/                    # Source code
│   ├── build_engine.py    # Main build logic (TeconMoon + UWUVCI)
│   ├── paths.py           # Path management
│   ├── batch_window.py    # GUI
│   └── ...
├── core/                   # Tools (WIT, nfs2iso2nfs, etc.)
├── resources/              # UI resources
├── OLD/                    # Reference (TeconMoon, UWUVCI)
├── run.py                  # Entry point
└── README.md
```

## 🔧 Build Process

The enhanced build process follows this order:

1. **Download Base Files** - Rhythm Heaven Fever from Nintendo CDN
2. **Process Game** - Convert WBFS, trim ISO with WIT
3. **Generate Metadata** - Read game code from ISO, generate random IDs
4. **Convert Images** - PNG to TGA (128x128, 1280x720, 854x480)
5. **Extract TIK/TMD** - Critical for preventing "Corrupted Software" error
6. **Convert to NFS** - Using nfs2iso2nfs
7. **Pack WUP** - Final package with NUSPacker

## 🎯 Key Improvements

### vs TeconMoon
- ✅ TIK/TMD extraction (prevents corrupted software error)
- ✅ Random ID generation (multiple installs)
- ✅ Game code read from ISO (accurate metadata)

### vs UWUVCI
- ✅ Simpler codebase (Wii-only focus)
- ✅ Cleaner temp file management
- ✅ Direct tool usage (no wrapper complexity)

## 📊 Technical Details

### TIK/TMD Handling
```python
# Extract from ISO
wit extract game.iso --files +tmd.bin --files +ticket.bin

# Copy to build
code/rvlt.tmd
code/rvlt.tik
```

### Random ID Generation
```python
# Title ID: 00050002 + 8 random hex digits
title_id = f"00050002{random_hex}"

# Product Code: 4 random hex digits
product_code = f"{random_hex}"
```

### WIT Options
```python
# Trim mode (preserves structure)
wit extract --psel WHOLE
wit copy --links --iso

# No-trim mode
wit extract --psel data
wit copy --psel WHOLE --iso
```

## 🗂️ Temp File Locations

- **Build Temp**: `%TEMP%\WiiUVCInjector\`
  - `SOURCETEMP/` - ISO processing
  - `BUILDDIR/` - Package being built
  - `TOOLDIR/` - Temporary tool copies

- **Base Cache**: `%PROGRAMDATA%\JNUSToolDownloads\`
  - Shared across all builds
  - Persistent storage

## ⚠️ Known Issues

- Windows only (uses Windows-specific paths)
- Requires valid Wii U keys

## 🙏 Credits

- **TeconMoon**: Original WiiVC Injector (simple logic)
- **UWUVCI-AIO**: TIK/TMD handling, random IDs
- **WIT**: Wii ISO tools by Wiimm
- **nfs2iso2nfs**: NFS conversion tool

## 📝 License

This project is for educational purposes. You must own the games you inject.

## 🔗 Related Projects

- [TeconMoon's WiiVC Injector](https://github.com/Teconmoon/WiiVC-Injector) - Original C# version
- [UWUVCI-AIO-WPF](https://github.com/stuff-by-3-random-dudes/UWUVCI-AIO-WPF) - Multi-console injector

---

**Made with ❤️ for the WiiU homebrew community**
