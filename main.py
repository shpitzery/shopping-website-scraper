from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
from product_info import extract_product_info
import requests
import functions_framework
import json
import random
import time
import re

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store session cookies between requests
session = requests.Session()

# Device and browser combinations for realistic fingerprinting
device_profiles = [
    {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "viewport": "1920x1080",
        "platform": "Windows",
        "browser": "Chrome"
    },
    {
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
        "viewport": "1680x1050",
        "platform": "MacOS",
        "browser": "Safari"
    },
    {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
        "viewport": "1366x768",
        "platform": "Windows",
        "browser": "Firefox"
    }
]

def get_headers():
    # Choose a random device profile
    profile = random.choice(device_profiles)
    
    # Basic headers all browsers use
    headers = {
        "User-Agent": profile["user_agent"],
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
    }
    
    # referer from popular sites
    referrers = [
        "https://www.google.com/",
        "https://www.bing.com/",
        "https://duckduckgo.com/",
        "https://www.google.com/search?q=amazon"
    ]
    headers["Referer"] = random.choice(referrers)
    
    return headers


def get_soup(sess, url, attempt, attempts=3):
    headers = get_headers()
    
    try:
        # Make the request with our session
        response = sess.get(url, headers=headers, timeout=15)
        
        
        # Check if the request was successful
        if response.status_code != 200 and attempt >= attempts - 1:
            return f"error: Failed to get data: HTTP {response.status_code}", f"attempt: {attempt + 1}", False
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, "html.parser")
            
        # Check for blocking or captcha
        if any(text in soup.text.lower() for text in ["captcha", "robot check", "unusual traffic"]) and attempt >= attempts - 1:
            return f"error: Anti-bot protection detected on product page", f"attempt: {attempt + 1}", False

        return response.status_code, soup, True
    
    except requests.exceptions.RequestException as e:
        return f"error: Request failed: {str(e)}", f"attempt: {attempt + 1}", False
        

def extract_first_product_url(soup, selectors):
    try:

        # Find all search result items
        # items = soup.find_all("div", {"data-component-type": "s-search-result"})
        items = soup.find_all("div", selectors["search_results"])
        
        if not items or len(items) == 0:
            return None
        
        # Get the first item
        item = items[0]
        
        # Extract product URL
        url_element = item.select_one(selectors["url_selector"])
        if url_element and "href" in url_element.attrs:
            product_url = f"https://www.{selectors['site_name'].lower()}.com" + url_element["href"]
            return product_url
            
        return None
    except Exception as e:
        print(f"Error extracting URL: {str(e)}")


# def extract_product_info(soup, product, query: str):
#     try:

#         # Extract product title
#         title = soup.select_one("span#productTitle")
#         if title:
#             product["title"] = title.text.strip()
        
#         # Extract product price
#         price_selectors = [
#             "span.a-offscreen",
#             "span.a-price-whole",
#             "#priceblock_ourprice",
#             "#priceblock_dealprice",
#             ".a-price .a-offscreen",
#             "#corePrice_feature_div .a-price .a-offscreen"
#         ]
        
#         for selector in price_selectors:
#             price_element = soup.select_one(selector)
#             if price_element and price_element.text.strip():
#                 product["price"] = price_element.text.strip()
#                 # check selector for debbugging
#                 product["price_selector"] = selector
#                 break
        
#         # Extract product image
#         images = soup.select("div.imgTagWrapper img")
#         image = None

#         for img in images:
#             if img.has_attr("alt") and f"{query}" in img.get("alt", ""):
#                 image = img
#                 break

#         if image:
#             if image.has_attr("data-a-dynamic-image"):
#                 try:
#                     dynamic_imgs = json.loads(image["data-a-dynamic-image"])
#                     if dynamic_imgs and isinstance(dynamic_imgs, dict) and len(dynamic_imgs) > 0:
#                         # Sort the image URLs by size to get the highest resolution
#                         sorted_urls = sorted(dynamic_imgs.keys(), 
#                                             key=lambda x: sum(int(dim) for dim in str(dynamic_imgs[x]).replace('[', '').replace(']', '').split(',')),
#                                             reverse=True)
                        
