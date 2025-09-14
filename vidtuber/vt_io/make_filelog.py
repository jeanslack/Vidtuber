# -*- coding: UTF-8 -*-
"""
File Name: make_filelog.py
Porpose: log file generator
Compatibility: Python3, Python2
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Mar.08.2024
Code checker: flake8, pylint

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
import time


def loginfo(info, logfile, url, usesep=True, txtenc="utf-8"):
    """
    This function writes log events as information messages
    to a given `logfile` during the process.
    """
    current_date = time.strftime("%c")  # date/time
    if usesep:
        sep = ('\n-----------------------------------------------'
               '----------------------------------------------\n')
    else:
        sep = '\n'

    apnd = f'{sep}DATE: {current_date}\nURL: "{url}"\n{info}\n'

    with open(logfile, "a", encoding=txtenc) as log:
        log.write(apnd)
# ----------------------------------------------------------------#


def logerror(err, logfile, usesep=True, txtenc="utf-8"):
    """
    This function writes log events as error messages
    to a given `logfile` during the process.
    """
    current_date = time.strftime("%c")  # date/time
    if usesep:
        sep = ('\n-----------------------------------------------'
               '----------------------------------------------\n')
    else:
        sep = '\n'

    apnd = f'{sep}DATE: {current_date}\n{err}\n'

    with open(logfile, "a", encoding=txtenc) as log:
        log.write(apnd)
# ----------------------------------------------------------------#


def make_log_template(logfile, mode="a", txtenc="utf-8"):
    """
    Most log files are initialized from a template
    before starting a process and writing status
    messages to a given log file.

    - logfile, str(full path name of log file)
    - mode,  str(open modality, a(ppend), w(rite), etc, default is "a")
    - txtenc, str(encoding type, default is UTF8)

    Returns an absolute/relative pathname of the logfile.
    """
    sep = ('==============================================='
           '==============================================')
    current_date = time.strftime("%c")  # date/time

    with open(logfile, mode, encoding=txtenc) as log:
        log.write(f"""{sep}

[PROGRAM NAME]: Vidtuber

[SESSION DATE]: {current_date}

[LOGFILE LOCATION]: "{logfile}"
""")
    return logfile
