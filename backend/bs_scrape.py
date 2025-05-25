import requests
import random
import os
from bs4 import BeautifulSoup

# Device profiles for anti-detection
device_profiles = [
    {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec_ch_ua_mobile": "?0",
        "sec_ch_ua_platform": '"Windows"'
    },
    {
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec_ch_ua_mobile": "?0",
        "sec_ch_ua_platform": '"macOS"'
    },
    {
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec_ch_ua_mobile": "?0",
        "sec_ch_ua_platform": '"Linux"'
    }
]

def get_headers():
    profile = random.choice(device_profiles)
    headers = {
        "User-Agent": profile["user_agent"],
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "Referer": random.choice([
            "https://www.google.com/",
            "https://www.bing.com/",
            "https://www.google.com/search?q=shopping"
        ])
    }
    if "Chrome" in profile["user_agent"]:
        headers.update({
            "sec-ch-ua": profile["sec_ch_ua"],
            "sec-ch-ua-mobile": profile["sec_ch_ua_mobile"],
            "sec-ch-ua-platform": profile["sec_ch_ua_platform"]
        })
    return headers

def write_html_with_bs(company, files_dir, url, selector):
    headers = get_headers()
    response = requests.get(url, headers=headers, timeout=15)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch page: HTTP {response.status_code}")
    
    bs = BeautifulSoup(response.text, 'html.parser')
    soup = bs.select_one(selector)
    target_dir = os.path.join(files_dir, f'{company}.html')

    with open(target_dir, "w", encoding="utf-8") as f:
        f.write(soup.prettify())
        f.write("\n\n<!-- ====== NEXT ITEM ====== -->\n\n")
