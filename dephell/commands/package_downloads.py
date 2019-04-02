# built-in
from argparse import ArgumentParser
from collections import defaultdict
from itertools import zip_longest
from typing import Iterable

import requests

# app
from ..config import builders
from .base import BaseCommand


class PackageDownloadsCommand(BaseCommand):
    recent_url = 'https://pypistats.org/api/packages/{}/recent'
    categories = dict(
        pythons='https://pypistats.org/api/packages/{}/python_minor',
        systems='https://pypistats.org/api/packages/{}/system',
    )
    ticks = '_▁▂▃▄▅▆▇█'

    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='dephell package downloads',
            description='Show downloads statistic for package from PyPI.org.',
        )
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_api(parser)
        builders.build_other(parser)
        parser.add_argument('name', help='package name')
        return parser

    def __call__(self):
        name = self.args.name.replace('_', '-')
        data = dict()

        url = self.recent_url.format(name)
        response = requests.get(url)
        if response.status_code != 200:
            self.logger.error('invalid status code', extra=dict(
                code=response.status_code,
                url=url,
            ))
            return False
        body = response.json()['data']
        data['total'] = dict(
            day=body['last_day'],
            week=body['last_week'],
            month=body['last_month'],
        )

        for category_name, category_url in self.categories.items():
            url = category_url.format(name)
            response = requests.get(url)
            if response.status_code != 200:
                self.logger.error('invalid status code', extra=dict(
                    code=response.status_code,
                    url=url,
                ))
                return False
            body = response.json()['data']

            grouped = defaultdict(list)
            for line in body:
                category = line['category'].replace('.', '')
                grouped[category].append(line['downloads'])

            data[category_name] = []
            for category, downloads in grouped.items():
                data[category_name].append(dict(
                    category=category,
                    day=downloads[-1],
                    week=sum(downloads[-7:]),
                    month=sum(downloads[-30:]),
                    chart=self.make_chart(downloads[-28:], group=7),
                ))

        print(self.get_value(data=data, key=self.config.get('filter')))

    def make_chart(self, values: Iterable[int], group: int = None) -> str:
        peek = max(values)
        if peek == 0:
            chart = self.ticks[-1] * len(values)
        else:
            chart = ''
            for value in values:
                index = round((len(self.ticks) - 1) * value / peek)
                chart += self.ticks[int(index)]
        if group:
            chunks = map(''.join, zip_longest(*[iter(chart)] * group, fillvalue=' '))
            chart = ' '.join(chunks).strip()
        return chart
