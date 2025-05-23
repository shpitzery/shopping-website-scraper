# from fastapi import FastAPI, Query
# from fastapi.middleware.cors import CORSMiddleware
# from bs4 import BeautifulSoup
# import requests
# import json
# import random
# import time
# import re

# app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Store session cookies between requests
# session = requests.Session()

# # Device profiles for anti-detection
# device_profiles = [
#     {
#         "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
#         "sec_ch_ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
#         "sec_ch_ua_mobile": "?0",
#         "sec_ch_ua_platform": '"Windows"'
#     },
#     {
#         "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
#         "sec_ch_ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
#         "sec_ch_ua_mobile": "?0",
#         "sec_ch_ua_platform": '"macOS"'
#     },
#     {
#         "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
#         "sec_ch_ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
#         "sec_ch_ua_mobile": "?0",
#         "sec_ch_ua_platform": '"Linux"'
#     }
# ]

# # Site configurations for the 4 target sites
# SITES_CONFIG = {
#     "amazon": {
#         "name": "Amazon",
#         "search_url": "https://www.amazon.com/s?k={query}&ref=nb_sb_noss",
#         "search_result_selector": "div[data-component-type='s-search-result']",
#         "selectors": {
#             "title": "h2.a-size-medium span",
#             "price": ".a-price .a-offscreen, .a-price-whole",
#             "rating": ".a-size-small .a-color-base, .a-icon-alt",
#             "reviews": "span.a-size-small.s-underline-text, .s-underline-text, a[href*='customerReviews']",
#             "image": ".s-image",
#             "url": "h2.a-size-mini a, .a-link-normal"
#         }
#     },

#     "bestbuy": {
#     "name": "Best Buy",
#     "search_url": "https://www.bestbuy.com/site/searchpage.jsp?st={query}&intl=nosplash",
#     "search_result_selector": "li.product-list-item",  # Fixed: was missing 'li.'
#     "selectors": {
#         "title": ".product-list-item-title",  # This should work
#         "price": ".visually-hidden",  # Need to parse this with regex
#         "rating": ".visually-hidden", # Same element, different regex
#         "reviews": ".visually-hidden", # Same element, different regex  
#         "image": ".product-image img",
#         "url": "a[href*='/site/']"
#         }
#     },
#     # "target": {
#     #     "name": "Target",
#     #     "search_url": "https://www.target.com/s?searchTerm={query}",
#     #     "search_result_selector": "div[data-test='@web/site/product_card/ProductCard']",
#     #     "selectors": {
#     #         "title": "a[data-test='product-title']",
#     #         "price": "span[data-test='product-price']",
#     #         "rating": "div[data-test='ratings-and-reviews'] span",
#     #         "reviews": "a[data-test='rating-count']",
#     #         "image": "img[data-test='productImage-primary']",
#     #         "url": "a[data-test='product-title']"
#     #     }
#     # },
#     # "newegg": {
#     #     "name": "Newegg",
#     #     "search_url": "https://www.newegg.com/p/pl?d={query}",
#     #     "search_result_selector": "div.item-container",
#     #     "selectors": {
#     #         "title": ".item-title",
#     #         "price": ".price-current strong, .price-current-num",
#     #         "rating": ".item-rating i",
#     #         "reviews": ".item-rating-num",
#     #         "image": ".item-img img",
#     #         "url": ".item-title"
#     #     }
#     # }
# }

# def get_headers():
#     """Generate realistic browser headers"""
#     profile = random.choice(device_profiles)
    
#     headers = {
#         "User-Agent": profile["user_agent"],
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
#         "Accept-Language": "en-US,en;q=0.9",
#         "Accept-Encoding": "gzip, deflate, br, zstd",
#         "DNT": "1",
#         "Connection": "keep-alive",
#         "Upgrade-Insecure-Requests": "1",
#         "Sec-Fetch-Dest": "document",
#         "Sec-Fetch-Mode": "navigate",
#         "Sec-Fetch-Site": "none",
#         "Sec-Fetch-User": "?1",
#         "Cache-Control": "max-age=0"
#     }

