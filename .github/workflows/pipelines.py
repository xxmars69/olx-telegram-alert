import os, json, requests
from pathlib import Path

class TelegramPipeline:
    def open_spider(self, spider):
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.token   = os.getenv("TELEGRAM_BOT_TOKEN")
        state        = Path("state.json")
        self.seen    = set(json.loads(state.read_text())) if state.exists() else set()

    def process_item(self, item, spider):
        if item["id"] not in self.seen:
            text = f"🆕 {item['title']} – {item['price'] or 'fără preț'}\n{item['link']}"
            requests.get(
                f"https://api.telegram.org/bot{self.token}/sendMessage",
                params={"chat_id": self.chat_id, "text": text},
                timeout=10,
            )
            self.seen.add(item["id"])
        return item

    def close_spider(self, spider):
        Path("state.json").write_text(json.dumps(list(self.seen)[-500:]))
