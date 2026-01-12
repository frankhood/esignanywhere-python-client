import datetime
import os
import unittest

from esignanywhere_python_client.esign_client import ESignAnyWhereClient
from esignanywhere_python_client.exceptions import ESawErrorResponse
from esignanywhere_python_client.models.models_v6 import (
    EnvelopeRestartExpiredRequest,
    EnvelopeSendRequest,
)


class TestRestartEnvelopeExpirationDays(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.client = ESignAnyWhereClient(
            api_token=os.environ.get("ESIGNANYWHERE_API_TOKEN"),
            is_test_env=True,
        )
        self.email = os.environ.get("ESIGNANYWHERE_EMAIL", "mail@example.com")

        r = self.client.upload_file("./tests/assets/example.pdf")
        self.file_id = r.FileId

        envelope_data = EnvelopeSendRequest(
            Documents=[
                {
                    "FileId": self.file_id,
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
        self.envelope_id = r.EnvelopeId

    def test_expiration_in_past(self):
        new_expiration_date = datetime.datetime.now(datetime.UTC).replace(
            microsecond=0
        ) - datetime.timedelta(days=1)

        with self.assertRaises(ESawErrorResponse) as cm:
            self.client.restart_envelope_expiration_days(
                EnvelopeRestartExpiredRequest(
                    EnvelopeId=self.envelope_id,
                    ExpirationDate=new_expiration_date,
                )
            )

        self.assertEqual(cm.exception.status_code, 400)
        self.assertEqual(cm.exception.response_data["ErrorId"], "ERR0163")

    def test_invalid_status(self):
        new_expiration_date = datetime.datetime.now(datetime.UTC).replace(
            microsecond=0
        ) + datetime.timedelta(days=1)

        with self.assertRaises(ESawErrorResponse) as cm:
            self.client.restart_envelope_expiration_days(
                EnvelopeRestartExpiredRequest(
                    EnvelopeId=self.envelope_id,
                    ExpirationDate=new_expiration_date,
                )
            )

        self.assertEqual(cm.exception.status_code, 400)
        self.assertEqual(cm.exception.response_data["ErrorId"], "ERR0013")


if __name__ == "__main__":
    unittest.main()
