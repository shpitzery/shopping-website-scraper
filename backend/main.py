from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import re
import os
import tempfile

app = FastAPI()

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.strip())

def fetch_html_with_scroll(website, url: str, scroll_pause_time: float = 1.5, max_scrolls: int = 10) -> str:
    print(f"[INFO] Launching browser for: {url}")
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--incognito")
    chrome_options.add_argument(f'--user-data-dir={tempfile.mkdtemp()}')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    # driver = webdriver.Chrome(options=chrome_options)

    def wait_for_first_available(driver, selectors, timeout=30):
        for selector in selectors:
            try:
                WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"[INFO] Found content with selector: {selector}")
                return selector
            except TimeoutException:
                print(f"[DEBUG] Timeout waiting for selector: {selector}")
        raise TimeoutException("None of the selectors matched in time.")

    try:
        driver.get(url)
        try:
            us_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, website['country_popup_selector']))
            )
            if "newegg.com" in url:
            # Verify it's the right button by checking text
                if us_button.text and "stay at united states" in us_button.text.lower():
                    us_button.click()
                    print("[INFO] Dismissed country popup by clicking 'Stay at United States'")
                else:
                    print("[INFO] Found button but text doesn't match")
                
            else:
                us_button.click()
                print("[INFO] Clicked 'United States' to dismiss BestBuy country selector.")
                time.sleep(2)

        except TimeoutException:
            print("[INFO] No country popup appeared.")
        

        # with open("debug_before_wait.html", "w", encoding="utf-8") as f:
        #     f.write(driver.page_source)

        print("[INFO] Page loaded. Waiting for product grid...")

        try:

            matched_selector = wait_for_first_available(driver, website['matched_selector'])
            print(f"[INFO] Product grid appeared using: {matched_selector}")
        except TimeoutException:
            print("[WARNING] Timeout waiting for products — saving what we have")

        # with open("debug_after_wait.html", "w", encoding="utf-8") as f:
        #     f.write(driver.page_source)

        print("[INFO] Waiting a few seconds before starting scroll...")
        time.sleep(3)

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

        print("[INFO] Waiting for JS content to populate...")
        time.sleep(3)

        html = driver.page_source
        print("[INFO] Finished scrolling and captured HTML.")

    finally:
        driver.quit()
        print("[INFO] Browser closed.")

    return html

def write_html_to_file(website, files_dir, html: str, website_name: str = "debug"):
    soup = BeautifulSoup(html, "html.parser")
    product_item = soup.select_one(website['html_selector'])
    
    target_dir = os.path.join(files_dir, f'{website_name}.html')
    with open(target_dir, "w", encoding="utf-8") as f:
        f.write(product_item.prettify())
        f.write("\n\n<!-- ====== NEXT ITEM ====== -->\n\n")
        f.flush()
        os.fsync(f.fileno())

