import json
from flask import Flask, request, jsonify
from securities.bond import Bond

app = Flask(__name__)


@app.route('/bond/price', methods=['POST'])
def calculate_bond():
    # return bond with price
    try:
        bond_dict = request.get_json()
        bond = Bond.from_dict(bond_dict)
        return json.dumps(bond.to_json())
    except KeyError as e:
        return json.dumps({"error": "KeyError", "text": str(e)})
    except TypeError as e:
        return json.dumps({"error": "TypeError", "text": str(e)})


@app.errorhandler(500)
def internal_server_error(e):
    return jsonify(error=500, text=str(e)), 500


@app.errorhandler(400)
def bad_request(e):
    return jsonify(error=400, text=str(e)), 400


@app.errorhandler(404)
def bad_request(e):
    return jsonify(error=404, text=str(e)), 404
