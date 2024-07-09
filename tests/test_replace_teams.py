import os
import unittest

from esignanywhere_python_client.esign_client import ESignAnyWhereClient
from esignanywhere_python_client.exceptions import ESawErrorResponse
from esignanywhere_python_client.models.models_v6 import (
    TeamReplaceRequest,
    TeamReplaceTeam,
    TeamReplaceTeamMember,
)


class TestReplaceTeams(unittest.TestCase):
    def setUp(self):
        self.client = ESignAnyWhereClient(
            api_token=os.environ.get("ESIGNANYWHERE_API_TOKEN"),
            is_test_env=True,
        )
        self.email = os.environ.get("ESIGNANYWHERE_EMAIL", "mail@example.com")

    def test_create_team(self):
        self.client.replace_teams(
            TeamReplaceRequest(
                Teams=[
                    TeamReplaceTeam(
                        Name="Team 1", Head=TeamReplaceTeamMember(Email=self.email)
                    )
                ]
            )
        )

    def test_invalid_email(self):
        with self.assertRaises(ESawErrorResponse) as cm:
            self.client.replace_teams(
                TeamReplaceRequest(
                    Teams=[
                        TeamReplaceTeam(
                            Name="Team 1",
                            Head=TeamReplaceTeamMember(
                                Email="invalid@invaliddomain.com"
                            ),
                        )
                    ]
                )
            )

        self.assertEqual(cm.exception.status_code, 400)
        self.assertEqual(cm.exception.response_data["ErrorId"], "ERR0110")


if __name__ == "__main__":
    unittest.main()
