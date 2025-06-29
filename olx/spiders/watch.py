import os, hashlib, scrapy

SEARCH_URL = os.getenv("SEARCH_URL")      # URL-ul OLX primit prin secret

class WatchSpider(scrapy.Spider):
    name = "watch"
    allowed_domains = ["olx.ro"]
    start_urls = [SEARCH_URL]

    custom_settings = {
        # pipeline-ul care trimite pe Telegram
        "ITEM_PIPELINES": {"pipelines.TelegramPipeline": 300},

        # Antete implicite
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0 Safari/537.36"
            ),
            # Acceptăm cookies ⇒ pagina vine fără overlay
            "Cookie": "cookiePolicy=1",
        },

        # mic delay să nu bombardăm site-ul
        "DOWNLOAD_DELAY": 1,
    }

    def parse(self, response):
        # carduri OLX: două variante de atribute
        for ad in response.css(
            'div[data-testid="listing-ad"], div[data-cy="l-card"]'
        ):
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

        # pagina următoare (săgeata „Următorul”)
        next_page = response.css('a[aria-label="Următorul"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
