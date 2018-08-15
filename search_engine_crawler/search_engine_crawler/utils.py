import re


from settings import email_regex


def match_email(text):
    pattern = re.compile(email_regex)
    return pattern.finditer(text)
