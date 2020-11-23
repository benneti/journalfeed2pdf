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

from LaTeX import elc
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
        return ret+"\n"


journals = ["prl", "nature", "science"]


def match_journal(article, journals=journals):
    "Check wether article was published in one of the journals."
    return article.journal in journals


summary_res = ["SiC", "silicon[\\s-]*carbide",
               "spin[\\s-]*defect", "spin[\\s-]*center", "colou?r[\\s-]*center", "NV",
               "quantum[\\s-]*memory", "quantum[\\s-]*emitter", "quantum[\\s-]*internet",
               "Bose-Hubbard", "soliton",
               "group[\\s-]*theory"]

title_res = [*summary_res, "spin", "quantum", "symmetry"]


def match_title(article, res=title_res):
    "Check wether article was published in one of the journals."
    # TODO make case insensitive
    return not(all(re.search(r, article.title) is None for r in res))


def match_summary(article, res=summary_res):
    "Check wether article was published in one of the journals."
    # TODO make case insensitive
    return not(all(re.search(r, article.summary) is None for r in res))


# danger with unicode!!!! better to have all possible spellings...
# firstname ... lastName
authors = ["Guido Burkard",
           "Gary Wolfowicz",
           "David D. Awschalom",
           "Gali Ádám", "Adam Gali",
           "András Csóré", "Andras Csore",
           "Lukas Spindlberger",
           "Jeronimo R. Maze",
           "Michael Trupke",
           "Mikhail D. Lukin",
           "Viktor Ivády", "Viktor Ivady",
           "Caspar H. van der Waal",
           "Carmem Gilardoni",
           "Tom Bosma",
           "Marcus William Doherty",
           "Hugo Ribeiro",
           "Aashish A. Clerk"]
# We actually only use the first letter and the last name
_authors = []
for a in authors:
    _a = a.split(" ")
    _a = (a[0], _a[-1])
    _authors.append(_a)


def match_author(article, authors=_authors):
    "Check wether article was authored by one of the authors. Actually only checks wether the last name and the first letter of the first name are contained in any of the author strings."
    return any(any(a[0] in artauth and a[1] in artauth for a in authors)
               for artauth in article.authors)


def match(article, matcher=[match_author, match_title, match_summary, match_journal]):
    """
    Check wether article is matched by any of the filter rules.
    Default filters are
      - match_author
      - match_title
      - match_summary
      - match_journal
    """
    return any(m(article) for m in matcher)
