#  SPDX-FileCopyrightText: 2025-present s-ball <s-ball@laposte.net>
#  #
#  SPDX-License-Identifier: MIT
"""
Test for the downloading part of the tp_folder_dl module
"""
import filecmp
import os
import typing
from pathlib import Path
from tempfile import TemporaryDirectory
from time import mktime
from unittest.mock import patch

import pytest

from tp_folder_dl.tp_folder_dl import MAIN_URL, do_copy, download_folder, handle_file


@pytest.fixture
def url() :
    """
    Return the full URL of the latest directory of i18nparse on the TP site

    :return: the full URL
    """
    return MAIN_URL.format(domain='i18nparse')


def test_load_dir(url) -> None:
    """
    Ensures that the i18nparse directory contains a de.po file

    :param url: Full URL of the i18nparse latest directory
    """
    tab = download_folder(url)
    nb_de = 0
    for row in tab:
        assert row[0].endswith('.po')
        if row[0] == 'de.po':
            nb_de += 1
    assert nb_de == 1


def test_handle_file_new(url: str) -> None:
    """
    Ensures that if a file is absent in the current directory, it is downloaded.

    :param url: Full URL of the i18nparse latest directory
    """
    assert not os.path.exists('foo.po')
    with (patch('os.stat') as stat,
          patch('tp_folder_dl.tp_folder_dl.do_copy') as cp,
          patch('os.path.exists') as exist,
          ):
        exist.return_value = False
        handle_file('foo.po', '2022-02-03 15:24', url)
        stat.assert_not_called()
        cp.assert_called_once()


class Stat(typing.NamedTuple):
    """
    Auxiliary class to help mocking the os.stat function
    """
    st_mtime: int


def test_handle_file_same_dat(url: str) -> None:
    """
    Ensure that if a local file has the expected timestamp, no download occurs

    :param url: Full URL of the i18nparse latest directory
    """
    assert not os.path.exists('foo.po')
    with (patch('os.stat') as stat,
          patch('tp_folder_dl.tp_folder_dl.do_copy') as cp,
          patch('os.path.exists') as exist,
          ):
        exist.return_value = True
        str_dat = '2022-02-03 15:24'
        from time import strptime
        stat.return_value = Stat(mktime(strptime(str_dat, '%Y-%m-%d %H:%M')))
        handle_file('foo.po', str_dat, url)
        stat.assert_called_once()
        cp.assert_not_called()


def test_handle_file_wrong_dat(url: str) -> None:
    """
    Ensure that if a local file has a wrong timestamp it is overwritten

    :param url: Full URL of the i18nparse latest directory
    """
    assert not os.path.exists('foo.po')
    with (patch('os.stat') as stat,
          patch('tp_folder_dl.tp_folder_dl.do_copy') as cp,
          patch('os.path.exists') as exist,
          ):
        exist.return_value = True
        stat.return_value = Stat(1234567890)
        handle_file('foo.po', '2022-02-03 15:24', url)
        stat.assert_called_once()
        cp.assert_called_once()

@pytest.fixture
def reception_dir():
    """
    Pytest fixture that returns a temporary directory

    It first changes the current directory to that temporary one,
    and yield its name.

    After the test ends, it restores the previous current directory
    """
    with TemporaryDirectory() as folder:
        old = os.getcwd()
        os.chdir(folder)
        yield folder
        os.chdir(old)


@pytest.mark.usefixtures('reception_dir')
def test_cp() -> None:
    """
    Ensures that do_copy actually copies a file and sets its mtime
    """
    data_path = Path(__file__).parent / 'data' / 'foo.po'
    assert data_path.exists()
    assert not os.path.exists('foo.po')
    with patch('urllib.request.urlopen') as op, open(data_path, 'rb') as fd:
        op.return_value = fd
        do_copy('foo.po', 1234567890, 'bar')
        op.assert_called_once_with('bar/foo.po')
    assert os.path.exists('foo.po')
    assert filecmp.cmp('foo.po', data_path)
    assert os.stat('foo.po').st_mtime == 1234567890
