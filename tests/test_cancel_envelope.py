import os
import unittest

from esignanywhere_python_client.esign_client import ESignAnyWhereClient
from esignanywhere_python_client.exceptions import ESawErrorResponse
from esignanywhere_python_client.models.models_v6 import (
    EnvelopeCancelRequest,
    EnvelopeSendRequest,
    EnvelopeStatus,
)


class TestCancelEnvelope(unittest.TestCase):
    def setUp(self):
        self.client = ESignAnyWhereClient(
            api_token=os.environ.get("ESIGNANYWHERE_API_TOKEN"),
            is_test_env=True,
        )
        self.email = os.environ.get("ESIGNANYWHERE_EMAIL", "mail@example.com")

    def test_cancel_envelope(self):
        r = self.client.upload_file("./tests/assets/example.pdf")
        file_id = r.FileId

        envelope_data = EnvelopeSendRequest(
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

        r = self.client.create_and_send_envelope(envelope_data)
        envelope_id = r.EnvelopeId

        self.client.cancel_envelope(EnvelopeCancelRequest(EnvelopeId=envelope_id))

        r = self.client.get_envelope(envelope_id)
        self.assertEqual(r.EnvelopeStatus, EnvelopeStatus.Canceled)

    def test_wrong_id(self):
        with self.assertRaises(ESawErrorResponse) as cm:
            self.client.cancel_envelope(
                EnvelopeCancelRequest(EnvelopeId="00000000-0000-0000-0000-000000000000")
            )

        self.assertEqual(cm.exception.status_code, 404)
        self.assertEqual(cm.exception.response_data["ErrorId"], "ERR0007")


if __name__ == "__main__":
    unittest.main()
