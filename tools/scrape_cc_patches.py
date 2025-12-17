#!/usr/bin/env python3
"""
Classic Controller Patch Scraper
Wii용 CC 패치를 온라인 소스에서 수집합니다.

소스:
1. codes.rc24.xyz - Wii 코드 DB
2. GameHacking.org - 치트 코드 DB
3. GBAtemp New Classic Controller Hacks 스레드 (Selenium 사용)
"""

import requests
import re
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import time

# Selenium imports
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("[WARN] Selenium not installed. Run: pip install selenium webdriver-manager")

# 출력 디렉토리
OUTPUT_DIR = Path(__file__).parent.parent / "core" / "CCPatches"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 결과 저장
collected_patches: Dict[str, dict] = {}


def fetch_url(url: str, headers: dict = None) -> Optional[str]:
    """URL에서 HTML/텍스트 가져오기"""
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    if headers:
        default_headers.update(headers)

    try:
        response = requests.get(url, headers=default_headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"[ERROR] Failed to fetch {url}: {e}")
        return None


def scrape_rc24_codes():
    """codes.rc24.xyz에서 Wii 코드 스크래핑"""
    print("\n=== Scraping codes.rc24.xyz ===")

    # RC24 API 엔드포인트 확인
    base_url = "https://codes.rc24.xyz"

    # 먼저 게임 목록 가져오기
    html = fetch_url(f"{base_url}/")
    if not html:
        print("[ERROR] Cannot access codes.rc24.xyz")
        return

    # 게임 ID 패턴 찾기 (예: RMCE01, RSBE01 등)
    game_ids = re.findall(r'/([A-Z0-9]{6})\.html', html)
    game_ids = list(set(game_ids))  # 중복 제거

    print(f"[INFO] Found {len(game_ids)} games")

    cc_keywords = [
        'classic controller', 'classic con', 'cc support', 'cc hack',
        'nunchuk', 'nunchuck', 'wiimote only', 'controller',
        'gamepad', 'button remap', 'control scheme'
    ]

    for i, game_id in enumerate(game_ids[:50]):  # 처음 50개만 테스트
        print(f"[{i+1}/{min(50, len(game_ids))}] Checking {game_id}...")

        game_url = f"{base_url}/{game_id}.html"
        game_html = fetch_url(game_url)

        if not game_html:
            continue

        # 게임 이름 추출
        title_match = re.search(r'<title>([^<]+)</title>', game_html)
        game_name = title_match.group(1) if title_match else game_id

        # CC 관련 코드 찾기
        lower_html = game_html.lower()
        for keyword in cc_keywords:
            if keyword in lower_html:
                print(f"  [FOUND] {game_name} - keyword: {keyword}")

                # 코드 블록 추출 시도
                code_blocks = re.findall(
                    r'<pre[^>]*>(.*?)</pre>',
                    game_html,
                    re.DOTALL | re.IGNORECASE
                )

                if code_blocks:
                    collected_patches[game_id] = {
                        'name': game_name,
                        'source': 'rc24',
                        'url': game_url,
                        'codes': code_blocks,
                        'keywords': [k for k in cc_keywords if k in lower_html]
                    }
                break

        time.sleep(0.5)  # Rate limiting


def scrape_gamehacking():
    """GameHacking.org에서 Wii CC 코드 스크래핑"""
    print("\n=== Scraping GameHacking.org ===")

    # Wii 게임 목록 페이지
    base_url = "https://gamehacking.org"

    # 검색 쿼리로 Classic Controller 관련 코드 찾기
    search_terms = [
        "classic controller wii",
        "nunchuk hack wii",
        "controller remap wii"
    ]

    for term in search_terms:
        search_url = f"{base_url}/search?q={term.replace(' ', '+')}&platform=wii"
        print(f"[INFO] Searching: {term}")

        html = fetch_url(search_url)
        if not html:
            continue

        # 결과 파싱
        game_links = re.findall(r'/game/(\d+)', html)

        for game_id in game_links[:10]:  # 각 검색당 10개
            game_url = f"{base_url}/game/{game_id}"
            game_html = fetch_url(game_url)

            if not game_html:
                continue

            # 게임 정보 추출
            title_match = re.search(r'<h1[^>]*>([^<]+)</h1>', game_html)
            game_name = title_match.group(1).strip() if title_match else f"Game_{game_id}"

            # Wii 게임 ID 추출 (6자리)
            wii_id_match = re.search(r'\b([A-Z]{4}[0-9]{2})\b', game_html)
            wii_id = wii_id_match.group(1) if wii_id_match else None

            if wii_id and wii_id not in collected_patches:
                print(f"  [FOUND] {game_name} ({wii_id})")
                collected_patches[wii_id] = {
                    'name': game_name,
                    'source': 'gamehacking',
                    'url': game_url,
                    'wii_id': wii_id
                }

            time.sleep(0.5)


