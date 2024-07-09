import os
import unittest

from esignanywhere_python_client.esign_client import ESignAnyWhereClient
from esignanywhere_python_client.models.models_v6 import DraftCreateRequest


class TestCreateDraft(unittest.TestCase):
    def setUp(self):
        self.client = ESignAnyWhereClient(
            api_token=os.environ.get("ESIGNANYWHERE_API_TOKEN"),
            is_test_env=True,
        )
        self.email = os.environ.get("ESIGNANYWHERE_EMAIL", "mail@example.com")

    def test_draft_creation(self):
        r = self.client.upload_file("./tests/assets/example.pdf")
        file_id = r.FileId

        envelope_data = DraftCreateRequest(
            Documents=[
                {
                    "FileId": file_id,
                    "DocumentNumber": 0,
                }
            ],
            Name="Test envelope",
            Activities=[
                {
                    "Action": {
                        "Sign": {
                            "RecipientConfiguration": {
                                "ContactInformation": {
                                    "Email": self.email,
                                    "GivenName": "Mario",
                                    "Surname": "Rossi",
                                    "PhoneNumber": "00000000000000000000000000",
                                    "LanguageCode": "IT",
                                },
                                "SendEmails": False,
                            },
                        },
                    }
                },
                {
                    "Action": {
                        "SendCopy": {
                            "RecipientConfiguration": {
                                "ContactInformation": {
                                    "Email": self.email,
                                    "GivenName": "Mario",
                                    "Surname": "Rossi",
                                    "PhoneNumber": "00000000000000000000000000",
                                    "LanguageCode": "IT",
                                },
                            },
                        },
                    }
                },
            ],
        )

        r = self.client.create_draft(envelope_data)
        draft_id = r.DraftId

        self.assertIsNotNone(draft_id)
        self.assertIsInstance(draft_id, str)


if __name__ == "__main__":
    unittest.main()
