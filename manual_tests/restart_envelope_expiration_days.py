import os
import time

import tqdm

from esignanywhere_python_client.esign_client import ESignAnyWhereClient
from esignanywhere_python_client.models.models_v6 import (
    EnvelopeRestartExpiredRequest,
    EnvelopeSendRequest,
)

client = ESignAnyWhereClient(
    api_token=os.environ.get("ESIGNANYWHERE_API_TOKEN"),
    is_test_env=True,
)

email = os.environ.get("ESIGNANYWHERE_EMAIL", "mail@example.com")


def create_envelope():
    r = client.upload_file("./tests/assets/example.pdf")
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
                                "Email": email,
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
                                "Email": email,
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
        ExpirationConfiguration={
            "ExpirationInSecondsAfterSending": 600,
        },
        ReminderConfiguration={
            "Enabled": False,
        },
    )

    r = client.create_and_send_envelope(envelope_data)
    envelope_id = r.EnvelopeId

    return envelope_id


def restart_envelope(envelope_id):
    client.restart_envelope_expiration_days(
        EnvelopeRestartExpiredRequest(
            EnvelopeId=envelope_id,
            ExpirationInSecondsAfterSending=600,
        )
    )


if __name__ == "__main__":
    envelope_id = create_envelope()

    with tqdm.tqdm(total=600) as p_bar:
        for _ in range(600):
            p_bar.update(1)
            p_bar.set_description("Waiting for envelope to expire")
            p_bar.refresh()
            time.sleep(1)

    try:
        restart_envelope(envelope_id)
        print("Envelope restarted successfully!")
    except Exception as e:
        print(f"Failed to restart envelope: {e}")
