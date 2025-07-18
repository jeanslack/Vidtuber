# -*- coding: UTF-8 -*-
"""
Name: long_processing_task.py
Porpose: Console to show logging messages during processing
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
from pubsub import pub
import wx
from vidtuber.vt_dialogs.widget_utils import notification_area
from vidtuber.vt_io.make_filelog import make_log_template
from vidtuber.vt_threads.ydl_downloader import YtdlExecDL
from vidtuber.vt_io import io_tools


class LogOut(wx.Panel):
    """
    displays a text control for the output logging and a
    progressive percentage text label. This panel is used
    in combination with separated threads for long processing
    tasks.

    """
    MSG_stop = '[Vidtuber]: STOP command received.'
    MSG_done = _('[Vidtuber]: SUCCESS !')
    MSG_failed = _('[Vidtuber]: FAILED !')
    MSG_taskfailed = _('Sorry, all task failed !')
    MSG_fatalerror = _("The process was stopped due to a fatal error.")
    MSG_interrupted = _('Interrupted Process !')
    MSG_completed = _('Successfully completed !')
    MSG_unfinished = _('Not everything was successful.')

    WHITE = '#fbf4f4'  # white for background status bar
    BLACK = '#060505'  # black for background status bar
    YELLOW = '#bd9f00'
    # ------------------------------------------------------------------#

    def __init__(self, parent):
        """
        The 'logfile' attribute 'full path log file.log',
        file in which log messages will be written

        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.parent = parent  # main frame
        self.thread_type = None  # the instantiated thread
        self.abort = False  # if True set to abort current process
        self.error = False  # if True, all the tasks was failed
        self.logfile = None  # full path log file
        self.result = []  # result of the final process
        self.count = 0  # keeps track of the counts (see `update_count`)
        self.clr = self.appdata['colorscheme']

        wx.Panel.__init__(self, parent=parent)

        sizer = wx.BoxSizer(wx.VERTICAL)
        infolbl = _("Download Status")
        lbl = wx.StaticText(self, label=infolbl)
        if self.appdata['ostype'] != 'Darwin':
            lbl.SetLabelMarkup(f"<b>{infolbl}</b>")
        sizer.Add((0, 25))
        sizer.Add(lbl, 0, wx.ALL, 5)
        sizer.Add((0, 10))
        self.btn_viewlog = wx.Button(self, wx.ID_ANY, _("Current Log"),
                                     size=(-1, -1))
        self.btn_viewlog.Disable()
        self.txtout = wx.TextCtrl(self, wx.ID_ANY, "",
                                  style=wx.TE_MULTILINE
                                  | wx.TE_READONLY
                                  | wx.TE_RICH2
                                  )
        sizer.Add(self.txtout, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.btn_viewlog, 0, wx.ALL, 5)
        self.labprog = wx.StaticText(self, label="")
        sizer.Add(self.labprog, 0, wx.ALL, 5)
        line = wx.StaticLine(self, wx.ID_ANY, pos=wx.DefaultPosition,
                             size=wx.DefaultSize, style=wx.LI_HORIZONTAL,
                             name=wx.StaticLineNameStr,
                             )
        sizer.Add(line, 0, wx.ALL | wx.EXPAND, 5)
        # set_properties:
        self.txtout.SetBackgroundColour(self.clr['BACKGRD'])
        self.SetSizerAndFit(sizer)
        # ------------------------------------------
        self.Bind(wx.EVT_BUTTON, self.view_log, self.btn_viewlog)

        pub.subscribe(self.youtubedl_exec, "UPDATE_YDL_EXECUTABLE_EVT")
        pub.subscribe(self.update_count, "COUNT_YTDL_EVT")
        pub.subscribe(self.end_proc, "END_YTDL_EVT")
    # ----------------------------------------------------------------------

    def view_log(self, event):
        """
        Opens the log file corresponding to the last executed process.
        """
        if self.logfile:
            fname = str(self.logfile)
            if os.path.exists(fname) and os.path.isfile(fname):
                io_tools.openpath(fname)
    # ----------------------------------------------------------------------

    def topic_thread(self, args, urls):
        """
        This method is resposible to create the Thread instance.
        args: type tuple data object.
        """
        if args[0] == 'Viewing last log':
            return

        self.txtout.Clear()
        self.labprog.SetLabel('')
        self.logfile = make_log_template("Download_yt-dlp.log",
                                         self.appdata['logdir'],
                                         mode="w",
                                         )
        self.btn_viewlog.Disable()
        self.thread_type = YtdlExecDL(args[1], urls, self.logfile)
    # ----------------------------------------------------------------------

    def youtubedl_exec(self, output, duration, status):
        """
        Receiving output messages from yt-dlp command line execution
        via pubsub "UPDATE_YDL_EXECUTABLE_EVT" .

        """
        if status == 'ERROR':  # error, exit status of the p.wait
            if output == 'STOP':
                msg, color = LogOut.MSG_stop, self.clr['ABORT']
            else:
                msg, color = LogOut.MSG_failed, self.clr['ERR1']
            self.txtout.SetDefaultStyle(wx.TextAttr(color))
            self.txtout.AppendText(f"\n{msg}\n")
            self.result.append('failed')
            return  # must be return here

        if '[download] Destination:' in output:
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['DEBUG']))
            self.txtout.AppendText(f'{output}')

        elif '[download]' in output:
            self.labprog.SetLabel(output)

        else:
            if 'WARNING:' in output:
                self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['WARN']))
                self.txtout.AppendText(f'{output}')
            elif '[info]' in output:
                self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['INFO']))
                self.txtout.AppendText(f'{output}')
            elif 'ERROR:' in output:
                self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['ERR0']))
                self.txtout.AppendText(f'{output}')
            else:
                self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT1']))
                self.txtout.AppendText(f'{output}')

            with open(self.logfile, "a", encoding='utf-8') as logerr:
                logerr.write(f"[YT_DLP]: {output}")
    # ---------------------------------------------------------------------#

    def update_count(self, count, fsource, destination, duration, end):
        """
        Receive messages from file count, loop or non-loop thread.
        """
        if end == 'DONE':
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['SUCCESS']))
            self.txtout.AppendText(f"{LogOut.MSG_done}\n")
            return
        if end == 'ERROR':
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['ERR1']))
            self.txtout.AppendText(f'\n{count}\n')
            self.error = True
        else:
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT0']))
            self.txtout.AppendText(f'\n{count}\n')
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['DEBUG']))
            self.txtout.AppendText(f'{fsource}\n')
            if destination:
                self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['DEBUG']))
                self.txtout.AppendText(f'{destination}\n')

        self.count += 1
    # ----------------------------------------------------------------------

    def end_proc(self):
        """
        At the end of the process
        """
        if self.error:
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT0']))
            self.txtout.AppendText(f"\n{LogOut.MSG_fatalerror}\n")
            notification_area(_("Fatal Error !"), LogOut.MSG_fatalerror,
                              wx.ICON_ERROR)
        elif self.abort:
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['ABORT']))
            self.txtout.AppendText(f"\n{LogOut.MSG_interrupted}\n")
        else:
            if not self.result:
                endmsg = LogOut.MSG_completed
                self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT0']))
                notification_area(endmsg, _("Get your files at the "
                                            "destination you specified"),
                                  wx.ICON_INFORMATION,
                                  )
            else:
                if len(self.result) == self.count:
                    endmsg = LogOut.MSG_taskfailed
                    self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT0']))
                    notification_area(endmsg, _("Check the current output "
                                                "or read the related log "
                                                "file for more information."),
                                      wx.ICON_ERROR,)
                else:
                    endmsg = LogOut.MSG_unfinished
                    self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT0']))
                    notification_area(endmsg, _("Check the current output "
                                                "or read the related log "
                                                "file for more information."),
                                      wx.ICON_WARNING, timeout=10)

            self.parent.statusbar_msg(_('...Finished'), None)
            self.txtout.AppendText(f"{endmsg}\n")

        self.txtout.AppendText('\n')
        self.reset_all()
        pub.sendMessage("PROCESS_TERMINATED", msg='Terminated')
    # ----------------------------------------------------------------------

    def on_stop(self):
        """
        The user change idea and was stop process
        """
        self.thread_type.stop()
        # self.thread_type.join()  trying not to use thread.join here
        self.parent.statusbar_msg(_("Please wait... interruption in progress"),
                                  LogOut.YELLOW, LogOut.BLACK)
        self.abort = True
    # ----------------------------------------------------------------------

    def reset_all(self):
        """
        Reset to default at any process terminated
        """
        self.thread_type = None
        self.abort = False
        self.error = False
        self.result.clear()
        self.count = 0
        self.parent.statusbar_msg(_('Done'), None)
        self.btn_viewlog.Enable()
    # ----------------------------------------------------------------------
