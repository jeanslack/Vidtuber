# -*- coding: UTF-8 -*-
"""
Name: get_output_thread.py
Porpose: long processing task
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Sep.09.2025
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
from vidtuber.vt_io.make_filelog import loginfo, logerror
if not platform.system() == 'Windows':
    import shlex


def killbill(pid):
    """
    kill the process sending a Ctrl+C event to subprocess executable
    """
    lambda: os.kill(pid, signal.CTRL_C_EVENT)
# ----------------------------------------------------------------#


class FetchOutputDataProcess(Thread):
    """
    This class can encapsulate subprocesses that require reading
    data from stdout and stderr through a separate thread.
    The received data is stored in the self.data attribute and
    can be retrieved by the caller at the end of the thread.

    Simple Example:
        thread = FetchOutputDataProcess(url, args, logfile)
        thread.join()
        data = thread.data

    Example using the pop-up dialog:
        thread = FetchOutputDataProcess(url, args, logfile)
        dlgload = PopupDialog(parent, "My Caption - Loading...",
                              "Wait....\nRetrieving required data.",
                              thread,
                              )
        dlgload.ShowModal()
        data = thread.data
        dlgload.Destroy()

    Stopping the current subprocess can be implemented by the
    caller using the stop() method (see thread arg on PopupDialog
    for example usage).
    """
    STOP = ('WARNING: [VIDTUBER]: STOP command received by signal '
            'event.\nTerminated process ')
    # -----------------------------------------------------------------------#

    def __init__(self, url, args, logfile):
        """
        Attributes defined here:
        self.logfile, str(pathname)
        self.status, group data
        self.data, this is taken from the caller `ytdlp_dump_single_json`
        self.cmd, group required command and arguments
        self.proc, sub-process object
        self.stop_work_thread, boolean process terminate value
        """
        self.logfile = logfile
        self.status = None
        self.data = None
        self.cmd = f'{args} "{url}"'
        self.proc = None
        self.stop_work_thread = False
        # write log cmd
        loginfo(f'INFO: VIDTUBER COMMAND: {self.cmd}',
                self.logfile, url)

        Thread.__init__(self)
        self.start()

    def run(self):
        """
        Start thread here.
        Note that the only way for the caller to receive output at
        the end of the thread is to use the self.data attribute.
        stderr=subprocess.STDOUT directs all stdout and stderr to
        standard out, making it impossible to separate errors from
        output. It's more convenient to separate stdout and stderr
        on the PIPE.
        """
        if not platform.system() == 'Windows':
            self.cmd = shlex.split(self.cmd)

        try:
            with Popen(self.cmd,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE,
                       # stderr=subprocess.STDOUT,
                       bufsize=1,
                       universal_newlines=True,
                       encoding='utf-8',
                       ) as self.proc:
                out = self.proc.communicate()

                if self.proc.returncode:  # if returncode == 1
                    if self.stop_work_thread:
                        out = (None, FetchOutputDataProcess.STOP
                               + f'with PID {self.proc.pid}')
                        logerror(out[1], self.logfile, usesep=False)
                    else:
                        logerror(f"[YT-DLP]: {out[1]}",
                                 self.logfile, usesep=False)
                    self.status = out[0], 'error'
                else:
                    logerror(f"[YT-DLP]: {out[1]}", self.logfile, usesep=False)
                    self.status = out[0], None

        except (OSError, FileNotFoundError) as err:
            logerror(f'[VIDTUBER]: ERROR: {err}', self.logfile, usesep=False)
            self.status = (f'{err}', 'error')

        self.data = self.status

        wx.CallAfter(pub.sendMessage,
                     "RESULT_EVT",
                     status=''
                     )
    # --------------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
        self.proc.terminate()
        killbill(self.proc.pid)
