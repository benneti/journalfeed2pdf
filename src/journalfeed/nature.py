#!/usr/bin/env python3
import datetime
import requests
import bs4
from bs4 import BeautifulSoup
from .Article import Article


def get_articles(enddate = datetime.date.today(),
                 startdate=datetime.date.today() - datetime.timedelta(days=8),
                 journals=["nature", "nmat", "nphys"], **kwargs):
    """
    Get's the list of current research articles from nature.com/<journals>/current-issue.

    Unsupported kwargs are passed on to the article contructor.
    """
    url_base = "https://www.nature.com"
    articles = []
    for journal in journals:
        url = url_base+"/"+journal+"/current-issue"
        response = requests.get(url)
        def check_words(words):
            return lambda x: x and frozenset(words.split()).intersection(x.split())

        soup = BeautifulSoup(response.content, "html.parser")

        section_tags = soup.find('div', {'data-container-type': check_words('issue-section-list')})

        for sec in section_tags:
            sec_title = sec.find('h2')
            if isinstance(sec_title, bs4.element.Tag) and any(s in sec_title.contents[0]
                                                              for s in ["Research", "Articles", "Letters"]):
                for article in sec.find_all('article'):
                    try:
                        url = url_base+article.find('a', {'itemprop': check_words('url')})['href']
                    except TypeError:
                        continue
                    if any(s in article.find(attrs={'data-test': check_words('article.type')}).text.strip()
                           for s in ["Article", "Letter"]):
                        title = article.find('h3', {'itemprop': check_words('name headline')}).text.strip()
                        date = article.find('time', {'itemprop': check_words('datePublished')}).text.strip()
                        date = datetime.datetime.strptime(date, "%d %B %Y").date()
                        authors = article.find_all('li', {'itemprop': check_words('creator')})
                        authors = [a.text.replace(",", "").replace("&\xa0", "").strip() for a in authors]
                        # TODO get real abstract, see science takes very long
                        # try:
                        #     soup_art = BeautifulSoup(requests.get(url).content, "html.parser")
                        #     abstract = soup_art.find("div", {"id": "Abs1-content"}).find("p").text
                        # except AttributeError:
                        #     abstract = "No Abstract found"
                        # naturearticles.append(Article(title.replace("\n", ""), url,
                        #                           date, authors, abstract, journal))
                        try:
                            abstract = article.find('div', attrs={'itemprop': check_words('description')}).find("p").text.strip()
                        except AttributeError:
                            abstract = "No Abstract found"
                        articles.append(Article(title.replace("\n", ""), url,
                                                date, authors, abstract, journal, **kwargs))
    return articles
