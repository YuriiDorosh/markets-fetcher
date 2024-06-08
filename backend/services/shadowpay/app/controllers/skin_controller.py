from flask import Blueprint, jsonify, request
from app.services.skin_service import SkinService
from app.infrastructure.shadowpay_scraper import ShadowPaySkinScraper

skin_controller = Blueprint('skin_controller', __name__)

@skin_controller.route('/skins', methods=['GET'])
def get_skins():
    search_term = request.args.get('search_term', 'Butterfly Knife')
    exterior = request.args.get('exterior')
    price_from = request.args.get('price_from')
    price_to = request.args.get('price_to')
    
    url = "https://shadowpay.com/csgo-items"
    
    if exterior == "factory":
        url += "?exteriors=Factory New"
    elif exterior == "minimal":
        url += "?exteriors=Minimal Wear"
    elif exterior == "field-tested":
        url += "?exteriors=Field-Tested"
    elif exterior == "well-worn":
        url += "?exteriors=Well-Worn"
    elif exterior == "battle-scarred":
        url += "?exteriors=Battle-Scarred"
    
    scraper = ShadowPaySkinScraper(url)
    service = SkinService(scraper)
    skins = service.get_skins(search_term, price_from, price_to)
    scraper.close()
    return jsonify([skin.to_dict() for skin in skins])
