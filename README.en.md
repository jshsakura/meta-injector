# 🎮 Meta-Injector

**[한국어](README.md) | English**

A tool that converts multiple Wii games into Wii U Virtual Console (VC) format at once. It supports batch processing and automatic metadata downloading.

## ✨ Key Features

### Core Functionality
- ✅ **Stable Installation**: Prevents 'Corrupted Software' errors with correct TIK/TMD handling
- ✅ **Multiple Installations Support**: Allows installing different versions of the same game via random ID generation
- ✅ **Metadata Extraction**: Reads game codes directly from ISO/WBFS files to verify information
- ✅ **Safe Operation**: Protects original files by working in temporary folders
- ✅ **Various Formats**: Supports WBFS, ISO, NKIT, Decrypted ISO (.iso.dec), NGC (.gcm)
- ✅ **Powerful Patch System**:
  - Built-in Classic Controller (CC) patches for over 200 games
  - Automatic detection of GamePad support via compatibility DB
  - Full GamePad support for Super Mario Galaxy 1/2 (AllStars/Nvidia profiles)
  - Support for user-defined GCT patches

### Batch Processing
- 🚀 **Mass Conversion**: Add dozens of games to the list and process them all at once
- 📊 **Status Monitoring**: Real-time progress check for each game in the queue
- 🎨 **Image Automation**: Automatically downloads high-quality icons and banners from GameTDB
- 🌍 **Language Support**: Provides Korean/English UI
- 🎮 **Various Controllers**: Supports 7 profiles including GamePad, Classic Controller, etc.

### Image & Data Management
- 🖼️ **Image Caching**:
  - Automatically saves icons and banners to speed up future tasks
  - Manually set images are preserved even when regenerated
- 🌐 **GameTDB Integration**:
  - Automatically fetches game titles and cover images
  - Can be updated to the latest images anytime from the edit window
- 🔍 **Compatibility Database**:
  - Automatically recommends optimal controller settings for each game
  - Automatically displays whether a GCT patch is needed
- ✏️ **Convenient Editing**:
  - Edit game titles and images directly from the GUI
  - ISO Trim disable option (for games with save conflicts)
  - Automatic detection and guidance for WBFS file formats

## 📋 System Requirements

- **Python 3.8+** (When running source code)
- **Wii U Common Key** (Required)
- **Base Title Key** (At least 1 required)
  - Rhythm Heaven Fever (USA)
  - Or Xenoblade Chronicles (USA), Super Mario Galaxy 2 (EUR)

## 🚀 Installation & Execution

### Method 1: Download Executable (Recommended)
Download the latest `Meta-Injector.exe` from the [Releases page](https://github.com/jshsakura/meta-injector/releases) and run it.

### Method 2: Run Source Code
1. Clone repository:
   ```bash
   git clone https://github.com/jshsakura/meta-injector.git
   cd Meta-Injector
   ```
2. Install packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Run:
   ```bash
   python run.py
   ```

## 🎮 How to Use

### 1. Execution and Settings

1. Run `Meta-Injector.exe` (or `python run.py`)
2. Click **⚙ Settings** button
3. Enter **Wii U Common Key** and **Base Title Key (Rhythm Heaven Fever)** (Green light should turn on)
4. Set output folder (Optional)
5. Click **Save**

### 2. Converting Games

#### Basic Usage
1. Click **Add Files** button and select Wii game files (.wbfs, .iso, etc.).
2. Game information is read and images are downloaded automatically.
3. Check the game in the list and click **Edit** button if necessary.
   - You can modify the title or image.
   - **Disable ISO Trim**: Check for games that require original capacity like Super Paper Mario.
4. Select desired controller method in **Pad Options**. (Automatically recommended if CC patch exists)
5. Click **Start Build** button to start conversion.

#### Mass Conversion (Batch Processing)
1. Select multiple game files at once and add them to the list.
2. Information and images for all games are prepared automatically.
3. Review the list, check settings, and click **Start Build** to convert all sequentially.

## 📁 Folder Structure

```
Meta-Injector/
├── src/                           # Source code
├── core/                          # External conversion tools (WIT, NUSPacker, etc.)
├── resources/                     # Images and databases
│   ├── images/
│   └── wiitdb.txt
├── run.py                         # Execution script
└── README.md                      # Manual
```

## 🎮 GCT Patch & Controller System

The most powerful feature of this tool is the **Various Controller Patch (GCT) System**.

### 1. Auto CC (Classic Controller) Patch
- Provides Classic Controller patches for **some supported games** so they can be played with the **Wii U GamePad**.
- When you add a game, it checks for patch availability, displays a notification, and suggests settings.

### 2. Custom GCT
- You can apply user-created cheat codes or patches (.gct).
- If a `.gct` file with the same ID exists in the `games` folder, it is automatically recognized.

### 3. Special Game Patches
- **Super Mario Galaxy 1 & 2**: Fully supports dedicated patches (AllStars / Nvidia style) that replace Wiimote pointing functionality with the right analog stick.

### 🛠 Supported Controller Modes
| Mode | Description |
|------|-------------|
| **No Pad (Wiimote)** | Native state (Wiimote required) |
| **Pad CC** | Classic Controller emulation (GamePad used) |
| **Pad Wiimote(↕/↔)** | Forces vertical/horizontal Wiimote grip setting |
| **Galaxy Patch** | Optimized patch for Galaxy series |

## ⚠️ Notes

- **Corrupted Software Error**: If this error occurs when running on Wii U, check if the encryption keys are correct and if the base files were downloaded properly.
- **Image Download Failure**: Check your internet connection, or GameTDB server might be temporarily down. You can also manually specify images.
- **nfs2iso2nfs Error**: There might be special characters in the ISO file path, or the file might be corrupted.

## 🙏 Credits

This project was made possible with the help of the following open source projects:
- **TeconMoon's WiiVC Injector**: Original Injector
- **UWUVCI-AIO-WPF**: Multi-Injector
- **Wiimm's ISO Tools (WIT)**: ISO Management Tool
- **GameTDB**: Game Database
- **JNUSTool, NUSPacker, nfs2iso2nfs**: Core Conversion Tools
- **Kiran Shastry**: Application Icon Design (Flaticon)

---
**Made with ❤️ for the Wii U Homebrew Community.**