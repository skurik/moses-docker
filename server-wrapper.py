#!/usr/bin/env python3

import re
import xmlrpc
from bottle import route, run, post, request, static_file, response, template


ALIGN_RE = re.compile(r'\|\d+-\d+\|')
BAD_DELIMITERS = re.compile(r'[|_]+')
INNER_URL = "http://localhost:8080/RPC2"

proxy = xmlrpc.client.ServerProxy(INNER_URL)


def unmangle(moses_output):
    tokens = moses_output.strip().split()
    result = []
    for token in tokens:
        # ignore the alignment data
        if not ALIGN_RE.match(token):
            clean_token = token.split('|')[0]
            # This will pass already Roman strings through without error
            # result.append(transliterate.translit(clean_token, 'ru', reversed=True))
            result.append(clean_token)
    return ' '.join(result)


# Accept text POST data and send it through xml rpc
# to the moses service
@post('/')
def translate():
    # TODO get encoding and possibly mime type
    encoding = 'UTF-8'
    text = request.body.read().decode(encoding, 'replace')

    # https://www.mail-archive.com/moses-support@mit.edu/msg14325.html
    # Moses doesn't like square brackets
    text1 = text.replace('[', '(').replace(']', ')')

    # «Номер 44» needs to be spaced out
    text1 = text1.replace('«', '« ').replace('»', ' »')

    # Moses doesn't like pipes & possibly underscores
    text1 = BAD_DELIMITERS.sub('*', text1)

    params = {"text": text1,
              "align": "true",
              "report-all-factors": "true"}

    result = unmangle(proxy.translate(params)['text'])

    return result


run(host='localhost', port=8081, debug=True)
