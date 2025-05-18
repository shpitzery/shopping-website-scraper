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

def extract_first_product(soup):
    try:
        # Find all search result items
        items = soup.find_all("div", {"data-component-type": "s-search-result"})
        
        if not items:
            return None
        
        # Get the first item
        item = items[0]
        
        # Create a product dictionary
        product = {}
        
        # Extract title
        title_element = item.select_one("h2 a span")
        if title_element:
            product["title"] = title_element.text.strip()
        
        # Extract price
        price_element = item.select_one(".a-price .a-offscreen")
        if price_element:
            product["price"] = price_element.text.strip()
        else:
            # Try alternative price selectors
            alt_price = item.select_one(".a-price") or item.select_one(".a-color-base")
            if alt_price:
                product["price"] = alt_price.text.strip()
        
        # Extract image URL
        image_element = item.select_one("img.s-image")
        if image_element and "src" in image_element.attrs:
            product["image"] = image_element["src"]
        
        # Extract product URL
        url_element = item.select_one("h2 a")
        if url_element and "href" in url_element.attrs:
            product["url"] = "https://www.amazon.com" + url_element["href"]
            
            # Extract ASIN from URL if possible
            try:
                import re
                asin_match = re.search(r'/dp/([A-Z0-9]{10})/', url_element["href"])
                if asin_match:
                    product["asin"] = asin_match.group(1)
            except:
                pass
        
        # Extract ratings if available
        try:
            rating_element = item.select_one("i.a-icon-star-small")
            if rating_element:
                rating_text = rating_element.text.strip()
                product["rating"] = rating_text
        except:
            pass
            
        return product
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def amazon(query: str = Query(...)):
    # Simulate human behavior with a small delay
    time.sleep(random.uniform(3, 6))

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
                result["error"] = "Anti-bot protection detected"
                result["content_sample"] = response.text[:500]  # First 500 chars for debugging
                return result
            
            # Extract just the first product
            product = extract_first_product(soup)
            
            if product:
                result["product"] = product
            else:
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