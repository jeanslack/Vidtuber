# -*- coding: UTF-8 -*-
"""
Name: utils.py
Porpose: It groups useful functions that are called several times
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: March.17.2023
Code checker: flake8, pylint .

This file is part of Vidtuber.

   Vidtuber is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   Vidtuber is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with Vidtuber.  If not, see <http://www.gnu.org/licenses/>.
"""
import subprocess
import platform
import shutil
import os
import glob
import math


class Popen(subprocess.Popen):
    """
    Inherit subprocess.Popen class to set _startupinfo.
    This avoids displaying a console window on MS-Windows
    using GUI's .

    NOTE MS Windows:

    subprocess.STARTUPINFO()

    https://stackoverflow.com/questions/1813872/running-
    a-process-in-pythonw-with-popen-without-a-console?lq=1>
    """
    if platform.system() == 'Windows':
        _startupinfo = subprocess.STARTUPINFO()
        _startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    else:
        _startupinfo = None

    def __init__(self, *args, **kwargs):
        """Constructor
        """
        super().__init__(*args, **kwargs, startupinfo=self._startupinfo)

    # def communicate_or_kill(self, *args, **kwargs):
        # return process_communicate_or_kill(self, *args, **kwargs)
# ------------------------------------------------------------------------


def open_default_application(pathname):
    """
    Given a path to a specific file or directory, opens the
    operating system's default application according to the
    user-set file type association. Currently supported platforms
    are Windows, Darwin and Linux. Note that Linux uses xdg-open
    which should also be used by other OSes that may support
    it, eg freebsd.

    Return error if any error, None otherwise.
    """
    if platform.system() == 'Windows':
        try:
            os.startfile(os.path.realpath(pathname))
        except FileNotFoundError as error:
            return str(error)

        return None

    if platform.system() == "Darwin":
        cmd = ['open', pathname]
    else:  # Linux, FreeBSD or any supported
        cmd = ['xdg-open', pathname]
    try:
        subprocess.run(cmd, check=True, shell=False, encoding='utf8')
    except subprocess.CalledProcessError as error:
        return str(error)

    return None
# ------------------------------------------------------------------------


def format_bytes(num):
    """
    Given a float number (bytes) returns size output
    strings human readable, e.g.
    out = format_bytes(9909043.20)
    It return a string digit with metric suffix

    """
    unit = ["B", "KiB", "MiB", "GiB", "TiB",
            "PiB", "EiB", "ZiB", "YiB"]
    const = 1024.0
    if num == 0.0:  # if 0.0 or 0 raise ValueError: math domain error
        exponent = 0
    else:
        exponent = int(math.log(num, const))  # get unit index

    suffix = unit[exponent]  # unit index
    output_value = num / (const ** exponent)

    # return "%.2f%s" % (output_value, suffix)
    return f"{output_value:.2f}{suffix}"
# ------------------------------------------------------------------------


def to_bytes(string, key='ydl'):
    """
    Convert given size string to bytes, e.g.
    out = to_bytes('9.45MiB')
    It return a number 'float' object.
    Updated on March 23 2022:
        added key default arg.

    """
    value = 0.0
    if key == 'ydl':
        unit = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]

    elif key == 'ffmpeg':
        unit = ["byte", "Kibyte", "Mibyte", "Gibyte", "Tibyte",
                "Pibyte", "Eibyte", "Zibyte", "Yibyte"]

    const = 1024.0

    for index, metric in enumerate(reversed(unit)):
        if metric in string:
            value = float(string.split(metric)[0])
            exponent = index * (-1) + (len(unit) - 1)
            break

    return round(value * (const ** exponent), 2)
# ------------------------------------------------------------------------


def timehuman(seconds):
    """
    This is the old implementation to converting seconds to
    time format. Accept integear only e.g timehuman(2300).
    Useb by youtube-dl downloader, returns a string object
    in time format i.e '00:38:20' .

    """
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    # return "%02d:%02d:%02d" % (hours, minutes, seconds)
    return f"{hours:02}:{minutes:02}:{seconds:02}"
# ------------------------------------------------------------------------


