# -*- coding: UTF-8 -*-
"""
Name: main_frame.py
Porpose: top window main frame
Compatibility: Python3, wxPython Phoenix
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
import os
import sys
from urllib.parse import urlparse
import webbrowser
import wx
from pubsub import pub
import yt_dlp
from vidtuber.vdms_utils.get_bmpfromsvg import get_bmp
from vidtuber.vdms_dialogs import preferences
from vidtuber.vdms_dialogs import infoprg
from vidtuber.vdms_dialogs import vidtuber_check_version
from vidtuber.vdms_dialogs.showlogs import ShowLogs
from vidtuber.vdms_dialogs.ydl_mediainfo import YdlMediaInfo
from vidtuber.vdms_panels import textdrop
from vidtuber.vdms_panels import youtubedl_ui
from vidtuber.vdms_panels.long_processing_task import LogOut
from vidtuber.vdms_io import io_tools
from vidtuber.vdms_sys.msg_info import current_release
from vidtuber.vdms_sys.settings_manager import ConfigManager
from vidtuber.vdms_sys.argparser import info_this_platform


class MainFrame(wx.Frame):
    """
    This is the main frame top window for panels implementation.
    """
    # colour rappresentetion in rgb
    AZURE_NEON = 158, 201, 232
    YELLOW_LMN = 255, 255, 0
    BLUE = 0, 7, 12
    # set widget colours with html rappresentation:
    ORANGE = '#f28924'
    YELLOW = '#bd9f00'
    LIMEGREEN = '#87A615'
    DARK_BROWN = '#262222'
    WHITE = '#fbf4f4'
    BLACK = '#060505'
    # AZURE = '#d9ffff'  # rgb form (wx.Colour(217,255,255))
    # RED = '#ea312d'
    # GREENOLIVE = '#6aaf23'
    # GREEN = '#268826'
    # -------------------------------------------------------------#

    def __init__(self):
        """
        If not data_url ytDownloader panel will be disabled
        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.icons = get.iconset
        # -------------------------------#
        self.data_url = None  # list of urls in text box
        self.filedldir = None  # download file destination dir
        self.infomediadlg = False  # media info dialog
        self.showlogdlg = False

        wx.Frame.__init__(self, None, -1, style=wx.DEFAULT_FRAME_STYLE)

        # ---------- panel instances:
        self.ytDownloader = youtubedl_ui.Downloader(self)
        self.textDnDTarget = textdrop.TextDnD(self)
        self.ProcessPanel = LogOut(self)
        # hide panels
        self.ProcessPanel.Hide()
        self.ytDownloader.Hide()
        self.textDnDTarget.Show()
        # Layout toolbar buttons:
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)  # sizer base global
        # Layout external panels:
        self.mainSizer.Add(self.textDnDTarget, 1, wx.EXPAND)
        self.mainSizer.Add(self.ytDownloader, 1, wx.EXPAND)
        self.mainSizer.Add(self.ProcessPanel, 1, wx.EXPAND)

        # ----------------------Set Properties----------------------#
        self.SetTitle("Vidtuber")
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(self.icons['vidtuber'],
                                      wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        self.SetMinSize((850, 560))
        self.SetSizer(self.mainSizer)
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
        [self.toolbar.EnableTool(x, False) for x in (3, 13, 18)]
        self.Layout()
        # ---------------------- Binding (EVT) ----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_outputdir)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        pub.subscribe(self.check_modeless_window, "DESTROY_ORPHANED_WINDOWS")
        pub.subscribe(self.process_terminated, "PROCESS TERMINATED")

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

    def choosetopicRetrieve(self):
        """
        Retrieve to choose topic panel
        """

        if self.ytDownloader.IsShown():
            self.ytDownloader.Hide()
            self.textDnDTarget.Show()

            self.ydlpan.Enable(False)

            self.SetTitle(_('Vidtuber'))
            self.statusbar_msg(_('Ready'), None)
            self.Layout()
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
            self.showlogdlg.Destroy()
            self.showlogdlg = False
    # ------------------------------------------------------------------#

    def destroy_orphaned_window(self):
        """
        Destroys all orphaned modeless windows,
        ie. on application exit or on editing URLs text.
        """
        if self.infomediadlg:
            self.infomediadlg.Destroy()
            self.infomediadlg = False
        if self.showlogdlg:
            self.showlogdlg.Destroy()
            self.showlogdlg = False

    # ---------------------- Event handler (callback) ------------------#

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

        self.infomediadlg = YdlMediaInfo(info, self.appdata['ostype'])
        self.infomediadlg.Show()
    # ------------------------------------------------------------------#

    def on_close(self, event):
        """
        switch to panels or destroy the vidtuber app.

        """
        def _setsize():
            """
            Write last window size and position
            for next start if changed
            """
            confmanager = ConfigManager(self.appdata['fileconfpath'])
            sett = confmanager.read_options()
            sett['window_size'] = list(self.GetSize())
            sett['window_position'] = list(self.GetPosition())
            confmanager.write_options(**sett)

        if self.ProcessPanel.IsShown():
            self.ProcessPanel.on_close(self)
        else:
            if self.appdata['warnexiting']:
                if wx.MessageBox(_('Are you sure you want to exit?'),
                                 _('Exit'), wx.ICON_QUESTION | wx.YES_NO,
                                 self) == wx.NO:
                    return
            _setsize()
            self.destroy_orphaned_window()
            self.Destroy()
    # ------------------------------------------------------------------#

    def on_Kill(self):
        """
        Try to kill application during a process thread
        that does not want to terminate with the abort button

        """
        self.destroy_orphaned_window()
        self.Destroy()

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
        dscrp = (_("Downloads folder\tCtrl+D"),
                 _("Open the default downloads folder"))
        fold_downloads = fileButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        fileButton.AppendSeparator()
        dscrp = (_("Open temporary downloads"),
                 _("Open the temporary downloads folder"))
        self.fold_downloads_tmp = fileButton.Append(wx.ID_ANY, dscrp[0],
                                                    dscrp[1])
        self.fold_downloads_tmp.Enable(False)
        fileButton.AppendSeparator()
        dscrp = (_("Work Notes\tCtrl+N"),
                 _("Read and write useful notes and reminders."))
        notepad = fileButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        fileButton.AppendSeparator()
        exitItem = fileButton.Append(wx.ID_EXIT, _("Exit\tCtrl+Q"),
                                     _("Close Vidtuber"))
        self.menuBar.Append(fileButton, _("File"))

        # ------------------ View menu
        viewButton = wx.Menu()
        dscrp = (_("Version in Use"),
                 _("Shows the version in use"))
        self.ydlused = viewButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        dscrp = (_("Show the latest version..."),
                 _("Shows the latest version available on github.com"))
        self.ydllatest = viewButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        # timeline
        viewButton.AppendSeparator()
        dscrp = (_("Show Logs\tCtrl+L"),
                 _("Viewing log messages"))
        viewlogs = viewButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        self.menuBar.Append(viewButton, _("View"))

        # ------------------ setup menu
        setupButton = wx.Menu()

        dscrp = (_("Set up a temporary folder for downloads"),
                 _("Save all downloads to this temporary location"))
        setdownload_tmp = setupButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        setupButton.AppendSeparator()
        dscrp = (_("Restore the default destination folders"),
                 _("Restore the default folders for file conversions "
                   "and downloads"))
        self.resetfolders_tmp = setupButton.Append(wx.ID_ANY, dscrp[0],
                                                   dscrp[1])
        self.resetfolders_tmp.Enable(False)
        setupButton.AppendSeparator()
        setupItem = setupButton.Append(wx.ID_PREFERENCES,
                                       _("Preferences\tCtrl+P"),
                                       _("Application preferences"))
        self.menuBar.Append(setupButton, _("Settings"))

        # ------------------ help menu
        helpButton = wx.Menu()
        helpItem = helpButton.Append(wx.ID_HELP, _("User Guide"), "")
        wikiItem = helpButton.Append(wx.ID_ANY, _("Wiki"), "")
        helpButton.AppendSeparator()
        issueItem = helpButton.Append(wx.ID_ANY, _("Issue tracker"), "")
        helpButton.AppendSeparator()
        transItem = helpButton.Append(wx.ID_ANY, _('Translation...'), '')
        helpButton.AppendSeparator()
        DonationItem = helpButton.Append(wx.ID_ANY, _("Donation"), "")
        helpButton.AppendSeparator()
        helpButton.AppendSeparator()
        dscrp = (_("Check for newer version"),
                 _("Check for the latest Vidtuber version at "
                   "<https://pypi.org/project/vidtuber/>"))
        checkItem = helpButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        helpButton.AppendSeparator()
        dscrp = (_("System version"),
                 _("Get version about your operating system, version of "
                   "Python and wxPython."))
        sysinfo = helpButton.Append(wx.ID_ANY, dscrp[0], dscrp[1])
        infoItem = helpButton.Append(wx.ID_ABOUT, _("About Vidtuber"), "")
        self.menuBar.Append(helpButton, _("Help"))

        self.SetMenuBar(self.menuBar)

        # -----------------------Binding menu bar-------------------------#
        # ----FILE----
        self.Bind(wx.EVT_MENU, self.openMydownload, fold_downloads)
        self.Bind(wx.EVT_MENU, self.openMydownloads_tmp,
                  self.fold_downloads_tmp)
        self.Bind(wx.EVT_MENU, self.reminder, notepad)
        self.Bind(wx.EVT_MENU, self.quiet, exitItem)
        # ---- VIEW ----
        self.Bind(wx.EVT_MENU, self.ydl_used, self.ydlused)
        self.Bind(wx.EVT_MENU, self.ydl_latest, self.ydllatest)
        self.Bind(wx.EVT_MENU, self.view_logs, viewlogs)
        # ----SETUP----
        self.Bind(wx.EVT_MENU, self.on_outputdir, setdownload_tmp)
        self.Bind(wx.EVT_MENU, self.on_resetfolders_tmp, self.resetfolders_tmp)
        self.Bind(wx.EVT_MENU, self.setup, setupItem)
        # ----HELP----
        self.Bind(wx.EVT_MENU, self.helpme, helpItem)
        self.Bind(wx.EVT_MENU, self.wiki, wikiItem)
        self.Bind(wx.EVT_MENU, self.issues, issueItem)
        self.Bind(wx.EVT_MENU, self.translations, transItem)
        self.Bind(wx.EVT_MENU, self.donation, DonationItem)
        self.Bind(wx.EVT_MENU, self.checknewreleases, checkItem)
        self.Bind(wx.EVT_MENU, self.system_vers, sysinfo)
        self.Bind(wx.EVT_MENU, self.info, infoItem)

    # --------Menu Bar Event handler (callback)
    # --------- Menu  Files

    def openMydownload(self, event):
        """
        Open the download folder with file manager

        """
        io_tools.openpath(self.appdata['dirdownload'])
    # -------------------------------------------------------------------#

    def openMydownloads_tmp(self, event):
        """
        Open the temporary download folder with file manager

        """
        io_tools.openpath(self.filedldir)
    # -------------------------------------------------------------------#

    def quiet(self, event):
        """
        destroy the vidtuber.
        """
        self.on_close(self)
    # -------------------------------------------------------------------#
    # --------- Menu Tools  ##

    def reminder(self, event):
        """
        Call `io_tools.openpath` to open a 'user_memos.txt' file
        with default GUI text editor.
        """
        fname = os.path.join(self.appdata['confdir'], 'user_memos.txt')

        if os.path.exists(fname) and os.path.isfile(fname):
            io_tools.openpath(fname)
        else:
            try:
                with open(fname, "w", encoding='utf8') as text:
                    text.write("")
            except Exception as err:
                wx.MessageBox(_("Unexpected error while creating file:\n\n"
                                "{0}").format(err),
                              'Vidtuber', wx.ICON_ERROR, self)
            else:
                io_tools.openpath(fname)
    # ------------------------------------------------------------------#
    # --------- Menu View ###

    def ydl_used(self, event, msgbox=True):
        """
        check version of youtube-dl used from
        'Version in Use' bar menu
        """
        this = yt_dlp.version.__version__
        if msgbox:
            wx.MessageBox(_("You are using '{0}' version {1}"
                            ).format(self.appdata['downloader'], this),
                          'Vidtuber', wx.ICON_INFORMATION, self)
            return this
        return None
    # -----------------------------------------------------------------#

    def ydl_latest(self, event):
        """
        check for new version from github.com

        """
        if self.appdata['downloader'] == 'youtube_dl':
            url = ("https://api.github.com/repos/ytdl-org/youtube-dl"
                   "/releases/latest")
        elif self.appdata['downloader'] == 'yt_dlp':
            url = ("https://api.github.com/repos/yt-dlp/yt-dlp/"
                   "releases/latest")

        latest = io_tools.get_github_releases(url, "tag_name")

        if latest[0] in ['request error:', 'response error:']:
            wx.MessageBox(f"{latest[0]} {latest[1]}",
                          f"{latest[0]}", wx.ICON_ERROR, self)
            return
        wx.MessageBox(_("{0}: Latest version available: {1}").format(
                      self.appdata['downloader'], latest[0]),
                      "Vidtuber", wx.ICON_INFORMATION, self)
    # -----------------------------------------------------------------#

    def view_logs(self, event):
        """
        Show miniframe to view log files
        """
        if self.showlogdlg:
            self.showlogdlg.Raise()
            return

        self.showlogdlg = ShowLogs(self,
                                   self.appdata['logdir'],
                                   self.appdata['ostype']
                                   )
        self.showlogdlg.Show()
    # ------------------------------------------------------------------#

    # --------- Menu  Preferences  ###

    def on_outputdir(self, event):
        """
        This is a menu event but also intercept the button 'save'
        event in the textdrop panel and sets a new file destination
        path for downloading

        """
        dpath = '' if not self.filedldir else self.filedldir
        dialdir = wx.DirDialog(self, _("Choose a temporary destination for "
                                       "downloads"), dpath,
                               wx.DD_DEFAULT_STYLE
                               )
        if dialdir.ShowModal() == wx.ID_OK:
            getpath = self.appdata['getpath'](dialdir.GetPath())
            self.filedldir = getpath
            self.textDnDTarget.on_file_save(self.filedldir)
            self.textDnDTarget.file_dest = self.filedldir

            dialdir.Destroy()

            self.resetfolders_tmp.Enable(True)
            self.fold_downloads_tmp.Enable(True)
    # ------------------------------------------------------------------#

    def on_resetfolders_tmp(self, event):
        """
        Restore the default file destination if saving temporary
        files has been set.

        """
        self.filedldir = self.appdata['dirdownload']
        self.textDnDTarget.on_file_save(self.appdata['dirdownload'])
        self.textDnDTarget.file_dest = self.appdata['dirdownload']
        self.fold_downloads_tmp.Enable(False)

        self.resetfolders_tmp.Enable(False)

        wx.MessageBox(_("Default destination folders successfully restored"),
                      "Vidtuber", wx.ICON_INFORMATION, self)
    # ------------------------------------------------------------------#

    def setup(self, event):
        """
        Calls user settings dialog. Note, this dialog is
        handle like filters dialogs on Vidtuber, being need
        to get the return code from getvalue interface.
        """
        with preferences.SetUp(self) as set_up:
            if set_up.ShowModal() == wx.ID_OK:
                if set_up.getvalue():
                    self.on_Kill()

    # --------- Menu Help  ###

    def helpme(self, event):
        """
        Online User guide: Open default web browser via Python
        Web-browser controller.
        see <https://docs.python.org/3.8/library/webbrowser.html>
        """
        page = 'https://jeanslack.github.io/Vidtuber/vidtuber_use.html'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def wiki(self, event):
        """Wiki page """
        page = 'https://github.com/jeanslack/Vidtuber/wiki'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def issues(self, event):
        """Display Issues page on github"""
        page = 'https://github.com/jeanslack/Vidtuber/issues'
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def translations(self, event):
        """Display translation how to on github"""
        page = ('https://jeanslack.github.io/Vidtuber/Pages/'
                'Localization_Guidelines.html')
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def donation(self, event):
        """Display donation page on github"""
        page = ('https://jeanslack.github.io/Vidtuber/Contribute.html'
                '#donations')
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def docffmpeg(self, event):
        """Display FFmpeg page documentation"""
        page = 'https://www.ffmpeg.org/documentation.html'
        webbrowser.open(page)
    # -------------------------------------------------------------------#

    def checknewreleases(self, event):
        """
        Compare the Vidtuber version with a given
        new version found on github.
        """
        this = current_release()  # this version
        url = ("https://api.github.com/repos/jeanslack/"
               "Vidtuber/releases/latest")
        version = io_tools.get_github_releases(url, "tag_name")

        if version[0] in ['request error:', 'response error:']:
            wx.MessageBox(f"{version[0]} {version[1]}",
                          f"{version[0]}", wx.ICON_ERROR, self)
            return

        version = version[0].split('v')[1]
        newmajor, newminor, newmicro = version.split('.')
        new_version = int(f'{newmajor}{newminor}{newmicro}')
        major, minor, micro = this[2].split('.')
        this_version = int(f'{major}{minor}{micro}')

        if new_version > this_version:
            msg = _('A new release is available - '
                    'v.{0}\n').format(version)
        elif this_version > new_version:
            msg = _('You are using a development version '
                    'that has not yet been released!\n')
        else:
            msg = _('Congratulation! You are already '
                    'using the latest version.\n')

        dlg = vidtuber_check_version.CheckNewVersion(self,
                                                     msg,
                                                     version,
                                                     this[2]
                                                     )
        dlg.ShowModal()
    # -------------------------------------------------------------------#

    def system_vers(self, event):
        """
        Get system version
        """
        wx.MessageBox(info_this_platform(), "Vidtuber",
                      wx.ICON_INFORMATION, self)
    # -------------------------------------------------------------------#

    def info(self, event):
        """
        Display the program informations and developpers
        """
        infoprg.info(self, self.icons['vidtuber'])

    # -----------------  BUILD THE TOOL BAR  --------------------###

    def vidtuber_tool_bar(self):
        """
        Makes and attaches the toolsBtn bar.
        To enable or disable styles, use method `SetWindowStyleFlag`
        e.g.

            self.toolbar.SetWindowStyleFlag(wx.TB_NODIVIDER | wx.TB_FLAT)
        """
        if self.appdata['toolbarpos'] == 0:  # on top
            if self.appdata['toolbartext']:  # show text
                style = wx.TB_TEXT | wx.TB_HORZ_LAYOUT | wx.TB_HORIZONTAL
            else:
                style = wx.TB_DEFAULT_STYLE

        elif self.appdata['toolbarpos'] == 1:  # on bottom
            if self.appdata['toolbartext']:  # show text
                style = wx.TB_TEXT | wx.TB_HORZ_LAYOUT | wx.TB_BOTTOM
            else:
                style = wx.TB_DEFAULT_STYLE | wx.TB_BOTTOM

        elif self.appdata['toolbarpos'] == 2:  # on right
            if self.appdata['toolbartext']:  # show text
                style = wx.TB_TEXT | wx.TB_RIGHT
            else:
                style = wx.TB_DEFAULT_STYLE | wx.TB_RIGHT

        elif self.appdata['toolbarpos'] == 3:
            if self.appdata['toolbartext']:  # show text
                style = wx.TB_TEXT | wx.TB_LEFT
            else:
                style = wx.TB_DEFAULT_STYLE | wx.TB_LEFT

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
            bmpclear = get_bmp(self.icons['clear'], bmp_size)

        else:
            bmpback = wx.Bitmap(self.icons['previous'], wx.BITMAP_TYPE_ANY)
            bmpnext = wx.Bitmap(self.icons['next'], wx.BITMAP_TYPE_ANY)
            bmpstat = wx.Bitmap(self.icons['statistics'], wx.BITMAP_TYPE_ANY)
            bmpydl = wx.Bitmap(self.icons['download'], wx.BITMAP_TYPE_ANY)
            bmpstop = wx.Bitmap(self.icons['stop'], wx.BITMAP_TYPE_ANY)
            bmpclear = wx.Bitmap(self.icons['clear'], wx.BITMAP_TYPE_ANY)

        self.toolbar.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL,
                                     wx.NORMAL, 0, ""))

        tip = _("Go to the previous panel")
        back = self.toolbar.AddTool(3, _('Back'),
                                    bmpback,
                                    tip, wx.ITEM_NORMAL,
                                    )
        tip = _("Go to the next panel")
        forward = self.toolbar.AddTool(4, _('Next'),
                                       bmpnext,
                                       tip, wx.ITEM_NORMAL,
                                       )
        tip = _("Shows statistics and information")
        self.btn_ydlstatistics = self.toolbar.AddTool(14, _('Statistics'),
                                                      bmpstat,
                                                      tip, wx.ITEM_NORMAL,
                                                      )
        tip = _("Start downloading")
        self.run_download = self.toolbar.AddTool(13, _('Download'),
                                                 bmpydl,
                                                 tip, wx.ITEM_NORMAL,
                                                 )
        tip = _("Stops current process")
        stop = self.toolbar.AddTool(18, _('Stop'), bmpstop,
                                    tip, wx.ITEM_NORMAL,
                                    )
        tip = _("Clear the URL list")
        clear = self.toolbar.AddTool(20, _('Clear'), bmpclear,
                                     tip, wx.ITEM_NORMAL,
                                     )
        self.toolbar.Realize()

        # ----------------- Tool Bar Binding (evt)-----------------------#
        self.Bind(wx.EVT_TOOL, self.click_start, self.run_download)
        self.Bind(wx.EVT_TOOL, self.on_back, back)
        self.Bind(wx.EVT_TOOL, self.on_forward, forward)
        self.Bind(wx.EVT_TOOL, self.on_statistics, self.btn_ydlstatistics)
        self.Bind(wx.EVT_TOOL, self.click_stop, stop)
        self.Bind(wx.EVT_TOOL, self.textDnDTarget.delete_all, clear)

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

        data = self.textDnDTarget.topic_Redirect()
        if data:
            for url in data:  # Check malformed url
                res = urlparse(url)
                if not res[1]:  # if empty netloc given from ParseResult
                    wx.MessageBox(_('ERROR: Invalid URL: "{}"').format(
                                  url), "Vidtuber", wx.ICON_ERROR, self)
                    return
            if len(set(data)) != len(data):  # equal URLS
                wx.MessageBox(_("ERROR: Some equal URLs found"),
                              "Vidtuber", wx.ICON_ERROR, self)
                return
        self.switch_youtube_downloader(self, data)
    # ------------------------------------------------------------------#

    def switch_text_import(self, event):
        """
        Show URLs import panel.
        """
        self.ProcessPanel.Hide()
        self.ytDownloader.Hide()
        self.textDnDTarget.Show()
        if self.filedldir:
            self.textDnDTarget.text_path_save.SetValue("")
            self.textDnDTarget.text_path_save.AppendText(self.filedldir)
        [self.toolbar.EnableTool(x, True) for x in (4, 14, 20)]
        [self.toolbar.EnableTool(x, False) for x in (3, 13, 18)]
        self.toolbar.Realize()
        self.Layout()
        self.statusbar_msg(_('Ready'), None)
        self.SetTitle(_('Vidtuber - Queued URLs'))
    # ------------------------------------------------------------------#

    def switch_youtube_downloader(self, event, data):
        """
        Show youtube-dl downloader panel
        """
        if not data:
            self.ytDownloader.choice.SetSelection(0)
            self.ytDownloader.choice.Disable()
            self.ytDownloader.ckbx_pl.Disable()
            self.ytDownloader.cmbx_af.Disable()
            self.ytDownloader.cmbx_aq.Disable()
            self.ytDownloader.rdbvideoformat.Disable()
            self.ytDownloader.cod_text.Hide()
            self.ytDownloader.labtxt.Hide()
            self.ytDownloader.cmbx_vq.Clear()
            self.ytDownloader.fcode.ClearAll()

        elif not data == self.data_url:
            if self.data_url:
                msg = (_('URL list changed, please check the settings '
                         'again.'), MainFrame.ORANGE, MainFrame.WHITE)
                self.statusbar_msg(msg[0], msg[1], msg[2])
            self.data_url = data
            self.ytDownloader.choice.Enable()
            self.ytDownloader.ckbx_pl.Enable()
            self.ytDownloader.choice.SetSelection(0)
            self.ytDownloader.on_choicebox(self, statusmsg=False)
            del self.ytDownloader.info[:]
            self.ytDownloader.format_dict.clear()
            self.ytDownloader.ckbx_pl.SetValue(False)
            self.ytDownloader.on_playlist(self)
        else:
            self.statusbar_msg(_('Ready'), None)

        self.SetTitle(_('Vidtuber - YouTube Downloader'))
        self.filedldir = self.textDnDTarget.file_dest

        self.textDnDTarget.Hide()
        self.ytDownloader.Show()
        [self.toolbar.EnableTool(x, True) for x in (3, 4, 14, 13)]
        [self.toolbar.EnableTool(x, False) for x in (18, 20)]

        self.Layout()
    # ------------------------------------------------------------------#

    def switch_to_processing(self, *varargs):
        """
        Preparing to processing
        """
        if varargs[0] == 'Viewing last log':
            self.statusbar_msg(_('Viewing last log'), None)
            [self.toolbar.EnableTool(x, False) for x in (4, 18, 20)]
            [self.toolbar.EnableTool(x, True) for x in (3, 14)]

        elif varargs[0] == 'youtube_dl downloading':
            self.menuBar.EnableTop(2, False)
            [self.toolbar.EnableTool(x, False) for x in (3, 4, 13, 20)]
            self.toolbar.EnableTool(18, True)

        self.SetTitle(_('Vidtuber - Output Monitor'))
        self.textDnDTarget.Hide()
        self.ytDownloader.Hide()
        self.ProcessPanel.Show()
        self.ProcessPanel.topic_thread(varargs)
        self.Layout()
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
        self.menuBar.EnableTop(2, True)
        self.toolbar.EnableTool(3, True)
        self.toolbar.EnableTool(18, False)
    # ------------------------------------------------------------------#

    def panelShown(self):
        """
        When clicking 'stop button' of the long_processing_task panel,
        retrieval at previous panel showing and re-enables the functions
        provided by the menu bar (see `switch_to_processing` method above).
        """
        self.ProcessPanel.Hide()
        self.switch_youtube_downloader(self, self.data_url)

        # Enable all top menu bar:
        self.menuBar.EnableTop(2, True)
        # show buttons bar if the user has shown it:
        self.Layout()
