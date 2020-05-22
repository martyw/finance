import unittest
import ast
import json
from api.app_server import app


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
