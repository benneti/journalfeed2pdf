# journalfeed2pdf
Small python script to create a latex compilable file of titles, authors, and abstracts of scientific papers of the last week.

## Currently Supported websites:
- arXiv: via their api (Atom feeds)
- APS Journals: via their RSS feeds
- Nature: Using the TOC fo the current issue (only Research articles will be included)

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
