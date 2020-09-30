# journalfeed2pdf
Small python script to create a latex with file of titles, authors, and abstracts of scientific papers of the last week (monthly journals are included in the first week of the month).

## Currently Supported websites:
- arXiv: via their api (Atom feeds)
- APS Journals: via their RSS feeds
- Nature Journals: Using the TOC of the current issue (articles and letters)

## Requirements:
- Python 3, including
  - feedparser
  - requests
  - datetime
  - re
  - bs4 (BeautifulSoup)
- Latex

## Usage
simply run "bash journalfeed2pdf.sh"

## TODO
- Keyword filter
- Author filter
- First show "filtered results" than rest in PDF
- Journals to add:
  - Maybe switch APS to bs4
  - Maybe switch from arXiv API to https://github.com/Mahdisadjadi/arxivscraper
