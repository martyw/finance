"""define an API to call pricers and other routines in this library
"""
import json
from flask import Flask, request, jsonify
from securities.bond import Bond

# pylint: disable = invalid-name
app = Flask(__name__)


@app.route('/bond/price', methods=['POST'])
def calculate_bond():
    """return bond with price"""
    try:
        bond_dict = request.get_json()
        bond = Bond.from_dict(bond_dict)
        return json.dumps(bond.to_json())
    except KeyError as exc:
        return json.dumps({"error": "KeyError", "text": str(exc)})
    except TypeError as exc:
        return json.dumps({"error": "TypeError", "text": str(exc)})


@app.errorhandler(500)
def internal_server_error(e):
    """handle http 500"""
    return jsonify(error=500, text=str(e)), 500


@app.errorhandler(400)
def bad_request(e):
    """handle http 400"""
    return jsonify(error=400, text=str(e)), 400


@app.errorhandler(404)
def not_found(e):
    """handle http 404"""
    return jsonify(error=404, text=str(e)), 404
