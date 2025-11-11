# WiiU Expedition VC Injector (위유 원정대 VC 인젝터)

Python/PyQt5로 완전히 재작성한 Wii Virtual Console Injector.

## 🎮 About

TeconMoon의 WiiVC Injector를 Python으로 완전히 재작성한 버전입니다. 원본 C# 버전은 [여기](https://gbatemp.net/threads/release-wiivc-injector-script-gc-wii-homebrew-support.483577/)에서 확인하실 수 있습니다.

### 왜 Python?

- **크로스 플랫폼**: Windows, Linux, macOS 지원
- **유지보수 용이**: 깔끔한 코드 구조
- **모던 의존성**: Pillow (이미지), PyQt5 (GUI)
- **오픈 생태계**: 커뮤니티 기여 용이

## 🚀 Quick Start

### Requirements

- Python 3.8 or higher
- pip (Python package manager)

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

## 📦 Features

- ✅ Support for Wii Retail, Wii Homebrew, Wii NAND, and GC Retail
- ✅ Custom icon, banner, DRC, and logo images (auto-resizing)
- ✅ Custom boot sounds
- ✅ GamePad emulation options
- ✅ Advanced patching options (C2W, Wiimmfi, etc.)
- ✅ Encryption key management
- ✅ Automatic game info extraction from ISO
- ✅ SD Card utilities with Nintendont support
- ✅ Settings management

## 📁 Project Structure

```
TeconmoonWiiVCInjector/
├── src/wiivc_injector/      # Main application code
│   ├── main_window.py       # Main GUI window
│   ├── game_info.py         # Game ISO information extraction
│   ├── game_tdb.py          # Game database lookup
│   ├── image_utils.py       # Image processing (Pillow)
│   ├── paths.py             # Path management
│   ├── resources.py         # Resource handling
│   ├── utils.py             # Utility functions
│   ├── settings_dialog.py   # Settings window
│   ├── sdcard_dialog.py     # SD Card utilities
│   └── string_util.py       # String utilities
├── resources/               # Game database, icons, etc.
│   └── wiitdb.txt          # Wii/GC game database
├── OLD/                     # Original C# version (archived)
├── run.py                   # Quick launcher
├── setup.py                 # Installation script
├── requirements.txt         # Python dependencies
├── IMPROVEMENTS.md          # Detailed improvements log
└── TEST_GUIDE.md           # Testing checklist
```

## 🛠️ Development Status

### ✅ Completed
- [x] Full UI implementation (PyQt5)
- [x] Game information extraction
- [x] Image processing and preview
- [x] Settings management
- [x] SD Card utilities dialog
- [x] Path management system
- [x] Resource handling
- [x] Game database integration

### ⏳ In Progress / TODO
- [ ] Build process implementation
- [ ] External tool integration (wit, chdman, etc.)
- [ ] Encryption key validation
- [ ] Repository download functionality
- [ ] Audio conversion (boot sounds)
- [ ] Patch application (C2W, Wiimmfi)
- [ ] Complete build workflow

## 📖 Documentation

- **[IMPROVEMENTS.md](IMPROVEMENTS.md)** - Detailed changelog and improvements
- **[TEST_GUIDE.md](TEST_GUIDE.md)** - Testing checklist and known issues

## 🔨 Building Executable

To create a standalone executable:

```bash
python build.py
```

결과물:
- `dist/WiiU-Expedition-VC-Injector.exe` - 실행 파일
- `release/` - 배포용 패키지 (exe + README)

**또는 수동 빌드**:
```bash
pyinstaller --onefile --windowed --name "WiiU-Expedition-VC-Injector" \
  --add-data "resources:resources" \
  src/wiivc_injector/main.py
```

## 🤝 Contributing

Contributions are welcome! This is a community project.

### How to Contribute

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

Same as the original project.

## 🙏 Credits

- **Original Author**: TeconMoon (C# Version)
- **Python Edition**: WiiU Expedition Team (위유 원정대)
- **Original C# Source**: Archived in `OLD/` directory

## ⚠️ Disclaimer

This tool is for educational purposes and personal backups only. You must own the original games to use this software legally.

---

**Original C# Version**: The original C# project has been moved to the `OLD/` directory for reference.

**프로젝트 이름**: "위유 원정대 (WiiU Expedition)"는 Wii U 게임을 Virtual Console로 여행(탐험)한다는 의미입니다.
