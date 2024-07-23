import os
import unittest

from esignanywhere_python_client.esign_client import ESignAnyWhereClient
from esignanywhere_python_client.models.models_v6 import FileDeleteRequest


class TestDisposeUploadedFile(unittest.TestCase):
    def setUp(self):
        self.client = ESignAnyWhereClient(
            api_token=os.environ.get("ESIGNANYWHERE_API_TOKEN"),
            is_test_env=True,
        )
        self.email = os.environ.get("ESIGNANYWHERE_EMAIL", "mail@example.com")

    def test_dispose_file(self):
        r = self.client.upload_file("./tests/assets/example.pdf")
        file_id = r.FileId

        self.client.dispose_uploaded_file(FileDeleteRequest(FileId=file_id))


if __name__ == "__main__":
    unittest.main()
