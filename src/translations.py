"""Multi-language support for WiiVC Injector."""

class Translations:
    """Translation manager for multi-language support."""

    # Current language
    current_language = "en"  # Default: English

    # All translations
    STRINGS = {
        # Window titles
        "app_title": {
            "en": "WiiU Expedition VC Injector",
            "ko": "WiiU Expedition VC 인젝터"
        },

        # Main menu and buttons
        "settings": {
            "en": "Settings",
            "ko": "설정"
        },
        "sd_card_utilities": {
            "en": "SD Card Utilities",
            "ko": "SD 카드 유틸리티"
        },

        # System type
        "system_type": {
            "en": "System Type",
            "ko": "시스템 타입"
        },
        "wii_retail": {
            "en": "Wii Retail",
            "ko": "Wii 리테일"
        },
        "wii_homebrew": {
            "en": "Wii Homebrew",
            "ko": "Wii 홈브루"
        },
        "wii_nand": {
            "en": "Wii NAND",
            "ko": "Wii NAND"
        },
        "gc_retail": {
            "en": "GC Retail",
            "ko": "GC 리테일"
        },

        # Tab names
        "tab_source_files": {
            "en": "Required Source Files",
            "ko": "필수 소스 파일"
        },
        "tab_images_sound": {
            "en": "Optional Source Files",
            "ko": "선택적 소스 파일"
        },
        "tab_meta_info": {
            "en": "GamePad/Meta Options",
            "ko": "게임패드/메타 옵션"
        },
        "tab_advanced": {
            "en": "Advanced",
            "ko": "고급"
        },
        "tab_build": {
            "en": "Build Title",
            "ko": "타이틀 빌드"
        },

        # Source Files Tab
        "game_iso_wbfs": {
            "en": "Game ISO/WBFS",
            "ko": "게임 ISO/WBFS"
        },
        "no_game_file_selected": {
            "en": "No game file selected",
            "ko": "게임 파일이 선택되지 않음"
        },
        "game_information": {
            "en": "Game Information",
            "ko": "게임 정보"
        },
        "internal_name_na": {
            "en": "Internal Name: N/A",
            "ko": "내부 이름: 없음"
        },
        "title_id_na": {
            "en": "Title ID: N/A",
            "ko": "타이틀 ID: 없음"
        },
        "icon_banner_images": {
            "en": "Icon & Banner Images",
            "ko": "아이콘 & 배너 이미지"
        },
        "manual_icon": {
            "en": "Manual Icon",
            "ko": "수동 아이콘"
        },
        "manual_banner": {
            "en": "Manual Banner",
            "ko": "수동 배너"
        },
        "auto_download": {
            "en": "Auto Download",
            "ko": "자동 다운로드"
        },
        "no_icon": {
            "en": "No icon",
            "ko": "아이콘 없음"
        },
        "no_banner": {
            "en": "No banner",
            "ko": "배너 없음"
        },

        # Images & Sound Tab
        "drc_image": {
            "en": "GamePad (DRC) Image (854x480)",
            "ko": "게임패드 (DRC) 이미지 (854x480)"
        },
        "no_drc_image": {
            "en": "No DRC image selected",
            "ko": "DRC 이미지가 선택되지 않음"
        },
        "logo_image": {
            "en": "Logo Image (170x42)",
            "ko": "로고 이미지 (170x42)"
        },
        "no_logo": {
            "en": "No logo selected",
            "ko": "로고가 선택되지 않음"
        },
        "boot_sound": {
            "en": "Boot Sound",
            "ko": "부팅 사운드"
        },
        "select_wav_file": {
            "en": "Select WAV File...",
            "ko": "WAV 파일 선택..."
        },
        "preview": {
            "en": "Preview",
            "ko": "미리보기"
        },
        "no_sound_file": {
            "en": "No sound file selected",
            "ko": "사운드 파일이 선택되지 않음"
        },
        "loop_boot_sound": {
            "en": "Loop Boot Sound",
            "ko": "부팅 사운드 반복"
        },
        "second_disc_gc": {
            "en": "Second Disc (GameCube only)",
            "ko": "두 번째 디스크 (게임큐브만)"
        },
        "no_second_disc": {
            "en": "No second disc selected",
            "ko": "두 번째 디스크가 선택되지 않음"
        },

        # Meta Information Tab
        "game_title": {
            "en": "Game Title",
            "ko": "게임 제목"
        },
        "enter_game_title": {
            "en": "Enter game title (required)",
            "ko": "게임 제목 입력 (필수)"
        },
        "enable_second_line": {
            "en": "Enable second line",
            "ko": "두 번째 줄 활성화"
        },
        "optional_second_line": {
            "en": "Optional second line",
            "ko": "선택적 두 번째 줄"
        },
        "title_line_1": {
            "en": "Title Line 1:",
            "ko": "제목 줄 1:"
        },
        "title_line_2": {
            "en": "Title Line 2:",
            "ko": "제목 줄 2:"
        },
        "title_id": {
            "en": "Title ID",
            "ko": "타이틀 ID"
        },
        "title_id_placeholder": {
            "en": "16-digit hex (e.g., 00050000XXXXXXXX)",
            "ko": "16자리 16진수 (예: 00050000XXXXXXXX)"
        },
        "gamepad_emulation_mode": {
            "en": "GamePad Emulation Mode",
            "ko": "게임패드 에뮬레이션 모드"
        },
        "no_emulation": {
            "en": "No Emulation",
            "ko": "에뮬레이션 없음"
        },
        "cc_emulation": {
            "en": "Classic Controller Emulation",
            "ko": "클래식 컨트롤러 에뮬레이션"
        },
        "force_cc": {
            "en": "Force Classic Controller",
            "ko": "클래식 컨트롤러 강제"
        },
        "force_no_cc": {
            "en": "Force No Classic Controller",
            "ko": "클래식 컨트롤러 강제 비활성화"
        },
        "horizontal_wiimote": {
            "en": "Horizontal Wiimote",
            "ko": "가로 위모트"
        },
        "vertical_wiimote": {
            "en": "Vertical Wiimote",
            "ko": "세로 위모트"
        },
        "enable_lr_patch": {
            "en": "Enable L/R Patch",
            "ko": "L/R 패치 활성화"
        },

        # Advanced Tab
        "ancast_key": {
            "en": "Ancast Key (for C2W Patcher)",
            "ko": "Ancast 키 (C2W 패처용)"
        },
        "enter_ancast_key": {
            "en": "Enter Ancast key...",
            "ko": "Ancast 키 입력..."
        },
        "save": {
            "en": "Save",
            "ko": "저장"
        },
        "advanced_options": {
            "en": "Advanced Options",
            "ko": "고급 옵션"
        },
        "enable_c2w_patcher": {
            "en": "Enable C2W Patcher",
            "ko": "C2W 패처 활성화"
        },
        "use_custom_main_dol": {
            "en": "Use Custom Main DOL",
            "ko": "사용자 정의 Main DOL 사용"
        },
        "force_43_nintendont": {
            "en": "Force 4:3 (Nintendont)",
            "ko": "4:3 강제 (Nintendont)"
        },
        "force_interlaced": {
            "en": "Force Interlaced (Nintendont)",
            "ko": "인터레이스 강제 (Nintendont)"
        },
        "disable_passthrough": {
            "en": "Disable Passthrough",
            "ko": "패스스루 비활성화"
        },
        "force_43_nand": {
            "en": "Force 4:3 (NAND)",
            "ko": "4:3 강제 (NAND)"
        },
        "disable_iso_trimming": {
            "en": "Disable ISO Trimming",
            "ko": "ISO 트리밍 비활성화"
        },
        "disable_nintendont_autoboot": {
            "en": "Disable Nintendont Autoboot",
            "ko": "Nintendont 자동부팅 비활성화"
        },
        "disable_gamepad": {
            "en": "Disable GamePad",
            "ko": "게임패드 비활성화"
        },
        "wii_video_mode_changer": {
            "en": "Wii Video Mode Changer",
            "ko": "Wii 비디오 모드 체인저"
        },
        "wiimmfi_patch": {
            "en": "Wiimmfi Patch",
            "ko": "Wiimmfi 패치"
        },
        "c2w_description": {
            "en": "Enables GameCube to Wii controller patching for better compatibility",
            "ko": "더 나은 호환성을 위한 GameCube → Wii 컨트롤러 패칭 활성화"
        },
        "trimming_description": {
            "en": "Keep full ISO without trimming unused space (may improve compatibility)",
            "ko": "사용하지 않는 공간을 자르지 않고 전체 ISO 유지 (호환성 향상 가능)"
        },
        "custom_main_dol_file": {
            "en": "Custom Main DOL File",
            "ko": "사용자 정의 Main DOL 파일"
        },
        "select_dol_file": {
            "en": "Select DOL File...",
            "ko": "DOL 파일 선택..."
        },
        "no_file_selected": {
            "en": "No file selected",
            "ko": "파일이 선택되지 않음"
        },

        # Build Tab
        "build_requirements": {
            "en": "Build Requirements",
            "ko": "빌드 요구사항"
        },
        "source_files_not_ready": {
            "en": "Source Files: Not ready",
            "ko": "소스 파일: 준비 안 됨"
        },
        "source_files_ready": {
            "en": "Source Files: Ready",
            "ko": "소스 파일: 준비됨"
        },
        "meta_info_not_ready": {
            "en": "Meta Info: Not ready",
            "ko": "메타 정보: 준비 안 됨"
        },
        "meta_info_ready": {
            "en": "Meta Info: Ready",
            "ko": "메타 정보: 준비됨"
        },
        "encryption_keys_not_ready": {
            "en": "Encryption Keys: Not ready",
            "ko": "암호화 키: 준비 안 됨"
        },
        "encryption_keys_ready": {
            "en": "Encryption Keys: Ready",
            "ko": "암호화 키: 준비됨"
        },
        "advanced_options_ok": {
            "en": "Advanced Options: OK",
            "ko": "고급 옵션: OK"
        },
        "encryption_keys": {
            "en": "Encryption Keys",
            "ko": "암호화 키"
        },
        "wii_u_common_key": {
            "en": "Wii U Common Key:",
            "ko": "Wii U 공용 키:"
        },
        "common_key_placeholder": {
            "en": "32-character hex key",
            "ko": "32자리 16진수 키"
        },
        "verify_and_save": {
            "en": "Verify & Save",
            "ko": "확인 및 저장"
        },
        "title_key_label": {
            "en": "Title Key:",
            "ko": "타이틀 키:"
        },
        "title_key_placeholder": {
            "en": "32-character hex key",
            "ko": "32자리 16진수 키"
        },
        "build_progress": {
            "en": "Build Progress",
            "ko": "빌드 진행"
        },
        "ready_to_build": {
            "en": "Ready to build",
            "ko": "빌드 준비됨"
        },
        "build_injection": {
            "en": "BUILD INJECTION",
            "ko": "빌드"
        },

        # Common buttons
        "browse": {
            "en": "Browse...",
            "ko": "찾아보기..."
        },
        "close": {
            "en": "Close",
            "ko": "닫기"
        },
        "ok": {
            "en": "OK",
            "ko": "확인"
        },
        "cancel": {
            "en": "Cancel",
            "ko": "취소"
        },
        "yes": {
            "en": "Yes",
            "ko": "예"
        },
        "no": {
            "en": "No",
            "ko": "아니오"
        },

        # File dialogs
        "select_game_file": {
            "en": "Select Game File",
            "ko": "게임 파일 선택"
        },
        "select_icon_image": {
            "en": "Select Icon Image",
            "ko": "아이콘 이미지 선택"
        },
        "select_banner_image": {
            "en": "Select Banner Image",
            "ko": "배너 이미지 선택"
        },
        "select_drc_image": {
            "en": "Select DRC Image",
            "ko": "DRC 이미지 선택"
        },
        "select_logo_image": {
            "en": "Select Logo Image",
            "ko": "로고 이미지 선택"
        },
        "select_boot_sound": {
            "en": "Select Boot Sound",
            "ko": "부팅 사운드 선택"
        },
        "select_second_disc": {
            "en": "Select Second Disc",
            "ko": "두 번째 디스크 선택"
        },
        "select_main_dol": {
            "en": "Select Main DOL",
            "ko": "Main DOL 선택"
        },
        "select_output_directory": {
            "en": "Select Output Directory",
            "ko": "출력 디렉토리 선택"
        },

        # Message boxes
        "success": {
            "en": "Success",
            "ko": "성공"
        },
        "error": {
            "en": "Error",
            "ko": "오류"
        },
        "warning": {
            "en": "Warning",
            "ko": "경고"
        },
        "info": {
            "en": "Information",
            "ko": "정보"
        },

        # NAND selection
        "nand_title_id_title": {
            "en": "vWii NAND Title ID",
            "ko": "vWii NAND 타이틀 ID"
        },
        "nand_title_id_prompt": {
            "en": "Enter your installed Wii Channel's 4-letter Title ID.\nIf you don't know it, open a WAD for the channel in ShowMiiWads.\n\nExample: NADE for Star Fox 64 (USA)",
            "ko": "설치된 Wii 채널의 4자리 타이틀 ID를 입력하세요.\n모르는 경우 ShowMiiWads에서 채널의 WAD를 열어보세요.\n\n예: Star Fox 64 (USA)의 경우 NADE"
        },
        "invalid_title_id": {
            "en": "Invalid Title ID",
            "ko": "잘못된 타이틀 ID"
        },
        "invalid_title_id_msg": {
            "en": "Only 4 characters can be used. Try again.\n\nExample: The Star Fox 64 (USA) Channel's Title ID is NADE01,\nso you would specify NADE as the Title ID",
            "ko": "4자만 사용할 수 있습니다. 다시 시도하세요.\n\n예: Star Fox 64 (USA) 채널의 타이틀 ID는 NADE01이므로,\nNADE를 타이틀 ID로 지정합니다"
        },

        # Repository download
        "no_game_selected": {
            "en": "No Game Selected",
            "ko": "게임이 선택되지 않음"
        },
        "no_game_selected_msg": {
            "en": "Please select your game before using this option.",
            "ko": "이 옵션을 사용하기 전에 게임을 선택하세요."
        },
        "images_not_found": {
            "en": "Images Not Found",
            "ko": "이미지를 찾을 수 없음"
        },
        "images_not_found_msg": {
            "en": "Could not find images for this game in the repository.\n\nTried IDs: {ids}\nSystem: {system}\n\nYou will need to provide your own images.\n\nWould you like to visit the GBAtemp request thread?",
            "ko": "저장소에서 이 게임의 이미지를 찾을 수 없습니다.\n\n시도한 ID: {ids}\n시스템: {system}\n\n자체 이미지를 제공해야 합니다.\n\nGBAtemp 요청 스레드를 방문하시겠습니까?"
        },
        "download_success": {
            "en": "Success!",
            "ko": "성공!"
        },
        "download_success_msg": {
            "en": "Successfully downloaded images for {id}!\n\nIcon: {icon_size:,} bytes\nBanner: {banner_size:,} bytes",
            "ko": "{id}의 이미지를 성공적으로 다운로드했습니다!\n\n아이콘: {icon_size:,} 바이트\n배너: {banner_size:,} 바이트"
        },
        "not_found": {
            "en": "Not Found",
            "ko": "찾을 수 없음"
        },
        "not_found_msg": {
            "en": "Images not found in repository for:\nGame ID: {game_id}\nSystem: {system}\n\nThe repository may not have images for this title.\n\nURL: {url}",
            "ko": "저장소에서 이미지를 찾을 수 없습니다:\n게임 ID: {game_id}\n시스템: {system}\n\n저장소에 이 타이틀의 이미지가 없을 수 있습니다.\n\nURL: {url}"
        },
        "download_error": {
            "en": "Download Error",
            "ko": "다운로드 오류"
        },
        "network_error": {
            "en": "Network Error",
            "ko": "네트워크 오류"
        },
        "network_error_msg": {
            "en": "Failed to connect to repository:\n{error}\n\nPlease check your internet connection.",
            "ko": "저장소에 연결하지 못했습니다:\n{error}\n\n인터넷 연결을 확인하세요."
        },

        # Game info
        "game_info_error": {
            "en": "Game Info Error",
            "ko": "게임 정보 오류"
        },
        "game_info_error_msg": {
            "en": "Could not read game information from the file.\nThe file may be corrupted or in an unsupported format.",
            "ko": "파일에서 게임 정보를 읽을 수 없습니다.\n파일이 손상되었거나 지원되지 않는 형식일 수 있습니다."
        },
        "internal_name_could_not_read": {
            "en": "Internal Name: Could not read",
            "ko": "내부 이름: 읽을 수 없음"
        },
        "title_id_could_not_read": {
            "en": "Title ID: Could not read",
            "ko": "타이틀 ID: 읽을 수 없음"
        },

        # Key verification
        "common_key_verified": {
            "en": "Wii U Common Key verified!",
            "ko": "Wii U 공용 키 확인됨!"
        },
        "common_key_invalid": {
            "en": "Invalid Wii U Common Key!",
            "ko": "잘못된 Wii U 공용 키!"
        },
        "title_key_verified": {
            "en": "Title Key verified!",
            "ko": "타이틀 키 확인됨!"
        },
        "title_key_invalid": {
            "en": "Invalid Title Key!",
            "ko": "잘못된 타이틀 키!"
        },

        # Build errors
        "build_error_no_game": {
            "en": "Please select a game file first.",
            "ko": "먼저 게임 파일을 선택하세요."
        },
        "build_error_no_images": {
            "en": "Please select icon and banner images.",
            "ko": "아이콘과 배너 이미지를 선택하세요."
        },
        "build_error_no_keys": {
            "en": "Please enter encryption keys.",
            "ko": "암호화 키를 입력하세요."
        },
        "build_error_no_title": {
            "en": "Please enter a game title.",
            "ko": "게임 제목을 입력하세요."
        },
        "build_complete": {
            "en": "Build Complete!",
            "ko": "빌드 완료!"
        },
        "build_complete_msg": {
            "en": "Your WiiVC injection is ready!\n\nOutput: {output}\n\nInstall using WUP Installer GX2 with signature patches enabled.",
            "ko": "WiiVC 인젝션이 준비되었습니다!\n\n출력: {output}\n\n서명 패치가 활성화된 WUP Installer GX2를 사용하여 설치하세요."
        },
        "build_failed": {
            "en": "Build Failed",
            "ko": "빌드 실패"
        },
        "build_failed_msg": {
            "en": "Build process failed. Check the status message for details.",
            "ko": "빌드 프로세스가 실패했습니다. 자세한 내용은 상태 메시지를 확인하세요."
        },

        # File sources
        "from_repo": {
            "en": "from repo",
            "ko": "저장소에서"
        },
        "vwii_nand_title": {
            "en": "vWii NAND Title:",
            "ko": "vWii NAND 타이틀:"
        },
        "internal_name_nand": {
            "en": "Internal Name: N/A (NAND Title)",
            "ko": "내부 이름: 없음 (NAND 타이틀)"
        },

        # Language switcher
        "language": {
            "en": "Language",
            "ko": "언어"
        },
        "english": {
            "en": "English",
            "ko": "영어"
        },
        "korean": {
            "en": "Korean",
            "ko": "한국어"
        },

        # SD Card Dialog
        "sd_card_utilities": {
            "en": "SD Card Utilities",
            "ko": "SD 카드 유틸리티"
        },
        "sd_card_drive_selection": {
            "en": "SD Card Drive Selection",
            "ko": "SD 카드 드라이브 선택"
        },
        "select_drive": {
            "en": "Select Drive:",
            "ko": "드라이브 선택:"
        },
        "reload_drives": {
            "en": "Reload Drives",
            "ko": "드라이브 새로고침"
        },
        "nintendont_options": {
            "en": "Nintendont Options",
            "ko": "Nintendont 옵션"
        },
        "memory_card_emulation": {
            "en": "Memory Card Emulation",
            "ko": "메모리 카드 에뮬레이션"
        },
        "force_widescreen": {
            "en": "Force Widescreen",
            "ko": "와이드스크린 강제"
        },
        "force_progressive": {
            "en": "Force Progressive",
            "ko": "프로그레시브 강제"
        },
        "auto_boot": {
            "en": "Auto Boot",
            "ko": "자동 부팅"
        },
        "native_control": {
            "en": "Native Control",
            "ko": "네이티브 컨트롤"
        },
        "triforce_arcade_mode": {
            "en": "Triforce Arcade Mode",
            "ko": "트라이포스 아케이드 모드"
        },
        "wiiu_widescreen": {
            "en": "WiiU Widescreen",
            "ko": "WiiU 와이드스크린"
        },
        "auto_width": {
            "en": "Auto Width",
            "ko": "자동 너비"
        },
        "memory_card_settings": {
            "en": "Memory Card Settings",
            "ko": "메모리 카드 설정"
        },
        "memory_card_blocks": {
            "en": "Memory Card Blocks:",
            "ko": "메모리 카드 블록:"
        },
        "multi_game_memory_card": {
            "en": "Multi-game memory card",
            "ko": "다중 게임 메모리 카드"
        },
        "video_settings": {
            "en": "Video Settings",
            "ko": "비디오 설정"
        },
        "force_video_mode": {
            "en": "Force Video Mode:",
            "ko": "비디오 모드 강제:"
        },
        "video_type": {
            "en": "Video Type:",
            "ko": "비디오 타입:"
        },
        "video_width": {
            "en": "Video Width:",
            "ko": "비디오 너비:"
        },
        "other_settings": {
            "en": "Other Settings",
            "ko": "기타 설정"
        },
        "wiiu_gamepad_slot": {
            "en": "WiiU GamePad Slot:",
            "ko": "WiiU 게임패드 슬롯:"
        },
        "install_nintendont_to_sd": {
            "en": "Install Nintendont to SD",
            "ko": "Nintendont를 SD에 설치"
        },
        "no_removable_drives": {
            "en": "No removable drives found",
            "ko": "이동식 드라이브를 찾을 수 없음"
        },
        "platform_warning": {
            "en": "Platform",
            "ko": "플랫폼"
        },
        "platform_warning_msg": {
            "en": "SD Card detection is currently Windows-only.",
            "ko": "SD 카드 감지는 현재 Windows에서만 지원됩니다."
        },
        "no_drive": {
            "en": "No Drive",
            "ko": "드라이브 없음"
        },
        "no_drive_msg": {
            "en": "Please select a drive first.",
            "ko": "먼저 드라이브를 선택하세요."
        },
        "install_nintendont": {
            "en": "Install Nintendont",
            "ko": "Nintendont 설치"
        },
        "install_nintendont_confirm": {
            "en": "Install Nintendont to {drive}?\n\nThis will:\n• Download the latest Nintendont\n• Create required folders\n• Generate config file with selected options\n\nContinue?",
            "ko": "{drive}에 Nintendont를 설치하시겠습니까?\n\n다음 작업이 수행됩니다:\n• 최신 Nintendont 다운로드\n• 필요한 폴더 생성\n• 선택한 옵션으로 설정 파일 생성\n\n계속하시겠습니까?"
        },
        "not_implemented": {
            "en": "Not Implemented",
            "ko": "구현되지 않음"
        },
        "nintendont_install_preview": {
            "en": "Nintendont installation to {drive}\n\nSelected options:\n• Memory Card: {memcard}\n• Force Widescreen: {widescreen}\n• Force Progressive: {progressive}\n• Auto Boot: {autoboot}\n• Native Control: {native}\n• Triforce Arcade: {triforce}\n• WiiU Widescreen: {wiiu_wide}\n• Auto Width: {auto_width}\n\nThis feature will download and configure Nintendont.",
            "ko": "{drive}에 Nintendont 설치\n\n선택된 옵션:\n• 메모리 카드: {memcard}\n• 와이드스크린 강제: {widescreen}\n• 프로그레시브 강제: {progressive}\n• 자동 부팅: {autoboot}\n• 네이티브 컨트롤: {native}\n• 트라이포스 아케이드: {triforce}\n• WiiU 와이드스크린: {wiiu_wide}\n• 자동 너비: {auto_width}\n\n이 기능은 Nintendont를 다운로드하고 구성합니다."
        },

        # Batch Converter
        "batch_converter_title": {
            "en": "Batch WBFS/ISO Converter",
            "ko": "일괄 WBFS/ISO 변환기"
        },
        "batch_converter_header": {
            "en": "Batch Game File Converter",
            "ko": "게임 파일 일괄 변환기"
        },
        "selected_files": {
            "en": "Selected Files",
            "ko": "선택된 파일"
        },
        "add_files": {
            "en": "Add Files",
            "ko": "파일 추가"
        },
        "remove_selected": {
            "en": "Remove Selected",
            "ko": "선택 제거"
        },
        "clear_all": {
            "en": "Clear All",
            "ko": "전체 삭제"
        },
        "clear_all_confirm": {
            "en": "Are you sure you want to clear all files?",
            "ko": "모든 파일을 삭제하시겠습니까?"
        },
        "files_selected": {
            "en": "{count} file(s) selected",
            "ko": "{count}개 파일 선택됨"
        },
        "conversion_options": {
            "en": "Conversion Options",
            "ko": "변환 옵션"
        },
        "output_format": {
            "en": "Output Format:",
            "ko": "출력 형식:"
        },
        "output_directory": {
            "en": "Output Directory:",
            "ko": "출력 디렉토리:"
        },
        "same_as_source": {
            "en": "Same as source",
            "ko": "소스와 동일"
        },
        "verify_after_conversion": {
            "en": "Verify files after conversion",
            "ko": "변환 후 파일 검증"
        },
        "delete_source_after": {
            "en": "Delete source files after successful conversion",
            "ko": "변환 성공 후 소스 파일 삭제"
        },
        "delete_source_warning": {
            "en": "WARNING: This will permanently delete the source files after conversion. Are you sure?",
            "ko": "경고: 변환 후 소스 파일을 영구적으로 삭제합니다. 계속하시겠습니까?"
        },
        "conversion_progress": {
            "en": "Conversion Progress",
            "ko": "변환 진행 상황"
        },
        "ready_to_convert": {
            "en": "Ready to convert",
            "ko": "변환 준비 완료"
        },
        "conversion_log": {
            "en": "Conversion Log",
            "ko": "변환 로그"
        },
        "start_conversion": {
            "en": "Start Batch Conversion",
            "ko": "일괄 변환 시작"
        },
        "select_files_to_convert": {
            "en": "Select files to convert",
            "ko": "변환할 파일 선택"
        },
        "conversion_complete": {
            "en": "Conversion Complete",
            "ko": "변환 완료"
        },
        "conversion_complete_msg": {
            "en": "Batch conversion completed!\n\nSucceeded: {success}\nFailed: {failed}",
            "ko": "일괄 변환이 완료되었습니다!\n\n성공: {success}\n실패: {failed}"
        },
        "confirm": {
            "en": "Confirm",
            "ko": "확인"
        },
        "warning": {
            "en": "Warning",
            "ko": "경고"
        },
        "conversion_in_progress": {
            "en": "Conversion is in progress. Do you really want to quit?",
            "ko": "변환이 진행 중입니다. 정말 종료하시겠습니까?"
        },
        "file_preview": {
            "en": "File Preview",
            "ko": "파일 미리보기"
        },
        "select_file_to_preview": {
            "en": "Select a file to view details",
            "ko": "파일을 선택하여 상세 정보 보기"
        },
        "common_key_saved": {
            "en": "Common Key saved successfully!",
            "ko": "Common Key가 저장되었습니다!"
        },
        "title_key_saved": {
            "en": "Title Key saved successfully!",
            "ko": "Title Key가 저장되었습니다!"
        },
        "common_key_invalid_format": {
            "en": "Invalid format! Common Key must be 32 hexadecimal characters.",
            "ko": "잘못된 형식입니다! Common Key는 32자리 16진수여야 합니다."
        },
        "title_key_invalid_format": {
            "en": "Invalid format! Title Key must be 32 hexadecimal characters.",
            "ko": "잘못된 형식입니다! Title Key는 32자리 16진수여야 합니다."
        },
        "generate": {
            "en": "Generate",
            "ko": "생성"
        },
        "title_key_generated": {
            "en": "Title Key Generated",
            "ko": "Title Key 생성됨"
        },
        "title_key_generated_msg": {
            "en": "A random Title Key has been generated. Click 'Verify and Save' to save it.",
            "ko": "랜덤 Title Key가 생성되었습니다. '검증 및 저장'을 클릭하여 저장하세요."
        },
        "title_key_placeholder": {
            "en": "Enter or generate 32-character hex key",
            "ko": "32자리 hex 키 입력 또는 생성"
        },

        # Build progress messages
        "progress_verifying_keys": {
            "en": "Verifying encryption keys...",
            "ko": "암호화 키 확인 중..."
        },
        "progress_keys_verified": {
            "en": "Keys verified",
            "ko": "키 확인 완료"
        },
        "progress_copying_base_files": {
            "en": "Copying base files...",
            "ko": "베이스 파일 복사 중..."
        },
        "progress_converting_images": {
            "en": "Converting images...",
            "ko": "이미지 변환 중..."
        },
        "progress_converting_wbfs": {
            "en": "Converting WBFS to ISO...",
            "ko": "WBFS를 ISO로 변환 중..."
        },
        "progress_wbfs_converted": {
            "en": "WBFS converted to ISO",
            "ko": "WBFS를 ISO로 변환 완료"
        },
        "progress_using_iso": {
            "en": "Using ISO file",
            "ko": "ISO 파일 사용 중"
        },
        "progress_applying_patch": {
            "en": "Applying gamepad patch ({patch_type})...",
            "ko": "게임패드 패치 적용 중 ({patch_type})..."
        },
        "progress_patch_applied": {
            "en": "Gamepad patch applied",
            "ko": "게임패드 패치 적용 완료"
        },
        "progress_skipping_patch": {
            "en": "Skipping gamepad patch",
            "ko": "게임패드 패치 건너뛰기"
        },
        "progress_preparing_nfs": {
            "en": "Preparing NFS converter...",
            "ko": "NFS 변환기 준비 중..."
        },
        "progress_converting_nfs": {
            "en": "Converting ISO to NFS format (this will take several minutes)...",
            "ko": "ISO를 NFS 형식으로 변환 중 (시간이 상당히 소요될 수 있습니다. 잠시만 기다려주세요)"
        },
        "progress_nfs_complete": {
            "en": "NFS conversion complete",
            "ko": "NFS 변환 완료"
        },
        "progress_processing": {
            "en": "Processing... {percent}%",
            "ko": "처리 중... {percent}%"
        },
        "progress_preparing_encryption": {
            "en": "Preparing for encryption...",
            "ko": "암호화 준비 중..."
        },
        "progress_encrypting_packing": {
            "en": "Encrypting and packing (this may take a while)...",
            "ko": "암호화 및 패킹 중 (시간이 상당히 소요될 수 있습니다. 잠시만 기다려주세요)"
        },
        "progress_verifying_output": {
            "en": "Verifying output files...",
            "ko": "출력 파일 확인 중..."
        },
        "progress_checking_base_files": {
            "en": "Checking base files...",
            "ko": "베이스 파일 확인 중..."
        },
        "progress_wbfs_to_iso": {
            "en": "Converting WBFS to ISO...",
            "ko": "WBFS를 ISO로 변환 중..."
        },
        "progress_extracting_game_data": {
            "en": "Extracting game data...",
            "ko": "게임 데이터 추출 중..."
        },
        "progress_rebuilding_iso": {
            "en": "Rebuilding trimmed ISO...",
            "ko": "트림된 ISO 재구성 중..."
        },
        "progress_trimming_iso": {
            "en": "Trimming game ISO...",
            "ko": "게임 ISO 트리밍 중..."
        },
        "progress_initializing": {
            "en": "Initializing...",
            "ko": "초기화 중..."
        },
        "progress_downloading_base": {
            "en": "Downloading base files from Nintendo...",
            "ko": "닌텐도 서버에서 베이스 파일 다운로드 중..."
        },
        "progress_generating_meta": {
            "en": "Generating meta.xml...",
            "ko": "meta.xml 생성 중..."
        },
        "progress_processing_game": {
            "en": "Processing game file...",
            "ko": "게임 파일 처리 중..."
        },
        "progress_extracting_tik_tmd": {
            "en": "Extracting TIK and TMD from ISO...",
            "ko": "ISO에서 TIK 및 TMD 추출 중..."
        },
        "progress_packing_wup": {
            "en": "Packing final WUP...",
            "ko": "최종 WUP 패킹 중..."
        },
        "progress_build_successful": {
            "en": "Build successful!",
            "ko": "빌드 성공!"
        },
        "progress_copying_iso": {
            "en": "Copying ISO...",
            "ko": "ISO 복사 중..."
        },
        "progress_preparing_iso": {
            "en": "Preparing ISO...",
            "ko": "ISO 준비 중..."
        },
        "output_folder": {
            "en": "Output Folder:",
            "ko": "출력 폴더:"
        },
        "output_folder_placeholder": {
            "en": "Leave empty to use game file directory",
            "ko": "비워두면 게임 파일과 같은 경로에 출력"
        },
        "clear": {
            "en": "Clear",
            "ko": "초기화"
        },
        "loading_games_title": {
            "en": "Please wait",
            "ko": "잠시만 기다려주세요"
        },
        "loading_games_message": {
            "en": "Searching for game icons and banners...",
            "ko": "게임 아이콘 및 배너 이미지를 검색하고 있습니다..."
        },
        "loading_games_progress": {
            "en": "Searching for game icons and banners... ({current}/{total})",
            "ko": "게임 아이콘 및 배너 이미지를 검색하고 있습니다... ({current}/{total})"
        },
    }

    @classmethod
    def get(cls, key: str, **kwargs) -> str:
        """
        Get translated string for the current language.

        Args:
            key: Translation key
            **kwargs: Format arguments for string formatting

        Returns:
            Translated string
        """
        if key not in cls.STRINGS:
            print(f"Warning: Translation key '{key}' not found")
            return key

        translations = cls.STRINGS[key]
        text = translations.get(cls.current_language, translations.get("en", key))

        # Apply formatting if kwargs provided
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError as e:
                print(f"Warning: Missing format key {e} for '{key}'")

        return text

    @classmethod
    def set_language(cls, lang_code: str):
        """
        Set the current language.

        Args:
            lang_code: Language code ('en' or 'ko')
        """
        if lang_code in ["en", "ko"]:
            cls.current_language = lang_code
        else:
            print(f"Warning: Unsupported language code '{lang_code}'")

    @classmethod
    def get_available_languages(cls):
        """Get list of available languages."""
        return [
            ("en", cls.get("english")),
            ("ko", cls.get("korean"))
        ]


# Convenience instance
tr = Translations()
