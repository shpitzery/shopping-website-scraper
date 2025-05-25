import requests
import json
import os
from dotenv import load_dotenv
import re


PROMPT = """
You are a helpful assistant that extracts product information from this raw HTML.

From the HTML file in the bottom of the page, extract:
- title (full title)
- price (incuding currency symbol)
- image URL 
- rating (only a number, if available)
- number of reviews (if available)
- product URL

Your response must be valid JSON and **nothing else**.
Ignore secondary prices.

Example:

Input HTML:
<html><div class="product"><h1>Example Phone</h1><span class="price">$199.99</span></div></html>

Output:
{{
  "title": "Example Phone",
  "price": "$199.99",
  "image": null,
  "rating": null,
  "reviews": null,
  "url": null
}}

Now extract the fields from this HTML:
{html}
"""

SECONDARY_PROMPT = """
You are a helpful assistant that extracts the product's {attr} from this raw HTML.

From the HTML file in the bottom of the page, extract the {attr}.

Your response must be valid JSON and **nothing else**, like this:
```json
{{
  "<attribute>": "<value>"
}}
```

Now extract the {attr} from this HTML:
{html}
"""

load_dotenv()
api_key = os.getenv("API_KEY")

def extract_product_info(html_text, attr=None):
    if not attr:
      prompt = PROMPT.format(html=html_text)
    else:
      prompt = SECONDARY_PROMPT.format(attr=attr, html=html_text)

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": "deepseek/deepseek-chat-v3-0324:free",
            "messages": [{"role": "user", "content": prompt}],
        })
      )

    data = response.json()
    return data['choices'][0]['message']['content']


def clean(content):
  # Strip markdown block: ```json ... ```
  match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
  if match:
      return match.group(1)
  else:
      # fallback if no ``` block: remove `>`s like before
      return re.sub(r"^> ?", "", content, flags=re.MULTILINE)


def read_html_file(website_name):
    html_file_path = os.path.join(os.path.dirname(__file__), "scraped_html_files", f"{website_name}.html")

    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    return html_content

def parse_as_json(cleaned):
    try:
        print(cleaned,'\n')
        return json.loads(cleaned)
    except json.JSONDecodeError:
        print("⚠️ Could not parse JSON")
        print(cleaned)
        return {}

# if __name__ == "__main__": completion
def use_llm(product, website_name):
    MAX_RETRIES = 3
    sec_prompt_attr = {
        "title": "title (full title)",
        "price": "price (including currency symbol)",
        "image": "image URL",
        "rating": "rating (only a number, if available)",
        "reviews": "number of reviews (if available)",
        "url": "product URL"
    }
    html_content = read_html_file(website_name)
    for _ in range(MAX_RETRIES):
      content = extract_product_info(html_content)
      if content:
        break

    cleaned = clean(content)
    content = parse_as_json(cleaned)
    product.update(content)

    # attributes = ["title", "price", "image", "rating", "reviews", "url"]
    # tries = 0
    # while attributes:
    #     if ((attributes[-1] not in content) or (not content[attributes[-1]]) and tries < MAX_RETRIES):
    #         attr = sec_prompt_attr[attributes[-1]]
    #         res = extract_product_info(html_content, attr)
    #         cleaned = clean(res)
    #         content[attributes[-1]] = res[attributes[-1]]


    #     else:
    #         attributes.pop()
    #         tries = 0
    #         continue
    
    