#!/usr/bin/env python3
# journalfeed2pdf -- python script to get content from the web
# Copyright (C) 2020 Benedikt Tissot

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import feedparser as fp
import requests
import datetime
import re
import bs4
from bs4 import BeautifulSoup
import sys

# changing the query here is used to configure the arxiv see arxiv API for usage
arxivquery = "search_query=(cat:cond-mat*+OR+cat:quant-ph)"
# we get the arxiv articles for one week
# (starting 8 days ago..., such that we do not miss articles due to not all articles published today)

# add PR journals as one likes
prl = "prl"
pra = "pra"
prb = "prb"
prx = "prx"
prxquantum = "prxquantum"
prresearch = "prresearch"
prs = [prl, prxquantum, prresearch, pra, prb]

# for nature we only support nature right now
# (now config, only research articles are included)

def elc(s):
    """Ensure Latex compatibility of a string s"""
    ret = []
    # ensure even number of $'s
    if len(re.findall("\$", s)) % 2 != 0:
        return "Too many Dollar signs..."
    # get rid of some html directly, like links and special characters...
    for i, part in enumerate(BeautifulSoup(s, "html.parser").text.strip().split("$")):
        if i % 2 == 0: # we are not in math mode so better not use these!
            for rs in [["^", "\\^"],
                       ["_", "\\_"],
                       ["{\\deg}", "$^{\\circ}$"],
                       ]:
                part = part.replace(rs[0], rs[1])

        for rs in [["&amp;", "\\&"],
                   ["&quot;", '"'],
                   ["&gt;", ">"],
                   ["&lt;", "<"],
                   ["\\%", "%"], # ensure no escaped %
                   ["%", "\\%"],
                   ["\\cite", ""],
                   ["\\mathbit", ""],
                   ["o", "o"],
                   [" & ", " \\& "]
                   ]:
            part = part.replace(rs[0], rs[1])
        ret.append(part)
    return "$".join(ret)

class Article:
    """
    Container for an article (title, url, date, authors, summary, journal)
    """
    def __init__(self, title, url, date, authors, summary, journal):
        self.title = title
        self.url = url
        self.date = date
        self.authors = [elc(a).replace("}", "").replace("{", "") for a in authors]
        self.summary = summary
        self.journal = journal
    def author_string(self, max_authors=3):
        if max_authors < 2:
            raise ValueError("max_authors needs to be larger than 1.")
        authors = self.authors
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return authors[0]+" and "+authors[1]
        elif len(authors) <= max_authors:
            return ", ".join(authors[0:max_authors-2])+", and "+authors[-1]
        else:
            return authors[0]+", ..., and "+authors[-1]

    def latex(self, max_authors=3, show_journal=False, show_summary=True):
        """
        Create a latex compatible string for an article.
        """
        # write the title in a subsection and use href for url
        ret = "\\subsection*{\\href{"+self.url+"}{"
        ret += elc(self.title)+"}}\n"
        # write the authors and date in a subsubsection
        ret += "\\subsubsection*{"
        ret += self.author_string(max_authors=max_authors).replace("...", "\\dots")
        ret += " ("+self.date.isoformat()
        # if wished for also show the journal
        if show_journal:
            ret += " "+self.journal
        ret += ")}\n"
        # also add the summary/abstract
        if show_summary:
            ret += elc(self.summary)+"\n"
        return ret

def get_naturearticles(enddate = datetime.date.today(), timedelta = datetime.timedelta(days=7)):
    """
    Get's the list of current research articles from nature.com/nature/current-issue.
    Outputs a list of Articles.
    """
    startdate = enddate - timedelta
    url_base = "https://www.nature.com"
    url = url_base+"/nature/current-issue"
    response = requests.get(url)
    def check_words(words):
        return lambda x: x and frozenset(words.split()).intersection(x.split())

    soup = BeautifulSoup(response.content, "html.parser")

    section_tags = soup.find(
        'div', {'data-container-type': check_words('issue-section-list')}
    )

    naturearticles = []

    for sec in section_tags:
        sec_title = sec.find('h2')
        if isinstance(sec_title, bs4.element.Tag) and "Research" in sec_title.contents[0]:
            for article in sec.findAll('article'):
                try:
                    url = url_base+article.find('a', {'itemprop': check_words('url')})['href']
                except TypeError:
                    continue
                title = article.find('h3', {'itemprop': check_words('name headline')}).text.strip()
                date = article.find('time', {'itemprop': check_words('datePublished')}).text.strip()
                date = datetime.datetime.strptime(date, "%d %B %Y")
                authors = article.findAll('li', {'itemprop': check_words('creator')})
                authors = [a.text.replace(",", "").replace("&\xa0", "").strip() for a in authors]
                description = "(" + article.find(attrs={'data-test': check_words('article.type')}).text.strip() + ")"
                abstract = article.find('div', attrs={'itemprop': check_words('description')})
                if not abstract is None:
                    description += abstract.text.strip()
                naturearticles.append(Article(title.replace("\n", ""), url, date, authors, description, "Nature"))
    return naturearticles

