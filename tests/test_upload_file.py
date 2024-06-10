import io
import os
import unittest
import uuid

from esignanywhere_python_client.esign_client import ESignAnyWhereClient
from esignanywhere_python_client.exceptions import ESawErrorResponse


class TestUploadFile(unittest.TestCase):
    def setUp(self):
        self.client = ESignAnyWhereClient(
            api_token=os.environ.get("ESIGNANYWHERE_API_TOKEN"),
            is_test_env=True,
        )

    def test_pdf_upload_by_path(self):
        r = self.client.upload_file("./tests/assets/example.pdf")

        file_id = r.FileId

        self.assertIsNotNone(file_id)
        self.assertIsInstance(file_id, str)
        u = uuid.UUID(file_id)
        self.assertEqual(str(u), file_id)

    def test_txt_upload_by_path(self):
        r = self.client.upload_file("./tests/assets/example.txt")

        file_id = r.FileId

        self.assertIsNotNone(file_id)
        self.assertIsInstance(file_id, str)
        u = uuid.UUID(file_id)
        self.assertEqual(str(u), file_id)

    def test_pdf_upload_by_file(self):
        f = open("./tests/assets/example.pdf", "rb")
        r = self.client.upload_file(f)
        f.close()

        file_id = r.FileId

        self.assertIsNotNone(file_id)
        self.assertIsInstance(file_id, str)
        u = uuid.UUID(file_id)
        self.assertEqual(str(u), file_id)

    def test_upload_invalid_path(self):
        with self.assertRaises(FileNotFoundError):
            self.client.upload_file("invalid_file_path")

    def test_upload_empty_file(self):
        f = io.BufferedReader(io.BytesIO())

        with self.assertRaises(ESawErrorResponse) as cm:
            self.client.upload_file(f)

        self.assertEqual(cm.exception.status_code, 400)
        self.assertEqual(cm.exception.response_data["ErrorId"], "ERR0097")


if __name__ == "__main__":
    unittest.main()
