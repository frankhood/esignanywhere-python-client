import os
import unittest

from esignanywhere_python_client.esign_client import ESignAnyWhereClient


class TestGetLicense(unittest.TestCase):
    def setUp(self):
        self.client = ESignAnyWhereClient(
            api_token=os.environ.get("ESIGNANYWHERE_API_TOKEN"),
            is_test_env=True,
        )
        self.email = os.environ.get("ESIGNANYWHERE_EMAIL", "mail@example.com")

    def test_get_license(self):
        r = self.client.get_license()
        self.assertIsNotNone(r.Type)


if __name__ == "__main__":
    unittest.main()