#         # Add Chrome-specific headers
#     if "Chrome" in profile["user_agent"]:
#         headers.update({
#             "sec-ch-ua": profile["sec_ch_ua"],
#             "sec-ch-ua-mobile": profile["sec_ch_ua_mobile"],
#             "sec-ch-ua-platform": profile["sec_ch_ua_platform"]
#         })
    
#     referrers = [
#         "https://www.google.com/",
#         "https://www.bing.com/",
#         "https://www.google.com/search?q=shopping"
#     ]
#     headers["Referer"] = random.choice(referrers)
    
#     return headers

# def clean_text(text):
#     """Clean extracted text"""
#     if not text:
#         return ""
#     return re.sub(r'\s+', ' ', text.strip())

# def extract_price(price_text):
#     """Extract clean price from text"""
#     if not price_text:
#         return None
    
#     # Look for price patterns
#     price_match = re.search(r'[\$]?([\d,]+\.?\d{0,2})', price_text.replace(',', ''))
#     if price_match:
#         return f"${price_match.group(1)}"
#     return price_text.strip()

# def extract_rating(rating_text):
#     """Extract rating number from text"""
#     if not rating_text:
#         return None
    
#     rating_match = re.search(r'([\d\.]+)', rating_text)
#     if rating_match:
#         return rating_match.group(1)
#     return None

# def extract_bestbuy_data(first_result):
#     """Enhanced Best Buy data extraction"""
#     print(first_result.prettify())
#     product = {
#         "site": "Best Buy",
#         "site_key": "bestbuy", 
#         "success": True
#     }
    
#     # Extract title - it's in the product-list-item-title
#     title_elem = first_result.select_one(".product-list-item-title")
#     if title_elem:
#         product["title"] = clean_text(title_elem.get_text())
    
#     # Extract price - Best Buy has complex pricing structure
#     price_selectors = [
#         ".customer-price.medium",
#         ".medium-customer-price", 
#         "[data-testid*='price']",
#         ".visually-hidden:contains('current price')",
#         ".sr-only:contains('current price')"
#     ]
    
#     for selector in price_selectors:
#         try:
#             if ":contains(" in selector:
#                 # Handle contains selector manually
#                 elements = first_result.select(".visually-hidden, .sr-only")
#                 for elem in elements:
#                     text = elem.get_text().lower()
#                     if "current price" in text:
#                         # Extract price from the text
#                         price_match = re.search(r'\$[\d,]+\.?\d{0,2}', elem.get_text())
#                         if price_match:
#                             product["price"] = price_match.group()
#                             break
#             else:
#                 price_elem = first_result.select_one(selector)
#                 if price_elem:
#                     product["price"] = extract_price(price_elem.get_text())
#                     break
#         except Exception as e:
#             continue
    
#     # Extract rating - Best Buy uses visually-hidden elements
#     rating_elements = first_result.select(".visually-hidden")
#     for elem in rating_elements:
#         text = elem.get_text()
#         if "Rating" in text and "out of 5" in text:
#             rating_match = re.search(r'Rating ([\d\.]+) out of 5', text)
#             if rating_match:
#                 product["rating"] = rating_match.group(1)
#                 break
    
#     # Extract review count
#     for elem in rating_elements:
#         text = elem.get_text()
#         if "reviews" in text.lower():
#             review_match = re.search(r'(\d+(?:,\d{3})*)', text)
#             if review_match:
#                 product["reviews"] = review_match.group(1)
#                 break
    
#     # Extract image
#     img_elem = first_result.select_one(".product-image img")
#     if img_elem:
#         img_src = img_elem.get("src") or img_elem.get("data-src")
#         if img_src and not img_src.startswith("data:"):
#             product["image"] = img_src
    
#     # Extract product URL
#     url_elem = first_result.select_one("a[href*='/site/']")
#     if url_elem and url_elem.get("href"):
#         href = url_elem["href"]
#         if href.startswith("http"):
#             product["product_url"] = href
#         else:
#             product["product_url"] = "https://www.bestbuy.com" + href
    
