#  SPDX-FileCopyrightText: 2025-present s-ball <s-ball@laposte.net>
#  #
#  SPDX-License-Identifier: MIT
import filecmp
import os
import urllib.request
from collections import namedtuple
from pathlib import Path
from tempfile import TemporaryDirectory
from time import mktime
from unittest.mock import patch, DEFAULT

import pytest

import tp_folder_dl.tp_folder_dl
from tp_folder_dl.tp_folder_dl import download_folder, MAIN_URL, handle_file, do_copy


@pytest.fixture
def url():
    return MAIN_URL.format(domain='i18nparse')


def test_load_dir(url):
    tab = download_folder(url)
    nb_de = 0
    for row in tab:
        assert row[0].endswith('.po')
        if 'de.po' == row[0]:
            nb_de += 1
    assert nb_de == 1


def test_handle_file_new(url):
    assert not os.path.exists('foo.po')
    with (patch('os.stat') as stat,
          patch('tp_folder_dl.tp_folder_dl.do_copy') as cp,
          patch('os.utime') as utime,
          patch('os.path.exists') as exist,
          ):
        exist.return_value = False
        handle_file('foo.po', '2022-02-03 15:24', url)
        stat.assert_not_called()
        cp.assert_called_once()


def test_handle_file_same_dat(url):
    assert not os.path.exists('foo.po')
    with (patch('os.stat') as stat,
          patch('tp_folder_dl.tp_folder_dl.do_copy') as cp,
          patch('os.utime') as utime,
          patch('os.path.exists') as exist,
          ):
        exist.return_value = True
        Stat = namedtuple('Stat', ['st_mtime'])
        str_dat = '2022-02-03 15:24'
        from time import mktime
        from time import strptime
        stat.return_value = Stat(mktime(strptime(str_dat, '%Y-%m-%d %H:%M')))
        handle_file('foo.po', str_dat, url)
        stat.assert_called_once()
        cp.assert_not_called()


def test_handle_file_wrong_dat(url):
    assert not os.path.exists('foo.po')
    stat_orig = os.stat
    with (patch('os.stat') as stat,
          patch('tp_folder_dl.tp_folder_dl.do_copy') as cp,
          patch('os.utime') as utime,
          patch('os.path.exists') as exist,
          ):
        exist.return_value = True
        Stat = namedtuple('Stat', ['st_mtime'])
        stat.return_value = Stat(12345678)
        handle_file('foo.po', '2022-02-03 15:24', url)
        stat.assert_called_once()
        cp.assert_called_once()

@pytest.fixture
def reception_dir():
    with TemporaryDirectory() as dir:
        old = os.getcwd()
        os.chdir(dir)
        yield dir
        os.chdir(old)


def test_cp(reception_dir):
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