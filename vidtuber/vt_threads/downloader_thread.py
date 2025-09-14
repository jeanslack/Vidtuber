# -*- coding: UTF-8 -*-
"""
Name: downloader_thread.py
Porpose: long processing task using yt-dlp executable
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: June.05.2025
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
import time
import itertools
import platform
import subprocess
import wx
from pubsub import pub
from vidtuber.vt_utils.utils import Popen
from vidtuber.vt_io.make_filelog import loginfo, logerror
if not platform.system() == 'Windows':
    import shlex


def killbill(pid):
    """
    kill the process sending a Ctrl+C event to yt-dlp
    """
    lambda: os.kill(pid, signal.CTRL_C_EVENT)


class DownloadProcess(Thread):
    """
    DownloadProcess represents a separate thread for running
    download using yt-dlp as subprocess and capture its stdout/stderr
    in real time .

    """
    STOP = ('ERROR: VIDTUBER: STOP command received by signal '
            'event.\nTerminated process ')
    # -----------------------------------------------------------------------#

    def __init__(self, args, urls, logfile):
        """
        Attributes defined here:
        self.stop_work_thread -  boolean process terminate value
        self.urls - type list
        self.logfile - str path object to log file
        self.arglist - option arguments list
        """
        self.stop_work_thread = False  # process terminate
        self.urls = urls
        self.logfile = logfile
        self.arglist = args
        self.countmax = len(self.arglist)
        self.count = 0

        Thread.__init__(self)
        self.start()  # start the thread (va in self.run())

    def run(self):
        """
        Subprocess run thread.
        """
        for url, opts in itertools.zip_longest(self.urls,
                                               self.arglist,
                                               fillvalue='',
                                               ):
            self.count += 1
            count = f"URL {self.count}/{self.countmax}"

            wx.CallAfter(pub.sendMessage,
                         "COUNT_YTDL_EVT",
                         count=count,
                         fsource=f'Source: {url}',
                         destination='',
                         duration=100,
                         end='CONTINUE',
                         )
            cmd = f'{opts} "{url}"'
            # write log cmd
            loginfo(f'INFO: {count}\nINFO: VIDTUBER COMMAND: {cmd}\n',
                    self.logfile, url)
            if not platform.system() == 'Windows':
                cmd = shlex.split(cmd)
            try:
                with Popen(cmd,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           bufsize=1,
                           universal_newlines=True,
                           encoding='utf-8',
                           ) as proc:
                    for line in proc.stdout:
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_YDL_EXECUTABLE_EVT",
                                     output=line,
                                     duration=100,
                                     status=0,
                                     )
                        if self.stop_work_thread:
                            killbill(proc.pid)
                            wx.CallAfter(pub.sendMessage,
                                         "UPDATE_YDL_EXECUTABLE_EVT",
                                         output='STOP',
                                         duration=100,
                                         status='ERROR',
                                         )
                            msg = (DownloadProcess.STOP
                                   + f'with PID {proc.pid}')
                            logerror(msg, self.logfile, usesep=False)
                            time.sleep(.5)
                            wx.CallAfter(pub.sendMessage, "END_YTDL_EVT")
                            return

                    if proc.wait():
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_YDL_EXECUTABLE_EVT",
                                     output='FAILED',
                                     duration=100,
                                     status='ERROR',
                                     )
                        logerror(f"[YT-DLP]: {proc.wait()}",
                                 self.logfile, usesep=False)
                        time.sleep(1)
                        continue

            except (OSError, FileNotFoundError) as err:
                wx.CallAfter(pub.sendMessage,
                             "COUNT_YTDL_EVT",
                             count=err,
                             fsource='',
                             destination='',
                             duration=0,
                             end='ERROR'
                             )
                logerror(f'VIDTUBER: ERROR: {err}', self.logfile, usesep=False)
                break

            if proc.wait() == 0:  # ..Finished
                wx.CallAfter(pub.sendMessage,
                             "COUNT_YTDL_EVT",
                             count='',
                             fsource='',
                             destination='',
                             duration=100,
                             end='DONE',
                             )
                time.sleep(1)
        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_YTDL_EVT")
    # --------------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
# ------------------------------------------------------------------------#
