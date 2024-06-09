from flask import Blueprint, jsonify, request

from app.infrastructure.shadowpay_scraper import ShadowPaySkinScraper
from app.services.skin_service import SkinService

skin_controller = Blueprint("skin_controller", __name__)


@skin_controller.route("/skins", methods=["GET"])
def get_skins():
    search_term = request.args.get("search_term", "Butterfly Knife")
    exterior = request.args.get("exterior")
    price_from = request.args.get("price_from")
    price_to = request.args.get("price_to")

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

    if price_from and exterior:
        url += "&price_from=" + price_from
    elif price_from:
        url += "?price_from=" + price_from

    if price_to and (exterior or price_from):
        url += "&price_to=" + price_to
    elif price_to:
        url += "?price_to=" + price_to

    if search_term and (exterior or price_from or price_to):
        url += "&search=" + search_term
    else:
        url += "?search=" + search_term

    scraper = ShadowPaySkinScraper(url)
    service = SkinService(scraper)
    skins = service.get_skins()
    scraper.close()
    return jsonify([skin.to_dict() for skin in skins])
