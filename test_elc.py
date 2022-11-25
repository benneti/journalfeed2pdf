# run with pytest -q ./test_elc.py
import pytest

from src.journalfeed.LaTeX import *
from src.journalfeed.config import load_config
import src.journalfeed.arxiv as arxiv
import src.journalfeed.nature as nature
import src.journalfeed.science as science
import src.journalfeed.aps as aps
import datetime

def arxiv_summary(aid, el=True):
    return arxiv.get_articles(query="", id_list=aid, ensure_latex=el)[0].summary

# functions must start with test, class with Test to be detected
class TestDetectBrockenCurlyBrackets():
  def test_not_all_escaped(self):
      for aid in [ "2211.09329v1", "2106.00624v1" ]:
          assert arxiv_summary(aid) == 'Curly braces not balanced.'
  def test_problems_in_math(self):
      for aid in [ "2205.15927v1", "2206.03707v1" ]:
          assert arxiv_summary(aid) == 'Curly braces not balanced in inline math.'

class TestMathEnvironment():
    def test_escaped_dollar(self):
        assert arxiv_summary("2205.04441v1").count("\\$") == arxiv_summary("2205.04441v1", el=False).count("\\$")
    def test_unusual_bracket_placement(self):
        assert "{\\mathbb C}" in arxiv_summary("2204.13104v1")
        assert "${M}$" in arxiv_summary("2011.01389v1")
    def test_various_equations(self):
        assert "$T_{\\mathrm{N1}}$" in arxiv_summary("2012.05392v1")
        assert "$\\frac{J_z}{J_{\\perp}}=-\\frac{1}{2}$" in arxiv_summary("2012.05930v1")
        assert "\\cdot \\text" in arxiv_summary("2010.15264")
        assert "\\simeq 152" in arxiv_summary("2011.03015v1")
        assert "\\mathcal{PT}" in arxiv_summary("2011.02114v1")
        assert "$m\\Omega /\\hbar k_{\\ell}^2<1$" in arxiv_summary("2011.00478v1")
    def test_various_symbols(self):
        summary = arxiv_summary("2010.15589v1")
        for sym in [ "\\lambda=", "\\hbar \\omega", "\\mathbf{r}" ]:
            assert sym in summary
        assert "_{\\mathcal{L}}" in arxiv_summary("2011.07246v1")
    def test_double_exponentiation(self):
        # http://link.aps.org/doi/10.1103/PhysRevA.102.062805
        "^{{2}{1}}" in elc("""$6{s}^{2}^{1}$""")
    def test_html_escaping(self):
        s = """$\\text{spin}&gt;1/2$ quan..."""
        assert "$\\text{spin}>1/2$" in elc(s)
    def test_weird_math_nesting(self):
        assert "$\\text{\\ensuremath{\\sqrt{q}}}$" in arxiv_summary("2211.11266v1")
