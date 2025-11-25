# 🎮 Meta-Injector

**[한국어](README.md) | English**

Enhanced Wii Virtual Console injector for WiiU with batch processing support and automatic metadata retrieval.

## ✨ Key Features

### Core Functionality
- ✅ **No Corrupted Software Error**: Proper TIK/TMD handling prevents installation issues
- ✅ **Multiple Versions**: Random ID generation allows installing multiple versions of the same game
- ✅ **Accurate Metadata**: Reads game code directly from ISO/WBFS files
- ✅ **Safe Processing**: Uses temporary folders to protect source files
- ✅ **Multiple Format Support**: WBFS, ISO, NKIT, decrypted ISO (.iso.dec), GameCube (.gcm)

### Batch Processing
- 🚀 **Mass Injection**: Process multiple games simultaneously
- 📊 **Progress Tracking**: Real-time status for each game in queue
- 🎨 **Auto Image Download**: Fetches icons and banners from GameTDB
- 🌍 **Multi-Language Support**: Korean and English UI
- 🎮 **Gamepad Profiles**: 7 controller configurations including Galaxy patches

### Image & Metadata
- 🖼️ **Smart Image Caching**: Persistent cache for faster subsequent builds
- 🌐 **GameTDB Integration**: Automatic game title and cover art retrieval
- 🔍 **Compatibility Database**: Built-in gamepad compatibility information
- ✏️ **Easy Editing**: Edit game metadata, titles, and images through GUI

## 📋 Requirements

- **Python 3.8+** (for running from source)
- **PyQt5** - GUI framework
- **Pillow** - Image processing
- **Wii U Common Key** - Required for decryption
- **Base Title Keys** - At least Rhythm Heaven Fever (USA) required
  - Optional: Xenoblade Chronicles (USA), Super Mario Galaxy 2 (EUR)

## 🚀 Quick Start

### Option 1: Standalone Executable (Recommended)

