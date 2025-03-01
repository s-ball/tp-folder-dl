#  SPDX-FileCopyrightText: 2025-present s-ball <s-ball@laposte.net>
#  #
#  SPDX-License-Identifier: MIT
"""
Tests for the command line parsing
"""
from unittest.mock import patch

import pytest

import tp_folder_dl
from tp_folder_dl.tp_folder_dl import parse


def test_param_ok():
    """Ensure that a single argument is correctly processed"""
    cf = parse(['foo'])
    assert cf.domain == 'foo'


def test_param_wrong(capfd):
    """Ensure that passing 2 arguments causes a program error"""
    with patch('argparse.ArgumentParser.exit') as ex:
        parse(['foo', 'bar'])
        ex.assert_called()
    assert 'usage:' in capfd.readouterr().err


@pytest.mark.parametrize('param', ['-v', '--version'])
def test_version(capfd, param):
    """Ensure that options -v or --version show the current program version"""
    with patch('argparse.ArgumentParser.exit') as ex:
        parse([param])
        ex.assert_called()
    assert tp_folder_dl.__version__ in capfd.readouterr().out
