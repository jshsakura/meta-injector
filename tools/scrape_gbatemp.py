
import cloudscraper
import re

def scrape_gbatemp():
    scraper = cloudscraper.create_scraper()
    url = "https://gbatemp.net/threads/new-classic-controller-hacks.659837/"
    
    try:
        print(f"Fetching {url}...")
        response = scraper.get(url)
        if response.status_code == 200:
            print("Successfully fetched the page.")
            content = response.text
            
            # Save Page 1
            with open("gbatemp_page_1.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("Saved Page 1 to gbatemp_page_1.html")

            # Simple check for keywords in Page 1
            if "X button" in content or "cursor" in content:
                print("Found 'X button' or 'cursor' in Page 1.")
                
            # Try to find the last page number to jump to end
            # classic pagination: page-nav ... /page-34
            page_matches = re.findall(r'page-(\d+)', content)
            if page_matches:
                max_page = max(int(p) for p in page_matches)
                print(f"Max page found: {max_page}")
                
                last_page_url = f"{url}page-{max_page}"
                print(f"Fetching last page: {last_page_url}")
                response_last = scraper.get(last_page_url)
                if response_last.status_code == 200:
                    print(f"Successfully fetched last page ({max_page}).")
                    # Save content to file for analysis
                    with open("gbatemp_last_page.html", "w", encoding="utf-8") as f:
                        f.write(response_last.text)
                    print(f"Saved last page to gbatemp_last_page.html")
        else:
            print(f"Failed to fetch. Status: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    scrape_gbatemp()
