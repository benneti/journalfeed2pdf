#!/usr/bin/env python3
import datetime
import feedparser as fp
from .Article import Article
from .helpers import parsed_datetime, abstract_from_doi


def get_articles(enddate = datetime.date.today(),
                 startdate=datetime.date.today() - datetime.timedelta(days=7),
                 journals=["science", "sciadv"], **kwargs):
    """
    Get's the list of current research articles from <journal>.sciencemag.com.

    Unsupported kwargs are passed on to the article contructor.
    """
    feeds = []
    for j in journals:
        feeds.append(fp.parse("https://www.science.org/action/showFeed?type=etoc&feed=rss&jc="+j))

    articles = []

    for feed in feeds:
        for e in feed.entries:
            published = parsed_datetime(e.updated_parsed)
            if startdate <= published <= enddate and ( "research article" in e.dc_type.lower() or "review" in e.dc_type.lower() ):
                authors = []
                try:
                    for aths in e.authors:
                        aths = aths["name"].strip().replace(".\u2009T.", ".").replace(" and ", ", ").replace("\n", "")
                        for author in aths.split(", "):
                            author = author.strip()
                            if author != "":
                                authors.append(author)
                except AttributeError:
                    authors.append("No authors found")
                    continue
                url = e.link
                journal = e.prism_publicationname.strip()
                try:
                    summary = abstract_from_doi(e.prism_doi)
                except:
                    summary = "No summary or abstract found"
                articles.append(Article(e.title.replace("\n", "").strip(), url, published, authors, summary, journal, **kwargs))
    return articles
