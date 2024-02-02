#!/usr/bin/env python3
import datetime
import requests
from bs4 import BeautifulSoup  # used to get rid of HTML stuff

def parsed_datetime(parsed_date):
    """Parse a feedparser date again to create a datetime object"""
    return datetime.date(parsed_date.tm_year, parsed_date.tm_mon, parsed_date.tm_mday)

def check_words(words):
    return lambda x: x and frozenset(words.split()).intersection(x.split())

def abstract_from_doi(doi):
    """Fetch the abstract from doi.org for the given doi"""
    try:
        response = requests.get("https://doi.org/"+doi, headers={"Accept": "application/citeproc+json"})
        data = response.json()
        return BeautifulSoup(data["abstract"], "html.parser").get_text(strip=True)
    except:
        return "no abstract found for doi:"+doi
