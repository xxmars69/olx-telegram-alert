import os, hashlib, json, urllib.parse, scrapy

SEARCH_URL = os.getenv("SEARCH_URL")
API_BASE   = "https://www.olx.ro/api/v1/offers/"

def build_api_url(search_url: str, offset=0, limit=40) -> str:
    parsed = urllib.parse.urlparse(search_url)
    params = urllib.parse.parse_qs(parsed.query)
    params["offset"] = [str(offset)]
    params["limit"]  = [str(limit)]
    query = urllib.parse.urlencode({k: v[0] for k, v in params.items()})
    return f"{API_BASE}?{query}"

class WatchJsonSpider(scrapy.Spider):
    name = "watch"
    custom_settings = {
        "ITEM_PIPELINES": {"pipelines.TelegramPipeline": 300},
        "DOWNLOAD_DELAY": 1,
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
            ),
            "Accept": "application/json",
        },
    }

    def start_requests(self):
        yield scrapy.Request(build_api_url(SEARCH_URL), callback=self.parse_api)

    def parse_api(self, response):
        data = json.loads(response.text)

        for offer in data.get("data", []):
            uid   = str(offer.get("id"))
            title = offer.get("title", "").strip()
            link  = offer.get("url")
            # preţul poate lipsi; afişăm None → pipeline pune „fără preț”
            price = (
                offer["price"]["value"]["display"]
                if offer.get("price") and offer["price"].get("value")
                else None
            )

            if uid and title and link:
                yield {"id": uid, "title": title, "price": price, "link": link}

        # pagina următoare
        next_link = data.get("links", {}).get("next")
        if next_link:
            yield scrapy.Request(next_link, callback=self.parse_api)
