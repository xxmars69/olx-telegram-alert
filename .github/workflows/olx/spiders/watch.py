import os, hashlib, scrapy

SEARCH_URL = os.getenv("SEARCH_URL")   # linkul OLX setat în Secrets

class WatchSpider(scrapy.Spider):
    name = "watch"
    allowed_domains = ["olx.ro"]
    start_urls = [SEARCH_URL]

    custom_settings = {
        "ITEM_PIPELINES": {"pipelines.TelegramPipeline": 300},
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
            )
        },
        "DOWNLOAD_DELAY": 1,
    }

    def parse(self, response):
        # cardurile de anunțuri OLX (HTML iunie 2025)
        for ad in response.css('div[data-testid="l-card"]'):
            link  = ad.css("a::attr(href)").get()
            title = ad.css("h6::text, h5::text").get()
            price = ad.css('p[data-testid="ad-price"]::text').get()
            if link and title:
                uid = hashlib.sha1(link.encode()).hexdigest()
                yield {
                    "id": uid,
                    "title": title.strip(),
                    "price": price,
                    "link": link,
                }

        # pagina următoare
        next_page = response.css('a[aria-label="Următorul"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
