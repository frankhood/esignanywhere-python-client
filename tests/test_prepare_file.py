import os
import unittest

from esignanywhere_python_client.esign_client import ESignAnyWhereClient
from esignanywhere_python_client.models.models_v6 import FilePrepareRequest


class TestPrepareFile(unittest.TestCase):
    def setUp(self):
        self.client = ESignAnyWhereClient(
            api_token=os.environ.get("ESIGNANYWHERE_API_TOKEN"),
            is_test_env=True,
        )

    def test_prepare_plain_pdf(self):
        r = self.client.upload_file("./tests/assets/example.pdf")
        file_id = r.FileId

        r = self.client.prepare_file(FilePrepareRequest(FileIds=[file_id]))

        self.assertEqual(len(r.Activities), 0)
        self.assertEqual(len(r.UnassignedElements.TextBoxes), 0)
        self.assertEqual(len(r.UnassignedElements.CheckBoxes), 0)
        self.assertEqual(len(r.UnassignedElements.ComboBoxes), 0)
        self.assertEqual(len(r.UnassignedElements.RadioButtons), 0)
        self.assertEqual(len(r.UnassignedElements.ListBoxes), 0)
        self.assertEqual(len(r.UnassignedElements.Signatures), 0)
        self.assertEqual(len(r.UnassignedElements.Attachments), 0)

    def test_prepare_interactive_pdf(self):
        r = self.client.upload_file("./tests/assets/example_interactive.pdf")
        file_id = r.FileId

        r = self.client.prepare_file(FilePrepareRequest(FileIds=[file_id]))

        self.assertEqual(len(r.Activities), 0)
        self.assertEqual(len(r.UnassignedElements.TextBoxes), 1)
        self.assertEqual(r.UnassignedElements.TextBoxes[0].Value, "Write here")
        self.assertEqual(len(r.UnassignedElements.CheckBoxes), 0)
        self.assertEqual(len(r.UnassignedElements.ComboBoxes), 0)
        self.assertEqual(len(r.UnassignedElements.RadioButtons), 0)
        self.assertEqual(len(r.UnassignedElements.ListBoxes), 0)
        self.assertEqual(len(r.UnassignedElements.Signatures), 0)
        self.assertEqual(len(r.UnassignedElements.Attachments), 0)


if __name__ == "__main__":
    unittest.main()
