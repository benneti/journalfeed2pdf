#!/usr/bin/env python3
import re  # used to better ensure compiling latex!
from bs4 import BeautifulSoup  # used to get rid of HTML stuff

# Here we can configure
# environmants for math
math_envs = ["equation", "align"]
math_matchers = ["(\\$)([^\\$]+)(\\$)", "(\\$\\$)([^\\$]+)(\\$\\$)",
                 "(\\\\\\[)((?:.(?!\\\\\\]))*.)(\\\\\\])", "(\\\\\\()((?:.(?!\\\\\\)))*.)(\\\\\\))",
                 "(\\\\begin\\{(?P<env>"+"|".join(math_envs)+")\\*?\\})(.+(?!(?P=env)))(\\\\end\\{(?P=env)\\*?\\})"]
math_regex = re.compile("("+"|".join(math_matchers)+")", flags=re.DOTALL)

# supports regexp (needs to be escaped accordingly)
# the general sub bevore is applied bevore \\ are stripped
general_sub_bevore = [('\\\\"o', "ö"),
                      ('\\\\"a', "ä"),
                      ('\\\\"u', "ü")]
# the general sub is applied last after \\ are stripped
general_sub = [("cite\\{([^}]+)\\}", "[\\1]"),  # citekeys are pointless as we do not have the bib file
               ("\\\\*mathbit", ""),  # we need the backslash, else we can be left with a backslash that destroys everything
               ("o", "o")]
# Add things that should have a backslash here, as we strip all backslashes outside math
# right now this does not support keeping the matches of groups
outside_math_sub = [("{\\\\deg}", "$^{\\\\circ}$"),
                          ("\\\\'", "\\\\'")]
# latex commands that do not make sense without the backslash (no regexp)
prepend_backslash = ["emph\\{", "textit\\{", "textbf\\{", "^", "_", "&" ,"$", "%"]
# ensure no unescaped %
for command in prepend_backslash:
    outside_math_sub.append(((re.compile("\\\\*"+re.escape(command))), "\\\\"+command))
# here we ensure no newlines and tabbing in math
inside_math_sub = [("\\\\\\\\", "\\\\ "),  # newline to space
                   ("([^\\\\])%", "\\1\\\\%"),  # escape %
                   ("([^\\\\])#", "\\1\\\\%"),  # escape #
                   ("\\&", ""),  # no amperes and
                   ("\n", " "),  # no newlines
                   ("\\\\left", ""),  # no left and rights, just to be on the save side
                   ("\\\\right", ""),
                   ("\\\\textit", ""),  # textit is useless in math mode
                   ("\\{\\\\bf\\s([^}]+)\\}", "\\\\mathbf{\\1}")]

# we strip backslashes from commands not in the whitelist to ensure we do not get problems with custom commands
# Mind that we only strip backslashes infront of a-z, A-Z, and 0-9
math_command_whitelist = [
    "alpha", "aleph", "beta", "chi", "delta", "partial", "epsilon", "varepsilon", "exists", "eta", "gamma", "kappa", "lambda", "mu", "nu", "nabla", "omega", "pi", "varpi", "psi", "varphi", "phi", "tau", "theta", "vartheta", "rho", "varrho", "sigma", "upsilon", "varsigma", "vee", "xi", "zeta",
    "ell",
    "ll", "leq", "le", "gg", "geq", "ge", "approx", "equiv", "simeq", "sim",
    "cdot", "cdots", "dots",
    "dag", "infty", "hbar",
    "Delta", "Gamma", "Omega", "Lambda", "Phi", "Pi", "Psi", "Sigma", "Theta", "Upsilon", "Xi", "Zeta",
    "Re", "Im", "Vert",
    "Leftrightarrow", "Leftarrow", "Rightarrow", "Longleftrightarrow", "Longleftarrow", "Longrightarrow", "wedge",
    "to", "leftrightarrow", "leftarrow", "rightarrow", "longleftrightarrow", "longleftarrow", "longrightarrow", "uparrow", "downarrow",
    "parallel", "perp", "mapsto", "longmapsto", "not", "prime",
    "binom", "sqrt", "overset", "int", "frac", "in",
    "exp", "ln", "log", "cos", "sin", "tan",
    "sum", "cup", "times", "prod", "otimes", "propto", "circ", "setminus", "forall", "emptyset", "wedge", "subset", "supset",
    "quad", "qquad", "hat", "langle", "rangle",
    # "bra", "ket", "norm", "abs", "braket", "comm", "acomm", "proj", "ev", "eval",  # these are actually not avaible
    "mathrm", "text", "mathbf", "mathbb", "mathcal", "overline"]

