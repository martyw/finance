import ast
import json
import unittest

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


class ApiTest(unittest.TestCase):
    def setUp(self) -> None:
        app.testing = True

    def test_bond(self):
        with app.test_client() as client:
            sent = {"par": 100.0,
                    "maturity_term": 2.5,
                    "coupon": 0.5,
                    "ytm": 0.003,
                    "compounding_frequency": 2}
            response = client.post("/bond/price", data=json.dumps(sent), content_type="application/json")
            json_response = json.loads(response.get_data())
            returned = ast.literal_eval(json_response)
            self.assertEqual(returned["par"], sent["par"])
            self.assertEqual(returned["maturity_term"], sent["maturity_term"])
            self.assertEqual(returned["coupon"] * 100.0, sent["coupon"])
            self.assertEqual(returned["ytm"], sent["ytm"])
            self.assertEqual(returned["compounding_frequency"], sent["compounding_frequency"])
            self.assertEqual(round(returned["price"], 12), 100.497757851439)


if __name__ == "__main__":
    unittest.main()
