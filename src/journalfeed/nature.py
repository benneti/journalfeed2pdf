#!/usr/bin/env python3
import datetime
import requests
import bs4
from bs4 import BeautifulSoup
from .Article import Article
import dateutil.parser


def get_articles(enddate = datetime.date.today(),
                 startdate=datetime.date.today() - datetime.timedelta(days=7),
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

        section_tags = soup.find_all('section', {'data-container-type': check_words('issue-section-list')})
        if section_tags is None:
            section_tags = soup.find('div', {'data-container-type': check_words('issue-section-list')})

        if section_tags is not None:
            for sec in section_tags:
                sec_title = sec.find('h2')
                if isinstance(sec_title, bs4.element.Tag) and sec_title.contents[0] == "Research":
                    subsecs = soup.find('ul', {'class': check_words('app-article-list-row')}).find_all("li", recursive=False)
                    for subsec in subsecs:
                        subsec_title = subsec.find('h3', {'class': check_words('c-section-heading')})
                        if isinstance(subsec_title, bs4.element.Tag) and any(s in subsec_title.contents[0]
                                                                           for s in ["Research", "Articles", "Letters", "Reviews"]):
                            for article in sec.find_all('article'):
                                try:
                                    url = url_base+article.find('a', {'itemprop': check_words('url')})['href']
                                except TypeError:
                                    continue
                                title = article.find('h3', {'itemprop': check_words('name headline')}).text.strip()
                                date = dateutil.parser.parse( article.find('time', {'itemprop': check_words('datePublished')}).text.strip() ).date()
                                authors = article.find_all('li', {'itemprop': check_words('creator')})
                                authors = [a.text.replace(",", "").replace("&\xa0", "").strip() for a in authors]
                                try:
                                    abstract = article.find('div', attrs={'itemprop': check_words('description')}).find("p").text.strip()
                                except AttributeError:
                                    abstract = "No Abstract found"
                                articles.append(Article(title.replace("\n", ""), url,
                                                        date, authors, abstract, journal, **kwargs))
    return articles
