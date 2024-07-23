import os
import unittest

from esignanywhere_python_client.esign_client import ESignAnyWhereClient
from esignanywhere_python_client.exceptions import ESawErrorResponse
from esignanywhere_python_client.models.models_v6 import (
    DraftCreateRequest,
    DraftSendRequest,
    TemplateCreateDraftRequest,
)


class TestSendDraft(unittest.TestCase):
    def setUp(self):
        self.client = ESignAnyWhereClient(
            api_token=os.environ.get("ESIGNANYWHERE_API_TOKEN"),
            is_test_env=True,
        )
        self.email = os.environ.get("ESIGNANYWHERE_EMAIL", "mail@example.com")
        self.template_id = os.environ.get("ESIGNANYWHERE_TEMPLATE")

    def test_send_draft_from_template(self):
        r = self.client.create_draft_from_template(
            TemplateCreateDraftRequest(TemplateId=self.template_id)
        )
        draft_id = r.DraftId

        r = self.client.send_draft(DraftSendRequest(DraftId=draft_id))
        self.assertIsNotNone(r.Envelope)

    def test_send_manual_draft(self):
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

        r = self.client.send_draft(DraftSendRequest(DraftId=draft_id))
        self.assertIsNotNone(r.Envelope)

    def test_wrong_id(self):
        with self.assertRaises(ESawErrorResponse) as cm:
            self.client.send_draft(
                DraftSendRequest(DraftId="00000000-0000-0000-0000-000000000000")
            )

        self.assertEqual(cm.exception.status_code, 404)
        self.assertEqual(cm.exception.response_data["ErrorId"], "ERR0250")


if __name__ == "__main__":
    unittest.main()
