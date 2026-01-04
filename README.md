# Meta-Injector

**한국어 | [English](README.en.md)**

Wii 게임을 Wii U 버추얼 콘솔(VC)로 변환하는 도구입니다.

## 주요 기능

- **배치 변환**: 여러 게임을 한 번에 변환
- **자동 이미지**: GameTDB에서 아이콘/배너 자동 다운로드
- **컨트롤러 패치**: CC 패치, Galaxy 패치, GCT 패치 지원
- **다양한 포맷**: WBFS, ISO, NKIT, GCM 지원

## 시스템 요구사항

- Windows 10/11
- **Wii U Common Key**
- **베이스 타이틀 키** (Rhythm Heaven Fever 등)

## 설치

[Releases](https://github.com/jshsakura/meta-injector/releases)에서 `Meta-Injector.exe`를 다운로드하여 실행하세요.

## 사용 방법

### 1. 초기 설정

1. **설정** 버튼 클릭
2. Wii U Common Key 입력
3. 베이스 타이틀 키 입력 (최소 1개)
4. 저장

### 2. 게임 변환

1. **파일 추가**로 게임 파일 선택 (.wbfs, .iso 등)
2. 자동으로 게임 정보와 이미지를 가져옴
3. 필요시 **편집**에서 제목/이미지 수정
4. 컨트롤러 옵션 선택
5. **빌드 시작**

### 컨트롤러 옵션

| 옵션 | 설명 |
|------|------|
| Wiimote | 위모트 전용 |
| GamePad (CC) | 게임패드로 클래식 컨트롤러 에뮬레이션 |
| GamePad + LR | CC 에뮬레이션 + LR 버튼 패치 |
| Galaxy Patch | 갤럭시 시리즈 전용 (포인터→스틱) |
| GCT Patch | 사용자 정의 GCT 코드 적용 |

### 편집 기능

- **제목 수정**: 게임 제목 변경
- **이미지 변경**: 아이콘, 배너, 게임패드 화면 개별 설정
- **자동 복원**: 수정한 이미지를 자동 다운로드 이미지로 복원
- **트림 비활성화**: 세이브 문제가 있는 게임용 (슈퍼 페이퍼 마리오 등)

## 문제 해결

| 문제 | 해결 방법 |
|------|----------|
| 손상된 소프트웨어 오류 | Common Key와 타이틀 키 확인 |
| 이미지 다운로드 실패 | 인터넷 연결 확인 또는 수동 이미지 설정 |
| 빌드 실패 | 파일 경로에 특수문자 확인, 로그 확인 |

## 크레딧

- TeconMoon's WiiVC Injector
- UWUVCI-AIO-WPF
- Wiimm's ISO Tools (WIT)
- GameTDB
- JNUSTool, NUSPacker, nfs2iso2nfs

---
**Wii U 홈브루 커뮤니티를 위해 제작되었습니다.**
