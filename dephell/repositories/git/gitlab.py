# built-in
import re
from urllib.parse import urlencode

# external
import requests

# app
from ..utils import cached_property
from .base import BaseRepo


rex_author = re.compile(r'gitlab\.com[/:]([a-zA-Z_-])')


class GitLabRepo(BaseRepo):

    @cached_property
    def author(self):
        match = rex_author.search(self.link)
        if match:
            # get from `#hash=...`
            return match.group(1)

    # https://gitlab.com/api/v4/projects/inkscape%2Finkscape/repository/tags
    # https://docs.gitlab.com/ee/api/tags.html
    def _get_tags(self):
        url = 'https://gitlab.com/api/v4/projects/{id}/repository/tags'.format(
            id=urlencode(self.author + '/' + self.name),
        )
        response = requests.get(url)

        tags = []
        for tag in response.json():
            tags.append(tag['name'])
        return tags
