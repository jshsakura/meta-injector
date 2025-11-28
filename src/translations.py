"""Multi-language support for Meta-Injector."""

class Translations:
    """Translation manager for multi-language support."""

    # Current language
    current_language = "en"  # Default: English

    # All translations
    STRINGS = {
        # Window titles
        "app_title": {
            "en": "Meta-Injector",
            "ko": "위유 원정대 - 메타 인젝터"
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
            "en": "Auto Download Images",
            "ko": "이미지 자동 다운로드"
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
            "en": "Ancast Key (Wii U Starbuck Key)",
            "ko": "Ancast 키 (Wii U Starbuck 키)"
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
        "online_patch": {
            "en": "Apply WiiLink WFC / Trucha Patches",
            "ko": "WiiLink WFC / Trucha 패치 적용"
        },
        "online_patch_description": {
            "en": "• Trucha bug patch: Always applied\n• Bypasses signature verification (fixes error 22000)\n• Required for C2W and modified games",
            "ko": "• Trucha 버그 패치: 항상 적용\n• 서명 검증 우회 (오류 22000 해결)\n• C2W 및 수정된 게임에 필요"
        },
        "trucha_patch_option": {
            "en": "Apply Trucha Bug Patch",
            "ko": "Trucha 버그 패치 적용"
        },
        "trucha_patch_desc": {
            "en": "Bypasses signature verification (fixes error 22000, required for modified games)",
            "ko": "서명 검증 우회 (오류 22000 해결, 수정된 게임에 필요)"
        },
        "c2w_patch_option": {
            "en": "Apply C2W CPU Unlock Patch",
            "ko": "C2W CPU 클럭 해제 패치 적용"
        },
        "c2w_patch_desc": {
            "en": "Unlock CPU from 729MHz to 1.215GHz (requires Ancast key in settings)",
            "ko": "CPU를 729MHz에서 1.215GHz로 상향 (설정에서 Ancast 키 필요)"
        },
        "c2w_description": {
            "en": "• C2W (Cafe2Wii) CPU clock unlock patch\n• Unlocks CPU from 729MHz to 1.215GHz\n• Improves performance for demanding games\n• Requires Ancast (Starbuck) key",
            "ko": "• C2W (Cafe2Wii) CPU 클럭 제한 해제 패치\n• CPU를 729MHz에서 1.215GHz로 상향\n• 고사양 게임의 성능 향상\n• Ancast (Starbuck) 키 필요"
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
            "en": "Close",
            "ko": "닫기"
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
            "en": "Your Wii VC injection is ready!\n\nOutput: {output}\n\nInstall using WUP Installer GX2 with signature patches enabled.",
            "ko": "Wii VC 인젝션이 준비되었습니다!\n\n출력: {output}\n\n서명 패치가 활성화된 WUP Installer GX2를 사용하여 설치하세요."
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
            "ko": ""
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
            "en": "Remove All",
            "ko": "전체 제거"
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

        # Fun rotating messages for NFS conversion (long operation)
        "fun_nfs_messages": {
            "en": [
                "Converting to NFS... Boss battle in progress! HP: ████████ 80%",
                "Converting to NFS... Your ISO is evolving! B Button not working...",
                "Converting to NFS... Summoning Bahamut to encrypt your data!",
                "Converting to NFS... Save point ahead! (Just kidding, keep waiting...)",
                "Converting to NFS... Collecting all 7 dragon balls of conversion!",
                "Converting to NFS... Chocobo is running... but very slowly...",
                "Converting to NFS... Loading the next area... (this isn't a hint)",
                "Converting to NFS... Crafting Legendary-tier NFS file! +999 patience",
                "Converting to NFS... Victory fanfare will play soon! Probably...",
                "Converting to NFS... A Metal Slime appeared! ...and ran away with your ISO!",
                "Converting to NFS... The party is resting at an inn! Wait, no—still converting.",
                "Converting to NFS... You gained 256 EXP! Level up at 99% completion!",
                "Converting to NFS... Critical Hit! Your ISO took 9999 damage (but survived)!",
                "Converting to NFS... A coffin is examining your game data carefully...",
                "Converting to NFS... The Legendary Hero's ISO is being forged in sacred flames!",
                "Converting to NFS... Puff Puff time! Just kidding, converter says no.",
                "Converting to NFS... Your ISO learned a new spell: 'Compression'!",
                "Converting to NFS... The King says: 'Thou hast waited long. Wait more.'",
                "Converting to NFS... Slime べホイミ! ...wait, that doesn't help conversion.",
                "Converting to NFS... The Goddess statue asks: 'Wilt thou continue?' YES!",
                "Converting to NFS... Searching for Yggdrasil leaves... found padding instead.",
                "Converting to NFS... The merchant's cart broke down! Repairs take 5-10 minutes.",
                "Converting to NFS... You opened a treasure chest! It was a Mimic. Run!",
                "Converting to NFS... Party member: 'Are we there yet?' Narrator: They weren't.",
                "Converting to NFS... Zoom spell failed! You must walk the whole conversion...",
                "Converting to NFS... The sage says: 'Patience, young hero. This too shall pass.'",
                "Converting to NFS... Monster fight! Padding Slime × 9999! Battle will be long...",
                "Converting to NFS... You entered the Tower of Conversion. 99 floors to go!",
                "Converting to NFS... The party's HP is fine, but your patience is at 1%.",
                "Converting to NFS... A wild Metal King Slime! ...it ran away. No shortcuts here.",
                "Converting to NFS... The fortuneteller says: 'I see... more waiting in your future.'",
                "Converting to NFS... ⚠️ IT'S DANGEROUS TO GO ALONE! But you must wait anyway.",
                "Converting to NFS... Navi: 'Hey! Listen!' You: 'NOT NOW, CONVERTING!'",
                "Converting to NFS... Playing the Song of Time... Nothing happened. Still converting.",
                "Converting to NFS... A wild ISO appeared! Trainer used COMPRESS! It's super effective!",
                "Converting to NFS... Your ISO is confused! It hurt itself in confusion!",
                "Converting to NFS... Professor Oak: 'Now is not the time to use that!'",
                "Converting to NFS... It's a-me, NFS-io! Let's-a go! ...very slowly.",
                "Converting to NFS... Mario jumped on the ISO! POW! ...Nothing changed.",
                "Converting to NFS... Yoshi is carrying your ISO... across a very long bridge...",
                "Converting to NFS... YOU DIED. Just kidding! But you might die of boredom.",
                "Converting to NFS... Bonfire lit! Now you can rest... ha, no. Keep waiting.",
                "Converting to NFS... 'Praise the Sun!' \\[T]/ ...Still converting though.",
                "Converting to NFS... POTG: NFS Converter - Overtime Hold: 5 minutes",
                "Converting to NFS... Defeat the enemy team! ...or just wait 10 more minutes.",
                "Converting to NFS... Victory is near! Unlike this conversion.",
                "Converting to NFS... 'I used to be an adventurer like you, then...' STILL CONVERTING!",
                "Converting to NFS... Fus Ro Dah! ...Doesn't speed up conversion. Worth a try.",
                "Converting to NFS... Loading screen tip: Conversion takes time. Who knew?",
                "Converting to NFS... Going PLUS ULTRA! ...at normal speed. Sorry.",
                "Converting to NFS... NANI?! Your ISO is already converted? Nope, still going.",
                "Converting to NFS... Kamehameha! ⚡ ...Conversion progress: +0.1%",
                "Converting to NFS... Bankai! ⚔️ ...Attack: MAX, Speed: Minimum.",
                "Converting to NFS... Gathering 5 Exodia pieces... Found 4. Where's the 5th?!",
                "Converting to NFS... Attack mode: ON! Defense mode: WAITING...",
                "Converting to NFS... Trap card activated! 'Mirror Force'... oh wait, wrong game.",
                "Converting to NFS... Level 99 Legendary Item Crafting! 0.01% drop rate success!",
                "Converting to NFS... Mega Evolution! ...Failed. Need more time charging.",
                "Converting to NFS... One Piece is closer than this conversion finishing.",
                "Converting to NFS... Shadow Clone Jutsu! Now converting at... the same speed.",
                "Converting to NFS... Rasengan! 🌀 ...Spinning, but not speeding up.",
                "Converting to NFS... Alchemy: Combining ISO + Patience = NFS (maybe)",
                "Converting to NFS... Titan is converting your data! SHINZOU WO SASAGEYO!",
                "Converting to NFS... OBJECTION! The conversion is taking too long! Overruled.",
                "Converting to NFS... Phoenix Wright: 'Your Honor, just a few more minutes...'",
                "Converting to NFS... ZA WARUDO! Time stopped! ...Conversion keeps going somehow.",
                "Converting to NFS... ORA ORA ORA ORA! ...Punching doesn't make it faster.",
                "Converting to NFS... Stand Power: 「NFS Converter」 Speed: E Precision: A",
            ],
            "ko": [
                "NFS 변환 중... 보스전 진행 중! HP: ████████ 80%",
                "NFS 변환 중... ISO가 진화하고 있어요! B 버튼이 안 먹혀요...",
                "NFS 변환 중... 바하무트를 소환해서 데이터를 암호화 중!",
                "NFS 변환 중... 앞에 세이브 포인트 발견! (농담이에요, 계속 기다리세요...)",
                "NFS 변환 중... 변환의 드래곤볼 7개를 모으는 중!",
                "NFS 변환 중... 초코보가 달리는 중... 하지만 아주 천천히...",
                "NFS 변환 중... 다음 구역 로딩 중... (힌트 아닙니다)",
                "NFS 변환 중... 전설등급 NFS 파일 제작 중! +999 인내",
                "NFS 변환 중... 승리 팡파레가 곧 연주될 거예요! 아마도...",
                "NFS 변환 중... 메탈 슬라임이 나타났다! ...ISO를 들고 도망쳤다!",
                "NFS 변환 중... 일행은 여관에서 휴식 중! 아니 잠깐, 아직 변환 중...",
                "NFS 변환 중... 256의 경험치를 얻었다! 99%에서 레벨 업!",
                "NFS 변환 중... 회심의 일격! ISO는 9999 데미지를 받았다! (살아남았다)",
                "NFS 변환 중... 관이 당신의 게임 데이터를 신중히 살펴보고 있다...",
                "NFS 변환 중... 전설의 용사의 ISO가 성스러운 불꽃 속에서 단련되고 있다!",
                "NFS 변환 중... 퍼프퍼프 시간! 농담입니다, 변환기가 거절했습니다.",
                "NFS 변환 중... ISO는 새로운 주문 '압축'을 배웠다!",
                "NFS 변환 중... 왕이 말했다: '그대는 오래 기다렸도다. 더 기다리라.'",
                "NFS 변환 중... 슬라임이 베호이미! ...어? 변환에는 도움 안 돼요.",
                "NFS 변환 중... 여신상이 묻습니다: '계속하시겠습니까?' 네!",
                "NFS 변환 중... 세계수의 잎을 찾는 중... 패딩만 발견했다.",
                "NFS 변환 중... 상인의 마차가 고장났다! 수리에 5-10분 소요됩니다.",
                "NFS 변환 중... 보물상자를 열었다! 미믹이었다! 도망쳐!",
                "NFS 변환 중... 동료: '우리 다 왔어?' 내레이터: 아니었다.",
                "NFS 변환 중... 루라 주문이 실패했다! 변환 전체를 걸어가야 합니다...",
                "NFS 변환 중... 현자: '인내하라, 젊은 용사여. 이 또한 지나가리라.'",
                "NFS 변환 중... 몬스터 전투! 패딩 슬라임 × 9999마리! 전투가 길 거예요...",
                "NFS 변환 중... 변환의 탑에 입장했다! 99층이 남았습니다!",
                "NFS 변환 중... 일행의 HP는 괜찮지만, 당신의 인내심은 1%입니다.",
                "NFS 변환 중... 야생의 메탈 킹 슬라임! ...도망쳤다. 지름길은 없다.",
                "NFS 변환 중... 점술가: '보이는군요... 당신의 미래엔 더 많은 대기가...'",
                "NFS 변환 중... ⚠️ 혼자 가기엔 위험해! 하지만 어쨌든 기다려야 해.",
                "NFS 변환 중... 나비: '저기! 들어봐!' 당신: '지금 변환 중이라고!'",
                "NFS 변환 중... 시간의 노래를 연주했다... 아무 일도 일어나지 않았다. 여전히 변환 중.",
                "NFS 변환 중... 야생의 ISO가 나타났다! 트레이너는 압축을 사용했다! 효과가 굉장했다!",
                "NFS 변환 중... ISO가 혼란에 빠졌다! ISO는 혼란으로 자신을 공격했다!",
                "NFS 변환 중... 오박사: '지금은 그럴 때가 아니란다!'",
                "NFS 변환 중... 잇츠미, NFS-io! 렛츠-아 고! ...아주 천천히.",
                "NFS 변환 중... 마리오가 ISO를 밟았다! 퐁! ...아무 변화 없음.",
                "NFS 변환 중... 요시가 ISO를 태우고... 아주 긴 다리를 건너는 중...",
                "NFS 변환 중... YOU DIED. 농담이에요! 하지만 지루함으로 죽을지도.",
                "NFS 변환 중... 모닥불 점화! 이제 쉴 수... 아니 농담. 계속 기다려.",
                "NFS 변환 중... '태양을 찬양하라!' \\[T]/ ...하지만 여전히 변환 중.",
                "NFS 변환 중... POTG: NFS 변환기 - 거점 수비 시간: 5분",
                "NFS 변환 중... 적 팀을 물리쳐라! ...아니면 그냥 10분만 더 기다려.",
                "NFS 변환 중... 승리가 가까워졌다! 이 변환은 아니지만.",
                "NFS 변환 중... '나도 옛날엔 모험가였는데, 그러다가...' 아직도 변환 중!",
                "NFS 변환 중... 푸스 로 다! ...변환 속도는 안 빨라짐. 시도는 해봤어요.",
                "NFS 변환 중... 로딩 화면 팁: 변환은 시간이 걸립니다. 누가 몰랐겠어요?",
                "NFS 변환 중... PLUS ULTRA를 외친다! ...보통 속도로. 미안.",
                "NFS 변환 중... 나니?! ISO가 벌써 변환됐다고? 아니, 아직 진행 중.",
                "NFS 변환 중... 카메하메하! ⚡ ...변환 진행도: +0.1%",
                "NFS 변환 중... 卍解(만해)! ⚔️ ...공격력: MAX, 속도: 최소.",
                "NFS 변환 중... 5개의 엑조디아 조각을 모으는 중... 4개 발견. 5번째는 어디?!",
                "NFS 변환 중... 공격 표시! 수비 표시... 아니 대기 표시!",
                "NFS 변환 중... 함정 카드 발동! '성스러운 방어막 거울의 힘'... 아 게임 잘못 골랐네.",
                "NFS 변환 중... 레벨 99 전설 아이템 제작! 0.01% 드랍률 성공!",
                "NFS 변환 중... 메가진화! ...실패. 충전 시간이 더 필요합니다.",
                "NFS 변환 중... 원피스를 찾는 게 이 변환 끝나는 것보다 빠를 듯.",
                "NFS 변환 중... 그림자 분신술! 이제 변환이... 똑같은 속도로 진행됩니다.",
                "NFS 변환 중... 나선환! 🌀 ...회전은 하는데 빨라지진 않네요.",
                "NFS 변환 중... 연금술: ISO + 인내 = NFS (아마도)",
                "NFS 변환 중... 거인이 당신의 데이터를 변환 중! 심장을 바쳐라!",
                "NFS 변환 중... 이의 있음! 변환이 너무 오래 걸립니다! 기각.",
                "NFS 변환 중... 나루호도 류이치: '재판장님, 몇 분만 더...'",
                "NFS 변환 중... 더 월드! 시간이 멈췄다! ...변환은 계속 진행 중.",
                "NFS 변환 중... 오라오라오라오라! ...주먹으로 빠르게 안 돼요.",
                "NFS 변환 중... 스탠드 능력: 「NFS 변환기」 스피드: E 정밀도: A",
            ]
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

        # Fun rotating messages for long operations
        "fun_trimming_messages": {
            "en": [
                "Trimming ISO... Your party is fighting unnecessary data! Critical hit!",
                "Trimming ISO... Defeating padding slimes for EXP... 99 to go!",
                "Trimming ISO... Casting Materia magic to optimize space!",
                "Trimming ISO... Link is cutting the grass... finding hidden space!",
                "Trimming ISO... Pikachu used Compress! It's super effective!",
                "Trimming ISO... Collecting chaos emeralds of efficiency!",
                "Trimming ISO... Mario is jumping on bloated blocks!",
                "Trimming ISO... Samus is scanning for removable sectors...",
                "Trimming ISO... A wild Zubat appeared! Wait, wrong encounter...",
                "Trimming ISO... You found a Potion! No wait, just empty data blocks.",
                "Trimming ISO... Would you like to save? No! Keep trimming!",
                "Trimming ISO... The princess is in another castle... of data!",
                "Trimming ISO... Snake is hiding in unnecessary cardboard boxes!",
                "Trimming ISO... Cloud is using Limit Break: Omnislash Trim!",
                "Trimming ISO... Kirby is inhaling bloated sectors! *Poyo!*",
                "Trimming ISO... Sonic says: 'Gotta go fast!' ...but trimming is slow.",
                "Trimming ISO... A Metal Slime of padding appeared! 1 EXP gained.",
                "Trimming ISO... The merchant says: 'I'll buy that bloat for a high price!'",
                "Trimming ISO... Your ISO used 'Reduce'! File size fell drastically!",
                "Trimming ISO... Solid Snake: 'Kept you waiting, huh?' Yes. Yes we did.",
                "Trimming ISO... Lara Croft is raiding unnecessary tombs of data!",
                "Trimming ISO... Master Chief is finishing this... trim. Eventually.",
                "Trimming ISO... The cake is a lie, but this trim is real!",
                "Trimming ISO... All your base (game data) are belong to us!",
                "Trimming ISO... The Hero found a Small Medal! 99 more to go...",
                "Trimming ISO... Yangus is smashing pots! No gold, just empty blocks.",
                "Trimming ISO... The party used 'Zoom' to skip trimming! ...Zoom failed.",
                "Trimming ISO... Jessica's Tension is maxed! Critical Trim incoming!",
                "Trimming ISO... The Alchemist is mixing... Chimaera Wing + ISO = ???",
                "Trimming ISO... A Cosmic Chimera appeared! It blocks with padding!",
            ],
            "ko": [
                "ISO 트리밍 중... 파티가 불필요한 데이터와 전투 중! 크리티컬 히트!",
                "ISO 트리밍 중... 패딩 슬라임을 처치하고 경험치 획득... 99마리 남음!",
                "ISO 트리밍 중... 마테리아 마법으로 용량 최적화 시전!",
                "ISO 트리밍 중... 링크가 풀을 베고 있습니다... 숨겨진 공간 발견!",
                "ISO 트리밍 중... 피카츄가 압축을 사용했다! 효과가 굉장했다!",
                "ISO 트리밍 중... 효율성의 카오스 에메랄드 수집 중!",
                "ISO 트리밍 중... 마리오가 부풀려진 블록을 밟고 있어요!",
                "ISO 트리밍 중... 사무스가 제거 가능한 섹터를 스캔 중...",
                "ISO 트리밍 중... 야생의 주뱃이 나타났다! 어? 잘못된 인카운터...",
                "ISO 트리밍 중... 상처약을 발견했다! 아니다 빈 데이터 블록이었다.",
                "ISO 트리밍 중... 저장하시겠습니까? 아니! 계속 트리밍!",
                "ISO 트리밍 중... 공주님은 다른 성에... 아니 데이터 성에 계십니다!",
                "ISO 트리밍 중... 스네이크가 불필요한 골판지 상자에 숨어있어요!",
                "ISO 트리밍 중... 클라우드가 리미트 브레이크 시전: 초절 트리밍!",
                "ISO 트리밍 중... 커비가 비대한 섹터를 흡입 중! *포요!*",
                "ISO 트리밍 중... 소닉: '빨리 가야지!' ...근데 트리밍은 느려요.",
                "ISO 트리밍 중... 패딩 메탈 슬라임이 나타났다! 경험치 1을 얻었다.",
                "ISO 트리밍 중... 상인: '그 비대한 데이터 비싸게 사주지!' (레지던트 이블)",
                "ISO 트리밍 중... ISO가 '사이즈 줄이기'를 사용했다! 파일 크기가 급락했다!",
                "ISO 트리밍 중... 솔리드 스네이크: '기다렸지?' 네, 엄청 기다렸어요.",
                "ISO 트리밍 중... 라라 크로프트가 불필요한 데이터 무덤을 탐험 중!",
                "ISO 트리밍 중... 마스터 치프가 이 트리밍을 끝내는 중... 언젠가는.",
                "ISO 트리밍 중... 케이크는 거짓말이지만, 이 트리밍은 진짜입니다!",
                "ISO 트리밍 중... 너희 베이스(게임 데이터)는 이미 우리 것이다!",
                "ISO 트리밍 중... 용사가 작은 메달을 발견했다! 99개 더 필요해요...",
                "ISO 트리밍 중... 양거스가 항아리를 부수고 있어요! 골드는 없고 빈 블록만...",
                "ISO 트리밍 중... 일행이 '루라'로 트리밍 스킵 시도! ...루라 실패.",
                "ISO 트리밍 중... 제시카의 텐션이 최대! 회심의 트리밍 발동!",
                "ISO 트리밍 중... 연금술사가 조합 중... 키메라의 날개 + ISO = ???",
                "ISO 트리밍 중... 우주 키메라가 나타났다! 패딩으로 막고 있다!",
            ]
        },
        "controller_mapping_info": {
            "en": "Gamepad Patch Mapping Info",
            "ko": "게임패드 패치시 매핑 정보"
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

        # Fun rotating messages for WUP packing (also takes a while!)
        "fun_packing_messages": {
            "en": [
                "Packing WUP... The blacksmith is forging your Legendary Game! +999 ATK!",
                "Packing WUP... Sealing the Dark Lord's power into a cartridge!",
                "Packing WUP... The alchemist is creating a Philosopher's WUP!",
                "Packing WUP... Wrapping your game in dragon scales for protection!",
                "Packing WUP... Enchanting the package with ancient runes of DRM!",
                "Packing WUP... The merchant is carefully packing your treasure!",
                "Packing WUP... Summoning the Four Crystals of Installation!",
                "Packing WUP... The party gained a new item: [WiiU Game Package]!",
                "Packing WUP... Placing your game in the Legendary Treasure Vault!",
                "Packing WUP... The Hero's journey is being archived for eternity!",
                "Packing WUP... Sealing ceremony in progress! Don't break the circle!",
                "Packing WUP... The Royal Archiver is documenting your adventure!",
                "Packing WUP... Packaging cuteness into 5000MB! Slimes included!",
                "Packing WUP... Your game learned 'Pakuga'! ...wait, that's not a spell.",
                "Packing WUP... The King's vault master is securing your game files!",
                "Packing WUP... Applying the Sacred Seal of Nintendo! Holy encryption!",
                "Packing WUP... Boss battle: NUSPacker.exe! HP: ████ 100%",
                "Packing WUP... The Goddess blesses your packaged game! +999 Luck!",
                "Packing WUP... Metal Slime helper is organizing files! So fast!",
                "Packing WUP... Legendary blacksmith: 'Almost done! Just 99 more hits...'",
                "Packing WUP... Wrapping with Orichalcum foil! Unbreakable protection!",
                "Packing WUP... The sage says: 'This WUP shall be thy greatest treasure!'",
                "Packing WUP... Loading game onto the Starflight Express! Departing soon!",
                "Packing WUP... Coffin is putting final touches... very meticulously...",
                "Packing WUP... The party rests before the final boss: WiiU Installation!",
                "Packing WUP... Achievement Unlocked: 'Master Packager' - 1000G!",
                "Packing WUP... Your patience stat increased by +50! New record!",
                "Packing WUP... The fortuneteller sees... success in your near future!",
                "Packing WUP... Almost there! Victory fanfare loading... 🎵",
                "Packing WUP... The final seal is... complete! Quest accomplished!",
                "Packing WUP... Link is sealing Ganon's data into the Master Cartridge!",
                "Packing WUP... Zelda: 'The Triforce of Packaging is nearly assembled!'",
                "Packing WUP... Epona is carrying your WUP package across Hyrule Field!",
                "Packing WUP... Catching a Legendary Pokemon! Throw the Ultra Ball... Gotcha!",
                "Packing WUP... Professor Elm: 'This WUP is an unprecedented discovery!'",
                "Packing WUP... Nurse Joy: 'We hope to see you again!' ...but later, please.",
                "Packing WUP... Bowser kidnapped Princess Peach! ...Wait, wrong quest.",
                "Packing WUP... Luigi's Mansion is now Luigi's WUP Archive!",
                "Packing WUP... Toad: 'Thank you Mario! Your WUP is in another castle!'",
                "Packing WUP... Praise the Sun! \\[T]/ The chosen undead packs the WUP!",
                "Packing WUP... Estus Flask refilled! You can rest now... or can you?",
                "Packing WUP... You defeated the Asylum Demon of packaging! Soul acquired!",
                "Packing WUP... Ryujin no ken wo kurae! Dragon Strike packages the WUP!",
                "Packing WUP... High Noon... Time to pack this WUP. It's 12 o'clock.",
                "Packing WUP... NERF THIS! D.Va's mech is delivering the WUP package!",
                "Packing WUP... Courier 6 is delivering your WUP to the Mojave Wasteland!",
                "Packing WUP... War. War never changes. But WUP packing does take time.",
                "Packing WUP... Vault-Tec approved! S.P.E.C.I.A.L. packaging in progress!",
                "Packing WUP... Master Chief: 'Wake me when the packing is done.'",
                "Packing WUP... Cortana: '99.9% complete. Just a few more cycles...'",
                "Packing WUP... Spartans never die. They're just packing... very slowly.",
                "Packing WUP... Gordon Freeman packages in silence. No commentary needed.",
                "Packing WUP... The G-Man: 'Time, Dr. Freeman? Is it really that time again?'",
                "Packing WUP... The cake is a lie, but this WUP package is very real!",
                "Packing WUP... Geralt: 'Winds howling... and so is this packer.'",
                "Packing WUP... Toss a coin to your packager, O Valley of Plenty!",
                "Packing WUP... Place of power... gotta be. Packaging power increased!",
                "Packing WUP... Snake? SNAKE?! SNAAAAKE! ...Just packing. Relax.",
                "Packing WUP... Kept you waiting, huh? The WUP is almost ready.",
                "Packing WUP... ! Alert! Packaging detected! No wait, that's normal.",
                "Packing WUP... Kamehameha! ⚡ Super Saiyan Packaging Mode!",
                "Packing WUP... Goku: 'This packaging power level... it's over 9000!'",
                "Packing WUP... Vegeta: 'Kakarot! Stop packing and fight me!'",
                "Packing WUP... Believe it! Naruto's Shadow Clone Packing Jutsu!",
                "Packing WUP... Sasuke uses Chidori! ⚡ Critical packaging hit!",
                "Packing WUP... Kakashi's Sharingan sees the future: WUP complete soon!",
                "Packing WUP... Luffy: 'I'm gonna be King of the Packers!' 🏴‍☠️",
                "Packing WUP... Gomu Gomu no... Packaging! Rubber WUP stretch!",
                "Packing WUP... Zoro got lost looking for the WUP directory... again.",
                "Packing WUP... Lelouch: 'I command you... FINISH PACKING!' Doesn't work.",
                "Packing WUP... Code Geass activated! ...Still takes the same time.",
                "Packing WUP... All according to keikaku (Translator's note: keikaku = plan)",
                "Packing WUP... Eren: 'I'll destroy all the bugs!' Levi: 'Wrong enemy.'",
                "Packing WUP... Survey Corps deploying 3D Maneuver Gear to pack faster!",
                "Packing WUP... Titans approaching! ...Just the packing titans. We're fine.",
            ],
            "ko": [
                "WUP 패킹 중... 대장장이가 전설의 게임을 단조 중! 공격력 +999!",
                "WUP 패킹 중... 마왕의 힘을 카트리지에 봉인하는 중!",
                "WUP 패킹 중... 연금술사가 현자의 WUP를 만들고 있어요!",
                "WUP 패킹 중... 당신의 게임을 용의 비늘로 감싸는 중!",
                "WUP 패킹 중... 고대의 DRM 룬으로 패키지를 마법 부여 중!",
                "WUP 패킹 중... 상인이 당신의 보물을 신중히 포장 중!",
                "WUP 패킹 중... 설치의 사대 크리스탈을 소환 중!",
                "WUP 패킹 중... 일행이 새로운 아이템을 얻었다: [WiiU 게임 패키지]!",
                "WUP 패킹 중... 전설의 보물고에 게임을 안치하는 중!",
                "WUP 패킹 중... 용사의 여정이 영원히 보관되고 있어요!",
                "WUP 패킹 중... 봉인 의식 진행 중! 마법진을 깨트리지 마세요!",
                "WUP 패킹 중... 왕국의 기록관이 당신의 모험을 문서화 중!",
                "WUP 패킹 중... 귀여움을 5000MB에 압축! 슬라임 포함!",
                "WUP 패킹 중... 게임이 '파쿠가'를 배웠다! ...어? 그런 주문 없는데.",
                "WUP 패킹 중... 왕의 금고지기가 게임 파일을 보안 중!",
                "WUP 패킹 중... 닌텐도의 성스러운 봉인 적용 중! 신성한 암호화!",
                "WUP 패킹 중... 보스전: NUSPacker.exe! HP: ████ 100%",
                "WUP 패킹 중... 여신이 당신의 패키지에 축복을! 행운 +999!",
                "WUP 패킹 중... 메탈 슬라임 도우미가 파일 정리 중! 정말 빨라!",
                "WUP 패킹 중... 전설의 대장장이: '거의 다 됐어! 99번만 더 두드리면...'",
                "WUP 패킹 중... 오리하르콘 포일로 포장 중! 파괴 불가 보호!",
                "WUP 패킹 중... 현자: '이 WUP는 그대의 최고 보물이 되리라!'",
                "WUP 패킹 중... 스타플라이트 특급에 게임 적재 중! 곧 출발!",
                "WUP 패킹 중... 관이 마지막 손질 중... 아주 꼼꼼하게...",
                "WUP 패킹 중... 최종 보스 전 휴식: WiiU 설치! 준비됐나요?",
                "WUP 패킹 중... 업적 달성: '마스터 패키저' - 1000G!",
                "WUP 패킹 중... 인내심 스탯이 +50 증가했다! 신기록!",
                "WUP 패킹 중... 점술가가 보고 있어요... 가까운 미래에 성공이!",
                "WUP 패킹 중... 거의 다 왔어요! 승리 팡파레 로딩 중... 🎵",
                "WUP 패킹 중... 최종 봉인이... 완료! 퀘스트 달성!",
                "WUP 패킹 중... 링크가 가논의 데이터를 마스터 카트리지에 봉인 중!",
                "WUP 패킹 중... 젤다: '패키징의 트라이포스가 거의 조립됐어요!'",
                "WUP 패킹 중... 에포나가 하이랄 평원을 가로질러 WUP 패키지 운반 중!",
                "WUP 패킹 중... 전설의 포켓몬을 잡는 중! 하이퍼볼을 던진다... 잡았다!",
                "WUP 패킹 중... 공박사: '이 WUP는 전례 없는 발견이야!'",
                "WUP 패킹 중... 포켓몬센터 간호순: '또 만나요!' ...나중에요, 제발.",
                "WUP 패킹 중... 쿠파가 피치 공주를 납치했다! ...어? 퀘스트 잘못 골랐네.",
                "WUP 패킹 중... 루이지 맨션이 이제 루이지 WUP 보관소!",
                "WUP 패킹 중... 키노피오: '고마워 마리오! WUP는 다른 성에 있어!'",
                "WUP 패킹 중... 태양을 찬양하라! \\[T]/ 불사의 선택받은 자가 WUP 패킹!",
                "WUP 패킹 중... 에스트 병 재충전! 이제 쉴 수... 있나요?",
                "WUP 패킹 중... 보호소 악마를 물리쳤다! 소울 획득!",
                "WUP 패킹 중... 류진노 검을 쿠라에! 용의 일격이 WUP를 패키징!",
                "WUP 패킹 중... 하이 눈... 이제 이 WUP를 패킹할 시간. 정오입니다.",
                "WUP 패킹 중... 너프 디스! 디바의 메카가 WUP 패키지 배달 중!",
                "WUP 패킹 중... 쿠리어 6이 모하비 황무지로 WUP를 배달 중!",
                "WUP 패킹 중... 전쟁. 전쟁은 변하지 않아. 하지만 WUP 패킹은 시간 걸려.",
                "WUP 패킹 중... Vault-Tec 승인! S.P.E.C.I.A.L. 패키징 진행 중!",
                "WUP 패킹 중... 마스터 치프: '패킹 끝나면 깨워줘.'",
                "WUP 패킹 중... 코타나: '99.9% 완료. 몇 사이클만 더...'",
                "WUP 패킹 중... 스파르탄은 죽지 않아. 단지 패킹... 아주 천천히.",
                "WUP 패킹 중... 고든 프리맨은 침묵 속에 패키징. 해설 불필요.",
                "WUP 패킹 중... G맨: '시간, 프리맨 박사? 정말 그 시간이 또 왔나요?'",
                "WUP 패킹 중... 케이크는 거짓말이지만, 이 WUP 패키지는 진짜!",
                "WUP 패킹 중... 게롤트: '바람이 울부짖는다... 그리고 이 패커도.'",
                "WUP 패킹 중... 패키저에게 동전을 던져라, 오 풍요의 계곡이여!",
                "WUP 패킹 중... 힘의 장소... 분명해. 패키징 파워 증가!",
                "WUP 패킹 중... 스네이크? 스네이크?! 스네~~이크! ...그냥 패킹 중. 진정해.",
                "WUP 패킹 중... 기다리게 해서 미안, 응? WUP가 거의 준비됐어.",
                "WUP 패킹 중... ! 경고! 패키징 감지! 아니 잠깐, 정상이네.",
                "WUP 패킹 중... 카메하메하! ⚡ 슈퍼 사이어인 패키징 모드!",
                "WUP 패킹 중... 오공: '이 패키징 파워... 9000을 넘었어!'",
                "WUP 패킹 중... 베지터: '카카로트! 패킹 그만하고 나랑 싸워!'",
                "WUP 패킹 중... 믿어봐요! 나루토의 그림자 분신 패킹술!",
                "WUP 패킹 중... 사스케가 치도리를 사용! ⚡ 패키징 크리티컬 히트!",
                "WUP 패킹 중... 카카시의 사륜안이 미래를 본다: WUP 곧 완성!",
                "WUP 패킹 중... 루피: '나는 패커왕이 될 거야!' 🏴‍☠️",
                "WUP 패킹 중... 고무고무 노... 패키징! 고무 WUP 늘리기!",
                "WUP 패킹 중... 조로가 WUP 디렉토리 찾다가 길을 잃었다... 또.",
                "WUP 패킹 중... 를르슈: '명령한다... 패킹을 완료하라!' 안 먹혀요.",
                "WUP 패킹 중... 코드 기아스 발동! ...여전히 같은 시간 걸려요.",
                "WUP 패킹 중... 모두 계획대로 (번역자 주: 계획 = 케이카쿠)",
                "WUP 패킹 중... 에렌: '버그를 다 없애버리겠어!' 리바이: '적 잘못 골랐어.'",
                "WUP 패킹 중... 조사병단이 입체기동장치 전개! 더 빠른 패킹!",
                "WUP 패킹 중... 거인이 접근 중! ...그냥 패킹 거인들. 괜찮아요.",
            ]
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
            "en": "Build Result Save Path:",
            "ko": "빌드 결과 저장 경로:"
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