#     return product

# def find_element_with_multiple_selectors(soup_element, selector_string):
#     """
#     Try multiple selectors separated by comma until one works
    
#     Args:
#         soup_element: BeautifulSoup element to search within
#         selector_string: String with multiple selectors separated by commas
    
#     Returns:
#         First matching element or None
#     """
#     selectors = [s.strip() for s in selector_string.split(", ")]
#     for selector in selectors:
#         try:
#             element = soup_element.select_one(selector)
#             if element and element.get_text().strip():  # Make sure it has text
#                 return element
#         except Exception as e:
#             continue
#     return None

# # Updated scrape_site function to handle Best Buy specifically:
# def scrape_site(site_key, query):
#     """
#     Enhanced site scraping with Best Buy specific handling
#     """
#     config = SITES_CONFIG[site_key]
    
#     try:
#         # Build search URL
#         search_url = config["search_url"].format(query=query.replace(' ', '+'))
#         print(f"Searching {config['name']}: {search_url}")
        
#         # Make request
#         headers = get_headers()
#         response = requests.get(search_url, headers=headers, timeout=15)
        
#         if response.status_code != 200:
#             return {
#                 "site": config["name"],
#                 "error": f"HTTP {response.status_code}",
#                 "success": False
#             }
        
#         # Parse HTML
#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         # Check for anti-bot detection
#         if any(keyword in soup.text.lower() for keyword in ["captcha", "robot check", "unusual traffic"]):
#             return {
#                 "site": config["name"],
#                 "error": "Anti-bot detection triggered",
#                 "success": False
#             }
        
#         # Find first search result
#         first_result = soup.select_one(config["search_result_selector"])
#         if not first_result:
#             # Debug: Let's see what we can find
#             debug_containers = soup.select("li[class*='product'], div[class*='product'], [data-testid*='product']")
#             print(f"Debug {config['name']}: Found {len(debug_containers)} potential containers")
            
#             if debug_containers:
#                 first_result = debug_containers[0]
#                 print(f"Using fallback container: {first_result.get('class', [])}")
#             else:
#                 return {
#                     "site": config["name"],
#                     "error": "No search results found",
#                     "success": False,
#                     "debug": f"Page title: {soup.title.string if soup.title else 'No title'}"
#                 }
        
#         # Use Best Buy specific extraction if it's Best Buy
#         if site_key == "bestbuy":
#             return extract_bestbuy_data(first_result)
        
#         # For other sites, use the existing generic extraction logic
#         product = {
#             "site": config["name"],
#             "site_key": site_key,
#             "success": True
#         }
        
#         selectors = config["selectors"]
        
#         # Extract title
#         title_elem = find_element_with_multiple_selectors(first_result, selectors["title"])
#         if title_elem:
#             product["title"] = clean_text(title_elem.get_text())
        
#         # Extract price
#         price_elem = find_element_with_multiple_selectors(first_result, selectors["price"])
#         if price_elem:
#             product["price"] = extract_price(price_elem.get_text())
        
#         # Extract rating
#         rating_elem = find_element_with_multiple_selectors(first_result, selectors["rating"])
#         if rating_elem:
#             rating_text = rating_elem.get_text() or rating_elem.get("title", "")
#             product["rating"] = extract_rating(rating_text)
        
#         # Extract review count
#         reviews_elem = find_element_with_multiple_selectors(first_result, selectors["reviews"])
#         if reviews_elem:
#             reviews_text = reviews_elem.get_text()
#             review_match = re.search(r'\((\d+(?:,\d{3})*)\)|(\d+(?:,\d{3})*)', reviews_text)
#             if review_match:
#                 product["reviews"] = review_match.group(1) or review_match.group(2)
        
#         # Extract image
#         img_elem = find_element_with_multiple_selectors(first_result, selectors["image"])
#         if img_elem:
#             img_src = img_elem.get("src") or img_elem.get("data-src")
#             if img_src and not img_src.startswith("data:"):
#                 product["image"] = img_src
        
