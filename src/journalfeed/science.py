#!/usr/bin/env python3
import datetime
import requests
import bs4
from bs4 import BeautifulSoup
from .Article import Article


def get_articles(enddate = datetime.date.today(),
                 startdate=datetime.date.today() - datetime.timedelta(days=8),
                 journals=["science", "advances"], **kwargs):
    """
    Get's the list of current research articles from <journal>.sciencemag.com.

    Unsupported kwargs are passed on to the article contructor.
    """
    articles = []
    for journal in journals:
        url_base = "https://"+journal+".sciencemag.org"
        url = url_base+"/content/current"
        response = requests.get(url)
        def check_words(words):
            return lambda x: x and frozenset(words.split()).intersection(x.split())

        soup = BeautifulSoup(response.content, "html.parser")

        section_tags = soup.find_all(
            'li', {'class': check_words('issue-toc-section')}
        )

        for sec in section_tags:
            sec_title = sec.find('h2')
            if isinstance(sec_title, bs4.element.Tag) and any(s in sec_title.contents[0] for s in ["Research", "Articles"]):
                for article in sec.find_all('article'):
                    try:
                        url = url_base+article.find('a')['href']
                    except TypeError:
                        continue
                    title = article.find('div', {'class': check_words('highwire-cite-title')}).text.strip()
                    date = article.find('time').text.strip()
                    date = datetime.datetime.strptime(date, "%d %b %Y").date()

                    authors = article.find_all('span', {'class': check_words('highwire-citation-author')})
                    authors = [a.text.strip() for a in authors]
                    abstract = article.find('div', {'class': check_words('section precis')}).find("p").text.strip()
                    # try:
                    #     soup_art = BeautifulSoup(requests.get(url+".abstract").content, "html.parser")
                    #     abstract = soup_art.find("div", {"class": check_words("abstract")}).find("p").text
                    # except AttributeError:
                    #     abstract = "No Abstract found"
                    articles.append(Article(title.replace("\n", ""), url, date, authors, abstract, journal, **kwargs))
    return articles
