#!/usr/bin/env python3
import datetime
import feedparser as fp
import time  # used for connections to arxiv
from .Article import Article
from .helpers import parsed_datetime


def get_articles(enddate=datetime.date.today(),
                 startdate=datetime.date.today() - datetime.timedelta(days=8),
                 query="cat:cond-mat*+OR+cat:quant-ph", id_list="", **kwargs):
    """get arxiv articles from startdate 00:00 to enddate 00:00.
    If an id_list is provided start and end dates are ignored.

    Unsupported kwargs are passed on to the article contructor.
    """
    feeds = []
    cond = True
    retry = 0
    while cond and len(feeds) < 100:  # tenthousand entries is pretty long
        # either lastUpdatedDate or submittedDate
        # We use the latter as we are only interested in new papers
        # see https://github.com/ContentMine/getpapers/issues/180
        # and https://github.com/ContentMine/getpapers/wiki/arxiv-query-format
        url = "https://export.arxiv.org/api/query?"
        if query != "":
            url += "search_query=(" + query + ")+AND+"
        if id_list != "":
            url += "id_list=" + id_list
        else:
            url += "submittedDate:["+startdate.strftime("%Y%m%d")+"0000+TO+"+enddate.strftime("%Y%m%d")+"0000]"
        url += "&start="+str(100*len(feeds))+"&max_results=100&sortBy=submittedDate&sortOrder=descending"
        feeds.append(fp.parse(url))
        totalresults = int(feeds[-1]["feed"]["opensearch_totalresults"])
        if totalresults == 0 or len(feeds[-1].entries) == 0:
            # something has gone wrong
            retry += 1
            del feeds[-1]  # remove the last entry
            cond = True
        if len(feeds) * 100 >= totalresults or retry > 5:
            cond = False
        if cond:  # arxiv asks users to wait for 3 seconds between queries
            time.sleep(3)

    articles = []
    for feed in feeds:
        for e in feed.entries:
            published = parsed_datetime(e.published_parsed)
            articles.append(Article(e.title.replace("\n", ""), e.link, published,
                                         [a["name"].strip() for a in e.authors], e.summary,
                                         "arXiv", **kwargs))
    return articles
