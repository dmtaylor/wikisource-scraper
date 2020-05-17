#!/usr/bin/env python3

import sys
import re
import logging
import requests
import pdfkit
from bs4 import BeautifulSoup, UnicodeDammit

logLevel = logging.INFO

log = logging.getLogger('wikisource-scraper')
log.setLevel(logLevel)
ch = logging.StreamHandler()
ch.setLevel(logLevel)
ch.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
log.addHandler(ch)

wikisource_url_rex = re.compile(r'^(?:https?://)?[a-z]{2}\.wikisource\.org/wiki/(.*)$')

def get_filename_base(url: str) -> str:
    return url.strip().replace('/','-')

def convert_from_url(url: str):
    match = wikisource_url_rex.match(url)
    if not match :
        log.error("Failed to validate url: " + url)
        return None
    res = requests.get(url)
    try:
        res.raise_for_status()
    except HTTPError as exc:
        log.error("Failed to get " + url + ": " + exc)
        res.close()
        return None
    
    document = BeautifulSoup(res.text, features='lxml')
    text_area = document.body.find('div', id='mw-content-text')
    output_text = text_area.select('div p')
    text = '''
    <head>
        <meta charset="utf-8">
    </head>
    <body>
    '''
    for p in output_text :
        text += str(p)
    text += '</body>'

    log.debug("doc = " + text)

    filename_base = match.group(1).strip().replace('/', '-')
    filename = filename_base + ".pdf"

    options = {
            'page-size': 'Letter',
            'encoding': 'UTF-8',
            'title': filename_base,
            'margin-top': '1in',
            'margin-bottom': '1in',
            'margin-left': '1in',
            'margin-right': '1in',
            'disable-external-links': '',
            'disable-javascript': '',
            'minimum-font-size': '12'
            }

    pdfkit.from_string(text, filename, options=options)

    res.close()
    return filename

if __name__ == '__main__':
    urls = sys.argv[1:]
    for url in urls:
        log.info("Starting conversion for: " + url)
        result = convert_from_url(url)
        if result:
            log.info("Converted " + url + " to pdf file: " + result)
        else:
            log.warning("Conversion failed for " + url)
    sys.exit(0)
