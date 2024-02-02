#!/usr/bin/env python3
import datetime

def parsed_datetime(parsed_date):
    """Parse a feedparser date again to create a datetime object"""
    return datetime.date(parsed_date.tm_year, parsed_date.tm_mon, parsed_date.tm_mday)

def check_words(words):
    return lambda x: x and frozenset(words.split()).intersection(x.split())
