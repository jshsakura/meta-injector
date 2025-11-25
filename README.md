# 🎮 Meta-Injector

**한국어 | [English](README.en.md)**

배치 처리와 자동 메타데이터 가져오기를 지원하는 향상된 Wii 버추얼 콘솔 인젝터입니다.

## ✨ 주요 기능

### 핵심 기능
- ✅ **손상된 소프트웨어 오류 해결**: 올바른 TIK/TMD 처리로 설치 오류 방지
- ✅ **다중 버전 설치**: 랜덤 ID 생성으로 같은 게임의 여러 버전 설치 가능
- ✅ **정확한 메타데이터**: ISO/WBFS 파일에서 직접 게임 코드 읽기
- ✅ **안전한 처리**: 임시 폴더 사용으로 원본 파일 보호
- ✅ **다양한 포맷 지원**: WBFS, ISO, NKIT, 복호화된 ISO (.iso.dec), 게임큐브 (.gcm)

### 배치 처리
- 🚀 **대량 주입**: 여러 게임 동시 처리
- 📊 **진행률 추적**: 대기열의 각 게임에 대한 실시간 상태 표시
- 🎨 **자동 이미지 다운로드**: GameTDB에서 아이콘과 배너 자동 가져오기
- 🌍 **다국어 지원**: 한국어 및 영어 UI
- 🎮 **게임패드 프로필**: Galaxy 패치 포함 7가지 컨트롤러 구성

### 이미지 & 메타데이터
- 🖼️ **스마트 이미지 캐싱**: 영구 캐시로 후속 빌드 속도 향상
- 🌐 **GameTDB 통합**: 게임 제목 및 커버 아트 자동 가져오기
- 🔍 **호환성 데이터베이스**: 게임패드 호환성 정보 내장
- ✏️ **간편한 편집**: GUI를 통한 게임 메타데이터, 제목, 이미지 편집

## 📋 요구사항

- **Python 3.8+** (소스에서 실행 시)
- **PyQt5** - GUI 프레임워크
- **Pillow** - 이미지 처리
- **Wii U Common Key** - 복호화에 필수
- **베이스 타이틀 키** - 최소한 Rhythm Heaven Fever (USA) 필요
  - 선택사항: Xenoblade Chronicles (USA), Super Mario Galaxy 2 (EUR)

## 🚀 빠른 시작

### 옵션 1: 독립 실행 파일 (권장)

