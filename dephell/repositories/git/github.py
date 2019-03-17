# built-in
import re

# external
import requests

# app
from ..utils import cached_property
from .base import BaseRepo


rex_author = re.compile(r'github\.com[/:]([a-zA-Z_-])')


class GitHubRepo(BaseRepo):

    @cached_property
    def author(self):
        match = rex_author.search(self.link)
        if match:
            return match.group(1)

    # https://developer.github.com/v3/repos/releases/
    # https://api.github.com/repos/orsinium/textdistance/releases
    def _get_tags(self):
        url = 'https://api.github.com/repos/{author}/{name}/releases'.format(
            author=self.author,
            name=self.name,
        )
        response = requests.get(url)

        tags = []
        for release in response.json():
            tags.append(release['tag_name'])
        return tags
