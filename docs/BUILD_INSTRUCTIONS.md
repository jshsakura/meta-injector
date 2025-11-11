# 🏗️ WiiVC Injector - 빌드 가이드

## 📋 준비사항

1. **Python 3.8+** 설치 확인
   ```bash
   python --version
   ```

2. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

3. **PyInstaller 설치**
   ```bash
   pip install pyinstaller
   ```

## 🚀 빌드 방법

### 방법 1: 자동 빌드 스크립트 (권장)

```bash
cd standalone
build_standalone.bat
```

완료되면:
- `standalone/dist/WiiVC-Injector.exe` - 실행 파일
- `standalone/release/` - 배포 패키지

### 방법 2: 빠른 빌드 (테스트용)

```bash
cd standalone
quick_build.bat
```

### 방법 3: 수동 빌드

```bash
cd standalone
pyinstaller WiiVC-Injector.spec
```

## 📦 빌드 결과물

```
standalone/
├── dist/
│   └── WiiVC-Injector.exe    # 약 40-60MB
└── release/
    ├── WiiVC-Injector.exe
    └── README.txt
```

## 🧪 테스트

빌드 후 즉시 실행:

```bash
cd standalone\dist
WiiVC-Injector.exe
```

또는 release 패키지에서:

```bash
cd standalone\release
WiiVC-Injector.exe
```

## ✅ 체크리스트

빌드 전 확인사항:

- [ ] Python 3.8+ 설치됨
- [ ] requirements.txt 의존성 설치됨
- [ ] PyInstaller 설치됨
- [ ] resources/icon.ico 파일 존재
- [ ] resources/wiitdb.txt 파일 존재

빌드 후 확인사항:

- [ ] WiiVC-Injector.exe 생성됨
- [ ] 실행 파일 크기 정상 (40-60MB)
- [ ] 더블클릭으로 실행 가능
- [ ] UI가 정상 표시됨
- [ ] 파일 선택 다이얼로그 동작
- [ ] 에러 없이 종료됨

## 🐛 문제 해결

### "Failed to execute script" 오류

**원인**: 숨겨진 import 누락

**해결**:
1. `WiiVC-Injector.spec` 열기
2. `hiddenimports`에 누락 모듈 추가
3. 재빌드

### "No module named 'PyQt5'" 오류

```bash
pip install --upgrade PyQt5
pip install --upgrade pyinstaller
```

### 실행 파일이 너무 큼

**최적화 옵션**:

1. UPX 압축 활성화 (spec 파일에 `upx=True`)
2. 불필요한 모듈 제외:
   ```python
   excludes=[
       'matplotlib',
       'numpy',
       'pandas',
       'scipy',
       'tkinter',
   ]
   ```

### 아이콘이 안보임

1. `resources/icon.ico` 파일 확인
2. spec 파일의 icon 경로 확인
3. ICO 포맷인지 확인 (PNG는 안됨)

## 🎯 배포 준비

### 1. 압축

```bash
# PowerShell
Compress-Archive -Path standalone\release\* -DestinationPath WiiVC-Injector-v1.0.0-Windows.zip

# 또는 7-Zip
7z a WiiVC-Injector-v1.0.0-Windows.zip .\standalone\release\*
```

### 2. 파일 검증

- [ ] ZIP 압축 확인
- [ ] 압축 해제 후 실행 테스트
- [ ] README.txt 포함 확인
- [ ] 바이러스 스캔 통과

### 3. 릴리즈

GitHub Releases에 업로드:
- Tag: `v1.0.0`
- 파일: `WiiVC-Injector-v1.0.0-Windows.zip`
- 설명: 변경사항, 사용법 등

## 📊 빌드 시간

| 단계 | 예상 시간 |
|------|----------|
| 의존성 분석 | ~30초 |
| 파일 수집 | ~20초 |
| 컴파일 | ~1분 |
| 패키징 | ~30초 |
| **총 시간** | **~2-3분** |

## 💡 팁

1. **개발 중**: `quick_build.bat` 사용 (빠름)
2. **최종 배포**: `build_standalone.bat` 사용 (완전 정리)
3. **디버그**: spec 파일에서 `console=True` 설정
4. **용량 최적화**: UPX + excludes 활용

## 🔗 관련 문서

- [PyInstaller 공식 문서](https://pyinstaller.org/)
- [spec 파일 상세](https://pyinstaller.readthedocs.io/en/stable/spec-files.html)
- [IMPROVEMENTS.md](IMPROVEMENTS.md) - 기능 개선사항
- [TEST_GUIDE.md](TEST_GUIDE.md) - 테스트 가이드
