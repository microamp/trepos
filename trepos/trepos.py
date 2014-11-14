# -*- coding: utf-8 -*-

"""
Usage: trepos.py [OPTIONS]

Options:
  -l, --lang TEXT                 Language(s) to filter
  -p, --period [daily|weekly|monthly]
                                  daily/weekly/monthly (default: weekly)
  -s, --showall BOOLEAN           To include/exclude non-starred repos
                                  (default: no)
  --help                          Show this message and exit.
"""

from pprint import pprint

import click

from .lib import VALID_PERIODS, PERIOD_DAILY, fetch_repos


@click.command()
@click.option("--lang", "-l",
              multiple=True,
              help="Language(s) to filter")
@click.option("--period", "-p",
              type=click.Choice(VALID_PERIODS),
              default=PERIOD_DAILY,
              help="daily/weekly/monthly (default: daily)")
@click.option("--showall", "-s",
              type=bool,
              default=False,
              help="Flag to include non-starred repos (default: no)")
def main(lang, period, showall):
    repos = fetch_repos(langs=lang,
                        period=PERIOD_DAILY,
                        showall=showall)
    pprint(repos)


if __name__ == "__main__":
    main()
