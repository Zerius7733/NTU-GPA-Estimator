# pip install playwright beautifulsoup4
# playwright install

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os,json

DIR = os.path.dirname(__file__)
URL = "https://ntumods.com/mods"
CACHE_FILE = 'mods_cache.json'
mods_cache = {}
# --- Load persistent cache on startup ---
def checking_cache_file(DIR=DIR):
    global CACHE_FILE,mods_cache
    CACHE_FILE = os.path.join(DIR,CACHE_FILE)
    print(CACHE_FILE)
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            try:
                mods_cache = json.load(f)
                #print(f"checking ip cache: {mods_cache}")
            except json.JSONDecodeError:
                mods_cache = {}
    else:
        mods_cache = {}
    return mods_cache

def _save_cache():
    """Helper to safely save persistent cache."""
    tmp_file = CACHE_FILE + ".tmp"
    with open(tmp_file, "w") as f:
        json.dump(mods_cache, f, indent=2)
    os.replace(tmp_file, CACHE_FILE)
    
def scrape_ntumods():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="networkidle")
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    mods = {}

    # Each module is likely a clickable <a> card
    for a in soup.select('a[href^="/mods/"]'):
        href = urljoin(URL, a["href"])
        lines = [x.strip() for x in a.stripped_strings if x.strip()]

        if len(lines) >= 3:
            code = lines[0]
            title = lines[1]
            # Middle items = tags, last one = school
            tags = lines[2:-1]
            school = lines[-1]
        else:
            continue  # skip incomplete cards

        mods[code] = {
            "title": title,
            "tags": tags,
            "school": school,
            "url": href
        }
    return mods

def main():
    global mods_cache
    #checking_cache_file(DIR)
    modules = scrape_ntumods()
    print(modules)
    print(f"Collected {len(modules)} modules")
    for i, (k, v) in enumerate(list(modules.items())[:], 1):
        #print(f"{i:>2}. {k}: {v['title']} ({v['school']}) {v['tags']}")
        mods_cache[k] = v["title"]
    #_save_cache()
        

if __name__ == "__main__":
    main()
    #checking_cache_file(DIR)