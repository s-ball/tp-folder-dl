#  SPDX-FileCopyrightText: 2025-present s-ball <s-ball@laposte.net>
#  #
#  SPDX-License-Identifier: MIT
""" Tests for the high level command processing """
from unittest.mock import patch

from tp_folder_dl.tp_folder_dl import MAIN_URL, do_work


def test_main() -> None:
    """
    Ensures that calling the module ends in executing the do_work function
    """
    with patch('tp_folder_dl.tp_folder_dl.do_work') as dw:
        # noinspection PyUnresolvedReferences
        import tp_folder_dl.__main__
        dw.assert_called_once()


def test_run() -> None:
    """
    Ensure that do_work correctly tries to download the relevant files
    """
    with patch('tp_folder_dl.tp_folder_dl.download_folder') as df, \
        patch('tp_folder_dl.tp_folder_dl.handle_file') as hf:
        df.return_value = [('foo.po', 1234567890)]
        do_work(['bar'])
        url = f'{MAIN_URL.format(domain="bar")}'
        hf.assert_called_once_with('foo.po', 1234567890, url)