#         # Extract product URL
#         url_elem = find_element_with_multiple_selectors(first_result, selectors["url"])
#         if url_elem and url_elem.get("href"):
#             href = url_elem["href"]
#             if href.startswith("http"):
#                 product["product_url"] = href
#             else:
#                 base_url = f"https://www.{site_key}.com"
#                 product["product_url"] = base_url + href
 
        
#         print(f"✅ {config['name']}: Found {product.get('title', 'Product')[:50]}...")
#         return product
        
#     except requests.exceptions.RequestException as e:
#         return {
#             "site": config["name"],
#             "error": f"Request failed: {str(e)}",
#             "success": False
#         }
#     except Exception as e:
#         return {
#             "site": config["name"],
#             "error": f"Parsing failed: {str(e)}",
#             "success": False
#         }

# def compare_product(query):
#     """
#     Compare product across all 4 sites
    
#     Args:
#         query: Product name/model to search for
    
#     Returns:
#         Dictionary with results from all sites plus comparison
#     """
#     print(f"\n🔍 Searching for: {query}")
#     print("=" * 50)
    
#     results = {
#         "query": query,
#         "timestamp": time.time(),
#         "sites": {},
#         "comparison": {
#             "lowest_price": None,
#             "highest_rating": None,
#             "most_reviews": None
#         }
#     }
    
#     # Scrape each site
#     for site_key in SITES_CONFIG.keys():
#         try:
#             site_result = scrape_site(site_key, query)
#             results["sites"][site_key] = site_result
            
#             if not site_result.get("success"):
#                 print(f"❌ {site_result['site']}: {site_result.get('error', 'Unknown error')}")
            
#             # Add delay between sites to be respectful
#             time.sleep(random.uniform(2, 4))
            
#         except Exception as e:
#             results["sites"][site_key] = {
#                 "site": SITES_CONFIG[site_key]["name"],
#                 "error": str(e),
#                 "success": False
#             }
#             print(f"❌ {SITES_CONFIG[site_key]['name']}: {str(e)}")
    
#     # Analyze results for comparison
#     successful_results = [r for r in results["sites"].values() if r.get("success")]
#     print(f"\n📊 Successfully scraped {len(successful_results)}/4 sites")
    
#     if successful_results:
#         # Find lowest price
#         prices = []
#         for result in successful_results:
#             if "price" in result:
#                 price_match = re.search(r'([\d,]+\.?\d{0,2})', result["price"].replace('$', '').replace(',', ''))
#                 if price_match:
#                     price_val = float(price_match.group(1))
#                     prices.append({"site": result["site"], "price": price_val, "display": result["price"]})
        
#         if prices:
#             lowest = min(prices, key=lambda x: x["price"])
#             results["comparison"]["lowest_price"] = {
#                 "site": lowest["site"],
#                 "price": lowest["display"]
#             }
#             print(f"💰 Lowest price: {lowest['display']} at {lowest['site']}")
        
#         # Find highest rating
#         ratings = []
#         for result in successful_results:
#             if "rating" in result:
#                 try:
#                     rating_val = float(result["rating"])
#                     ratings.append({"site": result["site"], "rating": rating_val})
#                 except ValueError:
#                     pass
        
#         if ratings:
#             highest = max(ratings, key=lambda x: x["rating"])
#             results["comparison"]["highest_rating"] = {
#                 "site": highest["site"],
#                 "rating": highest["rating"]
#             }
#             print(f"⭐ Highest rating: {highest['rating']} at {highest['site']}")
        
#         # Find most reviews
#         review_counts = []
#         for result in successful_results:
#             if "reviews" in result:
#                 try:
#                     review_val = int(result["reviews"].replace(',', ''))
#                     review_counts.append({"site": result["site"], "count": review_val})
#                 except ValueError:
#                     pass
        
