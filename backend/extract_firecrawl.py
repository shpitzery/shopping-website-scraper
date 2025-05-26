from firecrawl import FirecrawlApp, JsonConfig, AsyncFirecrawlApp
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import json
import os
import asyncio


load_dotenv()
api_key = os.getenv("FIRECRAWL_KEY")
app = FirecrawlApp(api_key=api_key)


class ExtractSchema(BaseModel):
    title: str
    price: float
    url: str
    rating: float = None
    reviews: float = None
    image: str = None

async def extract_with_firecrawl(product, query, url: str, timeout_sec: int = 180):
    app = AsyncFirecrawlApp(api_key=api_key)
    try:
        print(f"🔄 Starting extraction with {timeout_sec}s timeout...")

        response = await asyncio.wait_for(
            app.extract(
                urls=[url],
                prompt=f"Extract the title, price, and URL of the product {query}.",
                schema=ExtractSchema.model_json_schema(),
                agent={"model": "FIRE-1"}
            ),
            timeout=timeout_sec    
        ) 

        if response.success and response.data:
            extracted_data = response.data
            print("✅ Extraction successful!")

            clean_data = {
                "title": extracted_data.get("title"),
                "price": extracted_data.get("price"),
                "url": extracted_data.get("url"),
                "rating": extracted_data.get("rating"),
                "reviews": extracted_data.get("reviews"),
                "image": extracted_data.get("image")
            }
            print("\nClean data:")
            print(json.dumps(clean_data, indent=2))
            product.update(clean_data)

        else:
            print("❌ Extraction failed:", response.error)
            product.update({
                "status": "failed",
                "error": response.error,
                "message": "Firecrawl extraction returned no data"
            })
    except asyncio.TimeoutError:
        print(f"⏰ Extraction timed out after {timeout_sec} seconds.")
        product.update({
            "status": "failed",
            "error": "TimeoutError",
            "message": f"Extraction timed out after {timeout_sec} seconds"
        })
    except Exception as e:
        print(f"💥 Extraction failed: {e}")
        product.update({
            "status": "error",
            "error": type(e).__name__,
            "message": str(e)
        })


def firecrawl_main(product, query, url: str):
    asyncio.run(extract_with_firecrawl(product, query, url))





# if __name__ == "__main__":
#     query = "Lenovo+Tab+P12-2024"
#     urll = f"https://www.walmart.com/search?q={query}&ref=nb_sb_noss"
#     asyncio.run(extract_with_firecrawl(urll))