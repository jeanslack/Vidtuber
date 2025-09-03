# -*- coding: UTF-8 -*-
"""
Name: ydl_get_formatcode.py
Porpose: long processing task to get format codes
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Sep.03.2025
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
from threading import Thread
import signal
import platform
import subprocess
import wx
from pubsub import pub
from vidtuber.vt_utils.utils import Popen
from vidtuber.vt_io.make_filelog import logwrite
if not platform.system() == 'Windows':
    import shlex


def killbill(pid):
    """
    kill the process sending a Ctrl+C event to yt-dlp
    """
    lambda: os.kill(pid, signal.CTRL_C_EVENT)


class YdlExtractInfo(Thread):
    """
    Embed youtube-dl as module into a separated thread in order
    to get output during process (see help(youtube_dl.YoutubeDL) ) .

    """
    STOP = '[Vidtuber]: STOP command received.'
    # -----------------------------------------------------------------------#

    def __init__(self, url, args, logfile):
        """
        Attributes defined here:
        self.url  str('url')
        self.data  tupla(None, None)
        """
        get = wx.GetApp()  # get vidtuber wx.App attribute
        self.appdata = get.appset
        self.logfile = logfile
        self.status = None
        self.data = None
        self.cmd = f'{args} "{url}"'

        logwrite(f'INFO: COMMAND: {self.cmd}', '',
                 self.logfile)  # write log cmd

        Thread.__init__(self)
        self.start()  # start the thread (va in self.run())

    def run(self):
        """
        Defines options to extract_info with youtube_dl
        """
        if not platform.system() == 'Windows':
            self.cmd = shlex.split(self.cmd)

        try:
            with Popen(self.cmd,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT,
                       bufsize=1,
                       universal_newlines=True,
                       encoding='utf-8',
                       ) as proc:
                out = proc.communicate()

                if proc.returncode:  # if returncode == 1
                    logwrite('', (f"[VIDTUBER]: ERROR: {out[0]}"),
                             self.logfile)
                    self.status = (out[0], 'error')
                else:
                    self.status = (out[0], out[1])

        except (OSError, FileNotFoundError) as err:
            logwrite('', f'{err}', self.logfile)
            self.status = (f'{err}', 'error')

        self.data = self.status

        wx.CallAfter(pub.sendMessage,
                     "RESULT_EVT",
                     status=''
                     )
