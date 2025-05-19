from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import requests
import functions_framework
import json
import random
import time

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

def extract_first_product_url(soup):
    try:
        # Find all search result items
        items = soup.find_all("div", {"data-component-type": "s-search-result"})
        
        if not items or len(items) == 0:
            return None
        
        # Get the first item
        item = items[0]
        
        # Extract product URL
        url_element = item.select_one("a.a-link-normal.s-line-clamp-2") # Finds the first <a> tag that has both classes: a-link-normal and s-line-clamp-2.
        if url_element and "href" in url_element.attrs:
            product_url = "https://www.amazon.com" + url_element["href"]
            return product_url
            
        return None
    except Exception as e:
        print(f"Error extracting URL: {str(e)}")

def extract_product_info(soup, product_url):
    try:
        product = {
            "url": product_url,
            "scraped_from": "product_page"
        }

        # Extract product title
        title = soup.select_one("span#productTitle")
        if title:
            product["title"] = title.text.strip()
        
        # Extract product price
        price = soup.select_one("span.a-offscreen")
        if price:
            product["price"] = price.text.strip()
        
        # Extract product image
        images = soup.select("div.imgTagWrapper img")
        image = None

        for img in images:
            if img.has_attr("atr") and "Lenovo Tab P12-2024" in img["alt"]:
                image = img
                break

        if image:
            if image.has_attr("data-a-dynamic-image"):
                try:
                    import json
                    dynamic_imgs = json.loads(image["data-a-dynamic-image"])
                    if dynamic_imgs and isinstance(dynamic_imgs, dict) and len(dynamic_imgs) > 0:
                        # Sort the image URLs by size to get the highest resolution
                        sorted_urls = sorted(dynamic_imgs.keys(), 
                                            key=lambda x: sum(int(dim) for dim in str(dynamic_imgs[x]).replace('[', '').replace(']', '').split(',')),
                                            reverse=True)
                        
                        product["image"] = sorted_urls[0]
                        product["image_alt"] = image.get('alt', '')  # Preserve the detailed alt text
                        # Also extract all available image sizes
                        product["available_image_sizes"] = {url: dynamic_imgs[url] for url in dynamic_imgs}
                except Exception as e:
                    # Fallback to src if JSON parsing fails
                    product["image"] = image.get('src', '')
                    product["image_alt"] = image.get('alt', '')
            else:
                # Use src attribute directly if no data-a-dynamic-image
                product["image"] = image.get('src', '')
                product["image_alt"] = image.get('alt', '')
                
        
        # Fallback to other image selectors if the specific image wasn't found
        if "image" not in product or not product["image"]:
            # Fallback extraction code from before...
            pass
        
       
        
    #     # Extract ratings if available
        try:
            rating_element = item.select_one("i.a-icon-star-small")
            if rating_element:
                rating_text = rating_element.text.strip()
                product["rating"] = rating_text
        except:
            pass

        
        return product
    except Exception as e:
        return {"error": str(e), "error_type": type(e).__name__}
                        






@app.get("/")
def amazon(query: str = Query(...)):
    attempts = 3

    for attempt in range(attempts):
        # Simulate human behavior with a small delay
        time.sleep(random.uniform(3, 6 + attempt * 2))  # Increase delay with each attempt

        attempt_info = f"Attempt {attempt + 1} of {attempts}"

        new_session = random.random() < 0.2 # 20% chance to create a new session
        sess = requests.Session() if new_session else session
        
        # Create a more natural looking Amazon search URL
        url_templates = [
            f"https://www.amazon.com/s?k={query.replace(' ', '+')}&ref=nb_sb_noss",
            f"https://www.amazon.com/s?k={query.replace(' ', '+')}&crid={random.randint(10000000, 99999999)}",
            f"https://www.amazon.com/s?k={query.replace(' ', '+')}&sprefix={query.lower().replace(' ', '+')}"
        ]
        
        url = random.choice(url_templates)
        
        # Get fresh headers
        headers = get_headers()
    
        try:
            # Make the request with our session
            response = sess.get(url, headers=headers, timeout=15)
            
            # Create the result object
            result = {
                "status_code": response.status_code,
                "url": response.url
            }
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the HTML
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Check for blocking or captcha
                if any(text in soup.text.lower() for text in ["captcha", "robot check", "unusual traffic"]):
                    if attempt < attempts - 1:
                        continue
                    
                    result["error"] = "Anti-bot protection detected"
                    result["content_sample"] = response.text[:500]  # First 500 chars for debugging
                    return result
                
                # Extract just the first product
                product = extract_first_product_url(soup)
                
                if product:
                    result["product"] = product
                    return result
                else:
                    if attempt < attempts - 1:
                        continue
                    result["message"] = "No products found"
                    
            else:
                result["message"] = f"Failed to get data: HTTP {response.status_code}"
                result["content_sample"] = response.text[:500]  # First 500 chars for debugging
                return result
            
        except Exception as e:
            return {
                "error": str(e),
                "error_type": type(e).__name__
            }
        
    return {
        "error": f"All {attempts} attempts failed",
    }

@functions_framework.http
def amazon_function(request):
    query = request.args.get('query')
    if not query:
        return json_response({"error": "Query parameter is required"}, 400)
    
    result = amazon(query)
    return json_response(result)

def json_response(data, status_code=200):
    response = json.dumps(data)
    return (response, status_code, {'Content-Type': 'application/json'})