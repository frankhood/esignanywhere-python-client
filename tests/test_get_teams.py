import os
import unittest

from esignanywhere_python_client.esign_client import ESignAnyWhereClient
from esignanywhere_python_client.models.models_v6 import (
    TeamReplaceRequest,
    TeamReplaceTeam,
    TeamReplaceTeamMember,
)


class TestGetTeams(unittest.TestCase):
    def setUp(self):
        self.client = ESignAnyWhereClient(
            api_token=os.environ.get("ESIGNANYWHERE_API_TOKEN"),
            is_test_env=True,
        )
        self.email = os.environ.get("ESIGNANYWHERE_EMAIL", "mail@example.com")

    def test_get_teams(self):
        self.client.replace_teams(
            TeamReplaceRequest(
                Teams=[
                    TeamReplaceTeam(
                        Name="Team 1", Head=TeamReplaceTeamMember(Email=self.email)
                    )
                ]
            )
        )

        r = self.client.get_teams()

        self.assertEqual(len(r.Teams), 1)
        self.assertEqual(r.Teams[0].Name, "Team 1")

    def test_get_replaced_teams(self):
        self.client.replace_teams(
            TeamReplaceRequest(
                Teams=[
                    TeamReplaceTeam(
                        Name="Team 1", Head=TeamReplaceTeamMember(Email=self.email)
                    )
                ]
            )
        )

        self.client.replace_teams(
            TeamReplaceRequest(
                Teams=[
                    TeamReplaceTeam(
                        Name="Team 2", Head=TeamReplaceTeamMember(Email=self.email)
                    ),
                    TeamReplaceTeam(
                        Name="Team 3", Head=TeamReplaceTeamMember(Email=self.email)
                    ),
                ]
            )
        )

        r = self.client.get_teams()

        self.assertEqual(len(r.Teams), 2)

        team_names = [team.Name for team in r.Teams]
        self.assertIn("Team 2", team_names)
        self.assertIn("Team 3", team_names)


if __name__ == "__main__":
    unittest.main()
