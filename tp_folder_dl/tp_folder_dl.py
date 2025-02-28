#  SPDX-FileCopyrightText: 2025-present s-ball <s-ball@laposte.net>
#  #
#  SPDX-License-Identifier: MIT
import argparse
import gettext
import os
import sys
import urllib.request
from shutil import copyfileobj
from time import mktime, strptime

from bs4 import BeautifulSoup

from . import __version__

MAIN_URL = 'https://translationproject.org/latest/{domain}'
_ = gettext.gettext


def download_folder(url):
    print(f'Downloading everything from {url}')
    resp = urllib.request.urlopen(url)
    soup = BeautifulSoup(resp)
    tab = soup.table
    for row in tab.find_all('tr'):
        if '.po' in row.text:
            a = row.a
            href = a['href']
            str_dat = a.parent.next_sibling.text.strip()
            yield href, str_dat
    return tab


def handle_file(href, str_dat, url):
    dat = mktime(strptime(str_dat, '%Y-%m-%d %H:%M'))
    if os.path.exists(href):
        cur_time = os.stat(href).st_mtime
        if cur_time == dat:
            print(f'{href} already ok')
            return
    print(f'Processing {href} - {str_dat}')
    do_copy(href, dat, url)


def do_copy(href, dat, url):
    with open(href, 'wb') as fd_out, urllib.request.urlopen(f'{url}/{href}') as fd_in:
        # noinspection PyTypeChecker
        copyfileobj(fd_in, fd_out)
    os.utime(href, (dat, dat))


def do_work(args):
    conf = parse(args)
    url = MAIN_URL.format(domain=conf.domain)
    for href, dat in download_folder(url):
        handle_file(href, dat, url)


def parse(args):
    parser = argparse.ArgumentParser(
        description=_('Download PO files for a domain'))
    parser.add_argument('domain', action='store',
                        help=_('domain of interest'))
    parser.add_argument('-v', '--version', action='version',
                        version=__version__)
    return parser.parse_args(args)


def run():
    do_work(sys.argv[1:])

