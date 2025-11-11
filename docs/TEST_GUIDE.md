# 테스트 가이드

## 설치

```bash
cd python_version
pip install -r requirements.txt
```

## 실행

```bash
python run.py
```

또는

```bash
python -m wiivc_injector.main
```

## 테스트 체크리스트

### UI 기본 동작
- [ ] 프로그램 실행되는가?
- [ ] 메인 윈도우 표시되는가?
- [ ] 5개 탭 (Source Files, Source Files 2, Meta, Advanced, Build) 표시되는가?
- [ ] 시스템 타입 라디오 버튼 (Wii Retail, Wii Homebrew, Wii NAND, GC Retail) 동작하는가?

### Source Files 탭
- [ ] "Select Game..." 버튼 클릭 시 파일 다이얼로그 열리는가?
- [ ] ISO 파일 선택 시:
  - [ ] 파일 경로 표시되는가?
  - [ ] Title ID 자동 추출되는가?
  - [ ] Game Name 자동 추출되는가?
- [ ] "Select Icon..." 버튼으로 이미지 선택 가능한가?
- [ ] 아이콘 선택 시 프리뷰 표시되는가?
- [ ] "Select Banner..." 버튼 동작하는가?
- [ ] 배너 프리뷰 표시되는가?

### Source Files 2 탭
- [ ] DRC 이미지 선택 가능한가?
- [ ] Logo 이미지 선택 가능한가?
- [ ] Boot Sound 선택 가능한가?
- [ ] GC2 파일 선택 가능한가?
- [ ] Boot Sound Loop 체크박스 동작하는가?

### Meta 탭
- [ ] Packed Title 입력 필드 동작하는가?
- [ ] Enable Line 2 체크박스 동작하는가?
- [ ] Packed Title ID 입력 가능한가?
- [ ] GamePad Mode 라디오 버튼들 동작하는가?
- [ ] LR Patch 체크박스 동작하는가?

### Advanced 탭
- [ ] Ancast Key 입력 필드 동작하는가?
- [ ] Save Ancast Key 버튼 있는가?
- [ ] C2W Patcher 체크박스 동작하는가?
- [ ] Custom Main DOL 옵션 동작하는가?
- [ ] 모든 체크박스들 동작하는가?

### Build 탭
- [ ] Requirements 체크리스트 표시되는가?
- [ ] Wii U Common Key 입력 필드 있는가?
- [ ] Title Key 입력 필드 있는가?
- [ ] Save 버튼들 동작하는가?
- [ ] Progress bar 표시되는가?
- [ ] BUILD 버튼 클릭 가능한가?
- [ ] BUILD 버튼 클릭 시 메시지 표시되는가?

### 다이얼로그
- [ ] Settings 버튼 클릭 시 설정 창 열리는가?
  - [ ] Banners Repository 입력 가능한가?
  - [ ] Output Directory 선택 가능한가?
  - [ ] OK/Cancel 버튼 동작하는가?
- [ ] SD Card Stuff 버튼 클릭 시 SD 카드 창 열리는가?
  - [ ] Drive 목록 표시되는가?
  - [ ] Reload 버튼 동작하는가?
  - [ ] Nintendont Options 리스트 동작하는가?
  - [ ] Memory Card/Video 설정 표시되는가?

### 리소스 & 경로
- [ ] wiitdb.txt 파일이 resources/ 에 있는가?
- [ ] 임시 디렉토리 생성되는가?
- [ ] 프로그램 종료 시 임시 디렉토리 정리되는가?

## 알려진 제한사항

1. **TOOLDIR.zip 없음** - 외부 툴(wit, chdman 등) 아직 포함 안됨
2. **빌드 기능 미구현** - BUILD 버튼은 placeholder 메시지만 표시
3. **네트워크 기능 없음** - Repository 다운로드 미구현
4. **오디오 처리 없음** - Boot Sound 변환 미구현
5. **암호화 키 검증 없음** - 키 유효성 체크 미구현

## 에러 발생 시

로그 확인:
```bash
python run.py 2>&1 | tee log.txt
```

## 개발자 모드

디버그 출력 보려면:
```python
# main_window.py에서
import logging
logging.basicConfig(level=logging.DEBUG)
```
