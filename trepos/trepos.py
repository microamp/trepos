# -*- coding: utf-8 -*-

from scrapy.selector import Selector
import requests


ENDPOINT = "https://github.com"
PATH = "/trending"

PERIOD_DAILY = "daily"
PERIOD_WEEKLY = "weekly"
PERIOD_MONTHLY = "monthly"
VALID_PERIODS = (PERIOD_DAILY, PERIOD_WEEKLY, PERIOD_MONTHLY,)

ERR_MISSING_KWARG = "Required keyword argument missing: {0}"


def recur(obj, methods):
    return obj if not methods else recur(getattr(obj, methods[0])(),
                                         methods[1:])


def merge_dicts(*dicts):
    return {k: v for d in dicts for k, v in d.items()}


def build_params(**params):
    return "&".join("{0}={1}".format(k, v)
                    for k, v in params.items() if v is not None)


class Trepos(object):
    def __init__(self, endpoint=ENDPOINT, path=PATH):
        self.endpoint = endpoint
        self.path = path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def build_url(self, **params):
        p = "&".join("{0}={1}".format(k, v)
                     for k, v in params.items() if v is not None)
        return "{0}{1}{2}".format(self.endpoint, self.path, p or "")

    def extract_body(self, url):
        return requests.get(url).text

    def extract_name(self, repo):
        repo_name = repo.xpath('.//h3[@class="repo-list-name"]')
        return recur(repo_name.css("a").xpath("@href"),
                     ("pop", "extract", "strip",))

    def extract_desc(self, repo):
        repo_desc = repo.xpath('.//p[@class="repo-list-description"]/text()')
        return recur(repo.xpath('.//p[@class="repo-list-description"]/text()'),
                     ("pop", "extract", "strip",)) if len(repo_desc) else ""

    def extract_meta(self, repo):
        repo_meta = repo.xpath('.//p[@class="repo-list-meta"]/text()')
        return [f.strip() for f in repo_meta.extract()[0].split(u"•")]

    def fetch_langs(self):
        """Fetch all languages on GitHub."""
        body = self.extract_body("{0}{1}".format(self.endpoint, self.path))
        class_vals = ("select-menu-item-text", "js-select-button-text",
                      "js-navigation-open",)
        path = '//a[@class="{0}"]/text()'.format(" ".join(class_vals))
        return [lang.extract().strip()
                for lang in Selector(text=body).xpath(path)]

    def fetch_repos(self, l=None, since=None, **kwargs):
        """Fetch all trending repos."""
        params = build_params(**merge_dicts({"l": l, "since": since}, kwargs))
        url = "{0}{1}{2}".format(self.endpoint, self.path,
                                 "?{0}".format(params) if params else "")
        body = self.extract_body(url)

        return [
            {"name": self.extract_name(r),
             "desc": self.extract_desc(r),
             "meta": self.extract_meta(r)}
            for r in Selector(text=body).xpath('//li[@class="repo-list-item"]')
        ]


if __name__ == "__main__":
    from pprint import pprint

    with Trepos() as trepos:
        # print all languages
        pprint(trepos.fetch_langs())
        # print all repos
        pprint(trepos.fetch_repos(l="python", since=PERIOD_DAILY))
