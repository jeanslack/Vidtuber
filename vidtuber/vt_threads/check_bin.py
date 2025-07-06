# -*- coding: UTF-8 -*-
"""
Name: check_bin.py
Porpose: Gets the output to display the features of FFmpeg
Compatibility: Python3 (Unix, Windows)
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: May.15.2021
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

import subprocess
from vidtuber.vt_utils.utils import Popen


def subp(args, ostype):
    """
    Execute commands which *do not* need to read the stdout/stderr in
    real time.

    Parameters:
        [*args* command list object]
        *ostype* result of the platform.system()

    """
    cmd = []
    for opt in args:
        cmd.append(opt)

    if ostype == 'Windows':
        cmd = ' '.join(cmd)
    try:
        with Popen(cmd,
                   stdout=subprocess.PIPE,
                   stderr=subprocess.STDOUT,
                   universal_newlines=True,  # mod text
                   encoding='utf-8',
                   ) as proc:
            out = proc.communicate()

            if proc.returncode:  # if returncode == 1
                return ('Not found', out[0])

    except (OSError, FileNotFoundError) as oserr:  # no executable found
        return ('Not found', oserr)

    return ('None', out[0])