Download the latest release from the [Releases page](https://github.com/yourusername/Meta-Injector/releases) and run `Meta-Injector.exe`.

### Option 2: Run from Source

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/Meta-Injector.git
cd Meta-Injector
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python run.py
```

### First-Time Setup

1. Click **⚙ Settings** button
2. Enter your encryption keys:
   - **Wii U Common Key** (required)
   - **Rhythm Heaven Fever Title Key** (required)
   - **Xenoblade Chronicles Title Key** (optional)
   - **Super Mario Galaxy 2 Title Key** (optional)
3. Set output directory (optional - defaults to game directory)
4. Click **Save**

### Building Games

#### Single Game Build
1. Click **Add Files** and select your Wii game(s)
2. Wait for automatic metadata and image download
3. (Optional) Click **Edit** to customize title, images, or base ROM
4. Select gamepad profile from the dropdown
5. Click **Start Build**

#### Batch Build
1. Click **Add Files** and select multiple games
2. Auto-download will fetch icons/banners for all games
3. Review and edit any games as needed
4. Click **Start Build** to process all games

## 📁 Project Structure

```
Meta-Injector/
├── src/                           # Python source code
│   ├── main.py                    # Application entry point
│   ├── batch_window.py            # Main GUI (batch mode)
│   ├── batch_builder.py           # Batch build engine
│   ├── build_engine.py            # Core build logic
│   ├── game_info.py               # Game metadata extraction
│   ├── game_tdb.py                # GameTDB integration
│   ├── compatibility_db.py        # Compatibility database
│   ├── image_utils.py             # Image conversion (PNG→TGA)
│   ├── paths.py                   # Path management
│   ├── translations.py            # Multi-language support
│   ├── resources.py               # Resource path handling
│   └── utils.py                   # Utility functions
│
├── core/                          # External tools
│   ├── EXE/                       # Core executables
│   │   ├── nfs2iso2nfs.exe        # NFS converter
│   │   ├── jnustool.exe           # Base file downloader
│   │   ├── nuspacker.exe          # WUP packager
│   │   └── wbfs_file.exe          # WBFS converter
│   ├── WIT/                       # Wiimms ISO Tools
│   │   ├── wit.exe                # Wii ISO Tool
│   │   └── wstrt.exe              # String table tool
│   ├── Galaxy1GamePad_v1.2/       # Super Mario Galaxy patches
│   │   ├── *-AllStars.gct         # AllStars controller profile
│   │   └── *-Nvidia.gct           # Nvidia Shield profile
│   └── NKIT/                      # NKit converter
│       └── NKit.dll               # NKit library
│
├── resources/                     # Application resources
│   ├── images/                    # UI images
│   │   ├── icon.ico               # App icon
│   │   ├── icon.png               # Icon for UI
│   │   ├── default_icon.png       # Fallback game icon
│   │   ├── default_banner.png     # Fallback TV banner
│   │   └── default_drc.png        # Fallback GamePad image
│   └── wiitdb.txt                 # Game database (titles)
│
├── run.py                         # Entry point script
├── build.py                       # PyInstaller build script
├── requirements.txt               # Python dependencies
└── README.md                      # Korean README
└── README.en.md                   # This file (English)
```

## 🔧 Build Process

The build engine follows this workflow:

1. **Download Base Files** (first time only)
   - Fetches base ROM from Nintendo CDN using JNUSTool
   - Caches to `%PROGRAMDATA%\JNUSToolDownloads\`

2. **Extract Game Metadata**
   - Reads game ID, title, region from ISO/WBFS
   - Searches compatibility database

3. **Download Images** (if enabled)
   - Fetches from GameTDB (prioritized by region)
   - Falls back to UWUVCI-IMAGES repository
   - Uses default images if unavailable

4. **Process Game File**
   - Converts WBFS to ISO if needed
   - Extracts and trims using WIT
   - Preserves TIK/TMD files

5. **Apply Controller Patches** (if selected)
   - Injects gamepad profile GCT codes
   - Supports 7 different profiles
   - Special Galaxy 1 patches available

6. **Convert Images**
   - Converts PNG to TGA format
   - Resizes: icon (128x128), TV banner (1280x720), DRC (854x480)

7. **Convert to NFS Format**
   - Uses nfs2iso2nfs for Wii U filesystem

8. **Pack WUP Installable**
   - Creates installable package with NUSPacker
   - Outputs to configured directory

## 🎮 Gamepad Profiles

| Profile | Description | Use Case |
|---------|-------------|----------|
| **No Pad (Wiimote)** | Wii Remote only | Motion control games |
| **Pad CC** | Classic Controller | Most compatible option |
| **Pad CC+LR** | CC with L2/R2 triggers | Games needing triggers |
| **Pad Wiimote(↕)** | Vertical Wiimote | Vertical orientation games |
| **Pad Wiimote(↔)** | Horizontal Wiimote | Horizontal games (e.g., NSMB) |
| **Galaxy Patch(AllStars)** | SMG optimized | Super Mario Galaxy (AllStars style) |
| **Galaxy Patch(Nvidia)** | SMG alternative | Super Mario Galaxy (Nvidia Shield) |

## 🗂️ Storage Locations

### Temporary Files
- **Build Temp**: `%TEMP%\MetaInjector\`
  - `SOURCETEMP/` - Game extraction workspace
  - `BUILDDIR/` - Active build directory
  - `TOOLDIR/` - Temporary tool copies
  - Auto-cleaned after successful build

### Persistent Cache
- **Base Files**: `%PROGRAMDATA%\JNUSToolDownloads\`
  - Downloaded base ROMs (shared across builds)
- **Image Cache**: `%TEMP%\MetaInjector\IMAGECACHE\`
  - Downloaded game covers and banners

### Settings
- **User Settings**: `%USERPROFILE%\.meta_injector_settings.json`
  - Encryption keys (stored locally)
  - Output directory preference
- **Compatibility DB**: `%USERPROFILE%\.meta_injector_compatibility.db`
  - SQLite database with gamepad compatibility info

## 🎯 Key Improvements

### vs TeconMoon's WiiVC Injector
- ✅ TIK/TMD extraction (prevents corrupted software error)
- ✅ Random ID generation (multiple installs possible)
- ✅ Game code read from ISO (accurate metadata)
- ✅ Batch processing support
- ✅ Automatic image download

## 📊 Technical Details

### Metadata Extraction
```python
# Game ID from ISO header (offset 0x0)
game_id = iso_data[0x0:0x6].decode('ascii')

# Title from opening.bnr
title = extract_from_opening_bnr(iso_path)

# Generate Title ID
title_id = f"00050000{game_id[:4].encode().hex().upper()}"
```

### Random ID Generation
```python
# Each build gets unique random ID to allow multiple installs
title_id = f"00050002{secrets.token_hex(4).upper()}"
product_code = secrets.token_hex(2).upper()
```

### Image Download Priority
```python
# 1. Original game ID (e.g., RVYK52)
# 2. Alternative IDs (same name, different regions)
# 3. Prefix matches (first 3 chars)

# Region priority based on game
if game_id[3] == 'K':  # Korean
    region_codes = ['KO', 'EN', 'US', 'JA']
elif game_id[3] == 'J':  # Japanese
    region_codes = ['JA', 'EN', 'US', 'KO']
elif game_id[3] == 'P':  # Europe
    region_codes = ['EN', 'US', 'JA', 'KO']
else:  # USA
    region_codes = ['US', 'EN', 'JA', 'KO']
```

## 🏗️ Building Standalone EXE

To create a standalone executable:

```bash
python build.py
```

The executable will be created in `dist/Meta-Injector.exe` and includes:
- All Python dependencies
- Core tools (WIT, nfs2iso2nfs, etc.)
- Resources (images, database)
- Single-file distribution (~80MB)

## ⚠️ Known Issues & Limitations

- **Windows Only**: Uses Windows-specific paths and executables
- **Valid Keys Required**: Must have legitimate Wii U encryption keys
- **Base ROM Download**: Requires internet connection for first-time base file download
- **Large File Support**: ISOs over 4GB may take several minutes to process

## 🐛 Troubleshooting

### "Corrupted Software" Error on Wii U
- Ensure you're using valid encryption keys
- Check that base files downloaded correctly
- Try using a different base ROM (Xenoblade/Galaxy 2)

### Images Not Downloading
- Check internet connection
- GameTDB may be temporarily unavailable
- Use manual image selection (click icon/banner in table)

### Build Fails with "nfs2iso2nfs error"
- ISO may be corrupted - try re-dumping
- Check for special characters in file paths
- Ensure enough disk space (15GB+ free recommended)

## 🙏 Credits & Acknowledgments

### Original Projects
- **[TeconMoon's WiiVC Injector](https://github.com/Teconmoon/WiiVC-Injector)** - Original C# injector, simple and effective
- **[UWUVCI-AIO-WPF](https://github.com/stuff-by-3-random-dudes/UWUVCI-AIO-WPF)** - TIK/TMD handling, random ID generation
- **[Wiimm's ISO Tools (WIT)](https://wit.wiimm.de/)** - Essential Wii ISO manipulation
- **[nfs2iso2nfs](https://github.com/VitaSmith/nfs2iso2nfs)** - NFS filesystem conversion

### Tools & Resources
- **JNUSTool** - Nintendo CDN downloader
- **NUSPacker** - WUP package creator
- **GameTDB** - Game metadata and artwork
- **NKit** - ISO verification and processing

### Design
- **[Kiran Shastry](https://www.flaticon.com/authors/kiranshastry)** - Application icon design (Flaticon)

### Community
- **GBAtemp** - Research and testing community
- **WiiU Homebrew Community** - Tools and documentation

## 📝 License

This project is for educational purposes only. You must own legitimate copies of:
- The games you inject
- The base Wii U Virtual Console titles (Rhythm Heaven Fever, etc.)
- Wii U console with legal access to encryption keys

No copyrighted files (keys, ROMs, base files) are distributed with this software.

## 🔗 Related Projects

- [TeconMoon's WiiVC Injector](https://github.com/Teconmoon/WiiVC-Injector) - Original C# implementation
- [UWUVCI-AIO-WPF](https://github.com/stuff-by-3-random-dudes/UWUVCI-AIO-WPF) - Multi-console injector
- [Wii Backup Manager](http://www.wiibackupmanager.co.uk/) - Wii game management
- [Wiimm's ISO Tools](https://wit.wiimm.de/) - Command-line ISO tools

---

**Made with ❤️ for the WiiU homebrew community**

*Current Version: 1.0.0-beta*
