from scrapyd_api import ScrapydAPI
from app.config.settings import SCRAPYD_URL


client = ScrapydAPI(base_url=SCRAPYD_URL)
