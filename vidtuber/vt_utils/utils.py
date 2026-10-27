# -*- coding: UTF-8 -*-
"""
Name: utils.py
Purpose: It groups useful functions that are called several times
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Feb.05.2024
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
import sys
import subprocess
import shutil
import os
import math


class Popen(subprocess.Popen):
    """
    Inherit subprocess.Popen class to set startupinfo.
    This avoids displaying a console window on MS-Windows
    using GUI's.

    NOTE MS Windows:

    subprocess.STARTUPINFO()

    https://stackoverflow.com/questions/1813872/running-
    a-process-in-pythonw-with-popen-without-a-console?lq=1>

    """
    def __init__(self, *args, **kwargs):
        """
        On MSWindows, retrieves the existing startupinfo or creates
        a new one if it is missing.
        """
        if sys.platform == 'win32':
            startupinfo = kwargs.get('startupinfo')
            if startupinfo is None:
                startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kwargs['startupinfo'] = startupinfo

        super().__init__(*args, **kwargs)
# ------------------------------------------------------------------------


def open_default_application(pathname):
    """
    Given a path to a specific file or directory, opens the
    operating system's default application according to the
    user-set file type association. Currently supported platforms
    are Windows, Darwin and Linux. Note that Linux uses xdg-open
    which should be work on freebsd (?).

    Return error string if any error occurs, None otherwise.
    """
    # Normalizzazione del percorso per garantire la massima compatibilità
    real_path = os.path.realpath(pathname)

    if sys.platform == 'win32':
        try:
            os.startfile(real_path)
            return None
        # OSError (covers also FileNotFoundError, PermissionError, etc.)
        except OSError as error:
            return str(error)

    if sys.platform == 'darwin':
        cmd = ['open', real_path]
    else:  # Linux, FreeBSD, etc.
        cmd = ['xdg-open', real_path]

    try:
        # Uses Popen class defined above in this module intead of run().
        # It is asynchronous and does NOT block the GUI.
        # It redirects stdout and stderr to DEVNULL to prevent crashes
        # caused by full pipes or orphaned consoles.
        Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return None
    except (OSError, subprocess.SubprocessError) as error:
        return str(error)
# ------------------------------------------------------------------------


def format_bytes(num):
    """
    Given a float number (bytes) returns size output
    strings human readable, e.g.
    out = format_bytes(9909043.20)
    It return a string digit with metric suffix
    """
    if num <= 0.0:  # handles null, negative, or sub-byte values
        return "0.00B"

    unit = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]
    const = 1024.0

    exponent = int(math.log(num, const))
    exponent = max(0, min(exponent, len(unit) - 1))

    suffix = unit[exponent]
    output_value = num / (const ** exponent)

    return f"{output_value:.2f}{suffix}"
# ------------------------------------------------------------------------


def to_bytes(string, key='ydl'):
    """
    Convert given size string to bytes, e.g.
    out = to_bytes('9.45MiB')
    It return a number 'float' object.

    Updated on October 27 2026
    """
    units = (["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]
             if key == 'ydl' else
             ["byte", "Kibyte", "Mibyte", "Gibyte", "Tibyte", "Pibyte",
              "Eibyte", "Zibyte", "Yibyte"])

    const = 1024.0
    value = 0.0
    exponent = 0  # Security Fallback

    clean_string = string.strip()

    # Units in ascending order (from largest to smallest), with
    # the list reversed to prevent "B" from being matched within "MiB"
    for index, metric in enumerate(units):
        if metric in clean_string:
            try:
                value = float(clean_string.split(metric)[0].strip())
                exponent = index
                break
            except ValueError:
                continue

    # if nothing unity try to convert directly
    if exponent == 0 and value == 0.0:
        try:
            value = float(clean_string)
        except ValueError:
            pass

    return round(value * (const ** exponent), 2)
# ------------------------------------------------------------------------


def time_to_integer(timef: str = '0', sec=False, rnd=False) -> int:
    """
    Converts strings representing the 24-hour format to an
    integer equivalent to the time duration in milliseconds
    (default).

    ARGUMENTS:
    ---------
    timef: Accepts a string representing the 24-hour clock in the
           following valid string formats:

            '0' | '00' | '00.0' | '00.00' | 00:0 | '00:00:00'
            '0:00:00' | '0:0:0' | '00:00.000' | '00:00:00.000

           Default is '0' .
           Any other representation passed as a string argument will
           be returned as an integer object equal to 0 (int).
           If the argument passed is an object other than the string
           object (str) the exception `TypeError` will be raised.

    sec: if `True`, returns the duration in seconds instead
         of milliseconds.

    rnd: if `True` rounds the result, i.e. "00:00:02.999" > 3000
         milliseconds instead of 2999 milliseconds or 3 seconds
         instead of 2 seconds using `sec=True` argument.

    Return an int object.
    Raise `TypeError` if argument != `str` .
    """
    if not isinstance(timef, str):
        raise TypeError("Only a string (str) object is expected.")

    # adds leading zeros to fill up possibly non-existing fields.
    hours, minutes, seconds = (["0", "0"] + timef.split(":"))[-3:]

    try:
        h_val = int(hours)
        m_val = int(minutes)
        s_val = float(seconds)
    except ValueError:
        return 0

    # Calculates absolute total in millisenconds first
    total_ms = (h_val * 3600000) + (m_val * 60000) + (s_val * 1000)

    if rnd:
        # Round total overall based on mode (seconds or milliseconds)
        if sec:
            return round(total_ms / 1000)
        return round(total_ms)

    # Without round perform the standard truncate (int)
    if sec:
        return int(total_ms / 1000)
    return int(total_ms)
# ------------------------------------------------------------------------


def integer_to_time(integer: int = 0, mills=True, rnd=False) -> str:
    """
    Converts integers to 24-hour clock format calculating in
    sexagesimal format. Accept an `int` object, such as 2998.
    Float numbers, such as 2000.999, must be rounded using
    `round()` function first.

    ARGUMENTS:
    ---------
    integer: Any int object, default is 0.

    mills: Include milliseconds like "HH:MM:SS.MIL" (default).
           Milliseconds will be excluded and ignored if set
           to `False`. You could instead use the `rnd` argument
           to round them and add the offset to the seconds.

    rnd: If `True` rounds the result. This argument will have
         no effect with `mills=True` default argument.

    Returns a string object.
    Raise `TypeError` if argument != `int` .

    """
    if not isinstance(integer, int):
        raise TypeError("An integer (int) object is expected.")

    # Protect from accidental negative numbers
    integer = max(integer, 0)

    # Rounding is applied to the total if milliseconds are to be excluded.
    # If there are fewer than 500ms remaining until the next second, it
    # truncates; otherwise, it adds one full second.
    if not mills and rnd:
        remainder = integer % 1000
        integer = ((integer + 1000 - remainder)
                   if remainder >= 500 else (integer - remainder))

    # The sexagesimal division should never produce ":60"
    minutes, sec_remainder = divmod(integer, 60000)
    hours, minutes = divmod(minutes, 60)

    if mills:
        seconds_float = float(sec_remainder) / 1000
        return f"{hours:02}:{minutes:02}:{seconds_float:06.3f}"

    # here, the value has already been rounded at an earlier
    # stage (if rnd=True), or it should simply be truncated
    seconds_int = int(sec_remainder / 1000)
    return f"{hours:02}:{minutes:02}:{seconds_int:02}"
# ------------------------------------------------------------------------


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

    # Check whether the file has a size greater than 0 bytes without reading it
    try:
        if os.path.getsize(filename) > 0:
            # Use "w" to zero out the file in place
            with open(filename, "w", encoding='utf-8'):
                pass
    except OSError:
        # Secure fallback: attempting direct atomic opening and truncation
        with open(filename, "r+", encoding='utf-8') as fname:
            fname.seek(0)  # it places the file pointer to position 0
            fname.truncate()  # truncates the file to the current file point.
# ------------------------------------------------------------------#


def detect_binaries(name, extradir=None):
    """
    <https://stackoverflow.com/questions/11210104/check-if
    -a-program-exists-from-a-python-script>

    name = name of executable without extension
    extradir = additional dirname to perform search

    Given an executable (binary) file name, it looks for it
    in the operating system using the `which` function, if it
    doesn't find it, it tries to look for it in the optional
    `extradir` .

        Return (None, path) if found in the OS $PATH.
        Return ('provided', path) if found on the `extradir`
        Return ('not installed', None) if both failed.

    """
    execpath = shutil.which(name)
    if execpath:
        return None, execpath
    if extradir:  # check onto extradir
        execpath = os.path.join(extradir, "bin", name)
        if os.path.isfile(execpath):
            return 'provided', execpath
    return 'not installed', None
