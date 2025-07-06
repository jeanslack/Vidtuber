# -*- coding: UTF-8 -*-
"""
Name: main_ytdlp.py
Porpose: window main frame for yt_dlp library
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: June.06.2025
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
import webbrowser
import wx
from pubsub import pub
from vidtuber.vt_utils.get_bmpfromsvg import get_bmp
from vidtuber.vt_dialogs.ydl_mediainfo import YdlMediaInfo
from vidtuber.vt_dialogs.showlogs import ShowLogs
from vidtuber.vt_dialogs import about_dialog
from vidtuber.vt_dialogs import check_new_version
from vidtuber.vt_panels.textdrop import Url_DnD_Panel
from vidtuber.vt_panels.youtubedl_ui import Downloader
from vidtuber.vt_panels.long_task_ytdlp import LogOut
from vidtuber.vt_io import io_tools
from vidtuber.vt_io.checkup import check_destination_dir
from vidtuber.vt_sys.settings_manager import ConfigManager
from vidtuber.vt_dialogs.settings_ytdlp import YtdlpSettings
from vidtuber.vt_dialogs import settings_vidtuber
from vidtuber.vt_threads.shutdown import shutdown_system
from vidtuber.vt_sys.argparser import info_this_platform
from vidtuber.vt_sys.about_app import VERSION
if wx.GetApp().appset['yt_dlp'] is True:
    import yt_dlp


class MainFrame(wx.Frame):
    """
    This is the main frame top window for panels implementation.
    """
    # set status bar colours in html rappresentation:
    ORANGE = '#f28924'
    WHITE = '#fbf4f4'
    # -------------------------------------------------------------#

    def __init__(self, appdata):
        """
        If not data_url ytDownloader panel will be disabled
        """
        get = wx.GetApp()
        self.appdata = appdata
        self.icons = get.iconset
        self.data_url = []  # list of urls in text box
        self.changed = True  # previous list is different from new one
        self.infomediadlg = False  # media info dialog
        self.showlogs = False

        wx.Frame.__init__(self, None, -1, style=wx.DEFAULT_FRAME_STYLE)

        # ---------- panel instances:
        #self.parent = parent
        self.ytDownloader = Downloader(self)
        self.textDnDTarget = Url_DnD_Panel(self)
        self.ProcessPanel = LogOut(self)
        # hide panels
        self.ProcessPanel.Hide()
        self.ytDownloader.Hide()
        self.textDnDTarget.Show()
        # Layout toolbar buttons:
        mainSizer = wx.BoxSizer(wx.VERTICAL)  # sizer base global
        # Layout external panels:
        mainSizer.Add(self.textDnDTarget, 1, wx.EXPAND)
        mainSizer.Add(self.ytDownloader, 1, wx.EXPAND)
        mainSizer.Add(self.ProcessPanel, 1, wx.EXPAND)

        # ----------------------Set Properties----------------------#
        self.SetTitle("Vidtuber - YouTube Downloader")
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(self.icons['vidtuber'],
                                      wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        self.SetMinSize((1100, 715))
        self.SetSizer(mainSizer)
        self.Fit()
        self.SetSize(tuple(self.appdata['window_size']))
        self.Move(tuple(self.appdata['window_position']))
        # menu bar
        self.vidtuber_menu_bar()
        # tool bar main
        self.vidtuber_tool_bar()
        # status bar
        self.sb = self.CreateStatusBar(1)
        self.statusbar_msg(_('Ready'), None)
        # disable some toolbar item
        [self.toolbar.EnableTool(x, False) for x in (20, 22, 23, 24)]
        self.Layout()
        # ---------------------- Binding (EVT) ----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_outputdir)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        pub.subscribe(self.check_modeless_window, "DESTROY_ORPHANED_WINDOWS")
        pub.subscribe(self.process_terminated, "PROCESS_TERMINATED")

    # -------------------Status bar settings--------------------#

    def statusbar_msg(self, msg, bcolor, fcolor=None):
        """
        Set the status-bar message and color.
        Note that These methods don't always work on every platform.
        Usage:
            - self.statusbar_msg(_('...Finished'))  # no color
            - self.statusbar_msg(_('...Finished'),
                                 bcolor=color,
                                 fcolor=color)  # with colors

        bcolor: background color, fcolor: foreground color
        """
        if self.appdata['ostype'] == 'Linux':
            if not bcolor:
                self.sb.SetBackgroundColour(wx.NullColour)
                self.sb.SetForegroundColour(wx.NullColour)
            else:
                self.sb.SetBackgroundColour(bcolor)
                self.sb.SetForegroundColour(fcolor)

        self.sb.SetStatusText(msg)
        self.sb.Refresh()
    # ------------------------------------------------------------------#

    def check_modeless_window(self, msg=None):
        """
        Receives a message from a modeless window close event.
        This method is called using pub/sub protocol subscribing
        "DESTROY_ORPHANED_WINDOWS".
        """
        if msg == 'YdlMediaInfo':
            self.infomediadlg.Destroy()
            self.infomediadlg = False
        elif msg == 'ShowLogs':
            self.showlogs.Destroy()
            self.showlogs = False
    # ------------------------------------------------------------------#

    def destroy_orphaned_window(self):
        """
        Destroys all orphaned modeless windows,
        ie. on application exit or on editing URLs text.
        """
        if self.infomediadlg:
            self.infomediadlg.Destroy()
            self.infomediadlg = False
        if self.showlogs:
            self.showlogs.Destroy()
            self.showlogs = False

    # ---------------------- Event handler (callback) ------------------#

    def write_option_before_exit(self):
        """
        Write user settings to the configuration file
        before exit the application.
        """
        confmanager = ConfigManager(self.appdata['fileconfpath'])
        sett = confmanager.read_options()
        sett['window_size'] = list(self.GetSize())
        sett['window_position'] = list(self.GetPosition())
        sett['subtitles_options'] = self.ytDownloader.opt["SUBS"]
        fcodecolwidth = [self.ytDownloader.panel_cod.fcode.GetColumnWidth(0),
                         self.ytDownloader.panel_cod.fcode.GetColumnWidth(1),
                         self.ytDownloader.panel_cod.fcode.GetColumnWidth(2),
                         self.ytDownloader.panel_cod.fcode.GetColumnWidth(3),
                         self.ytDownloader.panel_cod.fcode.GetColumnWidth(4),
                         self.ytDownloader.panel_cod.fcode.GetColumnWidth(5),
                         self.ytDownloader.panel_cod.fcode.GetColumnWidth(6),
                         self.ytDownloader.panel_cod.fcode.GetColumnWidth(7),
                         self.ytDownloader.panel_cod.fcode.GetColumnWidth(8),
                         ]
        sett['fcode_column_width'] = fcodecolwidth
        confmanager.write_options(**sett)
    # ------------------------------------------------------------------#

    def checks_running_processes(self):
        """
        Check currently running processes
        """
        if self.ProcessPanel.IsShown():
            if self.ProcessPanel.thread_type is not None:
                return True
        return False
    # ------------------------------------------------------------------#

    def on_close(self, event):
        """
        This event destroy the YouTube Downloader child frame.
        """
        if self.checks_running_processes():
            if self.ProcessPanel.thread_type is not None:
                wx.MessageBox(_("There are still active windows with running "
                                "processes, make sure you finish your work "
                                "before exit."),
                              _('Vidtuber - Warning!'), wx.ICON_WARNING, self)
                return

        if self.appdata['warnexiting']:
            if wx.MessageBox(_('Are you sure you want to exit '
                               'the application?'),
                             _('Exit'), wx.ICON_QUESTION
                             | wx.CANCEL | wx.YES_NO, self) != wx.YES:
                return

        self.write_option_before_exit()
        self.destroy_orphaned_window()
        self.destroy_application()
    # ------------------------------------------------------------------#

    def on_Kill(self):
        """
        This method is called after from the `main_setup_dlg()` method.
        """
        if self.checks_running_processes():
            wx.MessageBox(_("There are still active windows with running "
                            "processes, make sure you finish your work "
                            "before exit."),
                          _('Vidtuber - Warning!'), wx.ICON_WARNING, self)
            self.appdata['auto-restart-app'] = False
            return

        self.destroy_orphaned_window()
        self.destroy_application()
    # ------------------------------------------------------------------#

    def destroy_application(self):
        """
        Permanent exit from the application.
        Do not use this method directly.
        """
        self.Destroy()
    # ------------------------------------------------------------------#

    # -------------   BUILD THE MENU BAR  ----------------###

    def vidtuber_menu_bar(self):
        """
        Make a menu bar. Per usare la disabilitazione di un menu item devi
        prima settare l'attributo self sull'item interessato - poi lo gestisci
        con self.item.Enable(False) per disabilitare o (True) per abilitare.
        Se vuoi disabilitare l'intero top di items fai per esempio:
        self.menuBar.EnableTop(6, False) per disabilitare la voce Help.
        """
        self.menuBar = wx.MenuBar()

        # ----------------------- file menu
        fileButton = wx.Menu()
        dscrp = _("Open destination folder of downloads\tCtrl+D")
        fold_downloads = fileButton.Append(wx.ID_ANY, dscrp)
        fileButton.AppendSeparator()
        exitItem = fileButton.Append(wx.ID_EXIT,
                                     _("Exit\tCtrl+Q"),
                                     _("Exit the application"))
        self.menuBar.Append(fileButton, _("File"))

        # ------------------ Edit menu
        editButton = wx.Menu()
        dscrp = (_("Paste\tCtrl+V"),
                 _("Paste the copied URLs to clipboard"))
        self.paste = editButton.Append(wx.ID_PASTE, dscrp[0], dscrp[1])
        dscrp = (_("Remove selected URL\tDEL"),
                 _("Remove the selected URL from the list"))
        self.delete = editButton.Append(wx.ID_REMOVE, dscrp[0], dscrp[1])
        dscrp = (_("Clear list\tShift+DEL"),
                 _("Clear the URL list"))
        self.clearall = editButton.Append(wx.ID_CLEAR, dscrp[0], dscrp[1])
        editButton.AppendSeparator()
        self.setupItem = editButton.Append(wx.ID_PREFERENCES,
                                           _("Preferences\tCtrl+P"),
                                           _("Main application preferences"))
        self.menuBar.Append(editButton, _("Edit"))

        # ------------------ tools menu
        toolsButton = wx.Menu()
        dscrp = (_("Work notes\tCtrl+N"),
                 _("Read and write useful notes and reminders."))
        notepad = toolsButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        self.menuBar.Append(toolsButton, _("Tools"))

        # ------------------ View menu
        viewButton = wx.Menu()
        dscrp = (_("About yt-dlp"),
                 _("Shows useful information about yt-dlp"))
        self.ydlused = viewButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        self.menuBar.Append(viewButton, _("View"))
        # ------------------ help menu
        helpButton = wx.Menu()
        helpItem = helpButton.Append(wx.ID_HELP, _("User guide"),
                                     ('https://github.com/jeanslack/'
                                      'Vidtuber'))
        helpButton.AppendSeparator()
        dscrp = (_("System information"),
                 _("Get generic information about the installed system."))
        sysinfo = helpButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        helpButton.AppendSeparator()
        dscrp = (_("Show log files\tCtrl+L"),
                 _("Viewing log messages"))
        viewlogs = helpButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        helpButton.AppendSeparator()
        issueItem = helpButton.Append(wx.ID_ANY, _("Issue tracker"),
                                      "https://github.com/jeanslack/"
                                      "Vidtuber/issues")
        contribution = helpButton.Append(wx.ID_ANY,
                                         _('Contribute to the project'),
                                         ('https://github.com/jeanslack/'
                                          'Vidtuber/pulls'))
        spons = helpButton.Append(wx.ID_ANY, _("Sponsor this project"),
                                             _("Become a developer supporter"))
        donat = helpButton.Append(wx.ID_ANY, _("Donate"),
                                             _("Donate to the app developer"))
        helpButton.AppendSeparator()
        infoItem = helpButton.Append(wx.ID_ABOUT, _("About Vidtuber"), "")
        dscrp = (_("Check latest version"),
                 _("Check and download the latest version of the application"))
        chklatest = helpButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        self.menuBar.Append(helpButton, _("Help"))
        self.SetMenuBar(self.menuBar)
        # -------
        self.SetMenuBar(self.menuBar)

        # -----------------------Binding menu bar-------------------------#
        # ----FILE----
        self.Bind(wx.EVT_MENU, self.openMydownload, fold_downloads)
        self.Bind(wx.EVT_MENU, self.quiet_app, exitItem)
        # ----EDIT----
        self.Bind(wx.EVT_MENU, self.textDnDTarget.on_paste, self.paste)
        self.Bind(wx.EVT_MENU, self.textDnDTarget.on_del_url_selected,
                  self.delete)
        self.Bind(wx.EVT_MENU, self.textDnDTarget.delete_all, self.clearall)
        self.Bind(wx.EVT_MENU, self.main_setup_dlg, self.setupItem)
        # ----TOOLS----
        self.Bind(wx.EVT_MENU, self.reminder, notepad)
        # ---- VIEW ----
        self.Bind(wx.EVT_MENU, self.get_ytdlp_version, self.ydlused)
        # ----HELP----
        self.Bind(wx.EVT_MENU, self.helpme, helpItem)
        self.Bind(wx.EVT_MENU, self.system_vers, sysinfo)
        self.Bind(wx.EVT_MENU, self.view_logs, viewlogs)
        self.Bind(wx.EVT_MENU, self.issues, issueItem)
        self.Bind(wx.EVT_MENU, self.contribute, contribution)
        self.Bind(wx.EVT_MENU, self.sponsor_this_project, spons)
        self.Bind(wx.EVT_MENU, self.donate_to_dev, donat)
        self.Bind(wx.EVT_MENU, self.about_vidtuber, infoItem)
        self.Bind(wx.EVT_MENU, self.check_new_releases, chklatest)

    # --------Menu Bar Event handler (callbacks)

    def openMydownload(self, event):
        """
        Open the download dir using default file manager
        """
        io_tools.openpath(self.appdata['dirdownload'])
    # -------------------------------------------------------------------#

    def quiet_app(self, event):
        """
        destroy the application.
        """
        self.on_close(self)
    # -------------------------------------------------------------------#

    def reminder(self, event):
        """
        Call `io_tools.openpath` to open a 'user_memos.txt' file
        with default GUI text editor.
        """
        fname = os.path.join(self.appdata['confdir'], 'user_memos.txt')

        if os.path.exists(fname) and os.path.isfile(fname):
            io_tools.openpath(fname)
        else:
            with open(fname, "w", encoding='utf-8') as text:
                text.write("")
            io_tools.openpath(fname)
    # ------------------------------------------------------------------#

    def get_ytdlp_version(self, event):
        """
        Displays a dialog box that gathers useful information about yt-dlp.
        """
        pkg_version = 'Not found' if not self.ytdl_pkg() else self.ytdl_pkg()

        execpath = wx.GetApp().appset['ytdlp-exec-path']
        exec_version = io_tools.youtubedl_get_executable_version(execpath)

        latest = self.ydl_latest()
        url = '<https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest>'
        wx.MessageBox(_("- Version of the package currently used: {0}\n"
                        "- Executable version currently used: {1}\n"
                        "Latest version available on github.com: {2}\n"
                        "{3}").format(pkg_version, exec_version, latest, url),
                      _('Vidtuber - About «yt-dlp»'),
                      wx.ICON_INFORMATION, self)
    # ------------------------------------------------------------------#

    def ytdl_pkg(self):
        """
        Retrieve the version of yt_dlp from Python package
        currently used.
        """
        if wx.GetApp().appset['yt_dlp'] is True:
            return yt_dlp.version.__version__
        return None
    # -----------------------------------------------------------------#

    def ydl_latest(self):
        """
        Check the latest version of yt-dlp available on github.com
        """
        url = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
        latest = io_tools.get_github_releases(url, "tag_name")
        if latest[0] in ['request error:', 'response error:']:
            return f"{latest[0]} {latest[1]}"
        return latest[0]
    # -----------------------------------------------------------------#

    def on_outputdir(self, event):
        """
        Button event to set a new destination directory.
        """
        dialdir = wx.DirDialog(self, _("Choose Destination"),
                               self.appdata['dirdownload'],
                               wx.DD_DEFAULT_STYLE
                               )
        if dialdir.ShowModal() == wx.ID_OK:
            getpath = self.appdata['getpath'](dialdir.GetPath())
            self.textDnDTarget.on_file_save(getpath)
            self.appdata['dirdownload'] = getpath

            confmanager = ConfigManager(self.appdata['fileconfpath'])
            sett = confmanager.read_options()
            sett['dirdownload'] = self.appdata['dirdownload']
            confmanager.write_options(**sett)
            dialdir.Destroy()
    # ------------------------------------------------------------------#

    def main_setup_dlg(self, event):
        """
        Calls user settings dialog. Note, this dialog is
        handle like filters dialogs on Vidtuber, being need
        to get the return code from getvalue interface.
        """
        msg = _("Some changes require restarting the application.")
        with settings_vidtuber.SetUp(self) as set_up:
            if set_up.ShowModal() == wx.ID_OK:
                changes = set_up.getvalue()
                if [x for x in changes if x is False]:
                    if wx.MessageBox(_("{0}\n\nDo you want to restart "
                                       "the application now?").format(msg),
                                     _('Restart Vidtuber?'), wx.ICON_QUESTION
                                     | wx.CANCEL | wx.YES_NO, self) == wx.YES:
                        self.appdata['auto-restart-app'] = True
                        self.on_Kill()
    # ------------------------------------------------------------------#
    # --------- Menu Help  ###

    def helpme(self, event):
        """
        Online User guide: Open default web browser via Python
        Web-browser controller.
        see <https://docs.python.org/3.8/library/webbrowser.html>
        """
        page = 'https://github.com/jeanslack/Vidtuber'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def system_vers(self, event):
        """
        Get system version
        """
        wx.MessageBox(info_this_platform(), "Vidtuber",
                      wx.ICON_INFORMATION, self)
    # -------------------------------------------------------------------#

    def view_logs(self, event, flog=None):
        """
        Show to view log files dialog
        flog: filename to select on showlog if any.
        """
        if self.showlogs:
            self.showlogs.Raise()
            return

        self.showlogs = ShowLogs(self,
                                 self.appdata['logdir'],
                                 self.appdata['ostype'],
                                 )
        self.showlogs.Show()
    # ------------------------------------------------------------------#

    def issues(self, event):
        """Display Issues page on github"""
        page = 'https://github.com/jeanslack/Vidtuber/issues'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def contribute(self, event):
        """Display contribute web page"""
        page = 'https://github.com/jeanslack/Vidtuber/pulls'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def sponsor_this_project(self, event):
        """Go to sponsor page"""
        page = 'https://github.com/sponsors/jeanslack'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def donate_to_dev(self, event):
        """Go to donation page"""
        page = 'https://www.paypal.me/GPernigotto'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def about_vidtuber(self, event):
        """
        Display the program informations and developpers
        """
        about_dialog.show_about_dlg(self, self.icons['vidtuber'])
    # ------------------------------------------------------------------#

    def show_infoprog(self, event):
        """
        Display the program informations and developpers
        """
        infoprg.info_gui(self, self.icons['vidtuber'])
    # ------------------------------------------------------------------#

    def check_new_releases(self, event):
        """
        Compare the FFaudiocue version with a given
        new version found on github.
        """
        this = VERSION  # this version
        url = ("https://api.github.com/repos/jeanslack/"
               "Vidtuber/releases/latest")

        vers = io_tools.get_github_releases(url, "tag_name")
        if vers[0] in ['request error:', 'response error:']:
            if str(vers[1]) == "'tag_name'":
                msg = _('No publications found!\nERROR: tag_name')
                dlg = check_new_version.CheckNewVersion(self, msg, VERSION,
                                                        VERSION)
                dlg.ShowModal()
                return
            wx.MessageBox(f"{vers[0]} {vers[1]}", f"{vers[0]}",
                          wx.ICON_ERROR, self)
            return

        vers = vers[0].split('v')[1]
        newmajor, newminor, newmicro = vers.split('.')
        new_vers = int(f'{newmajor}{newminor}{newmicro}')
        major, minor, micro = this.split('.')
        this_vers = int(f'{major}{minor}{micro}')

        if new_vers > this_vers:
            msg = _('A new release is available - '
                    'v.{0}\n').format(vers)
        elif this_vers > new_vers:
            msg = _('You are using a development version '
                    'that has not yet been released!\n')
        else:
            msg = _('Congratulation! You are already '
                    'using the latest version.\n')
        dlg = check_new_version.CheckNewVersion(self, msg, vers, this)
        dlg.ShowModal()
    # -------------------------------------------------------------------#

    # -----------------  BUILD THE TOOL BAR  --------------------###

    def toolbar_pos(self):
        """
        Return the toolbar style
        """
        if self.appdata['toolbarpos'] == 0:  # on top
            return wx.TB_TEXT

        if self.appdata['toolbarpos'] == 1:  # on bottom
            return wx.TB_TEXT | wx.TB_BOTTOM

        if self.appdata['toolbarpos'] == 2:  # on right
            return wx.TB_TEXT | wx.TB_RIGHT

        if self.appdata['toolbarpos'] == 3:
            return wx.TB_TEXT | wx.TB_LEFT

        return None
    # ------------------------------------------------------------------#

    def vidtuber_tool_bar(self):
        """
        Makes and attaches the toolsBtn bar.
        To enable or disable styles, use method `SetWindowStyleFlag`
        e.g.
            self.toolbar.SetWindowStyleFlag(wx.TB_NODIVIDER | wx.TB_FLAT)
        """
        style = self.toolbar_pos()
        self.toolbar = self.CreateToolBar(style=style)
        bmp_size = (int(self.appdata['toolbarsize']),
                    int(self.appdata['toolbarsize']))
        self.toolbar.SetToolBitmapSize(bmp_size)

        if 'wx.svg' in sys.modules:  # available only in wx version 4.1 to up
            bmpback = get_bmp(self.icons['previous'], bmp_size)
            bmpnext = get_bmp(self.icons['next'], bmp_size)
            bmpstat = get_bmp(self.icons['statistics'], bmp_size)
            bmpydl = get_bmp(self.icons['download'], bmp_size)
            bmpstop = get_bmp(self.icons['stop'], bmp_size)
            bmpopt = get_bmp(self.icons['options'], bmp_size)

        else:
            bmpback = wx.Bitmap(self.icons['previous'], wx.BITMAP_TYPE_ANY)
            bmpnext = wx.Bitmap(self.icons['next'], wx.BITMAP_TYPE_ANY)
            bmpstat = wx.Bitmap(self.icons['statistics'], wx.BITMAP_TYPE_ANY)
            bmpydl = wx.Bitmap(self.icons['download'], wx.BITMAP_TYPE_ANY)
            bmpstop = wx.Bitmap(self.icons['stop'], wx.BITMAP_TYPE_ANY)
            bmpopt = wx.Bitmap(self.icons['options'], wx.BITMAP_TYPE_ANY)

        self.toolbar.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL,
                                     wx.NORMAL, 0, ""))

        tip = _("Go to the previous panel")
        back = self.toolbar.AddTool(20, _('Back'),
                                    bmpback,
                                    tip, wx.ITEM_NORMAL,
                                    )
        tip = _("Go to the next panel")
        forward = self.toolbar.AddTool(21, _('Next'),
                                       bmpnext,
                                       tip, wx.ITEM_NORMAL,
                                       )
        tip = _("Shows statistics and information")
        self.btn_ydlstatistics = self.toolbar.AddTool(22, _('Statistics'),
                                                      bmpstat,
                                                      tip, wx.ITEM_NORMAL,
                                                      )
        tip = _("yt-dlp options setting")
        options = self.toolbar.AddTool(26, _('Options'),
                                       bmpopt, tip, wx.ITEM_NORMAL)
        tip = _("Start downloading")
        self.run_download = self.toolbar.AddTool(23, _('Download'),
                                                 bmpydl, tip, wx.ITEM_NORMAL,
                                                 )
        tip = _("Stops current process")
        stop = self.toolbar.AddTool(24, _('Stop'), bmpstop,
                                    tip, wx.ITEM_NORMAL,
                                    )
        self.toolbar.Realize()

        # ----------------- Tool Bar Binding (evt)-----------------------#
        self.Bind(wx.EVT_TOOL, self.click_start, self.run_download)
        self.Bind(wx.EVT_TOOL, self.on_back, back)
        self.Bind(wx.EVT_TOOL, self.on_forward, forward)
        self.Bind(wx.EVT_TOOL, self.on_statistics, self.btn_ydlstatistics)
        self.Bind(wx.EVT_TOOL, self.click_stop, stop)
        self.Bind(wx.EVT_TOOL, self.on_options, options)

    # --------------- Tool Bar Callback (event handler) -----------------#

    def on_back(self, event):
        """
        Return to the previous panel.
        """
        if self.ProcessPanel.IsShown():
            self.panelShown()
            return

        if self.ytDownloader.IsShown():
            self.switch_text_import(self)
            return
    # ------------------------------------------------------------------#

    def on_forward(self, event):
        """
        redirect to corresponding next panel
        """
        if self.ytDownloader.IsShown():
            self.switch_to_processing('Viewing last log')
            return
        self.switch_youtube_downloader(self)
        self.changed = False
    # ------------------------------------------------------------------#

    def on_statistics(self, event):
        """
        Redirect input files at stream_info for media information
        """
        if self.infomediadlg:
            self.infomediadlg.Raise()
            return

        info = []
        if self.data_url:
            info = self.ytDownloader.on_show_statistics()
            if not info:
                return

        self.infomediadlg = YdlMediaInfo(info)
        self.infomediadlg.Show()
    # ------------------------------------------------------------------#

    def on_options(self, event):
        """
        Setting dialog event.
        """
        with YtdlpSettings(self) as set_up:
            if set_up.ShowModal() == wx.ID_OK:
                self.textDnDTarget.on_file_save(self.appdata['dirdownload'])
    # ------------------------------------------------------------------#

    def switch_text_import(self, event):
        """
        Show URLs import panel.
        """
        self.ProcessPanel.Hide()
        self.ytDownloader.Hide()
        self.textDnDTarget.Show()
        (self.delete.Enable(True),
         self.paste.Enable(True),
         self.clearall.Enable(True)
         )
        self.toolbar.EnableTool(21, True)
        [self.toolbar.EnableTool(x, False) for x in (20, 22, 23, 24)]
        self.toolbar.Realize()
        self.Layout()
        self.statusbar_msg(_('Ready'), None)
        self.SetTitle(_('Vidtuber - List of URLs'))
    # ------------------------------------------------------------------#

    def switch_youtube_downloader(self, event):
        """
        Show youtube-dl downloader panel
        """
        self.ytDownloader.clear_data_list(self.changed)
        self.SetTitle(_('Vidtuber - YouTube Downloader'))
        self.textDnDTarget.Hide()
        self.ytDownloader.Show()
        (self.delete.Enable(False),
         self.paste.Enable(False),
         self.clearall.Enable(False)
         )
        [self.toolbar.EnableTool(x, True) for x in (20, 21, 22, 23)]
        self.toolbar.EnableTool(24, False)
        self.Layout()
    # ------------------------------------------------------------------#

    def switch_to_processing(self, *args):
        """
        Preparing to processing
        """
        if args[0] == 'Viewing last log':
            self.statusbar_msg(_('Viewing last log'), None)
            [self.toolbar.EnableTool(x, False) for x in (21, 24)]
            [self.toolbar.EnableTool(x, True) for x in (20, 22, 23)]

        elif args[0] == 'YouTube Downloader':
            (self.delete.Enable(False),
             self.paste.Enable(False),
             self.clearall.Enable(False),
             self.setupItem.Enable(False)
             )
            [self.toolbar.EnableTool(x, False) for x in (20, 21, 23, 26)]
            [self.toolbar.EnableTool(x, True) for x in (22, 24)]

        self.SetTitle(_('Vidtuber - Downloader Message Monitoring'))
        self.textDnDTarget.Hide()
        self.ytDownloader.Hide()
        self.ProcessPanel.Show()
        self.Layout()
        self.ProcessPanel.topic_thread(args, self.data_url)
    # ------------------------------------------------------------------#

    def click_start(self, event):
        """
        By clicking on Download buttons, calls the
        `ytDownloader.on_start()` method, which calls the
        'switch_to_processing' method above.
        """
        if self.ytDownloader.IsShown() or self.ProcessPanel.IsShown():
            if not self.data_url:
                self.switch_text_import(self)
                return
            if check_destination_dir(self.appdata['dirdownload']):
                return
            self.ytDownloader.on_start()
            return
    # ------------------------------------------------------------------#

    def click_stop(self, event):
        """
        Stop/Abort the current process
        """
        if self.ProcessPanel.IsShown():
            if self.ProcessPanel.thread_type:
                self.ProcessPanel.on_stop()
    # ------------------------------------------------------------------#

    def process_terminated(self, msg):
        """
        Process report terminated. This method is called using
        pub/sub protocol. see `long_processing_task.end_proc()`)
        """
        self.toolbar.EnableTool(20, True)
        self.toolbar.EnableTool(24, False)
        self.toolbar.EnableTool(26, True)
        self.toolbar.EnableTool(23, True)
        self.setupItem.Enable(True)

        #if self.appdata['shutdown']:
            #self.parent.auto_shutdown()
        #elif self.appdata['auto_exit']:
            #self.parent.auto_exit()
    # ------------------------------------------------------------------#

    def panelShown(self):
        """
        Clicking 'Back button' from the `long_processing_task` panel,
        retrieval at previous panel (see `switch_to_processing`
        method above).
        """
        self.ProcessPanel.Hide()
        self.switch_youtube_downloader(self)
        self.Layout()
    # ------------------------------------------------------------------#

    def auto_shutdown(self):
        """
        Turn off the system when processing is finished
        """
        if self.checks_running_processes():
            return

        self.write_option_before_exit()

        msgdlg = _('The system will turn off in {0} seconds')
        title = _('Vidtuber - Shutdown!')
        dlg = CountDownDlg(self, timeout=59, message=msgdlg, caption=title)
        res = dlg.ShowModal() == wx.ID_OK
        dlg.Destroy()
        if res:
            succ = shutdown_system(self.appdata['sudo_password'])
            if not succ:
                msg = (_("Error while shutting down. Please see "
                         "file log for details."))
                wx.LogError(msg)
    # ------------------------------------------------------------------#

    def auto_exit(self):
        """
        Auto-exit the application when processing is finished
        """
        if self.checks_running_processes():
            return

        msgdlg = _('Exiting the application in {0} seconds')
        title = _('Vidtuber - Exiting!')
        dlg = CountDownDlg(self, timeout=10, message=msgdlg, caption=title)
        res = dlg.ShowModal() == wx.ID_OK
        dlg.Destroy()
        if res:
            self.write_option_before_exit()
            self.destroy_orphaned_window()
            self.destroy_application()
