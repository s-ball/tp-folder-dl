#  SPDX-FileCopyrightText: 2025-present s-ball <s-ball@laposte.net>
#  #
#  SPDX-License-Identifier: MIT
import argparse
import gettext
import os
import sys
import urllib.request
from collections.abc import Generator
from shutil import copyfileobj
from time import mktime, strptime

from bs4 import BeautifulSoup

from . import __version__

MAIN_URL = 'https://translationproject.org/latest/{domain}'
_ = gettext.gettext


def download_folder(url: str) -> Generator[tuple[str, str], None, None]:
    """
    Download the HTML folder list and generate (name, dat) tuples.

    The URL is expected to return the content of a directory in an HTML TABLE,
    following the contents of latest/domain on the TP site.

    The function then returns a generator of 2-tuples, the first element
    being the file name, the second one being the timestamp in yyyy-mm-dd HH24:MM.

    :param url: The full URL of the relevant folder
    :return: A generator of (name: str, dat: int) tuples
    """
    print(f'Downloading everything from {url}')
    resp = urllib.request.urlopen(url)
    soup = BeautifulSoup(resp, features='html.parser')
    # extract the table containing the directory listing
    tab = soup.table
    for row in tab.find_all('tr'):
        # only process the relevant rows
        if '.po' in row.text:
            a = row.a
            href = a['href']
            str_dat = a.parent.next_sibling.text.strip()
            yield href, str_dat
    return tab


def handle_file(href: str, str_dat: str, url: str) -> None:
    """
    Process a row from the TP directory.

    The file is downloaded if it is new (not present in the local folder)
    or if it has a different timestamp

    :param href: File name
    :param str_dat: Timestamp in yyyy/mm/dd HH24:MI format
    :param url: Full URL of the remote directory
    """
    dat = int(mktime(strptime(str_dat, '%Y-%m-%d %H:%M')))
    if os.path.exists(href):
        cur_time = os.stat(href).st_mtime
        if cur_time == dat:
            print(f'{href} already ok')
            return
    print(f'Processing {href} - {str_dat}')
    do_copy(href, dat, url)


def do_copy(href: str, dat: int, url: str) -> None:
    """
    Actually download a PO file and set its timestamp to match the remote one.

    :param href: File name
    :param dat: Timestamp in seconds from 1970-01-01
    :param url: Full URL of the remote domain directory
    """
    with open(href, 'wb') as fd_out, urllib.request.urlopen(f'{url}/{href}') as fd_in:
        # noinspection PyTypeChecker
        copyfileobj(fd_in, fd_out)
    os.utime(href, (dat, dat))


def do_work(args: list[str]) -> None:
    """
    Do the processing of the CLI command.

    Parse the command, and if appropriate download the relevant files

    :param args: the command arguments (past the command name itself)
    """
    # -h and -v arguments would immediately stop the program
    conf = parse(args)
    url = MAIN_URL.format(domain=conf.domain)
    for href, dat in download_folder(url):
        handle_file(href, dat, url)


def parse(args: list[str]) -> argparse.Namespace:
    """
    Parse the command line and process the special options -h and -v

    :param args: the arguments past the command name itself
    :return: A populated namespace
    """
    parser = argparse.ArgumentParser(
        description=_('Download PO files for a domain'))
    parser.add_argument('domain', action='store',
                        help=_('domain of interest'))
    parser.add_argument('-v', '--version', action='version',
                        version=__version__)
    return parser.parse_args(args)


def run() ->None:
    """
    Pass the command line arguments to do_work

    :return:
    """
    do_work(sys.argv[1:])