#                         product["image"] = sorted_urls[0]
#                         product["image_alt"] = image.get('alt', '')  # Preserve the detailed alt text

#                 except Exception as e:
#                     # Fallback to src if JSON parsing fails
#                     product["image"] = image.get('src', '')
#                     product["image_alt"] = image.get('alt', '')
#             else:
#                 # Use src attribute directly if no data-a-dynamic-image
#                 product["image"] = image.get('src', '')
#                 product["image_alt"] = image.get('alt', '')
                      
#         else:
#             # Fallback to any image if we can't find one with "Lenovo" in alt text
#             any_image = soup.select_one("div.imgTagWrapper img, #landingImage, #imgBlkFront")
#             if any_image:
#                 product["image"] = any_image.get('src', '')
#                 product["image_alt"] = any_image.get('alt', '')
  
        
#         # Extract rating and review count
#         try:
#             import re
#             # Method 1: Try the reviewCountTextLinkedHistogram which often contains the rating
#             rating_span = soup.select_one("span.reviewCountTextLinkedHistogram")
#             if rating_span and "title" in rating_span.attrs:
#                 rating_text = rating_span["title"]
#                 rating_match = re.search(r"([\d\.]+) out of", rating_text)
#                 if rating_match:
#                     product["rating"] = rating_match.group(1)
#                     product["rating_text"] = rating_text
            
#             # Method 2: Try the a-icon-alt which often contains the rating
#             if "rating" not in product:
#                 icon_alt = soup.select_one("span.a-icon-alt")
#                 if icon_alt:
#                     rating_text = icon_alt.text
#                     rating_match = re.search(r"([\d\.]+) out of", rating_text)
#                     if rating_match:
#                         product["rating"] = rating_match.group(1)
#                         product["rating_text"] = rating_text
            
#             # Method 3: Try other common rating elements
#             if "rating" not in product:
#                 rating_elements = soup.select(".a-star-4-5, .a-star-5, .a-star-4")
#                 for elem in rating_elements:
#                     class_str = " ".join(elem.get("class", []))
#                     if "a-star" in class_str:
#                         rating_match = re.search(r"a-star-(\d)-(\d)", class_str)
#                         if rating_match:
#                             whole = rating_match.group(1)
#                             fraction = rating_match.group(2)
#                             product["rating"] = f"{whole}.{fraction}"
#                             break
                            
#             # Extract review count
#             reviews = soup.select_one("#acrCustomerReviewText")
#             if reviews:
#                 count_text = reviews.text.strip()
#                 count_match = re.search(r"([\d,]+)", count_text)
#                 if count_match:
#                     product["reviews"] = count_match.group(1)
#         except Exception as e:
#             product["rating_extraction_error"] = str(e)
 

#         # Extract ASIN, whch is a unique identifier for Amazon products - 10 characters long
#         # try:
#         #     import re
#         #     asin_match = re.search(r'/dp/([A-Z0-9]{10})/', product["product_page_url"])
#         #     if asin_match:
#         #         product["asin"] = asin_match.group(1)

#         # except Exception as e:
#         #     product["asin_extraction_error"] = str(e)
        
#         # # DEBUGGING - save a snippet of the HTML to see structure
#         # product["html_sample"] = soup.prettify()[:1000]

#         return product
    
#     except Exception as e:
#         return {"error": str(e), "error_type": type(e).__name__}


