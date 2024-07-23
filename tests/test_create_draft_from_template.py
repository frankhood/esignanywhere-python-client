import os
import unittest

from esignanywhere_python_client.esign_client import ESignAnyWhereClient
from esignanywhere_python_client.exceptions import ESawErrorResponse
from esignanywhere_python_client.models.models_v6 import TemplateCreateDraftRequest


class TestCreateDraftFromTemplate(unittest.TestCase):
    def setUp(self):
        self.client = ESignAnyWhereClient(
            api_token=os.environ.get("ESIGNANYWHERE_API_TOKEN"),
            is_test_env=True,
        )
        self.email = os.environ.get("ESIGNANYWHERE_EMAIL", "mail@example.com")
        self.template_id = os.environ.get("ESIGNANYWHERE_TEMPLATE")

    def test_create_draft_from_template(self):
        r = self.client.create_draft_from_template(
            TemplateCreateDraftRequest(TemplateId=self.template_id)
        )
        self.assertIsNotNone(r)
        self.assertIsNotNone(r.DraftId)

    def test_wrong_id(self):
        with self.assertRaises(ESawErrorResponse) as cm:
            self.client.create_draft_from_template(
                TemplateCreateDraftRequest(
                    TemplateId="00000000-0000-0000-0000-000000000000"
                )
            )

        self.assertEqual(cm.exception.status_code, 404)
        self.assertEqual(cm.exception.response_data["ErrorId"], "ERR0260")


if __name__ == "__main__":
    unittest.main()
