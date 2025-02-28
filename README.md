# tp-folder-dl

[![PyPI - Version](https://img.shields.io/pypi/v/tp-folder-dl.svg)](https://pypi.org/project/tp-folder-dl)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tp-folder-dl.svg)](https://pypi.org/project/tp-folder-dl)

-----

## Table of Content

<!-- TOC -->
  * [Goal](#goal)
  * [Status](#status)
  * [Installation](#installation)
    * [End user (with pip)](#end-user-with-pip)
    * [Developer](#developer)
  * [Usage](#usage)
  * [License](#license)
<!-- TOC -->

## Goal

This is a simple tool to make it easier for maintainers to retrieve PO files
produced by the [Translation Project](https://translationproject.org/).
It automatically retrieves any new file
meaning a file missing in the local folder or having a timestamp different
from the date on the TP site.

## Status

Despite a high coverage rate (close to 100%), this is only a Beta quality work,
because it lacks an acceptable documentation, and real world tests.

## Installation

### End user (with pip)

As the project is available on PyPI, you can just do:

```commandline
pip install tp-folder-dl
```

### Developer

You can manually download a source package from GitHub, or better use `git`:

```commandline
git clone https://github.com/s-ball/tp-folder-dl.git
```

The project contains extensive tests which can be triggered
(from the main project folder) with

```commandline
pytest tests
```
or (when using `hatch`)

```commandline
hatch test
```

## Usage

Just open a terminal window on your system and change the current directory to
the `po` folder of your project. Then just call the tool passing it your project name:

```commandline
tp-folder-dl domain
```

That should be enough to download any new or updated PO file.

Of course, `td-folder-dl` supports the common `-v` and `-h` flags with their
usual meaning.

## License

`tp-folder-dl` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
