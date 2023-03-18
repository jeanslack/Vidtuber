# -*- coding: UTF-8 -*-
"""
Name: long_processing_task.py
Porpose: Console to show logging messages during processing
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: March.17.2023
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
from __future__ import unicode_literals
from pubsub import pub
import wx
from vidtuber.vt_dialogs.widget_utils import notification_area
from vidtuber.vt_io.make_filelog import make_log_template
from vidtuber.vt_threads.ydl_downloader import YdlDownloader


class LogOut(wx.Panel):
    """
    displays a text control for the output logging and a
    progressive percentage text label. This panel is used
    in combination with separated threads for long processing
    tasks.

    """
    MSG_done = _('[Vidtuber]: SUCCESS !')
    MSG_failed = _('[Vidtuber]: FAILED !')
    MSG_taskfailed = _('Sorry, all task failed !')
    MSG_fatalerror = _("The process was stopped due to a fatal error.")
    MSG_interrupted = _('Interrupted Process !')
    MSG_completed = _('Successfully completed !')
    MSG_unfinished = _('Not everything was successful.')

    WHITE = '#fbf4f4'  # white for background status bar
    BLACK = '#060505'  # black for background status bar
    # ------------------------------------------------------------------#

    def __init__(self, parent):
        """
        The 'logname' attribute is the name_of_panel.log
        file in which log messages will be written

        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.parent = parent  # main frame
        self.thread_type = None  # the instantiated thread
        self.abort = False  # if True set to abort current process
        self.error = False  # if True, all the tasks was failed
        self.logname = None  # log pathname, None otherwise
        self.result = []  # result of the final process
        self.count = 0  # keeps track of the counts (see `update_count`)
        self.clr = self.appdata['icontheme'][1]

        wx.Panel.__init__(self, parent=parent)

        infolbl = _("Process log:")
        lbl = wx.StaticText(self, label=infolbl)
        if self.appdata['ostype'] != 'Darwin':
            lbl.SetLabelMarkup(f"<b>{infolbl}</b>")
        self.txtout = wx.TextCtrl(self, wx.ID_ANY, "",
                                  style=wx.TE_MULTILINE
                                  | wx.TE_READONLY
                                  | wx.TE_RICH2
                                  )
        self.labprog = wx.StaticText(self, label="")
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((0, 10))
        sizer.Add(lbl, 0, wx.ALL, 5)
        sizer.Add(self.txtout, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.labprog, 0, wx.ALL, 5)
        line = wx.StaticLine(self, wx.ID_ANY, pos=wx.DefaultPosition,
                             size=wx.DefaultSize, style=wx.LI_HORIZONTAL,
                             name=wx.StaticLineNameStr,
                             )
        sizer.Add(line, 0, wx.ALL | wx.EXPAND, 5)
        # set_properties:
        self.txtout.SetBackgroundColour(self.clr['BACKGRD'])
        self.SetSizerAndFit(sizer)
        # bind
        self.Bind(wx.EVT_BUTTON, self.on_close)
        # ------------------------------------------

        pub.subscribe(self.downloader_activity, "UPDATE_YDL_EVT")
        pub.subscribe(self.update_count, "COUNT_EVT")
        pub.subscribe(self.end_proc, "END_EVT")
    # ----------------------------------------------------------------------

    def topic_thread(self, varargs):
        """
        Thread redirection
        varargs: type tuple data object
        duration: total duration or partial if time_seq is set
        """
        if varargs[0] == 'Viewing last log':
            return

        self.txtout.Clear()
        self.labprog.SetLabel('')
        self.logname = make_log_template(varargs[8], self.appdata['logdir'])
        self.thread_type = YdlDownloader(varargs, self.logname)
    # ----------------------------------------------------------------------

    def downloader_activity(self, output, duration, status):
        """
        Receiving output messages from youtube_dl library via
        pubsub "UPDATE_YDL_EVT" .
        """
        if status == 'ERROR':
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['ERR0']))
            self.txtout.AppendText(f'{output}\n')
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['FAILED']))
            self.txtout.AppendText(f"{LogOut.MSG_failed}\n")
            self.result.append('failed')

        elif status == 'WARNING':
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['WARN']))
            self.txtout.AppendText(f'{output}\n')

        elif status == 'DEBUG':
            if '[download] Destination' in output:
                self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['DEBUG']))
                self.txtout.AppendText(f'{output}\n')

            elif '[info]' in output:
                self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['INFO']))
                self.txtout.AppendText(f'{output}\n')

            elif '[download]' not in output:
                self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT1']))
                self.txtout.AppendText(f'{output}\n')
                with open(self.logname, "a", encoding='utf8') as logerr:
                    logerr.write(f"[{self.appdata['downloader'].upper()}]: "
                                 f"{status} > {output}\n")

        elif status == 'DOWNLOAD':
            perc = duration['_percent_str'].strip()
            tbytes = duration['_total_bytes_str'].strip()
            speed = duration['_speed_str'].strip()
            eta = duration['_eta_str'].strip()
            self.labprog.SetLabel(f'Downloading: {perc}  |  Size: {tbytes}  '
                                  f'|  Speed: {speed} |  ETA: {eta}')

        elif status == 'FINISHED':
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT1']))
            self.txtout.AppendText(f'{duration}\n')

        if status in ['ERROR', 'WARNING']:
            with open(self.logname, "a", encoding='utf8') as logerr:
                logerr.write(f"[{self.appdata['downloader'].upper()}]: "
                             f"{output}\n")
    # ---------------------------------------------------------------------#

    def update_count(self, count, fsource, destination, duration, end):
        """
        Receive messages from file count, loop or non-loop thread.
        """
        if end == 'ok':
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['SUCCESS']))
            self.txtout.AppendText(f"{LogOut.MSG_done}\n")
            return

        # if STATUS_ERROR == 1:
        if end == 'error':
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['WARN']))
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
            self.txtout.AppendText(f"\n{endmsg}\n")

        self.txtout.AppendText('\n')
        self.reset_all()
        pub.sendMessage("PROCESS TERMINATED", msg='Terminated')
    # ----------------------------------------------------------------------

    def on_stop(self):
        """
        The user change idea and was stop process
        """
        self.thread_type.stop()
        self.parent.statusbar_msg(_("wait... all operations will be stopped "
                                    "at the end of the download in progress "),
                                  'GOLDENROD', LogOut.WHITE)
        self.thread_type.join()
        self.parent.statusbar_msg(_("...Interrupted"), None)
        self.abort = True
    # ----------------------------------------------------------------------

    def reset_all(self):
        """
        Reset to default at any process terminated
        """
        self.logname = None
        self.thread_type = None
        self.abort = False
        self.error = False
        self.result.clear()
        self.count = 0
    # ----------------------------------------------------------------------

    def on_close(self, event):
        """
        close dialog and retrieve at previusly panel
        """
        if self.thread_type is not None:
            if wx.MessageBox(_('There are still processes running.. if you '
                               'want to stop them, use the "Abort" button.\n\n'
                               'Do you want to kill application?'),
                             _('Please confirm'),
                             wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                return
            self.parent.on_Kill()
        self.parent.panelShown()  # retrieve at previusly panel
