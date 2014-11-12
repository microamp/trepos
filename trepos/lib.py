# -*- coding: utf-8 -*-

import time

from scrapy.selector import Selector
import requests


API_ENDPOINT = "https://github.com"

PERIOD_DAILY = "daily"
PERIOD_WEEKLY = "weekly"
PERIOD_MONTHLY = "monthly"
VALID_PERIODS = (PERIOD_DAILY, PERIOD_WEEKLY, PERIOD_MONTHLY,)

ERR_MISSING_KWARG = "Required keyword argument missing: {0}"


def elapsed(fn):
    def _elapsed(*args, **kwargs):
        started = time.time()
        r = fn(*args, **kwargs)
        ended = time.time()
        print("time elapsed: %.2f seconds" % (ended - started))
        return r

    return _elapsed


def validate(fn):
    """Simple validation on input arguments."""
    def _validate(*args, **kwargs):
        # required fields
        for kwarg in {"langs", "period", "showall"}:
            assert kwarg in kwargs, ERR_MISSING_KWARG.format(kwarg)

        return fn(*args, **kwargs)

    return _validate


def build_url(**kwargs):
    def _build_args(**kwargs):
        return "&".join("{0}={1}".format(k, v) for k, v in kwargs.items())

    return "{endpoint}?{args}".format(endpoint="%s/trending" % API_ENDPOINT,
                                      args=_build_args(**kwargs))


def recur(obj, methods):
    return obj if not methods else recur(getattr(obj, methods[0])(),
                                         methods[1:])


def extract_name(repo):
    repo_name = repo.xpath('.//h3[@class="repo-list-name"]')
    return recur(repo_name.css("a").xpath("@href"),
                 ("pop", "extract", "strip",))


def extract_desc(repo):
    repo_desc = repo.xpath('.//p[@class="repo-list-description"]/text()')
    return recur(repo.xpath('.//p[@class="repo-list-description"]/text()'),
                 ("pop", "extract", "strip",)) if len(repo_desc) else ""


def extract_meta(repo):
    repo_meta = repo.xpath('.//p[@class="repo-list-meta"]/text()')
    return repo_meta.extract()[0].split(u"•")


def fetch_lang_repos(lang, period):
    body = requests.get(build_url(l=lang, since=period)).text

    repos = []
    for repo in Selector(text=body).xpath('//li[@class="repo-list-item"]'):
        repo_name = extract_name(repo)
        repo_desc = extract_desc(repo)
        repo_meta = extract_meta(repo)

        repos.append({"name": repo_name,
                      "desc": repo_desc,
                      "lang": repo_meta[0].strip(),
                      "stars": (int(repo_meta[1].strip().split(" ")[0])
                                if len(repo_meta) == 3 else 0)})

    return repos


@elapsed
@validate
def fetch_repos(**kwargs):
    repos = [repo
             for lang in kwargs["langs"]
             for repo in fetch_lang_repos(lang, kwargs["period"])]

    filtered = (filter(lambda d: d["stars"], repos)
                if not kwargs["showall"] else repos)

    return sorted(filtered, key=lambda d: d["stars"], reverse=True)


if __name__ == "__main__":
    from operator import eq
    from pprint import pprint

    assert eq(build_url(lang="c", since=PERIOD_DAILY),
              "https://github.com/trending?lang=c&since=daily")

    repos = fetch_repos(langs=("sml", "ocaml", "haskell", "rust",),
                        period=PERIOD_DAILY,
                        showall=False)
    pprint(repos)
