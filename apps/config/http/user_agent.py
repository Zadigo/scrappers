"""This module regroups all the necessary functionalities
to generate user agent for web requests.

John Pendenque @ pendenquejohn@gmail.com
"""

from collections import namedtuple
from random import choice

AGENTS_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0",
    "Mozilla/5.0 (Android 8.0; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0",
    "Mozilla/5.0 (Android 8.0; Tablet; rv:41.0) Gecko/41.0 Firefox/41.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:10.0) Gecko/20100101 Firefox/59.0",
    "Mozilla/5.0 (iPod touch; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) FxiOS/1.0 Mobile/12F69 Safari/600.1.4",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) FxiOS/1.0 Mobile/12F69 Safari/600.1.4",
    "Mozilla/5.0 (iPad; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) FxiOS/1.0 Mobile/12F69 Safari/600.1.4"
]


def get_user_agent(index=0):
    """Return a specific user agent from `USER_AGENTS`
    """
    return AGENTS_LIST[index]


def get_user_agents():
    """Return all user agents from `USER_AGENTS`
    """
    agents = namedtuple('Agents', ['headers'])
    return agents(AGENTS_LIST)


def get_rand_agent():
    """Return a random user agent from `USER_AGENTS`
    """
    return choice(AGENTS_LIST)


def cached_agents(func):
    """A storage for user agents and that checks that an agent
    has not been used twice.

    Example
    -------
        @cached_agents
        def test():
            return choice(agent)
    
    The `agents_cache` stores the already used agents and returns
    a incoming if it is not present in the cache.
    """
    agents_cache=[]
    def cache():
        agent = func()
        if agent not in agents_cache:
            agents_cache.append(agent)
            return agent
        # TODO: Find solution to generate agents
        print('[AGENT]: Agent already in cache. Using custom values.')
        agents_cache.append('')
        return ''
    return cache()


@cached_agents
def get_rand_unique_agent():
    """Return a random unique user agent from `USER_AGENTS`
    that has not been used. This ensures that you only use
    one unique agent request in a request loop

    Output
    ------
    Returns a user agent as string
    """
    return choice(AGENTS_LIST)
