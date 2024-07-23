import os
import unittest

import requests

from esignanywhere_python_client.esign_client import ESignAnyWhereClient
from esignanywhere_python_client.exceptions import ESawErrorResponse
from esignanywhere_python_client.models.models_v6 import EnvelopeSendRequest


class TestGetEnvelope(unittest.TestCase):
    def setUp(self):
        self.client = ESignAnyWhereClient(
            api_token=os.environ.get("ESIGNANYWHERE_API_TOKEN"),
            is_test_env=True,
        )
        self.email = os.environ.get("ESIGNANYWHERE_EMAIL", "mail@example.com")

    def test_get_envelope(self):
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

        r = self.client.get_envelope(envelope_id)
        self.assertEqual(r.Id, envelope_id)

        r = self.client.get_envelope_configuration(envelope_id)
        self.assertIsNotNone(r.Activities)

        r = self.client.get_envelope_files(envelope_id)
        self.assertIsNotNone(r.Documents[0].FileId)

        r = self.client.get_envelope_viewer_links(envelope_id)
        self.assertEqual(len(r.ViewerLinks), 1)

        r = self.client.get_envelope_history(envelope_id)
        self.assertIsNotNone(r.Events)

        r = self.client.get_envelope_elements(envelope_id)
        self.assertIsNotNone(r.Activities)

    def test_get_envelope_v5(self):
        r = self.client.upload_file("./tests/assets/example.pdf")
        file_id = r.FileId

        # NOTE: the creation in v5 is performed using requests since the client does not support it anymore
        service_url = self.client.api_uri + "v5/envelope/send"

        request_data = {
            "SspFileIds": [file_id],
            "SendEnvelopeDescription": {
                "Name": "test",
                "EmailSubject": "Please sign the enclosed envelope",
                "EmailBody": "Dear #RecipientFirstName# #RecipientLastName#\n\n#PersonalMessage#\n\nPlease sign the envelope #EnvelopeName#\n\nEnvelope will expire at #ExpirationDate#",
                "DisplayedEmailSender": "",
                "EnableReminders": True,
                "FirstReminderDayAmount": 5,
                "RecurrentReminderDayAmount": 3,
                "BeforeExpirationDayAmount": 3,
                "DaysUntilExpire": 28,
                "CallbackUrl": "",
                "StatusUpdateCallbackUrl": "",
                "Steps": [
                    {
                        "OrderIndex": 1,
                        "Recipients": [
                            {
                                "Email": self.email,
                                "FirstName": "Mario",
                                "LastName": "Rossi",
                                "LanguageCode": "IT",
                                "EmailBodyExtra": "",
                                "DisableEmail": False,
                                "AddAndroidAppLink": False,
                                "AddIosAppLink": False,
                                "AddWindowsAppLink": False,
                                "AllowDelegation": False,
                                "AllowAccessFinishedWorkstep": False,
                                "SkipExternalDataValidation": False,
                                "AuthenticationMethods": [
                                    {"Method": "Pin", "Parameter": "1234"}
                                ],
                            }
                        ],
                        "EmailBodyExtra": "",
                        "RecipientType": "Signer",
                        "WorkstepConfiguration": {
                            "WorkstepLabel": "test",
                            "SmallTextZoomFactorPercent": 100,
                            "FinishAction": {"ServerActions": [], "ClientActions": []},
                            "ReceiverInformation": {
                                "UserInformation": {
                                    "FirstName": "Mario",
                                    "LastName": "Rossi",
                                    "EMail": self.email,
                                },
                                "TransactionCodePushPluginData": [],
                            },
                            "SenderInformation": {
                                "UserInformation": {
                                    "FirstName": "Mario",
                                    "LastName": "Rossi",
                                    "EMail": self.email,
                                }
                            },
                            "TransactionCodeConfigurations": [
                                {
                                    "Id": "smsAuthTransactionCodeId",
                                    "HashAlgorithmIdentifier": "Sha256",
                                    "Texts": [],
                                }
                            ],
                            "SignatureConfigurations": [],
                            "ViewerPreferences": {
                                "FinishWorkstepOnOpen": False,
                                "VisibleAreaOptions": {
                                    "AllowedDomain": "*",
                                    "Enabled": False,
                                },
                            },
                            "ResourceUris": {
                                "SignatureImagesUri": "http://beta4.testlab.xyzmo.com//Resource/SignatureImages/?link=1agjn5MvqNpSt2jFiZQySxLEiAO~ecLOxKqy3soEHk2F4Dz1MPSYLxRkpA21XMkYY"
                            },
                            "AuditingToolsConfiguration": {
                                "WriteAuditTrail": False,
                                "NotificationConfiguration": {},
                            },
                            "Policy": {
                                "GeneralPolicies": {
                                    "AllowSaveDocument": True,
                                    "AllowSaveAuditTrail": True,
                                    "AllowRotatingPages": False,
                                    "AllowEmailDocument": True,
                                    "AllowPrintDocument": True,
                                    "AllowFinishWorkstep": True,
                                    "AllowRejectWorkstep": True,
                                    "AllowRejectWorkstepDelegation": False,
                                    "AllowUndoLastAction": False,
                                    "AllowAdhocPdfAttachments": False,
                                    "AllowAdhocSignatures": False,
                                    "AllowAdhocStampings": False,
                                    "AllowAdhocFreeHandAnnotations": False,
                                    "AllowAdhocTypewriterAnnotations": False,
                                    "AllowAdhocPictureAnnotations": False,
                                    "AllowAdhocPdfPageAppending": False,
                                },
                                "WorkstepTasks": {
                                    "PictureAnnotationMinResolution": 0,
                                    "PictureAnnotationMaxResolution": 0,
                                    "PictureAnnotationColorDepth": "Color16M",
                                    "SequenceMode": "NoSequenceEnforced",
                                    "PositionUnits": "PdfUnits",
                                    "ReferenceCorner": "Lower_Left",
                                    "Tasks": [
                                        {
                                            "Texts": [
                                                {
                                                    "Language": "*",
                                                    "Value": "Signature Disclosure Text",
                                                },
                                                {
                                                    "Language": "IT",
                                                    "Value": "Signature Disclosure Text",
                                                },
                                            ],
                                            "Headings": [
                                                {
                                                    "Language": "*",
                                                    "Value": "Signature Disclosure Subject",
                                                },
                                                {
                                                    "Language": "IT",
                                                    "Value": "Signature Disclosure Subject",
                                                },
                                            ],
                                            "IsRequired": False,
                                            "Id": "ra",
                                            "DisplayName": "ra",
                                            "DocRefNumber": 1,
                                            "DiscriminatorType": "Agreements",
                                        },
                                        {
                                            "PositionPage": 1,
                                            "Position": {
                                                "PositionX": 63.0,
                                                "PositionY": 603.0,
                                            },
                                            "Size": {"Height": 80.0, "Width": 190.0},
                                            "AdditionalParameters": [
                                                {"Key": "enabled", "Value": "1"},
                                                {
                                                    "Key": "positioning",
                                                    "Value": "onPage",
                                                },
                                                {"Key": "req", "Value": "1"},
                                                {"Key": "fd", "Value": ""},
                                                {
                                                    "Key": "fd_dateformat",
                                                    "Value": "dd-MM-yyyy HH:mm:ss",
                                                },
                                                {
                                                    "Key": "fd_timezone",
                                                    "Value": "datetimeutc",
                                                },
                                                {"Key": "spcId", "Value": "tLevelId"},
                                            ],
                                            "AllowedSignatureTypes": [
                                                {
                                                    "AllowedCapturingMethod": "Click2Sign",
                                                    "Id": "679dd763-6e25-4a68-929d-cb1ce13dac7e",
                                                    "DiscriminatorType": "SigTypeClick2Sign",
                                                    "Preferred": False,
                                                    "StampImprintConfiguration": {
                                                        "DisplayExtraInformation": True,
                                                        "DisplayEmail": True,
                                                        "DisplayIp": True,
                                                        "DisplayName": True,
                                                        "DisplaySignatureDate": True,
                                                        "FontFamily": "Times New Roman",
                                                        "FontSize": 11.0,
                                                    },
                                                }
                                            ],
                                            "UseTimestamp": False,
                                            "IsRequired": True,
                                            "Id": "1#XyzmoDuplicateIdSeperator#Signature_a1e940eb-bcd5-2222-9777-f3570faedf3f",
                                            "DisplayName": "",
                                            "DocRefNumber": 1,
                                            "DiscriminatorType": "Signature",
                                        },
                                    ],
                                },
                            },
                            "Navigation": {
                                "HyperLinks": [],
                                "Links": [],
                                "LinkTargets": [],
                            },
                        },
                        "DocumentOptions": [
                            {"DocumentReference": "1", "IsHidden": False}
                        ],
                        "UseDefaultAgreements": True,
                    },
                    {
                        "OrderIndex": 2,
                        "Recipients": [
                            {
                                "Email": self.email,
                                "FirstName": "Mario",
                                "LastName": "Rossi",
                                "LanguageCode": "IT",
                                "EmailBodyExtra": "",
                                "DisableEmail": False,
                                "AddAndroidAppLink": False,
                                "AddIosAppLink": False,
                                "AddWindowsAppLink": False,
                                "AllowDelegation": False,
                                "SkipExternalDataValidation": False,
                                "AuthenticationMethods": [],
                            }
                        ],
                        "EmailBodyExtra": "",
                        "RecipientType": "Cc",
                        "DocumentOptions": [],
                        "UseDefaultAgreements": False,
                    },
                ],
                "AddFormFields": {"Forms": {}},
                "OverrideFormFieldValues": {"Forms": {}},
                "AttachSignedDocumentsToEnvelopeLog": False,
            },
        }

        response = requests.post(
            url=service_url,
            json=request_data,
            headers=self.client._get_request_headers(),
        )
        if response.status_code != 200:
            self.client._handle_response_errors(
                service_url, response=response, request_data=request_data
            )

        envelope_id = response.json()["EnvelopeId"]

        r = self.client.get_envelope(envelope_id, version="v5")
        self.assertEqual(r.Id, envelope_id)

    def test_wrong_envelope_id(self):
        for method in [
            self.client.get_envelope_configuration,
            self.client.get_envelope_files,
            self.client.get_envelope_viewer_links,
            self.client.get_envelope_history,
            self.client.get_envelope_elements,
        ]:
            with self.assertRaises(ESawErrorResponse) as cm:
                method("00000000-0000-0000-0000-000000000000")

            self.assertEqual(cm.exception.status_code, 404)
            self.assertEqual(cm.exception.response_data["ErrorId"], "ERR0007")


if __name__ == "__main__":
    unittest.main()
