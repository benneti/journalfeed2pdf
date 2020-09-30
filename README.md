# journalfeed2pdf
Small python script to create a latex with file of titles, authors, and abstracts of scientific papers of the last week (monthly journals are included in the first week of the month).

## Currently Supported websites:
- arXiv: via the API (Atom feeds)
  To not miss any articles on acident the script shows the articles from 8 days ago until yesterday from arxive.org.
- APS Journals: via the RSS feeds
- Nature Journals: Using the TOC of the current issue (research, articles and letters sections)

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
