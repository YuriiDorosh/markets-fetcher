from app.infrastructure.shadowpay_scraper import ShadowPaySkinScraper


class SkinService:
    def __init__(self, scraper: ShadowPaySkinScraper):
        self.scraper = scraper

    def get_skins(self):
        return self.scraper.get_skins()
