from bs4 import BeautifulSoup
import requests
import functions_framework
import json

def extract_product_info(soup, product: dict, query: str, selectors: dict):
    try:

        # Extract product title
        title = soup.select_one(selectors["title_selector"])
        if title:
            product["title"] = title.text.strip()
        
        # Extract product price
        price_selectors = [
            "span.a-offscreen",
            "span.a-price-whole",
            "#priceblock_ourprice",
            "#priceblock_dealprice",
            ".a-price .a-offscreen",
            "#corePrice_feature_div .a-price .a-offscreen"
        ]
        
        for selector in price_selectors:
            price_element = soup.select_one(selector)
            if price_element and price_element.text.strip():
                product["price"] = price_element.text.strip()
                # check selector for debbugging
                product["price_selector"] = selector
                break
        
        # Extract product image
        images = soup.select(selectors["img_else"][0])
        image = None

        for img in images:
            if img.has_attr("alt") and f"{query}" in img.get("alt", ""):
                image = img
                break

        if image:
            if image.has_attr(selectors["img_attr"]):
                try:
                    dynamic_imgs = json.loads(image[selectors["img_attr"]])
                    if dynamic_imgs and isinstance(dynamic_imgs, dict) and len(dynamic_imgs) > 0:
                        # Sort the image URLs by size to get the highest resolution
                        sorted_urls = sorted(dynamic_imgs.keys(), 
                                            key=lambda x: sum(int(dim) for dim in str(dynamic_imgs[x]).replace('[', '').replace(']', '').split(',')),
                                            reverse=True)
                        
                        product["image"] = sorted_urls[0]
                        # product["image_alt"] = image.get('alt', '')  # Preserve the detailed alt text

                except Exception as e:
                    # Fallback to src if JSON parsing fails
                    product["image"] = image.get('src', '')
                    # product["image_alt"] = image.get('alt', '')
            else:
                # Use src attribute directly if no data-a-dynamic-image
                product["image"] = image.get('src', '')
                # product["image_alt"] = image.get('alt', '')
                      
        else:
            # Fallback to any image if we can't find one with "Lenovo" in alt text
            any_image = soup.select_one(f"{selectors['img_else'][0]}, {selectors['img_else'][1]}, {selectors['img_else'][2]}")
            if any_image:
                product["image"] = any_image.get('src', '')
                # product["image_alt"] = any_image.get('alt', '')
  
        
        # Extract rating and review count
        try:
            import re
            # Method 1: Try the reviewCountTextLinkedHistogram which often contains the rating
            rating_span = soup.select_one(selectors["rating_selector_method_1"])
            if rating_span and "title" in rating_span.attrs:
                rating_text = rating_span["title"]
                rating_match = re.search(selectors["rating_selector_method_1_2_regex"], rating_text)
                if rating_match:
                    product["rating"] = rating_match.group(1)
                    product["rating_text"] = rating_text
            
            # Method 2: Try the a-icon-alt which often contains the rating
            if "rating" not in product:
                icon_alt = soup.select_one("span.a-icon-alt")
                if icon_alt:
                    rating_text = icon_alt.text
                    rating_match = re.search(selectors["rating_selector_method_1_2_regex"], rating_text)
                    if rating_match:
                        product["rating"] = rating_match.group(1)
                        product["rating_text"] = rating_text
            
            # Method 3: Try other common rating elements
            if "rating" not in product:
                rating_elements = soup.select(".a-star-4-5, .a-star-5, .a-star-4")
                for elem in rating_elements:
                    class_str = " ".join(elem.get("class", []))
                    if "a-star" in class_str:
                        rating_match = re.search(selectors["rating_selector_method_3_regex"], class_str)
                        if rating_match:
                            whole = rating_match.group(1)
                            fraction = rating_match.group(2)
                            product["rating"] = f"{whole}.{fraction}"
                            break
                            
            # Extract review count
            reviews = soup.select_one(selectors["reviews_selector"])
            if reviews:
                count_text = reviews.text.strip()
                count_match = re.search(selectors["reviews_regex"], count_text)
                if count_match:
                    product["reviews"] = count_match.group(1)
        except Exception as e:
            product["rating_extraction_error"] = str(e)
 

        # Extract ASIN, whch is a unique identifier for Amazon products - 10 characters long
        # try:
        #     import re
        #     asin_match = re.search(r'/dp/([A-Z0-9]{10})/', product["product_page_url"])
        #     if asin_match:
        #         product["asin"] = asin_match.group(1)

        # except Exception as e:
        #     product["asin_extraction_error"] = str(e)
        
        # # DEBUGGING - save a snippet of the HTML to see structure
        # product["html_sample"] = soup.prettify()[:1000]

        return product
    
    except Exception as e:
        return {"error": str(e), "error_type": type(e).__name__}