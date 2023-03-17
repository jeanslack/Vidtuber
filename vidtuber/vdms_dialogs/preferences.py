# -*- coding: UTF-8 -*-
"""
Name: preferences.py
Porpose: vidtuber setup dialog
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
import webbrowser
import wx
from vidtuber.vdms_utils.utils import detect_binaries
from vidtuber.vdms_sys.settings_manager import ConfigManager
from vidtuber.vdms_sys.app_const import supLang
from vidtuber.vdms_io import io_tools


class SetUp(wx.Dialog):
    """
    Represents settings and configuration
    storing of the program.
    """
    # -----------------------------------------------------------------

    def __init__(self, parent):
        """
        self.appdata: (dict) settings already loaded from main_frame .
        self.confmanager: instance to ConfigManager class
        self.settings: (dict) current user settings from file conf.

        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.confmanager = ConfigManager(self.appdata['fileconfpath'])
        self.settings = self.confmanager.read_options()

        if self.appdata['ostype'] == 'Windows':
            self.ffmpeg = 'ffmpeg.exe'
            self.ffprobe = 'ffprobe.exe'
        else:
            self.ffmpeg = 'ffmpeg'
            self.ffprobe = 'ffprobe.exe'

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)

        # ----------------------------set notebook
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        notebook = wx.Notebook(self, wx.ID_ANY, style=0)
        sizer_base.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)

        # -----tab 1
        tabOne = wx.Panel(notebook, wx.ID_ANY)
        sizerGen = wx.BoxSizer(wx.VERTICAL)
        sizerGen.Add((0, 15))
        sbox = wx.StaticBox(tabOne, wx.ID_ANY, (_("Application Language")))
        boxlang = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        sizerGen.Add(boxlang, 0, wx.ALL | wx.EXPAND, 5)
        langs = [lang[1] for lang in supLang.values()]
        self.cmbx_lang = wx.ComboBox(tabOne, wx.ID_ANY,
                                     choices=langs,
                                     size=(-1, -1),
                                     style=wx.CB_DROPDOWN | wx.CB_READONLY
                                     )
        boxlang.Add(self.cmbx_lang, 0, wx.ALL | wx.EXPAND, 5)
        sizerGen.Add((0, 15))
        msg = _("Clear the cache when exiting the application")
        self.checkbox_cacheclr = wx.CheckBox(tabOne, wx.ID_ANY, (msg))
        sizerGen.Add(self.checkbox_cacheclr, 0, wx.ALL, 5)
        msg = _("Delete the contents of the log files "
                "when exiting the application")
        self.checkbox_logclr = wx.CheckBox(tabOne, wx.ID_ANY, (msg))
        sizerGen.Add(self.checkbox_logclr, 0, wx.ALL, 5)
        self.checkbox_exit = wx.CheckBox(tabOne, wx.ID_ANY,
                                         (_("Warn on exit"))
                                         )
        sizerGen.Add(self.checkbox_exit, 0, wx.ALL, 5)
        sizerGen.Add((0, 15))
        labconf = wx.StaticText(tabOne, wx.ID_ANY, _('Configuration folder'))
        sizerGen.Add(labconf, 0, wx.ALL | wx.EXPAND, 5)
        self.btn_conf = wx.Button(tabOne, wx.ID_ANY, "...", size=(35, -1))
        self.txtctrl_conf = wx.TextCtrl(tabOne, wx.ID_ANY,
                                        self.appdata['confdir'],
                                        style=wx.TE_READONLY,
                                        )
        sizerconf = wx.BoxSizer(wx.HORIZONTAL)
        sizerGen.Add(sizerconf, 0, wx.EXPAND)
        sizerconf.Add(self.txtctrl_conf, 1, wx.ALL, 5)
        sizerconf.Add(self.btn_conf, 0, wx.RIGHT | wx.CENTER, 5)

        lablog = wx.StaticText(tabOne, wx.ID_ANY, _('Log folder'))
        sizerGen.Add(lablog, 0, wx.ALL | wx.EXPAND, 5)
        self.btn_log = wx.Button(tabOne, wx.ID_ANY, "...", size=(35, -1))
        self.txtctrl_log = wx.TextCtrl(tabOne, wx.ID_ANY,
                                       self.appdata['logdir'],
                                       style=wx.TE_READONLY,
                                       )
        sizerlog = wx.BoxSizer(wx.HORIZONTAL)
        sizerGen.Add(sizerlog, 0, wx.EXPAND)
        sizerlog.Add(self.txtctrl_log, 1, wx.ALL, 5)
        sizerlog.Add(self.btn_log, 0, wx.RIGHT | wx.CENTER, 5)
        tabOne.SetSizer(sizerGen)
        notebook.AddPage(tabOne, _("Miscellanea"))

        # -----tab 2
        tabTwo = wx.Panel(notebook, wx.ID_ANY)
        sizerFiles = wx.BoxSizer(wx.VERTICAL)
        sizerFiles.Add((0, 15))
        msg = _("Where do you prefer to save your downloads?")
        labdown = wx.StaticText(tabTwo, wx.ID_ANY, msg)
        sizerFiles.Add(labdown, 0, wx.ALL | wx.EXPAND, 5)
        sizeYDLdirdest = wx.BoxSizer(wx.HORIZONTAL)
        sizerFiles.Add(sizeYDLdirdest, 0, wx.EXPAND)
        self.txtctrl_YDLpath = wx.TextCtrl(tabTwo, wx.ID_ANY, "",
                                           style=wx.TE_READONLY
                                           )
        sizeYDLdirdest.Add(self.txtctrl_YDLpath, 1, wx.ALL | wx.CENTER, 5)
        self.txtctrl_YDLpath.AppendText(self.appdata['dirdownload'])
        self.btn_YDLpath = wx.Button(tabTwo, wx.ID_ANY, "...", size=(35, -1))
        sizeYDLdirdest.Add(self.btn_YDLpath, 0, wx.RIGHT
                           | wx.ALIGN_CENTER_VERTICAL
                           | wx.ALIGN_CENTER_HORIZONTAL, 5
                           )
        descr = _("Auto-create subfolders when downloading playlists")
        self.ckbx_playlist = wx.CheckBox(tabTwo, wx.ID_ANY, (descr))
        sizerFiles.Add(self.ckbx_playlist, 0, wx.ALL, 5)

        tabTwo.SetSizer(sizerFiles)
        notebook.AddPage(tabTwo, _("File Preferences"))

        # -----tab 3
        tabThree = wx.Panel(notebook, wx.ID_ANY)
        sizerFFmpeg = wx.BoxSizer(wx.VERTICAL)
        sizerFFmpeg.Add((0, 15))
        labFFexec = wx.StaticText(tabThree, wx.ID_ANY,
                                  _('Path to the FFmpeg executables'))
        sizerFFmpeg.Add(labFFexec, 0, wx.ALL | wx.EXPAND, 5)
        # ----
        msg = _("Enable another location to run FFmpeg")
        self.checkbox_exeFFmpeg = wx.CheckBox(tabThree, wx.ID_ANY, (msg))
        self.btn_ffmpeg = wx.Button(tabThree, wx.ID_ANY, "...", size=(35, -1))
        self.txtctrl_ffmpeg = wx.TextCtrl(tabThree, wx.ID_ANY, "",
                                          style=wx.TE_READONLY
                                          )
        sizerFFmpeg.Add(self.checkbox_exeFFmpeg, 0, wx.ALL, 5)
        gridFFmpeg = wx.BoxSizer(wx.HORIZONTAL)
        sizerFFmpeg.Add(gridFFmpeg, 0, wx.EXPAND)
        gridFFmpeg.Add(self.txtctrl_ffmpeg, 1, wx.ALL, 5)
        gridFFmpeg.Add(self.btn_ffmpeg, 0, wx.RIGHT | wx.CENTER, 5)
        # ----
        msg = _("Enable another location to run FFprobe")
        self.checkbox_exeFFprobe = wx.CheckBox(tabThree, wx.ID_ANY, (msg))
        self.btn_ffprobe = wx.Button(tabThree, wx.ID_ANY, "...", size=(35, -1))
        self.txtctrl_ffprobe = wx.TextCtrl(tabThree, wx.ID_ANY, "",
                                           style=wx.TE_READONLY
                                           )
        sizerFFmpeg.Add(self.checkbox_exeFFprobe, 0, wx.ALL, 5)
        gridFFprobe = wx.BoxSizer(wx.HORIZONTAL)
        sizerFFmpeg.Add(gridFFprobe, 0, wx.EXPAND)
        gridFFprobe.Add(self.txtctrl_ffprobe, 1, wx.ALL, 5)
        gridFFprobe.Add(self.btn_ffprobe, 0, wx.RIGHT | wx.CENTER, 5)
        tabThree.SetSizer(sizerFFmpeg)
        notebook.AddPage(tabThree, _("FFmpeg"))

        # -----tab 4
        tabFour = wx.Panel(notebook, wx.ID_ANY)
        sizerAppearance = wx.BoxSizer(wx.VERTICAL)
        sizerAppearance.Add((0, 15))
        labTheme = wx.StaticText(tabFour, wx.ID_ANY, _('Icon themes'))
        sizerAppearance.Add(labTheme, 0, wx.ALL | wx.EXPAND, 5)
        msg = _("The chosen icon theme will only change the icons,\n"
                "background and foreground of some text fields.")
        labIcons = wx.StaticText(tabFour, wx.ID_ANY, (msg))
        sizerAppearance.Add(labIcons, 0, wx.ALL
                            | wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.cmbx_icons = wx.ComboBox(tabFour, wx.ID_ANY,
                                      choices=[("Vidtuber-Light"),
                                               ("Vidtuber-Dark"),
                                               ("Vidtuber-Colours"),
                                               ("Ubuntu-Light-Aubergine"),
                                               ("Ubuntu-Dark-Aubergine"),
                                               ],
                                      size=(200, -1),
                                      style=wx.CB_DROPDOWN | wx.CB_READONLY
                                      )
        sizerAppearance.Add(self.cmbx_icons, 0,
                            wx.ALL
                            | wx.ALIGN_CENTER_HORIZONTAL, 5
                            )
        sizerAppearance.Add((0, 15))
        labTB = wx.StaticText(tabFour, wx.ID_ANY, _("Toolbar customization"))
        sizerAppearance.Add(labTB, 0, wx.ALL | wx.EXPAND, 5)
        tbchoice = [_('At the top of window (default)'),
                    _('At the bottom of window'),
                    _('At the right of window'),
                    _('At the left of window')]
        self.rdbTBpref = wx.RadioBox(tabFour, wx.ID_ANY,
                                     (_("Place the toolbar")),
                                     choices=tbchoice,
                                     majorDimension=1,
                                     style=wx.RA_SPECIFY_COLS
                                     )
        sizerAppearance.Add(self.rdbTBpref, 0, wx.ALL | wx.EXPAND, 5)

        gridTBsize = wx.FlexGridSizer(0, 2, 0, 5)
        sizerAppearance.Add(gridTBsize, 0, wx.ALL, 5)
        lab1_appearance = wx.StaticText(tabFour, wx.ID_ANY,
                                        _('Icon size:'))
        gridTBsize.Add(lab1_appearance, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.cmbx_iconsSize = wx.ComboBox(tabFour, wx.ID_ANY,
                                          choices=[("16"), ("24"), ("32"),
                                                   ("64")], size=(120, -1),
                                          style=wx.CB_DROPDOWN | wx.CB_READONLY
                                          )
        gridTBsize.Add(self.cmbx_iconsSize, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        if 'wx.svg' not in sys.modules:  # only in wx version 4.1 to up
            self.cmbx_iconsSize.Disable()
            lab1_appearance.Disable()
        msg = _("Shows the text in the toolbar buttons")
        self.checkbox_tbtext = wx.CheckBox(tabFour, wx.ID_ANY, (msg))
        sizerAppearance.Add(self.checkbox_tbtext, 0, wx.ALL, 5)

        tabFour.SetSizer(sizerAppearance)  # aggiungo il sizer su tab 4
        notebook.AddPage(tabFour, _("Appearance"))

        # ------ btns bottom
        grdBtn = wx.GridSizer(1, 2, 0, 0)
        grdhelp = wx.GridSizer(1, 1, 0, 0)
        btn_help = wx.Button(self, wx.ID_HELP, "")
        grdhelp.Add(btn_help, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        grdBtn.Add(grdhelp)
        grdexit = wx.BoxSizer(wx.HORIZONTAL)
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        grdexit.Add(btn_close, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        btn_ok = wx.Button(self, wx.ID_OK, "")
        grdexit.Add(btn_ok, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        grdBtn.Add(grdexit, flag=wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, border=0)
        sizer_base.Add(grdBtn, 0, wx.EXPAND)
        # ------ set sizer
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        # ----------------------Properties----------------------#
        self.SetTitle(_("Settings"))
        # set font
        if self.appdata['ostype'] == 'Darwin':
            labconf.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            lablog.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labdown.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labFFexec.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labTheme.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labIcons.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
            labTB.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        else:
            labconf.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            lablog.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labdown.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labFFexec.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labTheme.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labIcons.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            labTB.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_COMBOBOX, self.on_set_lang, self.cmbx_lang)
        self.Bind(wx.EVT_BUTTON, self.openconf, self.btn_conf)
        self.Bind(wx.EVT_BUTTON, self.openlog, self.btn_log)
        self.Bind(wx.EVT_BUTTON, self.on_downloadPath, self.btn_YDLpath)
        self.Bind(wx.EVT_CHECKBOX, self.on_playlistFolder, self.ckbx_playlist)
        self.Bind(wx.EVT_CHECKBOX, self.exeFFmpeg, self.checkbox_exeFFmpeg)
        self.Bind(wx.EVT_BUTTON, self.open_path_ffmpeg, self.btn_ffmpeg)
        self.Bind(wx.EVT_CHECKBOX, self.exeFFprobe, self.checkbox_exeFFprobe)
        self.Bind(wx.EVT_BUTTON, self.open_path_ffprobe, self.btn_ffprobe)
        self.Bind(wx.EVT_COMBOBOX, self.on_Iconthemes, self.cmbx_icons)

        self.Bind(wx.EVT_RADIOBOX, self.on_toolbarPos, self.rdbTBpref)
        self.Bind(wx.EVT_COMBOBOX, self.on_toolbarSize, self.cmbx_iconsSize)
        self.Bind(wx.EVT_CHECKBOX, self.on_toolbarText, self.checkbox_tbtext)
        self.Bind(wx.EVT_CHECKBOX, self.exit_warn, self.checkbox_exit)

        self.Bind(wx.EVT_CHECKBOX, self.clear_Cache, self.checkbox_cacheclr)
        self.Bind(wx.EVT_CHECKBOX, self.clear_logs, self.checkbox_logclr)
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)
        # --------------------------------------------#
        self.current_settings()  # call function for initialize setting layout

    def current_settings(self):
        """
        Setting enable/disable in according to the configuration file
        """
        if self.appdata['locale_name'] in supLang:
            lang = supLang[self.appdata['locale_name']][1]
        else:
            lang = supLang["en_US"][1]
        self.cmbx_lang.SetValue(lang)
        self.cmbx_icons.SetValue(self.appdata['icontheme'][0])
        self.cmbx_iconsSize.SetValue(str(self.appdata['toolbarsize']))
        self.rdbTBpref.SetSelection(self.appdata['toolbarpos'])

        self.checkbox_cacheclr.SetValue(self.appdata['clearcache'])
        self.checkbox_tbtext.SetValue(self.appdata['toolbartext'])
        self.checkbox_exit.SetValue(self.appdata['warnexiting'])
        self.checkbox_logclr.SetValue(self.appdata['clearlogfiles'])
        self.ckbx_playlist.SetValue(self.appdata['playlistsubfolder'])

        if not self.appdata['ffmpeg_islocal']:
            self.btn_ffmpeg.Disable()
            self.txtctrl_ffmpeg.Disable()
            self.txtctrl_ffmpeg.AppendText(self.appdata['ffmpeg_cmd'])
            self.checkbox_exeFFmpeg.SetValue(False)
        else:
            self.txtctrl_ffmpeg.AppendText(self.appdata['ffmpeg_cmd'])
            self.checkbox_exeFFmpeg.SetValue(True)

        if not self.appdata['ffprobe_islocal']:
            self.btn_ffprobe.Disable()
            self.txtctrl_ffprobe.Disable()
            self.txtctrl_ffprobe.AppendText(self.appdata['ffprobe_cmd'])
            self.checkbox_exeFFprobe.SetValue(False)
        else:
            self.txtctrl_ffprobe.AppendText(self.appdata['ffprobe_cmd'])
            self.checkbox_exeFFprobe.SetValue(True)
    # --------------------------------------------------------------------#

    def openlog(self, event):
        """
        Open the log directory with file manager

        """
        io_tools.openpath(self.appdata['logdir'])
    # ------------------------------------------------------------------#

    def openconf(self, event):
        """
        Open the configuration folder with file manager

        """
        io_tools.openpath(self.appdata['confdir'])
    # -------------------------------------------------------------------#

    def on_set_lang(self, event):
        """set application language"""

        for key, val in supLang.items():
            if val[1] == self.cmbx_lang.GetValue():
                lang = key
        self.settings['locale_name'] = lang
    # --------------------------------------------------------------------#

    def on_downloadPath(self, event):
        """set up a custom user path for file downloads"""

        dlg = wx.DirDialog(self, _("Set a persistent location to save the "
                                   "file downloads"),
                           self.appdata['dirdownload'], wx.DD_DEFAULT_STYLE
                           )
        if dlg.ShowModal() == wx.ID_OK:
            self.txtctrl_YDLpath.Clear()
            getpath = self.appdata['getpath'](dlg.GetPath())
            self.txtctrl_YDLpath.AppendText(getpath)
            self.settings['dirdownload'] = getpath
            dlg.Destroy()
    # ---------------------------------------------------------------------#

    def on_playlistFolder(self, event):
        """auto-create subfolders when downloading playlists"""
        if self.ckbx_playlist.IsChecked():
            self.settings['playlistsubfolder'] = True
        else:
            self.settings['playlistsubfolder'] = False
    # ---------------------------------------------------------------------#

    def exeFFmpeg(self, event):
        """Enable or disable ffmpeg local binary"""
        if self.checkbox_exeFFmpeg.IsChecked():
            self.btn_ffmpeg.Enable()
            self.txtctrl_ffmpeg.Enable()
            self.settings['ffmpeg_islocal'] = True
        else:
            self.btn_ffmpeg.Disable()
            self.txtctrl_ffmpeg.Disable()
            self.settings['ffmpeg_islocal'] = False

            status = detect_binaries(self.ffmpeg,
                                     self.appdata['FFMPEG_vidtuber_pkg']
                                     )
            if status[0] == 'not installed':
                self.txtctrl_ffmpeg.Clear()
                self.txtctrl_ffmpeg.write(status[0])
                self.settings['ffmpeg_cmd'] = ''
            else:
                self.txtctrl_ffmpeg.Clear()
                getpath = self.appdata['getpath'](status[1])
                self.txtctrl_ffmpeg.write(getpath)
                self.settings['ffmpeg_cmd'] = getpath
    # --------------------------------------------------------------------#

    def open_path_ffmpeg(self, event):
        """Indicates a new ffmpeg path-name"""
        with wx.FileDialog(self, _("Choose the {} "
                                   "executable").format(self.ffmpeg), "", "",
                           f"ffmpeg binary (*{self.ffmpeg})|*{self.ffmpeg}| "
                           f"All files (*.*)|*.*",
                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fdlg:

            if fdlg.ShowModal() == wx.ID_OK:
                if os.path.basename(fdlg.GetPath()) == self.ffmpeg:
                    self.txtctrl_ffmpeg.Clear()
                    getpath = self.appdata['getpath'](fdlg.GetPath())
                    self.txtctrl_ffmpeg.write(getpath)
                    self.settings['ffmpeg_cmd'] = getpath
    # --------------------------------------------------------------------#

    def exeFFprobe(self, event):
        """Enable or disable ffprobe local binary"""
        if self.checkbox_exeFFprobe.IsChecked():
            self.btn_ffprobe.Enable()
            self.txtctrl_ffprobe.Enable()
            self.settings['ffprobe_islocal'] = True

        else:
            self.btn_ffprobe.Disable()
            self.txtctrl_ffprobe.Disable()
            self.settings['ffprobe_islocal'] = False

            status = detect_binaries(self.ffprobe,
                                     self.appdata['FFMPEG_videomass_pkg']
                                     )
            if status[0] == 'not installed':
                self.txtctrl_ffprobe.Clear()
                self.txtctrl_ffprobe.write(status[0])
                self.settings['ffprobe_cmd'] = ''
            else:
                self.txtctrl_ffprobe.Clear()
                getpath = self.appdata['getpath'](status[1])
                self.txtctrl_ffprobe.write(getpath)
                self.settings['ffprobe_cmd'] = getpath
    # --------------------------------------------------------------------#

    def open_path_ffprobe(self, event):
        """Indicates a new ffprobe path-name"""
        with wx.FileDialog(self, _("Choose the {} "
                                   "executable").format(self.ffprobe), "", "",
                           f"ffprobe binary "
                           f"(*{self.ffprobe})|*{self.ffprobe}| "
                           f"All files (*.*)|*.*",
                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fdlg:

            if fdlg.ShowModal() == wx.ID_OK:
                if os.path.basename(fdlg.GetPath()) == self.ffprobe:
                    self.txtctrl_ffprobe.Clear()
                    getpath = self.appdata['getpath'](fdlg.GetPath())
                    self.txtctrl_ffprobe.write(getpath)
                    self.settings['ffprobe_cmd'] = getpath
    # --------------------------------------------------------------------#

    def on_Iconthemes(self, event):
        """
        Set themes of icons
        """
        self.settings['icontheme'] = self.cmbx_icons.GetStringSelection()
    # --------------------------------------------------------------------#

    def on_toolbarSize(self, event):
        """
        Set the size of the toolbar buttons and the size of its icons
        """
        size = self.cmbx_iconsSize.GetStringSelection()
        self.settings['toolbarsize'] = size
    # --------------------------------------------------------------------#

    def on_toolbarPos(self, event):
        """
        Set toolbar position on main frame
        """
        self.settings['toolbarpos'] = self.rdbTBpref.GetSelection()
    # --------------------------------------------------------------------#

    def on_toolbarText(self, event):
        """
        Show or hide text along toolbar buttons
        """
        if self.checkbox_tbtext.IsChecked():
            self.settings['toolbartext'] = True
        else:
            self.settings['toolbartext'] = False
    # --------------------------------------------------------------------#

    def exit_warn(self, event):
        """
        Enable or disable the warning message before
        exiting the program
        """
        if self.checkbox_exit.IsChecked():
            self.settings['warnexiting'] = True
        else:
            self.settings['warnexiting'] = False
    # --------------------------------------------------------------------#

    def clear_Cache(self, event):
        """
        if checked, set to clear cached data on exit
        """
        if self.checkbox_cacheclr.IsChecked():
            self.settings['clearcache'] = True
        else:
            self.settings['clearcache'] = False
    # --------------------------------------------------------------------#

    def clear_logs(self, event):
        """
        if checked, set to clear all log files on exit
        """
        if self.checkbox_logclr.IsChecked():
            self.settings['clearlogfiles'] = True
        else:
            self.settings['clearlogfiles'] = False
    # --------------------------------------------------------------------#

    def on_help(self, event):
        """
        Open default web browser via Python Web-browser controller.
        see <https://docs.python.org/3.8/library/webbrowser.html>
        """
        if self.appdata['GETLANG'] in self.appdata['SUPP_LANGs']:
            lang = self.appdata['GETLANG'].split('_')[0]
            page = (f'https://jeanslack.github.io/Vidtuber/Pages/User-guide-'
                    f'languages/{lang}/2-Startup_and_Setup_{lang}.pdf')
        else:
            page = ('https://jeanslack.github.io/Vidtuber/Pages/User-guide-'
                    'languages/en/2-Startup_and_Setup_en.pdf')

        webbrowser.open(page)
    # --------------------------------------------------------------------#

    def getvalue(self):
        """
        Retrives data from here before destroyng this dialog.
        See main_frame --> on_setup method
        """
        if wx.MessageBox(_("Changes will take effect once the program "
                           "has been restarted.\n\n"
                           "Do you want to exit the application now?"),
                         _('Exit'),
                         wx.ICON_QUESTION
                         | wx.YES_NO, self) == wx.YES:
            return True

        return None
    # --------------------------------------------------------------------#

    def on_cancel(self, event):
        """
        Close event
        """
        event.Skip()
    # --------------------------------------------------------------------#

    def on_ok(self, event):
        """
        Applies all changes writing the new entries on
        `settings.json` file aka file configuration.
        """
        self.confmanager.write_options(**self.settings)

        event.Skip()
