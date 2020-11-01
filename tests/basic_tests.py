"""
This code will get the content of some variables in gitlab and put it into
the docker container to provide more compatibility when doing local testing
PROJECT_ID is the identificator of the project of Google Cloud Platform
TMP_ROUTE is the name of the temporary service created to perform some tests
CI is the origin branch in Gitlab
"""

import os

# Getting information from host to docker
PROJECT_ID = os.environ.get("PROJECT_ID")
TMP_ROUTE = os.environ.get("TMP_ROUTE")
CI = os.environ.get("CI_COMMIT_REF_NAME")

# Preproduction information
URL = ''.join(["https://", TMP_ROUTE, "-dot-", PROJECT_ID, ".appspot.com/"])


def gitlab_vars():
    """ This test will check that the variables to perform the process are
    not empty"""
    assert (PROJECT_ID, TMP_ROUTE, CI) != ""


def test_app_engine_error_code():
    """ This test will check if the new deployment slot is working and
    answering a 200 status code """
    import requests
    answer = requests.get(URL)

    assert answer.status_code == 200


def test_new_blog_post():
    """ This test will compare if the last element in the RSS feed of the
    temporal slot is the last one in the productive GAE slot """
    import feedparser

    if CI.startswith('post/'):
        tempfeed = feedparser.parse(''.join([URL, 'index.xml']))
        prodfeed = feedparser.parse('https://tangelov.me/index.xml')

        assert tempfeed.entries[0].title != prodfeed.entries[0].title