def copy_restore(src, dest):
    """
    copy a specific file from src to dest. If dest exists,
    it will be overwritten with src without confirmation.
    """
    try:
        shutil.copyfile(str(src), str(dest))
    except FileNotFoundError as err:
        # file src not exists
        return err
    except SameFileError as err:
        # src and dest are the same file and same dir.
        return err
    except OSError as err:
        # The dest location must be writable
        return err

    return None
# ------------------------------------------------------------------#


def copydir_recursively(source, destination, extraname=None):
    """
    recursively copies an entire directory tree rooted at source.
    If you do not provide the extraname argument, the destination
    will have the same name as the source, otherwise extraname is
    assumed as the final name.

    """
    if extraname:
        dest = os.path.join(destination, extraname)
    else:
        dest = os.path.join(destination, os.path.basename(source))
    try:
        shutil.copytree(str(source), str(dest))

    except FileExistsError as err:  # dest dir already exists
        return err
    except FileNotFoundError as err:  # source dir not exists
        return err

    return None
# ------------------------------------------------------------------#


def copy_on(ext, source, destination):
    """
    Given a source (dirname), use glob for a given file extension (ext)
    and iterate to move files to another directory (destination).
    Returns None on success, otherwise returns the error.

    ARGUMENTS:
    ext: files extension without dot
    source: path to the source directory
    destination: path to the destination directory
    """
    files = glob.glob(f"{source}/*.{ext}")
    if not files:
        return f'Error: No such file with ".{ext}" format found'
    for fln in files:
        try:
            shutil.copy(fln, f'{destination}')
        except IOError as error:
            # problems with permissions
            return error
    return None
# ------------------------------------------------------------------#


def del_filecontents(filename):
    """
    Delete the contents of the file if it is not empty.
    Please be careful as it assumes the file exists.

    HOW to USE:

        if fileExists:
            try:
                del_filecontents(logfile)
            except Exception as err:
                print("Unexpected error while deleting "
                      "file contents:\n\n{0}").format(err)

    MODE EXAMPLE SCHEME:

    |          Mode          |  r   |  r+  |  w   |  w+  |  a   |  a+  |
    | :--------------------: | :--: | :--: | :--: | :--: | :--: | :--: |
    |          Read          |  +   |  +   |      |  +   |      |  +   |
    |         Write          |      |  +   |  +   |  +   |  +   |  +   |
    |         Create         |      |      |  +   |  +   |  +   |  +   |
    |         Cover          |      |      |  +   |  +   |      |      |
    | Point in the beginning |  +   |  +   |  +   |  +   |      |      |
    |    Point in the end    |      |      |      |      |  +   |  +   |

    """
    with open(filename, "r+", encoding='utf8') as fname:
        content = fname.read()
        if content:
            fname.flush()  # clear previous content readed
            fname.seek(0)  # it places the file pointer to position 0
            fname.write("")
            fname.truncate()  # truncates the file to the current file point.
# ------------------------------------------------------------------#


def detect_binaries(executable, additionaldir=None):
    """
    <https://stackoverflow.com/questions/11210104/check-if
    -a-program-exists-from-a-python-script>

    Given an executable name (binary), find it on the O.S.
    via which function, if not found try to find it on the
    optional `additionaldir` .

        If both failed, return ('not installed', None)
        If found on the O.S., return (None, executable)
        If found on the additionaldir, return ('provided', executable).

    executable = name of executable without extension
    additionaldir = additional dirname to perform search

    """
    local = False

    if shutil.which(executable):
        installed = True

    else:
        if platform == 'Windows':
            installed = False

        elif platform == 'Darwin':

            if os.path.isfile(f"/usr/local/bin/{executable}"):
                local = True
                installed = True
            else:
                local = False
                installed = False

        else:  # Linux, FreeBSD, etc.
            installed = False

    if not installed:

        if additionaldir:  # check onto additionaldir

            if not os.path.isfile(os.path.join(f"{additionaldir}", "bin",
                                               f"{executable}")):
                provided = False

            else:
                provided = True

            if not provided:
                return 'not installed', None
            # only if ffmpeg is not installed, offer it if found
            return 'provided', os.path.join(f"{additionaldir}",
                                            "bin", f"{executable}")
        return 'not installed', None

    if local:  # only for MacOs
        return None, f"/usr/local/bin/{executable}"
    return None, shutil.which(executable)
