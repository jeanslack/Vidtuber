# -*- coding: UTF-8 -*-
"""
Name: shutdown.py
Purpose: Execute shutdown system using subprocess
Compatibility: Python3 (Unix, Windows)
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: October.25.2026
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
import os
import time
import subprocess
import shutil
import wx
from vidtuber.vt_utils.utils import Popen
from vidtuber.vt_io.make_filelog import make_log_template


def loginfo(info, logfile, usesep=True, txtenc="utf-8"):
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

    apnd = f'{sep}DATE: {current_date}\n{info}\n'

    with open(logfile, "a", encoding=txtenc) as log:
        log.write(apnd)
# ----------------------------------------------------------------#


def logerror(err, logfile, txtenc="utf-8"):
    """
    This function writes log events as error messages
    to a given `logfile` during the process.
    """
    with open(logfile, "a", encoding=txtenc) as log:
        log.write(f'{err}\n')
# ----------------------------------------------------------------#


def shutdown_system(password=None):
    """
    Turn off the system using subprocess
    """
    get = wx.GetApp()
    appdata = get.appset
    ostype = appdata['ostype']
    logfilepath = os.path.join(appdata['logdir'], "Shutdown.log")
    logfile = make_log_template(logfilepath, mode="w")

    if ostype == 'Linux':
        if password:
            password = f"{password}\n"
            cmd = ["sudo", "-S", "shutdown", "-h", "now"]
        else:
            # Dynamic detection of systemctl for modern compatibility
            # that does not require root access
            if shutil.which("systemctl"):
                cmd = ["systemctl", "poweroff"]
            else:
                cmd = ["shutdown", "-h", "now"]

    elif ostype == 'Darwin':
        password = f"{password}\n"
        cmd = ["sudo", "-S", "shutdown", "-h", "now"]

    elif ostype == 'Windows':
        cmd = ["shutdown", "/s", "/t", "1"]

    elif ostype in ['OpenBSD', 'FreeBSD']:
        password = f"{password}\n"
        cmd = ["sudo", "-S", "shutdown", "-p", "now"]

    else:
        return 'Error: unsupported platform'

    loginfo(f'INFO: VIDTUBER COMMAND: {" ".join(cmd)}', logfile)

    try:
        with Popen(cmd,
                   stdin=subprocess.PIPE,
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                   universal_newlines=True,
                   encoding='utf-8',
                   ) as proc:
            # Communicates input in an isolated manner and
            # safely extracts stdout and stderr
            stdout_data, stderr_data = proc.communicate(input=password)

            # Managing the wait timeout to prevent parent thread deadlocks
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

            if stderr_data:
                logerror(f"STDERR: {stderr_data}", logfile)
            if stdout_data:
                loginfo(f"STDOUT: {stdout_data}", logfile)

            # Returns success based on the actual returncode of the
            # operating process, without interpreting text strings
            return proc.returncode == 0

    except (OSError, FileNotFoundError) as err:
        logerror(f'VIDTUBER: ERROR: {err}', logfile)
        return err