[Releases 페이지](https://github.com/yourusername/Meta-Injector/releases)에서 최신 릴리스를 다운로드하고 `Meta-Injector.exe`를 실행하세요.

### 옵션 2: 소스에서 실행

1. **저장소 클론**
```bash
git clone https://github.com/yourusername/Meta-Injector.git
cd Meta-Injector
```

2. **의존성 설치**
```bash
pip install -r requirements.txt
```

3. **애플리케이션 실행**
```bash
python run.py
```

### 초기 설정

1. **⚙ 설정** 버튼 클릭
2. 암호화 키 입력:
   - **Wii U Common Key** (필수)
   - **Rhythm Heaven Fever Title Key** (필수)
   - **Xenoblade Chronicles Title Key** (선택)
   - **Super Mario Galaxy 2 Title Key** (선택)
3. 출력 디렉토리 설정 (선택사항 - 기본값은 게임 디렉토리)
4. **저장** 클릭

### 게임 빌드하기

#### 단일 게임 빌드
1. **파일 추가**를 클릭하고 Wii 게임 선택
2. 자동 메타데이터 및 이미지 다운로드 대기
3. (선택사항) **편집**을 클릭하여 제목, 이미지 또는 베이스 ROM 사용자 지정
4. 드롭다운에서 게임패드 프로필 선택
5. **빌드 시작** 클릭

#### 배치 빌드
1. **파일 추가**를 클릭하고 여러 게임 선택
2. 자동 다운로드가 모든 게임의 아이콘/배너를 가져옴
3. 필요에 따라 게임 검토 및 편집
4. **빌드 시작**을 클릭하여 모든 게임 처리

## 📁 프로젝트 구조

```
Meta-Injector/
├── src/                           # Python 소스 코드
│   ├── main.py                    # 애플리케이션 진입점
│   ├── batch_window.py            # 메인 GUI (배치 모드)
│   ├── batch_builder.py           # 배치 빌드 엔진
│   ├── build_engine.py            # 핵심 빌드 로직
│   ├── game_info.py               # 게임 메타데이터 추출
│   ├── game_tdb.py                # GameTDB 통합
│   ├── compatibility_db.py        # 호환성 데이터베이스
│   ├── image_utils.py             # 이미지 변환 (PNG→TGA)
│   ├── paths.py                   # 경로 관리
│   ├── translations.py            # 다국어 지원
│   ├── resources.py               # 리소스 경로 처리
│   └── utils.py                   # 유틸리티 함수
│
├── core/                          # 외부 도구
│   ├── EXE/                       # 핵심 실행 파일
│   │   ├── nfs2iso2nfs.exe        # NFS 변환기
│   │   ├── jnustool.exe           # 베이스 파일 다운로더
│   │   ├── nuspacker.exe          # WUP 패키저
│   │   └── wbfs_file.exe          # WBFS 변환기
│   ├── WIT/                       # Wiimms ISO Tools
│   │   ├── wit.exe                # Wii ISO Tool
│   │   └── wstrt.exe              # String table tool
│   ├── Galaxy1GamePad_v1.2/       # Super Mario Galaxy 패치
│   │   ├── *-AllStars.gct         # AllStars 컨트롤러 프로필
│   │   └── *-Nvidia.gct           # Nvidia Shield 프로필
│   └── NKIT/                      # NKit 변환기
│       └── NKit.dll               # NKit 라이브러리
│
├── resources/                     # 애플리케이션 리소스
│   ├── images/                    # UI 이미지
│   │   ├── icon.ico               # 앱 아이콘
│   │   ├── icon.png               # UI용 아이콘
│   │   ├── default_icon.png       # 기본 게임 아이콘
│   │   ├── default_banner.png     # 기본 TV 배너
│   │   └── default_drc.png        # 기본 GamePad 이미지
│   └── wiitdb.txt                 # 게임 데이터베이스 (타이틀)
│
├── run.py                         # 진입점 스크립트
├── build.py                       # PyInstaller 빌드 스크립트
├── requirements.txt               # Python 의존성
├── README.md                      # 이 파일 (한국어)
└── README.en.md                   # 영문 README
```

## 🔧 빌드 프로세스

빌드 엔진은 다음 워크플로우를 따릅니다:

1. **베이스 파일 다운로드** (최초 1회만)
   - JNUSTool을 사용하여 Nintendo CDN에서 베이스 ROM 가져오기
   - `%PROGRAMDATA%\JNUSToolDownloads\`에 캐시

2. **게임 메타데이터 추출**
   - ISO/WBFS에서 게임 ID, 제목, 지역 읽기
   - 호환성 데이터베이스 검색

3. **이미지 다운로드** (활성화된 경우)
   - GameTDB에서 가져오기 (지역별 우선순위)
   - UWUVCI-IMAGES 저장소로 대체
   - 사용 불가능한 경우 기본 이미지 사용

4. **게임 파일 처리**
   - 필요시 WBFS를 ISO로 변환
   - WIT를 사용하여 추출 및 트리밍
   - TIK/TMD 파일 보존

5. **컨트롤러 패치 적용** (선택된 경우)
   - 게임패드 프로필 GCT 코드 주입
   - 7가지 프로필 지원
   - 특별 Galaxy 1 패치 사용 가능

6. **이미지 변환**
   - PNG를 TGA 포맷으로 변환
   - 리사이즈: 아이콘 (128x128), TV 배너 (1280x720), DRC (854x480)

7. **NFS 포맷으로 변환**
   - Wii U 파일시스템용 nfs2iso2nfs 사용

8. **WUP 설치 가능 파일 패킹**
   - NUSPacker로 설치 가능한 패키지 생성
   - 구성된 디렉토리로 출력

## 🎮 게임패드 프로필

| 프로필 | 설명 | 사용 사례 |
|---------|-------------|----------|
| **No Pad (Wiimote)** | Wii 리모컨만 | 모션 컨트롤 게임 |
| **Pad CC** | 클래식 컨트롤러 | 가장 호환성 높음 |
| **Pad CC+LR** | L2/R2 트리거가 있는 CC | 트리거가 필요한 게임 |
| **Pad Wiimote(↕)** | 세로 Wiimote | 세로 방향 게임 |
| **Pad Wiimote(↔)** | 가로 Wiimote | 가로 게임 (예: NSMB) |
| **Galaxy Patch(AllStars)** | SMG 최적화 | Super Mario Galaxy (AllStars 스타일) |
| **Galaxy Patch(Nvidia)** | SMG 대체 | Super Mario Galaxy (Nvidia Shield) |

## 🗂️ 저장 위치

### 임시 파일
- **빌드 임시**: `%TEMP%\MetaInjector\`
  - `SOURCETEMP/` - 게임 추출 작업 공간
  - `BUILDDIR/` - 활성 빌드 디렉토리
  - `TOOLDIR/` - 임시 도구 복사본
  - 성공적인 빌드 후 자동 정리

### 영구 캐시
- **베이스 파일**: `%PROGRAMDATA%\JNUSToolDownloads\`
  - 다운로드된 베이스 ROM (빌드 간 공유)
- **이미지 캐시**: `%TEMP%\MetaInjector\IMAGECACHE\`
  - 다운로드된 게임 커버 및 배너

### 설정
- **사용자 설정**: `%USERPROFILE%\.meta_injector_settings.json`
  - 암호화 키 (로컬 저장)
  - 출력 디렉토리 기본 설정
- **호환성 DB**: `%USERPROFILE%\.meta_injector_compatibility.db`
  - 게임패드 호환성 정보가 있는 SQLite 데이터베이스

## 🎯 주요 개선 사항

### TeconMoon의 WiiVC Injector 대비
- ✅ TIK/TMD 추출 (손상된 소프트웨어 오류 방지)
- ✅ 랜덤 ID 생성 (다중 설치 가능)
- ✅ ISO에서 게임 코드 읽기 (정확한 메타데이터)
- ✅ 배치 처리 지원
- ✅ 자동 이미지 다운로드

## 📊 기술적 세부사항

### 메타데이터 추출
```python
# ISO 헤더에서 게임 ID (오프셋 0x0)
game_id = iso_data[0x0:0x6].decode('ascii')

# opening.bnr에서 제목
title = extract_from_opening_bnr(iso_path)

# Title ID 생성
title_id = f"00050000{game_id[:4].encode().hex().upper()}"
```

### 랜덤 ID 생성
```python
# 각 빌드는 고유한 랜덤 ID를 받아 다중 설치 허용
title_id = f"00050002{secrets.token_hex(4).upper()}"
product_code = secrets.token_hex(2).upper()
```

### 이미지 다운로드 우선순위
```python
# 1. 원본 게임 ID (예: RVYK52)
# 2. 대체 ID (같은 이름, 다른 지역)
# 3. 접두사 일치 (처음 3자)

# 게임 기반 지역 우선순위
if game_id[3] == 'K':  # 한국
    region_codes = ['KO', 'EN', 'US', 'JA']
elif game_id[3] == 'J':  # 일본
    region_codes = ['JA', 'EN', 'US', 'KO']
elif game_id[3] == 'P':  # 유럽
    region_codes = ['EN', 'US', 'JA', 'KO']
else:  # 미국
    region_codes = ['US', 'EN', 'JA', 'KO']
```

## 🏗️ 독립 실행 파일 빌드

독립 실행 파일을 만들려면:

```bash
python build.py
```

실행 파일은 `dist/Meta-Injector.exe`에 생성되며 다음을 포함합니다:
- 모든 Python 의존성
- 핵심 도구 (WIT, nfs2iso2nfs 등)
- 리소스 (이미지, 데이터베이스)
- 단일 파일 배포 (~80MB)

## ⚠️ 알려진 문제 및 제한사항

- **Windows 전용**: Windows 전용 경로 및 실행 파일 사용
- **유효한 키 필요**: 합법적인 Wii U 암호화 키가 있어야 함
- **베이스 ROM 다운로드**: 최초 베이스 파일 다운로드 시 인터넷 연결 필요
- **대용량 파일 지원**: 4GB 이상의 ISO는 처리에 몇 분 소요될 수 있음

## 🐛 문제 해결

### Wii U에서 "손상된 소프트웨어" 오류
- 유효한 암호화 키를 사용하고 있는지 확인
- 베이스 파일이 올바르게 다운로드되었는지 확인
- 다른 베이스 ROM 사용 시도 (Xenoblade/Galaxy 2)

### 이미지가 다운로드되지 않음
- 인터넷 연결 확인
- GameTDB가 일시적으로 사용 불가능할 수 있음
- 수동 이미지 선택 사용 (테이블에서 아이콘/배너 클릭)

### "nfs2iso2nfs 오류"로 빌드 실패
- ISO가 손상되었을 수 있음 - 다시 덤프 시도
- 파일 경로에 특수 문자 확인
- 충분한 디스크 공간 확보 (15GB+ 여유 권장)

## 🙏 크레딧 및 감사

### 원본 프로젝트
- **[TeconMoon's WiiVC Injector](https://github.com/Teconmoon/WiiVC-Injector)** - 원본 C# 인젝터, 간단하고 효과적
- **[UWUVCI-AIO-WPF](https://github.com/stuff-by-3-random-dudes/UWUVCI-AIO-WPF)** - TIK/TMD 처리, 랜덤 ID 생성
- **[Wiimm's ISO Tools (WIT)](https://wit.wiimm.de/)** - 필수 Wii ISO 조작 도구
- **[nfs2iso2nfs](https://github.com/VitaSmith/nfs2iso2nfs)** - NFS 파일시스템 변환

### 도구 및 리소스
- **JNUSTool** - Nintendo CDN 다운로더
- **NUSPacker** - WUP 패키지 생성기
- **GameTDB** - 게임 메타데이터 및 아트워크
- **NKit** - ISO 검증 및 처리

### 디자인
- **[Kiran Shastry](https://www.flaticon.com/kr/authors/kiranshastry)** - 애플리케이션 아이콘 디자인 (Flaticon)

### 커뮤니티
- **GBAtemp** - 연구 및 테스트 커뮤니티
- **WiiU Homebrew Community** - 도구 및 문서

## 📝 라이선스

이 프로젝트는 교육 목적으로만 사용됩니다. 다음의 합법적인 사본을 소유해야 합니다:
- 인젝트하는 게임
- 베이스 Wii U 버추얼 콘솔 타이틀 (Rhythm Heaven Fever 등)
- 암호화 키에 대한 합법적 접근 권한이 있는 Wii U 콘솔

이 소프트웨어와 함께 저작권이 있는 파일(키, ROM, 베이스 파일)은 배포되지 않습니다.

## 🔗 관련 프로젝트

- [TeconMoon's WiiVC Injector](https://github.com/Teconmoon/WiiVC-Injector) - 원본 C# 구현
- [UWUVCI-AIO-WPF](https://github.com/stuff-by-3-random-dudes/UWUVCI-AIO-WPF) - 멀티 콘솔 인젝터
- [Wii Backup Manager](http://www.wiibackupmanager.co.uk/) - Wii 게임 관리
- [Wiimm's ISO Tools](https://wit.wiimm.de/) - 커맨드 라인 ISO 도구

---

**WiiU 홈브루 커뮤니티를 위해 ❤️를 담아 제작**

*현재 버전: 1.0.0-beta*
