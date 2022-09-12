#!/usr/bin/env python3
import datetime
import requests
import bs4
from bs4 import BeautifulSoup
from .Article import Article
import dateutil.parser


def get_articles(enddate = datetime.date.today(),
                 startdate=datetime.date.today() - datetime.timedelta(days=7),
                 journals=["science", "advances"], **kwargs):
    """
    Get's the list of current research articles from <journal>.sciencemag.com.

    Unsupported kwargs are passed on to the article contructor.
    """
    articles = []
    for journal in journals:
        url_base = "https://"+journal+".sciencemag.org"
        url = url_base+"/toc/science/current"
        response = requests.get(url)
        def check_words(words):
            return lambda x: x and frozenset(words.split()).intersection(x.split())

        soup = BeautifulSoup(response.content, "html.parser")

        section_tags = soup.find_all(
            'section', {'class': check_words('toc__section')}
        )

        for sec in section_tags:
            sec_title = sec.find('h4')
            if isinstance(sec_title, bs4.element.Tag) and any(s in sec_title.contents[0] for s in ["Research", "Articles", "Reviews"]):
                for article in sec.find_all('div', {'class': check_words('card')}):
                    try:
                        url = url_base+article.find('a')['href']
                    except TypeError:
                        continue
                    title = article.find('h3', {'class': check_words('article-title')}).text.strip()
                    date = dateutil.parser.parse( article.find('time').text.strip() ).date()


                    authors = article.find('ul', {'title': check_words('authors')})
                    if authors is None:
                        authors = [ "No authors found" ]
                    else:
                        authors = authors.find_all('li', {'class': check_words('list-inline-item')})
                        authors = [a.text.strip() for a in authors]
                    abstract = article.find('div', {'class': check_words('card-body')})
                    if abstract is None:
                        abstract = ""
                    else:
                        abstract = abstract.text.strip()
                    _abstract = article.find('div', {'class': check_words('card-footer')}).find("div", {'class': check_words('accordion__content')})
                    if _abstract is not None:
                        abstract += _abstract.text.strip()
                        abstract += "\n"
                    articles.append(Article(title.replace("\n", ""), url, date, authors, abstract, journal, **kwargs))
    return articles
