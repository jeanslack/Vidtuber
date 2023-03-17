# -*- coding: UTF-8 -*-
"""
Name: argparser.py
Porpose: Vidtuber Command line arguments
Compatibility: Python3
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Jan.11.2023
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
import sys
from shutil import which
import argparse
import platform
from vidtuber.vdms_sys.msg_info import current_release
try:
    import wx
    MSGWX = f"{wx.version()}"
except ModuleNotFoundError as errwx:
    MSGWX = f"not installed! ({errwx})"


def info_this_platform():
    """
    Get information about operating system, version of
    Python and wxPython.
    """
    osys = platform.system_alias(platform.system(),
                                 platform.release(),
                                 platform.version(),
                                 )
    thisplat = (f"Platform: {osys[0]}\n"
                f"Version: {osys[2]}\n"
                f"Release: {osys[1]}\n"
                f"Architecture: {platform.architecture()}\n"
                f"Python: {sys.version}\n"
                f"wxPython: {MSGWX}"
                )
    return thisplat


def arguments():
    """Parser for command line options"""
    parser = argparse.ArgumentParser(description=('GUI for FFmpeg and '
                                                  'youtube-dl/yt-dlp'),)
    parser.add_argument('-v', '--version',
                        help="Show the current version and exit",
                        action="store_true",
                        )
    parser.add_argument('-c', '--check',
                        help=('List of executables used by Vidtuber '
                              'found in your operating system'),
                        action="store_true",
                        )
    parser.add_argument('--make-portable',
                        help=('In order to make the application fully '
                              'portable and stealth, this option can keeps '
                              'all application data stored separately from '
                              'conventional platform directories and provide '
                              'only relative paths. It expects you to specify '
                              'a preferred location of data used by the '
                              'application. Note that a new output folder '
                              '("My_Files") will be created ONLY during the '
                              'first startup of the application through the '
                              'Wizard. In all other cases the relative paths '
                              'may not be fully updated on the configuration '
                              'file.'
                              ),
                        metavar='URL',
                        )

    argmts = parser.parse_args()

    if argmts.check:
        deps = {'Required': {'ffmpeg': None, 'ffprobe': None, 'ffplay': None},
                'Recommended': {'youtube-dl': None, 'yt-dlp': None},
                'Optional': {'atomicparsley': None}
                }
        for key, val in deps.items():
            if key in ('Required', 'Recommended', 'Optional'):
                for exe in val:
                    val[exe] = which(exe, mode=os.F_OK | os.X_OK, path=None)
        print('\nList of executables used by Vidtuber:')
        for key, val in deps.items():
            for exe, path in val.items():
                if path:
                    print(f"\t[{key}] '{exe}' ...Ok")
                    print(f"\tpath: '{path}'\n")
                else:
                    print(f"\t[{key}] '{exe}' ...Not Installed")
                    print(f"\tpath: {path}\n")
        parser.exit(status=0, message=None)

    elif argmts.version:
        crel = current_release()
        print(f'{crel[0]}: {crel[2]} ({crel[3]})')
        print(info_this_platform())
        parser.exit(status=0, message=None)

    else:
        print("Type -h for help.")

    return vars(argmts)
