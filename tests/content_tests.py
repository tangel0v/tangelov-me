"""
This code will get the content of some variables in gitlab and put it into
the docker container to provide more compatibility when doing local testing
PROJECT_ID is the identificator of the project of Google Cloud Platform
TMP_ROUTE is the name of the temporary service created to perform some tests
CI is the origin branch in Gitlab
"""

import os
import glob
import yaml

# Getting information from host to docker
PROJECT_ID = os.environ.get("PROJECT_ID")
TMP_ROUTE = os.environ.get("TMP_ROUTE")
CI = os.environ.get("CI_COMMIT_REF_NAME")

# Preproduction information
URL = ''.join(["https://", TMP_ROUTE, "-dot-", PROJECT_ID, ".appspot.com/"])

def test_post_urls_not_change():
    """This tests will check if any post URL has changed to avoid broken links """

    directory = "content/posts/*.md"
    for filepath in glob.iglob(directory):
        with open(filepath) as post:
            metadata = [next(post) for x in range(3)]
            url = yaml.load(metadata[2], Loader=yaml.FullLoader)

            import requests
            answer = requests.get(URL + 'posts/' + url["slug"] + '.html')

            assert answer.status_code == 200


def test_pages_urls_not_change():
    """This tests will check if any page URL has changed to avoid broken links """

    directory = "content/pages/*.md"
    for filepath in glob.iglob(directory):
        with open(filepath) as page:
            metadata = [next(page) for x in range(3)]
            url = yaml.load(metadata[2], Loader=yaml.FullLoader)

            import requests
            answer = requests.get(URL + 'pages/' + url["slug"] + '.html')

            assert answer.status_code == 200
