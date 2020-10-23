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
import time  # used for connections to arxiv

# arxiv
# see arxiv API for options, here we search for cond-mat and quant-ph articles
# (logical +OR+)
arxivquery = "cat:cond-mat*+OR+cat:quant-ph"
# we get the arxiv articles for one week
# (starting 8 days ago..., such that we do not miss articles due to not all articles published today)

# APS journals
prs = ["prl", "prb", "prxquantum", "prresearch", "pra"]
# nature journals
nature_weekly = ["nature"]
nature_monthly = ["nmat", "nphys"]
# science journals
science_weekly = ["science"]
science_monthly = ["advances"]


# Here we can configure
# environmants for math
latex_math_envs = ["equation", "align"]
latex_math_matchers = ["(\\$)([^\\$]+)(\\$)", "(\\$\\$)([^\\$]+)(\\$\\$)",
                       "(\\\\\\[)((?:.(?!\\\\\\]))*.)(\\\\\\])", "(\\\\\\()((?:.(?!\\\\\\)))*.)(\\\\\\))",
                       "(\\\\begin\\{(?P<env>"+"|".join(latex_math_envs)+")\\*?\\})(.+(?!(?P=env)))(\\\\end\\{(?P=env)\\*?\\})"]
latex_math_regex = re.compile("("+"|".join(latex_math_matchers)+")", flags=re.DOTALL)

# supports regexp (needs to be escaped accordingly)
# the general sub is applied last after \\ are stripped
latex_general_sub = [("cite\\{([^}]+)\\}", "[\\1]"),  # citekeys are pointless as we do not have the bib file
                     ("\\\\*mathbit", ""),  # we need the backslash, else we can be left with a backslash that destroys everything
                     ("o", "o")]
# Add things that should have a backslash here, as we strip all backslashes outside math
# right now this does not support keeping the matches of groups
latex_outside_math_sub = [("{\\\\deg}", "$^{\\\\circ}$"),
                          ("\\\\'", "\\\\'")]
# latex commands that do not make sense without the backslash (no regexp)
latex_prepend_backslash = ["emph\\{", "textit\\{", "textbf\\{", "^", "_", "&" ,"$", "%"]
# ensure no unescaped %
for command in latex_prepend_backslash:
    latex_outside_math_sub.append(((re.compile("\\\\*"+re.escape(command))), "\\\\"+command))
# here we ensure no newlines and tabbing in math
# , ("\\\\begin\\{aligned\\}(.+(?!aligned))\\\\end\\{aligned\\}", "\\1")
latex_inside_math_sub = [("\\\\\\\\", "\\\\ "),  # newline to space
                         ("([^\\\\])%", "\\1\\\\%"),  # escape %
                         ("([^\\\\])#", "\\1\\\\%"),  # escape #
                         ("\\&", ""),
                         # whitelist of capital letter commands
                         # Double escape, because in the end we strip some \
                         ("(\\\\Delta)", "\\\\\\1"),
                         ("(\\\\Gamma)", "\\\\\\1"),
                         ("(\\\\Omega)", "\\\\\\1"),
                         ("(\\\\Lambda)", "\\\\\\1"),
                         ("(\\\\Phi)", "\\\\\\1"),
                         ("(\\\\Pi)", "\\\\\\1"),
                         ("(\\\\Psi)", "\\\\\\1"),
                         ("(\\\\Sigma)", "\\\\\\1"),
                         ("(\\\\Theta)", "\\\\\\1"),
                         ("(\\\\Upsilon)", "\\\\\\1"),
                         ("(\\\\Vert)", "\\\\\\1"),
                         ("(\\\\Xi)", "\\\\\\1"),
                         ("(\\\\Leftrightarrow)", "\\\\\\1"),
                         ("(\\\\Leftarrow)", "\\\\\\1"),
                         ("(\\\\Rightarrow)", "\\\\\\1"),
                         ("(\\\\Longleftrightarrow)", "\\\\\\1"),
                         ("(\\\\Longleftarrow)", "\\\\\\1"),
                         ("(\\\\Longrightarrow)", "\\\\\\1"),
                         ("(\\\\Im)", "\\\\\\1"),
                         ("(\\\\Re)", "\\\\\\1"),
                         # if something does not start with a small letter it probably is not a latex command
                         ("\\\\([A-Z0-9])", "\\1")]


def find_all_latex_math(s, math_regex=latex_math_regex):
    """Search for all valid latex environments, returns a list of list [[whole match, begin, content, end],...]"""
    math_matches = latex_math_regex.findall(s)
    math_matches = [[j for j in i if j != ""] for i in math_matches]
    for i in math_matches:
        if len(i) == 5:
            del i[2]
    return math_matches


def elc(s, general_sub=latex_general_sub,
        outside_math_sub=latex_outside_math_sub,
        inside_math_sub=latex_inside_math_sub):
    """Ensure Latex compatibility of a string s"""
    # first use BeautifulSoup to get rid of html artefacts
    ret = BeautifulSoup(s, "html.parser").text.strip()

    ret = re.sub("\\$\\\\require\\{[^\\]\\}]+\\}\\$", "", ret)   # require is used in math by MATHJAX to load additional packages

    if (len(re.findall("\\{", ret)) != len(re.findall("\\}", ret))):
        return "Amount of curly braces not balanced."
    if (len(re.findall("\\\\\\{", ret)) != len(re.findall("\\\\\\}", ret))):
        return "Amount of curly braces not balanced."

    math_matches = find_all_latex_math(s)
    for i, match in enumerate(math_matches):
        ret = ret.replace(match[0], "MATH{}MATH".format(i))
        for find, replace in inside_math_sub:
            match[2] = re.sub(find, replace, match[2])

    for i, finrep in enumerate(outside_math_sub):
        ret = re.sub(finrep[0], "OUTSIDE{}OUTSIDE".format(i), ret)

    ret = ret.replace("\\", "")

    for i, finrep in enumerate(outside_math_sub):
        ret = re.sub("OUTSIDE{}OUTSIDE".format(i), finrep[1], ret)

    for i, match in enumerate(math_matches):
        ret = ret.replace("MATH{}MATH".format(i), "$"+match[2]+"$")

    for find, replace in general_sub:
        ret = re.sub(find, replace, ret)

    return ret.strip()


