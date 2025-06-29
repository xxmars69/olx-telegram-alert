import os, hashlib, json, urllib.parse, scrapy

SEARCH_URL = os.getenv("SEARCH_URL")          # linkul OLX pus ca secret
API_BASE   = "https://www.olx.ro/api/v1/offers/"  # endpoint JSON

def build_api_url(search_url: str, offset=0, limit=40) -> str:
    """
    Convert URL-ul de căutare OLX în apel API.
    Păstrează toți parametrii (q, currency, sort etc.).
    """
    parsed = urllib.parse.urlparse(search_url)
    params = urllib.parse.parse_qs(parsed.query)
    # OLX API foloseşte alţi parametri pentru paginare
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
            # acceptăm răspuns JSON
            "Accept": "application/json",
        },
    }

    def start_requests(self):
        api_url = build_api_url(SEARCH_URL)
        yield scrapy.Request(api_url, callback=self.parse_api)

    def parse_api(self, response):
        data = json.loads(response.text)
        for offer in data.get("data", []):
            uid   = str(offer["id"])
            title = offer["title"]
            price = offer["price"]["value"]["display"]
            link  = offer["url"]
            yield {
                "id": uid,
                "title": title,
                "price": price,
                "link": link,
            }

        # Paginare – dacă API returnează `links.next`
        next_link = data.get("links", {}).get("next")
        if next_link:
            yield scrapy.Request(next_link, callback=self.parse_api)