#         if review_counts:
#             most_reviews = max(review_counts, key=lambda x: x["count"])
#             results["comparison"]["most_reviews"] = {
#                 "site": most_reviews["site"],
#                 "count": f"{most_reviews['count']:,}"
#             }
#             print(f"📝 Most reviews: {most_reviews['count']:,} at {most_reviews['site']}")
    
#     print("=" * 50)
#     return results

# @app.get("/")
# def root():
#     """Root endpoint with API info"""
#     return {
#         "app": "Product Price Comparison API",
#         "version": "1.0",
#         "supported_sites": list(SITES_CONFIG.keys()),
#         "usage": "GET /compare?product=YOUR_PRODUCT_NAME"
#     }

# @app.get("/compare")
# def compare_product_endpoint(product: str = Query(..., description="Product name or model to search for")):
#     """
#     Compare a product across Amazon, Best Buy, Target, and Newegg
    
#     Example: /compare?product=Lenovo Tab P12-2024
#     """
#     if not product or len(product.strip()) < 3:
#         return {
#             "error": "Product name must be at least 3 characters long",
#             "example": "Lenovo Tab P12-2024"
#         }
    
#     return compare_product(product.strip())

# @app.get("/health")
# def health_check():
#     """Health check endpoint"""
#     return {"status": "healthy", "timestamp": time.time()}

# if __name__ == "__main__":
#     import uvicorn
#     print("🚀 Starting Product Comparison API...")
#     print("📍 Visit: http://localhost:8000/compare?product=Lenovo Tab P12-2024")
#     print("📍 API Docs: http://localhost:8000/docs")
#     uvicorn.run(app, host="0.0.0.0", port=8000)




from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import re
import os

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.strip())

def fetch_html_with_scroll(url: str, scroll_pause_time: float = 1.5, max_scrolls: int = 10) -> str:
    print(f"[INFO] Launching browser for: {url}")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        print("[INFO] Page loaded. Starting to scroll...")

        last_height = driver.execute_script("return document.body.scrollHeight")

        for i in range(max_scrolls):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(f"[INFO] Scrolled to bottom (#{i + 1})")
            time.sleep(scroll_pause_time)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("[INFO] Reached end of page (no more content to load).")
                break
            last_height = new_height

        html = driver.page_source
        print("[INFO] Finished scrolling and captured HTML.")

    finally:
        driver.quit()
        print("[INFO] Browser closed.")

    return html

def write_html_to_file(html: str):
    soup = BeautifulSoup(html, "html.parser")
    product_items = soup.select(".product-list-item")
    with open("debug_products_only.html", "w", encoding="utf-8") as f:
        for item in product_items:
            f.write(item.prettify())
            f.write("\n\n<!-- ====== NEXT ITEM ====== -->\n\n")
        f.flush()
        os.fsync(f.fileno())

def extract_data_from_html():
    try:

        with open("debug_products_only.html", "r", encoding="utf-8") as f:
            html = f.read()

        # Parse it with BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        # Try different experiments here
        print("[DEBUG] Trying to find all product titles:\n")

        title_tags = soup.select("h2.product-title")
        if title_tags:
            title = title_tags[0].text
            title = clean_text(title)
            print("[DEBUG] Title:", title)
        else:
            print("[DEBUG] No titles found.")

        # for tag in soup.select("h2.product-title"):
            # print(tag.text.strip())
            # print(soup.find("h2", class_="product-title").text.strip())

        print("\n[DEBUG] Trying to find prices:\n")
        print(soup.select("div.pricing")[0].text.strip())
    
    except Exception as e:
        print(f"[ERROR] Failed to extract data: {str(e)}")
    
if __name__ == "__main__":
    url = "https://www.bestbuy.com/site/searchpage.jsp?st=lenovo+tab+p12-2024&intl=nosplash"
    html = fetch_html_with_scroll(url)
    # with open("debug_bestbuy.html", "w", encoding="utf-8") as f:
    #     f.write(html)
    write_html_to_file(html)
    extract_data_from_html()
    
    # print("[RESULT] Scraped data:")
    # for title, price in zip(data["titles"], data["prices"]):
    #     print(f"  - {title} | {price}")