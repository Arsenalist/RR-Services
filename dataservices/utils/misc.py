import base64
from urllib.parse import urlparse


def remove_attrs(soup):
    for tag in soup.findAll(True):
        tag.attrs = None
    return soup


def decorate_table_with_material_design(content):
    replacements = [
        {
        'target': 'class="suppress_glossary sortable stats_table"',
        'replacement': 'role="grid" class="mat-table"'
        },
        {
        'target': '<table ',
        'replacement': '<table role="grid" class="mat-table" '
        },
        {
        'target': '<td>',
        'replacement': '<td role="gridcell" class="mat-cell">'
        },
        {
        'target': '<th>',
        'replacement': '<th role="columnheader" class="mat-header-cell">'
        },
        {
        'target': '<tr>',
        'replacement': '<tr role="row" class="mat-row">'
        }
    ]
    for r in replacements:
        content = content.replace(r['target'], r['replacement'])
    return content


def findDomain(url):
    o = urlparse(url)
    return o.hostname


def sanitize_content(content):
    return content.replace("<amp-", "<").replace("</amp-", "</")


def encode_string(to_encode):
    return base64.b64encode(to_encode.encode()).decode('utf-8')


def decode_string(to_decode):
    return base64.b64decode(to_decode.encode('utf-8')).decode()