@app.get("/")
def website(first_product_selectors, product_info_selectors, query: str = Query(...)):
    attempts = 3

    for attempt in range(attempts):
        # Simulate human behavior with a small delay
        time.sleep(random.uniform(3, 6 + attempt * 2))  # Increase delay with each attempt

        new_session = random.random() < 0.2 # 20% chance to create a new session
        sess = requests.Session() if new_session else session
        
        # Create a more natural looking Amazon search URL
        url_templates = [
            f"https://www.{first_product_selectors['site_name']}.com/s?k={query.replace(' ', '+')}&ref=nb_sb_noss",
            f"https://www.{first_product_selectors['site_name']}.com/s?k={query.replace(' ', '+')}&crid={random.randint(10000000, 99999999)}",
            f"https://www.{first_product_selectors['site_name']}.com/s?k={query.replace(' ', '+')}&sprefix={query.lower().replace(' ', '+')}"
        ]
        
        # why in the code, you changed this: url = random.choice(url_templates) to this: url = url_templates[attempt % len(url_templates)]
        website_url = url_templates[attempt % len(url_templates)]
    
        try:
            ret1, ret2, flag = get_soup(sess, website_url, attempt)

            if not flag:
                return {
                    ret1, 
                    ret2
                }
            
            statusCode = ret1
            soup = ret2
            
            # Create the result object
            product = {
                "into_website_status_code": statusCode,
                "attempt": attempt + 1
            }

            # Extract just the first product
            product_url = extract_first_product_url(soup, first_product_selectors)
            
            if not product_url:
                if attempt < attempts - 1:
                    continue
                return {
                    "error": "No products found",
                    "attempt": attempt + 1,
                }
            
            # Get the product details page
            time.sleep(random.uniform(2,5)) # Delay before fetching product details

            ret1, ret2, flag = get_soup(sess, product_url, attempt)

            if not flag:
                return {
                    ret1, 
                    ret2
                }
            
            statusCode = ret1
            soup = ret2
            
            product["into_product_page_status_code"] = statusCode
            product["product_page_url"] = product_url

            product_info = extract_product_info(soup, product, query, product_info_selectors)

            neccessary_info = {"product_page_url", "title", "price", "rating", "reviews", "image"}

            if product_info:
                product.update(product_info)
                missing_info = neccessary_info - product.keys()
                return {"missing_info": list(missing_info)} if missing_info else product
            
            if attempt < attempts - 1:
                continue

            return {
                "error": "Failed to extract product information",
                "attempt": attempt + 1,
            }

        except Exception as e:
            if attempt < attempts - 1:
                continue

            return {
                "error": str(e),
                "error_type": type(e).__name__,
                "attempt": attempt + 1
            }
        
    return {
        "error": f"All {attempts} attempts failed",
        "attempts": attempts,
    }


@functions_framework.http
def amazon_function(request):
    query = request.args.get('query')
    if not query:
        return json_response({"error": "Query parameter is required"}, 400)
    
    Amazon = {
        "extract_first_product_selectors": {
            "site_name": "Amazon",
            "search_results": {"data-component-type": "s-search-result"},
            "url_selector": "a.a-link-normal.s-line-clamp-2",
        },

        "extract_product_info_selectors": {
            "title_selector": "span#productTitle",

            "img_attr": "data-a-dynamic-image",
            "img_else": ["div.imgTagWrapper img", "#landingImage", "#imgBlkFront"],

            "rating_selector_method_1": "span.reviewCountTextLinkedHistogram",
            "rating_selector_method_2": "span.a-icon-alt",
            "rating_selector_method_1_2_regex": r"([\d\.]+) out of",
            "rating_selector_method_3": ".a-star-4-5, .a-star-5, .a-star-4",
            "rating_selector_method_3_regex": r"a-star-(\d)-(\d)",

            "reviews_selector": "#acrCustomerReviewText",
            "reviews_regex": r"([\d,]+)",
        }
    }
    result = website(Amazon["extract_first_product_selectors"], Amazon["extract_product_info_selectors"], query)
    return json_response(result)

def json_response(data, status_code=200):
    response = json.dumps(data)
    return (response, status_code, {'Content-Type': 'application/json'})