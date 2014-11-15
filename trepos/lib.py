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
    """Print out the number of seconds taken to complete a given task.."""
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
        return "&".join("{0}={1}".format(k, v) for k, v in kwargs.iteritems())

    return "{endpoint}?{args}".format(endpoint="%s/trending" % API_ENDPOINT,
                                      args=_build_args(**kwargs))


def recur(obj, methods):
    return obj if not methods else recur(getattr(obj, methods[0])(),
                                         methods[1:])

def merge_dicts(*ds):
    return {k: v for d in ds for k, v in d.iteritems()}


def extract_name(repo):
    repo_name = repo.xpath('.//h3[@class="repo-list-name"]')
    return recur(repo_name.css("a").xpath("@href"),
                 ("pop", "extract", "strip",))


def extract_desc(repo):
    repo_desc = repo.xpath('.//p[@class="repo-list-description"]/text()')
    return recur(repo.xpath('.//p[@class="repo-list-description"]/text()'),
                 ("pop", "extract", "strip",)) if len(repo_desc) else ""


def extract_meta(repo):
    def _intify(stars):
        return int(stars.split(" stars ")[0].replace(",", ""))

    repo_meta = repo.xpath('.//p[@class="repo-list-meta"]/text()')
    vals = repo_meta.extract()[0].split(u"•")

    assert 1 <= len(vals) <= 3, "Invalid meta: {0}".format(" ".join(vals))

    # build meta dict consisting of keys: lang, stars and built_by
    lang, stars, built_by = None, None, None
    if len(vals) == 3:
        lang, stars, built_by = vals[0].strip(), _intify(vals[1]), vals[2]
    elif len(vals) == 2:
        if " stars " in vals[0]:
            stars, built_by = _intify(vals[0]), vals[1]
        else:
            lang, built_by = vals[0].strip(), vals[1]
    else:
        built_by = vals[0]

    return {"lang": lang, "stars": stars, "built_by": built_by}


def extract_body(url):
    return requests.get(url).text


def fetch_langs():
    body = extract_body("{0}/trending".format(API_ENDPOINT))

    classes = "select-menu-item-text js-select-button-text js-navigation-open"
    path = '//a[@class="{0}"]/text()'.format(classes)

    return [lang.extract().strip()
            for lang in Selector(text=body).xpath(path)]


def fetch_lang_repos(since=PERIOD_DAILY, **kwargs):
    def _build_dict(repo):
        name = extract_name(repo)
        desc = extract_desc(repo)
        meta = extract_meta(repo)

        return {"name": name,
                "desc": desc,
                "lang": meta["lang"] or "",
                "stars": meta["stars"] or 0}

    body = extract_body(build_url(**merge_dicts(kwargs, {"since": since})))
    return map(_build_dict,
               Selector(text=body).xpath('//li[@class="repo-list-item"]'))


@elapsed
@validate
def fetch_repos(**kwargs):
    repos = [repo
             for lang in kwargs["langs"]
             for repo in fetch_lang_repos(l=lang, since=kwargs["period"])]

    # filter out unstarred repos unless 'showall' is on
    filtered = (filter(lambda d: d["stars"], repos)
                if not kwargs["showall"] else repos)

    # repos with most stars first
    return sorted(filtered, key=lambda d: d["stars"], reverse=True)


if __name__ == "__main__":
    # list all langs
    langs = fetch_langs()
    print("{0} languages found:".format(len(langs)))
    print(", ".join(lang for lang in langs))

    assert build_url(l="c", since=PERIOD_DAILY) in (
        "https://github.com/trending?l=c&since=daily",
        "https://github.com/trending?since=daily&l=c",
    )

    print("-" * 20)

    # top 5 repos ()
    print("top 5 repos this month:")
    repos = fetch_lang_repos(since=PERIOD_MONTHLY)[:5]
    for repo in repos:
        print("[{lang}] *{stars}* {name} - {desc}".format(
            lang=repo["lang"],
            name=repo["name"],
            stars=repo["stars"],
            desc=repo["desc"],
        ))

    print("-" * 20)

    # list top 10 repos belonging to either python or ruby
    print("top 10 python/ruby repos this week:")
    repos = fetch_repos(langs=("python", "ruby",),
                        period=PERIOD_WEEKLY,
                        showall=False)[:10]
    for repo in repos:
        print("[{lang}] *{stars}* {name} - {desc}".format(
            lang=repo["lang"],
            name=repo["name"],
            stars=repo["stars"],
            desc=repo["desc"],
        ))
