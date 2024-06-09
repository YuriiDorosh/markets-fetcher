from flask import jsonify, Blueprint


status_controller = Blueprint("status_controller", __name__)


@status_controller.route("/status", methods=["GET"])
def get_status():
    return jsonify({"status": "ok"})