math_command_whitlist_regex = "("+"|".join(math_command_whitelist)+")"

math_env_whitelist = [ "cases", "matrix", "pmatrix", "array" ]


def find_all_math(s, math_regex=math_regex):
    """Search for all valid latex environments, returns a list of list [[whole match, begin, content, end],...]"""
    math_matches = math_regex.findall(s)
    math_matches = [[j for j in i if j != ""] for i in math_matches]
    for i in math_matches:
        if len(i) == 5:
            del i[2]
    return math_matches


def elc(s, general_sub=general_sub,
        outside_math_sub=outside_math_sub,
        inside_math_sub=inside_math_sub,
        math_command_whitelist=math_command_whitelist,
        math_env_whitelist=math_env_whitelist):
    """Ensure Latex compatibility of a string s"""
    # first use BeautifulSoup to get rid of html artefacts
    ret = BeautifulSoup(s, "html.parser").text.strip()

    ret = re.sub("\\$\\\\require\\{[^\\]\\}]+\\}\\$", "", ret)   # require is used in math by MATHJAX to load additional packages

    if (len(re.findall("\\{", ret)) != len(re.findall("\\}", ret))):
        return "Amount of curly braces not balanced."
    if (len(re.findall("\\\\\\{", ret)) != len(re.findall("\\\\\\}", ret))):
        return "Amount of curly braces not balanced."

    math_matches = find_all_math(s)
    for i, match in enumerate(math_matches):
        ret = ret.replace(match[0], "MATH{}MATH".format(i))
        for find, replace in inside_math_sub:
            match[2] = re.sub(find, replace, match[2])
        # try to clever strip "bad" backslashes:
        # first insert a tab if the command is directly followed by a \\ or a number
        match[2] = re.sub(math_command_whitlist_regex+"(\\\\|[0-9]|/)", "\\1 \\2", match[2])
        # after a command a (backslash or number or slash)
        # whitespace, super-, subscript, slash, a bracket or the end of the string are allowed
        match[2] = re.sub("\\\\"+math_command_whitlist_regex+"(\\s|\\^|_|\\{|\\}|\\(|\\)|\\[|\\]|=|\\Z)", "\\\\\\\\\\1\\2", match[2])
        regex = "(\\\\begin\\{(?P<env>"+"|".join(math_env_whitelist)+")\\*?\\})(.+(?!(?P=env)))(\\\\end\\{(?P=env)\\*?\\})"
        match[2] = re.sub(regex, "\\\\\\1\\3\\\\\\4", match[2])
        match[2] = re.sub("\\\\([a-zA-Z0-9])", "\\1", match[2])

    for i, finrep in enumerate(outside_math_sub):
        ret = re.sub(finrep[0], "OUTSIDE{}OUTSIDE".format(i), ret)

    for find, replace in general_sub_bevore:
        ret = re.sub(find, replace, ret)

    ret = ret.replace("\\", "")

    for i, finrep in enumerate(outside_math_sub):
        ret = re.sub("OUTSIDE{}OUTSIDE".format(i), finrep[1], ret)

    for i, match in enumerate(math_matches):
        ret = ret.replace("MATH{}MATH".format(i), "$"+match[2]+"$")

    for find, replace in general_sub:
        ret = re.sub(find, replace, ret)

    return ret.strip()