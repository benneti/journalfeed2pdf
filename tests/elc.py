import pytest
# run with pytest -q ./tests/elc.py from project dir
# NOTE test functions must start with test, class with Test to be detected

# incase the module is not in the loadpath try to load it
try:
    import sys
    sys.path.append("..")
    from src import *
except:
    print("Could not load local module, continuing")

from journalfeed.LaTeX import *
from journalfeed.config import load_config
import journalfeed.arxiv as arxiv
import journalfeed.nature as nature
import journalfeed.science as science
import journalfeed.aps as aps
import datetime

def arxiv_article(aid, el=True):
    return arxiv.get_articles(query="", id_list=aid, ensure_latex=el)[0]
def arxiv_summary(aid, el=True):
    return arxiv_article(aid, el).summary

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
    def test_multiple_equation_envs(self):
        summary = arxiv_summary("2412.05428v1")
        assert "$tag{A2}" in summary and ", $ po" in summary and "ate $R" in summary
    def test_unusual_bracket_placement(self):
        assert "{\\mathbb C}" in arxiv_summary("2204.13104v1")
        assert "${M}$" in arxiv_summary("2011.01389v1")
    def test_various_equations(self):
        assert "$T_{\\mathrm{N1}}$" in arxiv_summary("2012.05392v1")
        assert "$\\frac{J_z}{J_{\\perp}}=-\\frac{1}{2}$" in arxiv_summary("2012.05930v1")
        assert "\\cdot \\text" in arxiv_summary("2010.15264")
        assert "\\simeq 152" in arxiv_summary("2011.03015v1")
        assert "\\mathcal{PT}" in arxiv_summary("2011.02114v1")
        assert "$mΩ/\\hbar k_{\\ell}^2<1$" in arxiv_summary("2011.00478v1")
    def test_various_symbols(self):
        summary = arxiv_summary("2010.15589v1")
        for sym in [ "λ=", "hbarω", "\\mathbf{r}" ]:
            assert sym in summary
        assert "_{\\mathcal{L}}" in arxiv_summary("2011.07246v1")
    def test_double_exponentiation(self):
        assert "^{{2}{1}}" in elc("""$6{s}^{2}^{1}$""")
    def test_html_escaping(self):
        s = """$\\text{spin}&gt;1/2$ quan..."""
        assert "$\\text{spin}>1/2$" in elc(s)
    def test_weird_math_nesting(self):
        assert "$\\text{\\ensuremath{\\sqrt{q}}}$" in arxiv_summary("2211.11266v1")
    def test_expectation_value_that_could_be_a_html_tag(self):
        assert not "$$" in arxiv_summary("2303.14053v1")
    def test_greek_letter_in_index(self):
        assert "Λ_β" in arxiv_summary("2304.14099v1")
    def test_sub_or_super_script_ending_math(self):
        assert "\\^$" in arxiv_summary("2304.12924v1")
    def test_already_escaped_sub_or_super_script_ending_math(self):
        assert "$\\_$" in arxiv_summary("2306.06943v1")
    def test_stackrel_superscript_to_hat(self):
        s = """intensive quantity ($\\stackrel{^}{p}$) that..."""
        assert "$\\hat{p}$" in elc(s)
    def test_exponend_braceless_frac(self):
        summary = arxiv_summary("2409.02121v1")
        assert "^{\\frac 12}" in summary
    def test_very_strange_exponents(self):
        summary = arxiv_summary("2409.15379v1")
        assert "\\mathcal{U}^{\\mathcal{H}} \\mathcal{U} neq \\mathcal{U} \\mathcal{U} ^{\\mathcal{H}}" in summary


class TestOutsideMathEnvironment():
    def test_hat_outside_math(self):
        assert "\\textasciicircum" in elc('chirality $\\stackrel{^}{\\mathbf{n}}⋅(\\…')

class TestAuthors():
    def test_name_with_tex_command(self):
        assert "Si{\\textasciicircum}an" in  arxiv_article("2503.18833v1").authors[-1]