class Article:
    """
    Container for an article (title, url, date, authors, summary, journal)
    """
    def __init__(self, title, url, date, authors, summary, journal):
        self.title = elc(title)
        self.url = url
        self.date = date
        self.authors = [elc(a).replace("}", "").replace("{", "") for a in authors]
        self.summary = elc(summary)
        self.journal = elc(journal)


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
        ret += self.title+"}}\n"
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
            ret += self.summary+"\n"
        return ret


def get_naturearticles(enddate = datetime.date.today(),
                       startdate=datetime.date.today() - datetime.timedelta(days=8),
                       journals=["nature", "nmat", "nphys"]):
    """
    Get's the list of current research articles from nature.com/<journals>/current-issue.
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
                                        date, authors, abstract, journal))
    return articles


def get_sciencearticles(enddate = datetime.date.today(),
                       startdate=datetime.date.today() - datetime.timedelta(days=8),
                       journals=["science", "advances"]):
    """
    Get's the list of current research articles from <journal>.sciencemag.com.
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
                    articles.append(Article(title.replace("\n", ""), url, date, authors, abstract, journal))
    return articles


def parsed_datetime(parsed_date):
    """Parse a feedparser date again to create a datetime object"""
    return datetime.date(parsed_date.tm_year, parsed_date.tm_mon, parsed_date.tm_mday)


def get_arxivarticles(enddate=datetime.date.today(),
                      startdate=datetime.date.today() - datetime.timedelta(days=8),
                      query=arxivquery):
    """get arxiv articles from startdate 00:00 to enddate 00:00"""
    feeds = []
    cond = True
    retry = 0
    while cond and len(feeds) < 100:  # tenthousand entries is pretty long
        # either lastUpdatedDate or submittedDate
        # We use the latter as we are only interested in new papers
        # see https://github.com/ContentMine/getpapers/issues/180
        # and https://github.com/ContentMine/getpapers/wiki/arxiv-query-format
        url = "https://export.arxiv.org/api/query?search_query=(" + query + ")+AND+submittedDate:["
        url += startdate.strftime("%Y%m%d")+"0000+TO+"+enddate.strftime("%Y%m%d")+"0000]"
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
                                         "arXiv"))
    return articles


def pr_summary_extract(s):
    if "<p>" in s:
        return s[s.find("<p>")+3:s.find("</p>")]
    return s


def get_prarticles(enddate = datetime.date.today(), timedelta = datetime.timedelta(days=7), journals = prs):
    startdate = enddate - timedelta

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
                                          e.summary_detail["base"].split("/")[-1].replace(".xml", "")))
    return prarticles

if __name__ == "__main__":
    # enddate = datetime.date(2020, 10, 9)
    enddate = datetime.date.today()
    timedelta = datetime.timedelta(days=7)
    startdate = enddate - timedelta

    if len(sys.argv) != 2:
        print("Usage: python", sys.argv[0], "<output.tex>")
        sys.exit(2)
    else:
        if any(sys.argv[1] == h for h in ["-h", "--help"]):
            print("Usage: python", sys.argv[0], "<output.tex>")
            sys.exit(1)
        fname = sys.argv[1]

    prarticles = get_prarticles()

    # if we are in the first week of the month
    if enddate.day <= 7:
        # include the monthly journal(s) of nature and science families
        naturearticles = get_naturearticles(journals=[*nature_weekly, *nature_monthly],
                                            enddate=enddate, startdate=startdate)
        sciencearticles = get_sciencearticles(journals=[*science_weekly, *science_monthly],
                                              enddate=enddate, startdate=startdate)
    else:
        # else only include the weekly journal(s)
        naturearticles = get_naturearticles(journals=nature_weekly,
                                            enddate=enddate, startdate=startdate)
        sciencearticles = get_sciencearticles(journals=science_weekly,
                                              enddate=enddate, startdate=startdate)

    arxivarticles = get_arxivarticles()

    with open(fname, "w") as file:
        file.write("\\title{In the Journals}\n")
        if startdate.month == enddate.month:
            file.write("\\newcommand{{\\thedate}}{{{0:%d} to {1:%d %b. %Y}}}\n".format(startdate, enddate))
        elif startdate.year == enddate.year:
            file.write("\\newcommand{{\\thedate}}{{{0:%d %b.} to {1:%d %b. %Y}}}\n".format(startdate, enddate))
        else:
            file.write("\\newcommand{{\\thedate}}{{{0:%d %b. %Y} to {1:%d %b. %Y}}}\n".format(startdate, enddate))
        file.write("\\date{\\thedate}\n\n")
        file.write("\\maketitle\n\n")
        file.write("\\section{APS Journals}\n")
        for article in prarticles:
            file.write(article.latex(show_journal=True))
        file.write("\\clearpage\n")
        file.write("\\section{Nature}\n")
        for article in naturearticles:
            file.write(article.latex(show_journal=article.journal.lower() != "nature"))
        file.write("\\clearpage\n")
        file.write("\\section{Science}\n")
        for article in sciencearticles:
            file.write(article.latex(show_journal=article.journal.lower() != "science"))
        file.write("\\clearpage\n")
        file.write("\\section{arXiv}\n")
        for article in arxivarticles:
            file.write(article.latex()+"\n")
