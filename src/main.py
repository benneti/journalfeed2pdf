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

import sys
import datetime
from journalfeed.Article import Article
from journalfeed.config import load_config
import journalfeed.arxiv as arxiv
import journalfeed.nature as nature
import journalfeed.science as science
import journalfeed.aps as aps

# see arxiv API for options, here we search for cond-mat and quant-ph articles
# (logical +OR+)
# we get the arxiv articles for one week
# (starting 8 days ago..., such that we do not miss articles due to not all articles published today)


if __name__ == "__main__":
    sources, _filter, preamble = load_config()
    standalone = True

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

    prarticles = aps.get_articles()

    # if we are in the first week of the month
    # else only include the weekly journal(s)
    naturearticles = nature.get_articles(journals=sources["nature"]["weekly"],
                                         enddate=enddate, startdate=startdate)
    sciencearticles = science.get_articles(journals=sources["science"]["weekly"],
                                           enddate=enddate, startdate=startdate)
    if enddate.day <= 7:
        # include the monthly journal(s) of nature and science families
        # TODO startdate should then be the beginning of last month!
        _start = datetime.date(startdate.year, startdate.month, 1)
        naturearticles += nature.get_articles(journals=sources["nature"]["monthly"],
                                              enddate=enddate, startdate=_start)
        sciencearticles += science.get_articles(journals=sources["science"]["monthly"],
                                                enddate=enddate, startdate=_start)

    arxivarticles = arxiv.get_articles(query=sources["arxiv_query"])


    with open(fname, "w") as file:
        if standalone:
            file.write(preamble)
            file.write("\\begin{document}")
        file.write("\\title{In the Journals}\n")
        if startdate.month == enddate.month:
            file.write("\\newcommand{{\\thedate}}{{{0:%d} to {1:%d %b. %Y}}}\n".format(startdate, enddate))
        elif startdate.year == enddate.year:
            file.write("\\newcommand{{\\thedate}}{{{0:%d %b.} to {1:%d %b. %Y}}}\n".format(startdate, enddate))
        else:
            file.write("\\newcommand{{\\thedate}}{{{0:%d %b. %Y} to {1:%d %b. %Y}}}\n".format(startdate, enddate))
        file.write("\\date{\\thedate}\n\n")
        file.write("\\maketitle\n\n")

        unmatchedarticles = []

        file.write("\\section{APS Journals}\n")
        for article in prarticles:
            if article.match(*_filter):
                file.write(article.latex(show_journal=True))
            else:
                unmatchedarticles.append(article)
        file.write("\\clearpage\n")
        file.write("\\section{Nature}\n")
        for article in naturearticles:
            if article.match(*_filter):
                file.write(article.latex(show_journal=article.journal.lower() != "nature"))
            else:
                unmatchedarticles.append(article)
        file.write("\\clearpage\n")
        file.write("\\section{Science}\n")
        for article in sciencearticles:
            if article.match(*_filter):
                file.write(article.latex(show_journal=article.journal.lower() != "science"))
            else:
                unmatchedarticles.append(article)
        file.write("\\clearpage\n")
        file.write("\\section{arXiv}\n")
        for article in arxivarticles:
            if article.match(*_filter):
                file.write(article.latex())
            else:
                unmatchedarticles.append(article)
        file.write("\\clearpage\n")
        file.write("\\section{Unmatched Articles}\n")
        for article in unmatchedarticles:
            file.write(article.latex(show_journal=True))
        if standalone:
            file.write("\\end{document}")
