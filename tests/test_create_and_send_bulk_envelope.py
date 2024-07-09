import os
import unittest

from esignanywhere_python_client.esign_client import ESignAnyWhereClient
from esignanywhere_python_client.models.models_v6 import EnvelopeBulkSendRequest


class TestCreateAndSendBulkEnvelope(unittest.TestCase):
    def setUp(self):
        self.client = ESignAnyWhereClient(
            api_token=os.environ.get("ESIGNANYWHERE_API_TOKEN"),
            is_test_env=True,
        )
        self.email = os.environ.get("ESIGNANYWHERE_EMAIL", "mail@example.com")

    def test_envelope_send(self):
        r = self.client.upload_file("./tests/assets/example.pdf")
        file_id = r.FileId

        envelope_data = EnvelopeBulkSendRequest(
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
                        "SignBulk": {
                            "BulkRecipients": [
                                {
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
                                }
                            ],
                            "SequenceMode": "NoSequenceEnforced",
                            "BatchConfiguration": {
                                "Mode": "Basic",
                                "RequireScrollingOverAllSignaturesBeforeSigning": True,
                            },
                            "GeneralPoliciesOverrides": {
                                "AllowSaveDocument": True,
                                "AllowSaveAuditTrail": True,
                                "AllowPrintDocument": True,
                                "AllowAdhocPdfAttachments": True,
                                "AllowRejectWorkstep": True,
                                "AllowUndoLastAction": True,
                            },
                        }
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

        r = self.client.create_and_send_bulk_envelope(envelope_data)
        parent_id = r.EnvelopeBulkParentId

        self.assertIsNotNone(parent_id)
        self.assertIsInstance(parent_id, str)


if __name__ == "__main__":
    unittest.main()
