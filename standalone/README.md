# WiiVC Injector - Standalone Build

이 폴더는 Windows용 독립 실행형 EXE 파일을 빌드하기 위한 디렉토리입니다.

## 📦 빌드 방법

### Windows에서:

```bash
cd standalone
build_standalone.bat
```

### Linux/Mac에서:

```bash
cd standalone
chmod +x build_standalone.sh
./build_standalone.sh
```

## 🎯 빌드 과정

1. **의존성 체크**: PyInstaller 설치 확인
2. **이전 빌드 정리**: dist, build 폴더 삭제
3. **PyInstaller 실행**: 단일 EXE 파일 생성
4. **리소스 임베딩**: wiitdb.txt 포함
5. **릴리즈 패키징**: release 폴더에 최종 파일 복사

## 📂 빌드 결과

```
standalone/
├── build/                    # 임시 빌드 파일
├── dist/                     # PyInstaller 출력
│   └── WiiVC-Injector.exe   # 단일 실행 파일
└── release/                  # 최종 배포 패키지
    ├── WiiVC-Injector.exe   # 복사된 실행 파일
    └── README.txt           # 사용자 가이드
```

## ⚙️ 빌드 옵션

**spec 파일** (`WiiVC-Injector.spec`)에서 다음을 커스터마이징 가능:

- `--onefile`: 단일 파일 빌드 (현재 설정)
- `--windowed`: 콘솔 창 숨김 (현재 설정)
- `--icon`: 아이콘 파일 경로
- `--add-data`: 추가 리소스 파일
- `excludes`: 제외할 모듈 (용량 최적화)

## 🔍 트러블슈팅

### PyInstaller 오류

```bash
pip install --upgrade pyinstaller
```

### 임포트 오류

spec 파일의 `hiddenimports`에 누락된 모듈 추가:

```python
hiddenimports = [
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'PIL',
    # 추가 모듈...
]
```

### 리소스 파일 누락

`datas`에 리소스 경로 추가:

```python
datas = [
    (resources_path, 'resources'),
    # 추가 리소스...
]
```

## 📊 예상 파일 크기

- **실행 파일**: ~40-60 MB (PyQt5, Pillow 포함)
- **압축 후**: ~20-30 MB (UPX 사용 시)

## 🚀 배포

`release/` 폴더의 내용을 ZIP으로 압축하여 배포:

```bash
# Windows
powershell Compress-Archive -Path release\* -DestinationPath WiiVC-Injector-v1.0.0-Windows.zip

# Linux/Mac
zip -r WiiVC-Injector-v1.0.0.zip release/
```

## ⚡ 빠른 테스트

빌드 후 즉시 실행:

```bash
cd release
WiiVC-Injector.exe
```

## 🔧 고급 옵션

### UPX 압축 비활성화

spec 파일에서 `upx=False` 설정

### 디버그 빌드

spec 파일에서 `debug=True`, `console=True` 설정

### 멀티 파일 빌드

`--onedir` 옵션 사용 (더 빠른 실행)
