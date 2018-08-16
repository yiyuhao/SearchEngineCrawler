import re
from html.parser import HTMLParser
from lxml.html.clean import Cleaner

from settings import email_regex

cleaner = Cleaner()
cleaner.javascript = True
cleaner.style = True


class HTMLStripper(HTMLParser):

    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d.strip())

    def get_data(self):
        return '***'.join(self.fed)


def strip_tags(html_text):
    # remove javascript code
    cleaned_text = cleaner.clean_html(html_text)
    s = HTMLStripper()
    s.feed(cleaned_text)
    return s.get_data()


def match_email(text):
    pattern = re.compile(email_regex)
    return pattern.finditer(text)
