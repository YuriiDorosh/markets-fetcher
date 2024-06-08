from flask import Blueprint, jsonify, request
from app.services.skin_service import SkinService
from app.infrastructure.dmarket_scraper import DMartSkinScraper

skin_controller = Blueprint('skin_controller', __name__)

@skin_controller.route('/skins', methods=['GET'])
def get_skins():
    search_term = request.args.get('search_term', 'Butterfly Knife')
    exterior = request.args.get('exterior')
    price_from = request.args.get('price_from')
    price_to = request.args.get('price_to')
    
    url = "https://dmarket.com/ingame-items/item-list/csgo-skins"
    
    if exterior == "factory":
        url += "?exterior=factory"
    elif exterior == "minimal":
        url += "?exterior=minimal"
    elif exterior == "field-tested":
        url += "?exterior=field-tested"
    elif exterior == "well-worn":
        url += "?exterior=well-worn"
    elif exterior == "battle-scarred":
        url += "?exterior=battle-scarred"
    
    scraper = DMartSkinScraper(url)
    service = SkinService(scraper)
    skins = service.get_skins(search_term, price_from, price_to)
    scraper.close()
    return jsonify([skin.to_dict() for skin in skins])