def get_selenium_driver():
    """Selenium WebDriver 생성"""
    if not SELENIUM_AVAILABLE:
        return None

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 브라우저 창 숨김
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"[ERROR] Failed to create Selenium driver: {e}")
        return None


def scrape_gbatemp_cc_hacks():
    """GBAtemp New Classic Controller Hacks 스레드 스크래핑 (Selenium 사용)"""
    print("\n=== Scraping GBAtemp CC Hacks Thread (Selenium) ===")

    if not SELENIUM_AVAILABLE:
        print("[ERROR] Selenium not available. Install with: pip install selenium webdriver-manager")
        return

    driver = get_selenium_driver()
    if not driver:
        print("[ERROR] Could not initialize Selenium driver")
        return

    thread_url = "https://gbatemp.net/threads/new-classic-controller-hacks.659837/"

    try:
        print(f"[INFO] Loading {thread_url}")
        driver.get(thread_url)

        # 페이지 로드 대기
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "message-content"))
        )
        time.sleep(2)  # 추가 대기

        html = driver.page_source
        print(f"[INFO] Page loaded, size: {len(html)} bytes")

        # 스포일러 버튼 클릭하여 숨겨진 코드 표시
        try:
            spoiler_buttons = driver.find_elements(By.CSS_SELECTOR, ".bbCodeSpoiler-button")
            print(f"[INFO] Found {len(spoiler_buttons)} spoiler buttons")
            for btn in spoiler_buttons:
                try:
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(0.3)
                except:
                    pass
            time.sleep(1)
            html = driver.page_source  # 스포일러 열린 후 다시 가져오기
        except Exception as e:
            print(f"[WARN] Could not expand spoilers: {e}")

        # Google Docs/Sheets 링크 찾기
        spreadsheet_links = re.findall(
            r'https://docs\.google\.com/[^\s"<>\]]+',
            html
        )

        if spreadsheet_links:
            print(f"[INFO] Found spreadsheet links:")
            for link in set(spreadsheet_links):
                print(f"  - {link}")

        # 게임별 코드 블록 추출
        # Gecko 코드 블록 패턴 (code 태그 또는 pre 태그 내)
        code_block_pattern = r'<code[^>]*>([\s\S]*?)</code>|<pre[^>]*>([\s\S]*?)</pre>'

        # 모든 코드 블록 찾기
        code_blocks = re.findall(code_block_pattern, html, re.IGNORECASE)
        print(f"[INFO] Found {len(code_blocks)} code blocks")

        # 게임 ID 패턴들 (다양한 형식)
        game_id_patterns = [
            r'[\[\(]([A-Z]{4}[A-Z0-9]{2})[\]\)]',  # [RMCE01] 또는 (RMCE01)
            r'\b([A-Z]{4}[0-9]{2})\b',  # RMCE01 단독
            r'([A-Z]{3}[EJPK][0-9]{2})',  # 지역 코드 포함 (E/J/P/K)
        ]

        # 스포일러 버튼(제목)과 내용을 매칭
        spoilers = driver.find_elements(By.CSS_SELECTOR, ".bbCodeSpoiler")
        print(f"[INFO] Found {len(spoilers)} spoiler blocks")

        for spoiler in spoilers:
            try:
                # 스포일러 제목 (버튼 텍스트)
                try:
                    title_btn = spoiler.find_element(By.CSS_SELECTOR, ".bbCodeSpoiler-button-title")
                    title = title_btn.text
                except:
                    title = ""

                # 스포일러 내용
                try:
                    content_elem = spoiler.find_element(By.CSS_SELECTOR, ".bbCodeSpoiler-content")
                    content = content_elem.text
                except:
                    content = ""

                # 제목에서 게임 ID 찾기
                found_ids = []
                for pattern in game_id_patterns:
                    matches = re.findall(pattern, title, re.IGNORECASE)
                    found_ids.extend([m.upper() for m in matches])

                # 코드 블록 찾기
                codes = re.findall(
                    r'([0-9A-Fa-f]{8}\s+[0-9A-Fa-f]{8})',
                    content
                )

                if title:
                    print(f"[DEBUG] Spoiler title: '{title[:50]}', IDs: {found_ids}, codes: {len(codes)}")

                if found_ids and codes and len(codes) >= 5:
                    valid_ids = [gid for gid in found_ids if len(gid) == 6]
                    for game_id in valid_ids:
                        full_code = '\n'.join(codes)
                        if game_id not in collected_patches:
                            collected_patches[game_id] = {
                                'name': title or f'CC Patch ({game_id})',
                                'source': 'gbatemp',
                                'url': thread_url,
                                'codes': [full_code],
                                'raw_lines': codes
                            }
                            print(f"  [FOUND] {game_id} - {len(codes)} code lines")

            except Exception as e:
                continue

        # 첫 번째 포스트 (OP) 분석 - 모든 게임이 여기에 있음
        first_post = driver.find_elements(By.CSS_SELECTOR, "article.message")[0]
        post_html = first_post.get_attribute('innerHTML')

        # HTML을 디버그 파일로 저장
        debug_path = OUTPUT_DIR / "debug_first_post.html"
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write(post_html)
        print(f"[DEBUG] Saved first post HTML to {debug_path}")

        # 게임 섹션 패턴 찾기
        # 패턴: <b>게임이름</b> 또는 <strong>게임이름</strong> 다음에 게임 ID들
        # 예: <b>Little King's Story</b> ... [ROUE5G] [ROEP5G] [ROUJ5G]

        # 굵은 텍스트 (게임 제목) 찾기
        bold_pattern = r'<b>([^<]+)</b>|<strong>([^<]+)</strong>'
        bold_matches = re.findall(bold_pattern, post_html)
        bold_texts = [m[0] or m[1] for m in bold_matches]
        print(f"[DEBUG] Found {len(bold_texts)} bold texts: {bold_texts[:10]}")

        # 게임 섹션 분리
        # HTML을 게임별로 분할
        game_sections = re.split(r'<b>|<strong>', post_html)
        print(f"[DEBUG] Found {len(game_sections)} sections")

        for section in game_sections[1:]:  # 첫 번째는 헤더
            # 게임 이름 추출
            name_match = re.match(r'([^<]+)</b>|([^<]+)</strong>', section)
            if not name_match:
                continue
            game_name = (name_match.group(1) or name_match.group(2) or "").strip()

            # 게임 ID 찾기
            found_ids = []
            for pattern in game_id_patterns:
                matches = re.findall(pattern, section[:2000])  # 섹션 앞부분에서만
                found_ids.extend([m.upper() for m in matches])

            valid_ids = list(set([gid for gid in found_ids if len(gid) == 6]))

            # 코드 찾기
            codes = re.findall(
                r'([0-9A-Fa-f]{8}\s+[0-9A-Fa-f]{8})',
                section
            )

            if valid_ids and codes and len(codes) >= 5:
                print(f"[DEBUG] Section '{game_name[:30]}': IDs={valid_ids}, codes={len(codes)}")
                for game_id in valid_ids:
                    full_code = '\n'.join(codes)
                    if game_id not in collected_patches:
                        collected_patches[game_id] = {
                            'name': game_name,
                            'source': 'gbatemp',
                            'url': thread_url,
                            'codes': [full_code],
                            'raw_lines': codes
                        }
                        print(f"  [FOUND] {game_id} ({game_name}) - {len(codes)} code lines")

        # 페이지 2-5도 스크래핑 (첫 페이지에 모든 게임이 없을 수 있음)
        for page_num in range(2, 6):
            try:
                page_url = f"{thread_url}page-{page_num}"
                print(f"[INFO] Loading page {page_num}...")
                driver.get(page_url)

                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "message-content"))
                )
                time.sleep(1)

                # 스포일러 열기
                spoiler_buttons = driver.find_elements(By.CSS_SELECTOR, ".bbCodeSpoiler-button")
                for btn in spoiler_buttons:
                    try:
                        driver.execute_script("arguments[0].click();", btn)
                    except:
                        pass
                time.sleep(0.5)

                messages = driver.find_elements(By.CSS_SELECTOR, ".message-body")

                for msg in messages:
                    try:
                        msg_text = msg.text
                        id_matches = re.findall(game_id_pattern, msg_text)
                        codes_in_msg = re.findall(
                            r'([0-9A-Fa-f]{8}\s+[0-9A-Fa-f]{8})',
                            msg_text
                        )

                        if id_matches and codes_in_msg:
                            for game_id in id_matches:
                                game_id = game_id.upper()
                                full_code = '\n'.join(codes_in_msg)

                                if game_id not in collected_patches:
                                    collected_patches[game_id] = {
                                        'name': f'CC Patch ({game_id})',
                                        'source': 'gbatemp',
                                        'url': page_url,
                                        'codes': [full_code],
                                        'raw_lines': codes_in_msg
                                    }
                                    print(f"  [FOUND] {game_id} - {len(codes_in_msg)} code lines (page {page_num})")
                    except:
                        continue

            except Exception as e:
                print(f"[WARN] Could not load page {page_num}: {e}")
                break

    except Exception as e:
        print(f"[ERROR] Selenium scraping failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
        print("[INFO] Selenium driver closed")


def txt_to_gct(game_id: str, codes: List[str], output_path: Path) -> bool:
    """텍스트 형식의 Gecko 코드를 GCT 파일로 변환"""
    try:
        # GCT 헤더
        gct_header = bytes.fromhex('00D0C0DE00D0C0DE')
        # GCT 푸터
        gct_footer = bytes.fromhex('F000000000000000')

        code_bytes = bytearray()

        for code in codes:
            # 공백과 줄바꿈 제거
            hex_str = re.sub(r'\s+', '', code)

            # 유효한 hex 문자만
            if re.match(r'^[A-Fa-f0-9]+$', hex_str):
                try:
                    code_bytes.extend(bytes.fromhex(hex_str))
                except ValueError:
                    continue

        if not code_bytes:
            return False

        # GCT 파일 작성
        with open(output_path, 'wb') as f:
            f.write(gct_header)
            f.write(code_bytes)
            f.write(gct_footer)

        return True
    except Exception as e:
        print(f"[ERROR] Failed to create GCT for {game_id}: {e}")
        return False


def save_results():
    """수집된 패치 저장"""
    print(f"\n=== Saving Results ===")
    print(f"[INFO] Collected {len(collected_patches)} potential CC patches")

    # JSON으로 메타데이터 저장
    metadata_path = OUTPUT_DIR / "cc_patches_metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(collected_patches, f, indent=2, ensure_ascii=False)
    print(f"[INFO] Metadata saved to {metadata_path}")

    # GCT 파일 생성
    gct_count = 0
    for game_id, patch_info in collected_patches.items():
        if 'codes' in patch_info and patch_info['codes']:
            gct_path = OUTPUT_DIR / f"{game_id}-CC.gct"
            if txt_to_gct(game_id, patch_info['codes'], gct_path):
                gct_count += 1
                print(f"  [SAVED] {gct_path.name}")

    print(f"\n[DONE] Created {gct_count} GCT files in {OUTPUT_DIR}")


def scrape_wiigeckocodes():
    """wiigeckocodes.github.io에서 Wii 코드 스크래핑"""
    print("\n=== Scraping wiigeckocodes.github.io ===")

    base_url = "https://wiigeckocodes.github.io"

    # 메인 페이지에서 게임 목록 가져오기
    html = fetch_url(f"{base_url}/")
    if not html:
        # 직접 games/hacks 경로 시도
        html = fetch_url(f"{base_url}/games/")

    if not html:
        print("[ERROR] Cannot access wiigeckocodes.github.io")
        return

    # 게임 링크 찾기
    game_links = re.findall(r'href="([^"]*\.html)"', html)
    game_links = [l for l in game_links if 'games' in l.lower() or l.endswith('.html')]

    print(f"[INFO] Found {len(game_links)} game pages")

    cc_keywords = [
        'classic controller', 'classic con', 'cc support', 'cc hack',
        'nunchuk', 'nunchuck', 'button', 'controller', 'control'
    ]

    for link in game_links[:100]:  # 100개 제한
        if link.startswith('/'):
            url = f"{base_url}{link}"
        elif link.startswith('http'):
            url = link
        else:
            url = f"{base_url}/{link}"

        game_html = fetch_url(url)
        if not game_html:
            continue

        # 게임 ID 추출 (6자리)
        game_id_match = re.search(r'\[([A-Z]{4}[0-9]{2})\]', game_html)
        if not game_id_match:
            game_id_match = re.search(r'([A-Z]{4}[0-9]{2})', link.upper())

        if not game_id_match:
            continue

        game_id = game_id_match.group(1).upper()

        # CC 관련 코드 확인
        lower_html = game_html.lower()
        found_keywords = [k for k in cc_keywords if k in lower_html]

        if found_keywords:
            # 게임 이름 추출
            title_match = re.search(r'<title>([^<]+)</title>', game_html)
            game_name = title_match.group(1) if title_match else game_id

            # Gecko 코드 추출
            gecko_pattern = r'([A-F0-9]{8}\s+[A-F0-9]{8})'
            code_matches = re.findall(gecko_pattern, game_html, re.IGNORECASE)

            if code_matches and game_id not in collected_patches:
                print(f"  [FOUND] {game_name} ({game_id}) - {len(code_matches)} code lines")
                collected_patches[game_id] = {
                    'name': game_name,
                    'source': 'wiigeckocodes',
                    'url': url,
                    'codes': code_matches,
                    'keywords': found_keywords
                }

        time.sleep(0.3)


def main():
    print("=" * 60)
    print("Classic Controller Patch Scraper")
    print("=" * 60)

    # 각 소스에서 스크래핑
    scrape_wiigeckocodes()  # GitHub Pages - 가장 접근 용이
    scrape_gbatemp_cc_hacks()
    scrape_rc24_codes()
    # scrape_gamehacking()  # 필요시 활성화

    # 결과 저장
    save_results()


if __name__ == "__main__":
    main()
