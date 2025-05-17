from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests, random
from bs4 import BeautifulSoup

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

proxy_pool = [
    "http://45.55.67.34:8080",
    "http://209.97.150.167:8080",
    "http://134.209.29.120:8080",
]

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/58.0.3029.110 Safari/537.3"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

@app.get("/")
def amazon(query: str = Query(...,)):
    url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
    proxy = random.choice(proxy_pool)
    proxies = { "http": proxy, "https": proxy, }

    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=7)
        response.raise_for_status()
    