from app.infrastructure.dmarket_scraper import DMartSkinScraper

class SkinService:
    def __init__(self, scraper: DMartSkinScraper):
        self.scraper = scraper

    def get_skins(self, search_term, price_from=None, price_to=None):
        return self.scraper.get_skins(search_term, price_from, price_to)
