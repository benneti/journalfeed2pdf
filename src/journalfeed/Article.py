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

from .LaTeX import elc
import re

class Article:
    """
    Container for an article (title, url, date, authors, summary, journal)
    """
    def __init__(self, title, url, date, authors, summary, journal, ensure_latex=True):
        def _elc(s):
            if ensure_latex:
                return elc(s)
            else:
                return s
        self.title = _elc(title)
        self.url = url
        self.date = date
        self.authors = [_elc(a).replace("}", "").replace("{", "") for a in authors]
        self.summary = _elc(summary)
        self.journal = _elc(journal)

    def author_string(self, max_authors=3):
        if max_authors < 2:
            raise ValueError("max_authors needs to be larger than 1.")
        authors = self.authors
        if len(authors) == 0:
            return "no authors found"
        elif len(authors) == 1:
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
        return ret+"\n"


    def match_journal(self, journals):
        "Check wether article was published in one of the journals."
        return self.journal in journals

    def match_title(self, res):
        "Check wether article was published in one of the journals (case insensitive)."
        return not(all(re.search(r, self.title, re.IGNORECASE) is None for r in res))

    def match_summary(self, res):
        "Check wether article was published in one of the journals. (case insensitive)"
        return not(all(re.search(r, self.summary, re.IGNORECASE) is None for r in res))


    def match_authors(self, authors):
        "Check wether article was authored by one of the authors. Actually only checks wether the last name and the first letter of the first name are contained in any of the author strings."
        return any(any(a[0][0] in artauth and a[1] in artauth for a in authors)
                   for artauth in self.authors)


    def match(self, journals, authors, title_res, summary_res):
        """
        Check whether article is matched by any of the filter rules.
        Default filters are
        - match_authors
        - match_title
        - match_summary
        - match_journal
        """
        return self.match_journal(journals) or self.match_authors(authors) or self.match_title(title_res) or self.match_summary(summary_res)
