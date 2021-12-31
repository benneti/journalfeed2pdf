#!/usr/bin/env python3

import datetime
import feedparser as fp
from .Article import Article


def parsed_datetime(parsed_date):
    """Parse a feedparser date again to create a datetime object"""
    return datetime.date(parsed_date.tm_year, parsed_date.tm_mon, parsed_date.tm_mday)

def pr_summary_extract(s):
    if "<p>" in s:
        return s[s.find("<p>")+3:s.find("</p>")]
    return s

def get_articles(enddate = datetime.date.today(),
                 startdate=datetime.date.today() - datetime.timedelta(days=7),
                 journals = ["prl"], **kwargs):

    feeds = []
    for pr in journals:
        feeds.append(fp.parse("http://feeds.aps.org/rss/recent/"+pr+".xml"))

    prarticles = []
    for feed in feeds:
        for e in feed.entries:
            published = parsed_datetime(e.updated_parsed)
            if startdate <= published <= enddate:
                authors = []
                for aths in e.authors:
                    if " and " in aths["name"]:
                        ath1, ath2 = aths["name"].strip().replace(".\u2009T.", ".").split(" and ", 1)
                        for a in ath1.split(", "):
                            a = a.strip()
                            if a != "":
                                authors.append(a)
                        authors.append(ath2.strip())
                    else:
                        authors.append(aths["name"].strip())
                prarticles.append(Article(e.title.replace("\n", ""), e.link, published,
                                          authors, pr_summary_extract(e.summary),
                                          e.summary_detail["base"].split("/")[-1].replace(".xml", ""), **kwargs))
    return prarticles
