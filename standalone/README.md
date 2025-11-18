# Standalone Build

이 폴더는 WiiVC Injector를 단독 실행 가능한 EXE 파일로 빌드하는 데 사용됩니다.

## 빌드 방법

```bash
# standalone 폴더에서 실행
python build.py
```

또는 프로젝트 루트에서:

```bash
python standalone/build.py
```

## 빌드 결과

빌드가 완료되면 다음 구조로 파일이 생성됩니다:

```
standalone/
├── release/
│   ├── WiiVC-Injector.exe    # 단독 실행 파일
│   ├── core/                  # 변환 도구들
│   ├── resources/             # 리소스 파일
│   └── README.txt             # 사용 설명서
├── dist/                      # PyInstaller 출력
└── build/                     # PyInstaller 임시 파일
```

## 배포

`standalone/release/` 폴더 전체를 압축하여 배포하면 됩니다.

## 요구사항

- Python 3.8 이상
- PyInstaller (자동 설치됨)
- 모든 프로젝트 의존성 설치 완료

## 주의사항

- 빌드 시 약 100-200MB 크기의 exe 파일이 생성됩니다
- PyQt5와 모든 의존성이 포함되어 있어 별도 설치 없이 실행 가능합니다
- Windows 10/11에서 테스트되었습니다
