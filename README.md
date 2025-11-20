# WiiU Expedition VC Injector (위유 원정대 VC 인젝터)

Wii/GameCube 게임을 Wii U Virtual Console 형식으로 변환하는 배치 빌드 도구

## About

TeconMoon의 WiiVC Injector를 Python/PyQt5로 완전히 재작성한 버전입니다.
원본 C# 버전: [GBAtemp Thread](https://gbatemp.net/threads/release-wiivc-injector-script-gc-wii-homebrew-support.483577/)

## Features

- **배치 변환** - 여러 게임을 한 번에 변환
- **병렬 다운로드** - 8개 동시 다운로드로 빠른 처리
- **자동 이미지 다운로드** - GameTDB에서 아이콘/배너 자동 다운로드
- **한글 게임명 지원** - GameTDB에서 한글 타이틀 자동 가져오기
- **게임패드 호환성 DB** - 호환성 정보 기반 자동 설정
- **커스텀 이미지** - 아이콘(128x128), 배너(1280x720), DRC(854x480) 자동 리사이징
- **한국어/영어 UI** - 다국어 지원

## Requirements

- Python 3.8+
- Windows (외부 도구 의존성)

## Installation

```bash
# 의존성 설치
pip install -r requirements.txt

# 실행
python run.py
```

## Standalone Build

```bash
cd standalone
python build.py
```

결과물: `standalone/dist/WiiU-Expedition-VC-Injector.exe`

## Usage

1. **암호화 키 설정** - 설정 > 암호화 키에서 Common Key와 Title Key 입력
2. **게임 추가** - 게임 추가 버튼으로 ISO/WBFS 파일 선택
3. **설정 확인** - 패드 옵션, 게임명 등 확인/수정
4. **빌드 시작** - 빌드 시작 버튼으로 변환 시작
5. **결과 확인** - 출력 폴더에서 WUP 패키지 확인

## Encryption Keys

이 도구는 암호화 키를 **포함하지 않습니다**.
사용자가 합법적으로 획득한 키를 직접 입력해야 합니다.

- **Common Key** - Wii U 공통 키 (32자리 hex)
- **Title Key** - 호스트 게임 타이틀 키 (32자리 hex)

## Project Structure

```
WiiU-Expedition-VC-Injector/
├── src/wiivc_injector/     # 메인 애플리케이션
│   ├── batch_window.py     # 배치 빌드 UI
│   ├── batch_builder.py    # 배치 빌드 엔진
│   ├── build_engine.py     # 빌드 로직
│   ├── compatibility_db.py # 호환성 DB
│   ├── game_info.py        # 게임 정보 추출
│   ├── game_tdb.py         # GameTDB 연동
│   ├── image_utils.py      # 이미지 처리
│   └── translations.py     # 번역
├── resources/              # 리소스 파일
│   ├── core.zip           # 외부 도구
│   └── images/            # 기본 이미지
├── standalone/            # 빌드 스크립트
└── run.py                 # 실행 스크립트
```

## Image Sources

이미지는 다음 소스에서 자동 다운로드됩니다:
- [GameTDB](https://www.gametdb.com/) - 커버/배너 이미지, 게임 정보
- [UWUVCI-IMAGES](https://github.com/UWUVCI-PRIME/UWUVCI-IMAGES) - 대체 이미지

## Legal Notice

**이 도구는 교육 목적과 개인 백업용입니다.**

- 반드시 원본 게임을 소유하고 있어야 합니다
- 암호화 키는 사용자가 합법적으로 획득해야 합니다
- 게임 파일 배포는 불법입니다

## Credits

- **원작자**: TeconMoon (C# 버전)
- **Python 버전**: WiiU Expedition Team (위유 원정대)
- **이미지 소스**: GameTDB, UWUVCI-PRIME

## License

원본 프로젝트와 동일한 라이선스를 따릅니다.

---

**위유 원정대 (WiiU Expedition)** - Wii U Virtual Console로의 여행
