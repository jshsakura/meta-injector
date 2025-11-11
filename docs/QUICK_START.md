# 🚀 Quick Start Guide

## WiiU Expedition VC Injector (위유 원정대 VC 인젝터)

### 1️⃣ 개발자 모드 (소스에서 실행)

```bash
# 의존성 설치
pip install -r requirements.txt

# 실행
python run.py
```

### 2️⃣ 스탠드얼론 빌드 (EXE 생성)

```bash
# 빌드
python build.py

# 실행
release\WiiU-Expedition-VC-Injector.exe
```

## 📦 빌드 과정

`build.py`가 자동으로:

1. ✅ PyInstaller 설치 확인/설치
2. ✅ 의존성 확인 (PyQt5, Pillow)
3. ✅ 이전 빌드 정리
4. ✅ 리소스 확인 (icon, wiitdb.txt)
5. ✅ 실행 파일 생성
6. ✅ 배포 패키지 생성

## 🎯 결과물

```
프로젝트/
├── dist/
│   └── WiiU-Expedition-VC-Injector.exe    # 단일 실행 파일 (40-60MB)
└── release/
    ├── WiiU-Expedition-VC-Injector.exe    # 배포용 복사본
    └── README.txt                         # 사용자 가이드
```

## ⚡ 빠른 명령어

| 작업 | 명령어 |
|------|--------|
| 개발 실행 | `python run.py` |
| 빌드 | `python build.py` |
| 테스트 | `release\WiiU-Expedition-VC-Injector.exe` |
| 의존성 설치 | `pip install -r requirements.txt` |

## 🐛 문제 해결

### "PyInstaller not found"
```bash
pip install pyinstaller
```

### "PyQt5 not found"
```bash
pip install PyQt5
```

### "Failed to build"
- Python 3.8+ 설치 확인
- requirements.txt 설치 확인
- 프로젝트 루트에서 실행 확인

## 📖 더 자세한 내용

- [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) - 상세 빌드 가이드
- [TEST_GUIDE.md](TEST_GUIDE.md) - 테스트 체크리스트
- [IMPROVEMENTS.md](IMPROVEMENTS.md) - 개선 사항

## 🎮 프로젝트 이름

"위유 원정대 (WiiU Expedition)"는 Wii U 게임을 Virtual Console로 여행(탐험)한다는 의미입니다.

Based on TeconMoon's WiiVC Injector
