from scrappers.scrappers.config import utilities
from scrappers.scrappers.config.config import Configuration, configuration
from scrappers.scrappers.config.http import user_agent
from scrappers.scrappers.config.http.aws import (
    QueryManager, TransferManager, create_object_url, image_size_creator,
    unique_path_creator)
from scrappers.scrappers.config.http.engine import Requestor
from scrappers.scrappers.config.http.user_agent import (AGENTS_LIST,
                                                        get_rand_agent,
                                                        get_rand_unique_agent,
                                                        get_user_agent,
                                                        get_user_agents)
from scrappers.scrappers.tennis.matchstats.parser import MatchStats
from scrappers.scrappers.tennis.wta.models import (Player, Tournament,
                                                   TournamentMatch)
from scrappers.scrappers.tennis.wta.parser import ParsePage
from scrappers.scrappers.volleyball.volleyball import ParticipatingTeamsPage, IndivualTeamPage
