import time
import yaml
import random
import sentry_sdk
from urllib.parse import urlencode
from collections import OrderedDict
from datetime import datetime


# This test is for the homepage '/' transaction
def test_homepage(desktop_web_driver):
    sentry_sdk.set_tag("pytestName", "test_homepage")

    with open('endpoints.yaml', 'r') as stream:
        data_loaded = yaml.safe_load(stream)
        endpoints = data_loaded['react_endpoints']

    # Find what week it is, as this is used as the patch version in YY.MM.W like 22.6.2
    d=datetime.today()
    week=str((d.day-1)//7+1)
    week=int(week)

    # For setting a different Crash Free Rate each week
    upper_bound = 0

    if week % 2 == 0:
        # even patch version, e.g. 22.6.2
        upper_bound = .2
    else:
        # odd patch version, e.g. 22.6.3
        upper_bound = .4


    for endpoint in endpoints:
        sentry_sdk.set_tag("endpoint", endpoint)

        for i in range(random.randrange(20)):
            # Randomize the Failure Rate between 1% and 20% or 40%, depending what week it is. Returns values like 0.02, 0.14, 0.37
            n = random.uniform(0.01, upper_bound)

            # This query string is parsed by utils/errors.js wherever the 'crasher' function is used
            # and causes the page to periodically crash, for Release Health
            # TODO make a query_string builder function for sharing this across tests
            query_string = {
                'se': 'tda',
                'backend': random.sample(['flask','express','springboot', 'ruby', 'laravel'], 1)[0],
                'crash': "%s" % (n)
            }
            url = endpoint + '?' + urlencode(query_string)

            desktop_web_driver.get(url)
            time.sleep(random.randrange(3) + 3)