def extract_data_from_html(website, filepath, product: dict, website_name: str = "debug"):
    try:

        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()

        # Parse it with BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        # Try different experiments here
        print("[DEBUG] Trying to find all product titles:\n")
        print("\n===NEW website===\n")

        # TODO: title
        title_tags = soup.select(website['title_selector'])
        if title_tags:
            title = title_tags[0].text
            title = clean_text(title)
            product['title'] = title
            print("[DEBUG] Title:", title)
        else:
            product['title'] = None
            print("[DEBUG] No titles found.")

        print()
        # TODO: price
        raw_price_block = soup.select_one(website['price_selector'])
        if raw_price_block:
            parts = list(raw_price_block.stripped_strings)
            raw_price_block = clean_text(''.join(parts))
            # Use regex to extract the first price-like pattern
            price_match = re.search(r'\$[\d,]+\.?\d{0,2}', raw_price_block.replace(',', '').strip())
            if price_match:
                price = price_match.group(0)
                price = clean_text(price)
                product['price'] = price
                print("[DEBUG] Price:", price_match.group(0))
            else:
                product['price'] = "Price not available"
                print("[DEBUG] No price found in block.")
        else:
            product['price'] = "Price not available"
            print("[DEBUG] Price block not found.")

        print()
        # TODO: image
        img_elem = soup.select_one(website['img_selector'])
        if img_elem:
            img_src = img_elem.get("src") or img_elem.get("data-src")
            if img_src and not img_src.startswith("data:"):
                product["image"] = img_src
                print("[DEBUG] Image:", img_src)

            else:
                product["image"] = "Image not available"
                print("[DEBUG] No image found.")
        else:
            product["image"] = "Image not available"
            print("[DEBUG] No image element found.")

        print()
        # TODO: url
        # url_elem = soup.select_one(website['url_selector'])
        url_elem = soup.select_one(website['url_selector'])
        if url_elem and url_elem.get("href"):
            href = url_elem["href"]
            if href.startswith("http"):
                product["url"] = href
                print("[DEBUG] URL:", href)
            # for relative URLs, prepend the base URL
            elif href.startswith("/"):
                url = f"https://www.{website_name.lower()}.com" + href
                product["url"] = url
                print("[DEBUG] URL:", url)
            else:
                product["url"] = None
                print("[DEBUG] URL is not valid.")
        else:
            product["url"] = None
            print("[DEBUG] No URL found.")

        print()
        # TODO: rating
        if website_name == "Walmart":
            for span in soup.select(website['rating_selector']):
                if span and span.text:
                    if "out of 5 Stars" in span.text:
                        match = re.search(r"(\d+(?:\.\d+)?)\s+out of 5", span.text)
                        if match:
                            rating = match.group(1)
                            product['rating'] = rating
                            print("[DEBUG] Rating:", rating)
                        else:
                            product['rating'] = "No rating available"
                            print("[DEBUG] No rating found in block.")
                        break
                        
        else:
            rating_elem = soup.select_one(website['rating_selector'])
            if rating_elem:
                rating_match = re.search(r"([\d\.]+)", rating_elem.text.strip())
                if rating_match:
                    rating = rating_match.group(1)
                    product['rating'] = rating
                    print("[DEBUG] Rating:", rating)
                else:
                    product['rating'] = "No rating available"
                    print("[DEBUG] No rating found in block.")
            else:
                product['rating'] = "No rating available"
                print("[DEBUG] Rating block not found.")

        print()
        # TODO: reviews
        # reviews_elem = soup.select_one(website['reviews_selector'])
        reviews_elem = soup.select_one(website['reviews_selector'])
        if reviews_elem:
            part = ''.join(list(reviews_elem.stripped_strings)).replace(',', '')
            reviews_match = re.search(r"\((\d+)\)|^(\d+)$", part)
            if reviews_match:
                reviews = reviews_match.group(1) or reviews_match.group(2) 
                product['reviews'] = reviews
                print("[DEBUG] Reviews:", reviews)
            else:
                product['reviews'] = "No reviews Yet"
                print("[DEBUG] No reviews found in block.")
        else:
            product['reviews'] = "No reviews Yet"
            print("[DEBUG] Reviews block not found.")

        print()
        return product
    
    except Exception as e:
        print(f"[ERROR] Failed to extract data: {str(e)}")


from .config import SITES
from .bs_scrape import write_html_with_bs
from fastapi.responses import PlainTextResponse
from .extract_with_llm import use_llm

@app.get("/scrape", response_class=PlainTextResponse)
def scrape(query: str = Query(..., description="Product name")):
    query = query.strip().replace(' ', '+')
    products = []

    # Create a directory to store scraped HTML files
    backend_dir = os.path.dirname(__file__) # Get the directory where the current script (main.py) lives
    files_dir = os.path.join(backend_dir, "scraped_html_files")
    os.makedirs(files_dir, exist_ok=True)  # Create the directory if it doesn't exist

    for website in SITES:
        product = {"name": website['site_name']}
        url = website['url_template'].format(query=query)
        print("[DEBUG] Website config:", website)

        website_name = website['site_name'].split('.')[0]
        filepath = os.path.join(files_dir, f"{website_name}.html")

        if website_name in {"Amazon", "Walmart"}:
            write_html_with_bs(website_name, files_dir, url, website['html_selector'])
        else:
            html = fetch_html_with_scroll(website, url)
            write_html_to_file(website, files_dir, html, website_name)

        # extract_data_from_html(website, filepath, product, website_name)
        use_llm(product, website_name)
        products.append(product)

    output_lines = []
    for p in products:
        output_lines.append(f"name: {p.get('name', '')}")
        output_lines.append(f"title: {p.get('title', '')}")
        output_lines.append(f"image: {p.get('image', '')}")
        output_lines.append(f"price: {p.get('price', '')}")
        output_lines.append(f"rating: {p.get('rating', '')}")
        output_lines.append(f"reviews: {p.get('reviews', '')}")
        output_lines.append(f"url: {p.get('url', '')}")
        output_lines.append("\n##### NEXT website #####\n")  # Blank line between products

    return "\n".join(output_lines)