def parsed_datetime(parsed_date):
    """Parse a feedparser date again to create a datetime object"""
    return datetime.date(parsed_date.tm_year, parsed_date.tm_mon, parsed_date.tm_mday)

def get_arxivarticles(enddate = datetime.date.today(), timedelta = datetime.timedelta(days=7), query = arxivquery):
    startdate = enddate - timedelta
    feeds = []
    cond = True
    while cond and len(feeds) < 100:
        url = "https://export.arxiv.org/api/query?" + query
        url += "&start="+str(100*len(feeds))+"&max_results=100&sortBy=submittedDate&sortOrder=descending"
        feeds.append(fp.parse(url))
        # feeds.append(fp.parse("https://export.arxiv.org/api/query?search_query=(cat:cond-mat*+OR+cat:quant-ph)&start="+str(500*len(feeds))+"&max_results=500&sortBy=submittedDate&sortOrder=descending"))
        cond = len(feeds[-1].entries) != 0 and startdate <= parsed_datetime(feeds[-1].entries[-1].published_parsed) + datetime.timedelta(days=1) <= enddate


    arxivarticles = []
    for feed in feeds:
        for e in feed.entries:
            published = parsed_datetime(e.published_parsed)
            if startdate <= published + datetime.timedelta(days=1) <= enddate:
                arxivarticles.append(Article(e.title.replace("\n", ""), e.link, published,
                                             [a["name"].strip() for a in e.authors], e.summary,
                                             "arXiv"))
    return arxivarticles

def pr_summary_extract(s):
    if "<p>" in s:
        return s[s.find("<p>")+3:s.find("</p>")]
    return s


def get_prarticles(enddate = datetime.date.today(), timedelta = datetime.timedelta(days=7), prs = prs):
    startdate = enddate - timedelta

    feeds = []
    for pr in prs:
        feeds.append(fp.parse("http://feeds.aps.org/rss/recent/"+pr+".xml"))

    prarticles = []
    for feed in feeds:
        for e in feed.entries:
            published = parsed_datetime(e.updated_parsed)
            if startdate <= published <= enddate:
                authors = []
                for aths in e.authors:
                    if "and" in aths["name"]:
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
                                          e.summary_detail["base"].split("/")[-1].replace(".xml", "")))
    return prarticles

if __name__ == "__main__":
    enddate = datetime.date.today()
    timedelta = datetime.timedelta(days=7)

    if len(sys.argv) == 1:
        print("Usage: python", sys.argv[0], "<output.tex>")
        sys.exit(2)
    else:
        fname = sys.argv[1]

    prarticles = get_prarticles()
    naturearticles = get_naturearticles()
    arxivarticles = get_arxivarticles()

    with open(fname, "w") as file:
        file.write("\\title{In the Journals}\n")
        file.write("\\date{"+(enddate - timedelta).isoformat()+" to "+enddate.isoformat()+"}\n")
        file.write("\\maketitle\n\n")
        file.write("\\section{APS Journals ("+", ".join(prs)+")}\n")
        for article in prarticles:
            file.write(article.latex(show_journal=True))
        file.write("\\clearpage\n")
        file.write("\\section{Nature}\n")
        for article in naturearticles:
            file.write(article.latex())
        file.write("\\clearpage\n")
        file.write("\\section{arXiv}\n")
        for article in arxivarticles:
            file.write(article.latex()+"\n")
