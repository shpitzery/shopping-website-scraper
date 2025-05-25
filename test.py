import requests
import random
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

import re

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.strip())



def fetch_amazon_html(query):
    url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}&ref=nb_sb_noss"
    # url = "https://www.newegg.com/p/pl?d=Lenovo+Tab+P12-2024&intl=nosplash"
    headers = get_headers()
    response = requests.get(url, headers=headers, timeout=15)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch page: HTTP {response.status_code}")
    # return BeautifulSoup(response.text, 'html.parser')
    bs = BeautifulSoup(response.text, 'html.parser')
    # return bs.select_one("div[role='listitem']")
    return bs.select_one("div.item-cell")


from config import SITES as websites

# Example usage:
if __name__ == "__main__":
    # query = "Lenovo Tab P12-2024"
    query = "ipad"
    # soup = fetch_amazon_html(query)
    
    # with open("newegg_search_results.html", "w", encoding="utf-8") as f:
    #     for item in soup:
    #         f.write(item.prettify())
    #         f.write("\n\n<!-- ====== NEXT ITEM ====== -->\n\n")
    #         f.flush()

    # with open("newegg_search_results.html", "r", encoding="utf-8") as f:
    #         html = f.read()
    with open("Amazon.html", "r", encoding="utf-8") as f:
            html = f.read()


    soup = BeautifulSoup(html, "html.parser")


    title = soup.select_one(websites[0]["title_selector"])
    if title:
        print("Title:", clean_text(title.text), '\n')
    else:
        print("No title found.", '\n')

    raw_price_block = soup.select_one(websites[0]["price_selector"])
    if raw_price_block:
        parts = list(raw_price_block.stripped_strings)
        raw_price_block = clean_text(''.join(parts))
        # Use regex to extract the first price-like pattern
        price_match = re.search(r'\$[\d,]+\.?\d{0,2}', raw_price_block.replace(',', '').strip())
        if price_match:
            price = price_match.group(0)
            price = clean_text(price)
            print("Price:", price_match.group(0), '\n')
        else:
            print(raw_price_block, '\n')
            print("No price found in block.", '\n')
    else:
        print("Price block not found.", '\n')

    img_elem = soup.select_one(websites[0]["img_selector"])
    if img_elem:
        img_src = img_elem.get("src") or img_elem.get("data-src")
        if img_src and not img_src.startswith("data:"):
            print("Image:", img_src, '\n')
        else:
            print("No image found.", '\n')

    url_elem = soup.select_one(websites[0]["url_selector"])
    if url_elem and url_elem.get("href"):
        href = url_elem["href"]
        print("URL:", "https://www.walmart.com" + href, '\n')
    else:
        print("No URL found.", '\n')

    rating_elem = soup.select_one(websites[0]["rating_selector"])
    if rating_elem:
        rating_match = re.search(r"([\d\.]+)", rating_elem.text.strip())
        if rating_match:
            rating = rating_match.group(1)
            print("Rating:", rating, '\n')
        else:
            print(rating_elem, '\n')
            print(rating_match)
            print("No rating found in block.", '\n')
    else:
        print("Rating block not found.", '\n')

    # # TODO: walmart rating function
    # # for span in soup.select(""):
    # #     if "out of 5 Stars" in span.text:
    # #         match = re.search(r"(\d+(?:\.\d+)?)\s+out of 5", span.text)
    # #         if match:
    # #             print("Rating:", match.group(1), '\n')
    # #         break

    reviews_elem = soup.select_one(websites[0]["reviews_selector"])
    if reviews_elem:
        part = ''.join(list(reviews_elem.stripped_strings)).replace(',', '')
        reviews_match = re.search(r"\((\d+)\)|^(\d+)$", part)
        # reviews_match = reviews_match.group(1) or reviews_match.group(2) 
        if reviews_match:
            reviews = reviews_match.group(1) or reviews_match.group(2)
            print("Reviews:", reviews)
            reviews = reviews_match.group(0)
            print("Reviews:", reviews)
        else:
            print(part)
            print(reviews_match)
            # print(re.search(r"([\d\.]+)", s.group(0)))
            # print(reviews_match)
            print("No reviews found in block.")
    else:
        print("Reviews block not found.")







# def fetch_amazon_html(url):
#     headers = get_headers()
#     response = requests.get(url, headers=headers, timeout=15)
#     if response.status_code != 200:
#         raise Exception(f"Failed to fetch page: HTTP {response.status_code}")
    
#     bs = BeautifulSoup(response.text, 'html.parser')
#     soup = bs.select_one("div[role='listitem']")
#     with open("amazon.html", "w", encoding="utf-8") as f:
#         f.write(soup.prettify())
#         f.write("\n\n<!-- ====== NEXT ITEM ====== -->\n\n")