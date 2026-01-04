# Meta-Injector

**[한국어](README.md) | English**

A tool that converts Wii games to Wii U Virtual Console (VC) format.

## Features

- **Batch Conversion**: Convert multiple games at once
- **Auto Images**: Automatically download icons/banners from GameTDB
- **Controller Patches**: CC patch, Galaxy patch, GCT patch support
- **Various Formats**: WBFS, ISO, NKIT, GCM support

## Requirements

- Windows 10/11
- **Wii U Common Key**
- **Base Title Key** (Rhythm Heaven Fever, etc.)

## Installation

Download `Meta-Injector.exe` from [Releases](https://github.com/jshsakura/meta-injector/releases) and run it.

## How to Use

### 1. Initial Setup

1. Click **Settings** button
2. Enter Wii U Common Key
3. Enter Base Title Key (at least 1)
4. Save

### 2. Convert Games

1. Click **Add Files** to select game files (.wbfs, .iso, etc.)
2. Game info and images are fetched automatically
3. Click **Edit** to modify title/images if needed
4. Select controller option
5. Click **Start Build**

### Controller Options

| Option | Description |
|--------|-------------|
| Wiimote | Wiimote only |
| GamePad (CC) | Classic Controller emulation with GamePad |
| GamePad + LR | CC emulation + LR button patch |
| Galaxy Patch | Galaxy series only (pointer→stick) |
| GCT Patch | Apply custom GCT codes |

### Edit Features

- **Edit Title**: Change game title
- **Change Images**: Set icon, banner, GamePad screen individually
- **Auto Restore**: Restore modified images to auto-downloaded ones
- **Disable Trim**: For games with save issues (Super Paper Mario, etc.)

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Corrupted Software Error | Check Common Key and Title Key |
| Image Download Failure | Check internet or set images manually |
| Build Failure | Check for special characters in path, check log |

## Credits

- TeconMoon's WiiVC Injector
- UWUVCI-AIO-WPF
- Wiimm's ISO Tools (WIT)
- GameTDB
- JNUSTool, NUSPacker, nfs2iso2nfs

---
**Made for the Wii U Homebrew Community.**
