#!/usr/bin/env python3
import json # config file
from os import getenv
from pathlib import Path
from xdg_base_dirs import xdg_config_home


def load_config_file(name):
    configPath = Path(xdg_config_home()) / "journalfeed"
    configFile = configPath / name
    configDefault = Path(__file__).parent / name
    with configDefault.open("r") as f:
        config = json.load(f)
    # if local config exists ignore global config
    if configFile.exists():
        print(f"Loading local config \"{name}\".")
        with configFile.open("r") as f:
            config = json.load(f)
    return config


def load_filter():
    config = load_config_file("filter.json")

    # parse the config
    journals = []
    for j in config["journals"]:
        journals.append(j.lower())
    # We actually only use the first and the last names
    # danger with unicode!!!! better to have all possible spellings...
    authors = []
    for a in config["authors"]:
        a = a.split(" ")
        a = (a[0], a[-1])
        authors.append(a)
    title_res = config["title"]
    summary_res = config["summary"]
    title_res += summary_res

    return [journals, authors, title_res, summary_res]


def load_sources():
    config = load_config_file("sources.json")

    arxiv_query = config["arxiv_query"]
    aps_journals = config["aps_journals"]
    nature_weekly = config["nature_weekly"]
    nature_monthly = config["nature_monthly"]
    science = config["science"]

    return {
        "arxiv_query": arxiv_query,
        "aps_journals": aps_journals,
        "nature": {
            "weekly": nature_weekly,
            "monthly": nature_monthly
        },
        "science": science
    }


def load_config():
    config = load_config_file("config.json")
    latexclass = config["class"]
    options = config["class_options"]
    preamble = f"\\documentclass[{options}]{{{latexclass}}}"
    for line in config["preamble"]:
        preamble += "\n" + line
    return [ load_sources(), load_filter(), preamble ]

