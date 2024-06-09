class Skin:
    def __init__(self, name, price, share_link, game_link):
        self.name = name
        self.price = price
        self.share_link = share_link
        self.game_link = game_link

    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "share_link": self.share_link,
            "game_link": self.game_link,
        }
