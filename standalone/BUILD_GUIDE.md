# 빌드 가이드

## 빠른 시작

```bash
# 프로젝트 루트에서
python standalone/build.py
```

## 상세 과정

### 1. 준비사항 확인

빌드 전에 다음 사항을 확인하세요:

- Python 3.8 이상 설치
- 모든 프로젝트 의존성 설치 완료:
  ```bash
  pip install PyQt5 Pillow requests
  ```

### 2. 빌드 실행

```bash
cd standalone
python build.py
```

또는

```bash
python standalone/build.py
```

### 3. 빌드 과정

빌드 스크립트는 다음 작업을 자동으로 수행합니다:

1. **정리**: 이전 빌드 결과물 삭제
2. **의존성 확인**: PyInstaller 자동 설치 (필요시)
3. **EXE 빌드**: PyInstaller로 단일 실행 파일 생성
4. **릴리스 패키지 생성**: 필요한 파일들을 release/ 폴더에 복사

### 4. 빌드 결과

빌드가 완료되면:

```
standalone/
└── release/
    ├── WiiVC-Injector.exe    # 실행 파일 (약 100-200MB)
    ├── core/                  # 변환 도구
    ├── resources/             # 리소스 파일
    └── README.txt             # 사용 설명서
```

### 5. 배포

`standalone/release/` 폴더를 압축하여 배포:

```bash
# 7-Zip 사용 예시
7z a WiiVC-Injector-v1.0.zip standalone/release/*
```

## 문제 해결

### PyInstaller 오류

```bash
# PyInstaller 재설치
pip uninstall pyinstaller
pip install pyinstaller
```

### 빌드 크기가 너무 큼

build.py의 `--exclude-module` 옵션에 사용하지 않는 패키지를 추가하세요.

### 리소스 파일을 찾을 수 없음

- `resources/` 폴더가 프로젝트 루트에 있는지 확인
- `core/` 폴더가 프로젝트 루트에 있는지 확인

## 빌드 옵션

build.py를 수정하여 다음 옵션을 변경할 수 있습니다:

- `--onefile`: 단일 파일 (기본값)
- `--onedir`: 폴더 형태로 빌드
- `--windowed`: 콘솔 창 숨김 (기본값)
- `--console`: 콘솔 창 표시 (디버깅용)

## 테스트

빌드 후 반드시 다음을 테스트하세요:

1. EXE 파일 실행
2. 설정 저장/불러오기
3. 게임 파일 추가
4. 빌드 프로세스 실행

## 최적화 팁

- 불필요한 의존성 제거
- 이미지 최적화 (PNG 압축)
- 코드 난독화 (선택사항)
