# -*- coding: UTF-8 -*-
"""
Name: gui_app.py
Porpose: bootstrap for Vidtuber app.
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
from shutil import which, rmtree
import builtins
import wx
try:
    from wx.svg import SVGimage
except ModuleNotFoundError:
    pass
from vidtuber.vdms_sys.argparser import arguments
from vidtuber.vdms_sys.configurator import DataSource
from vidtuber.vdms_sys import app_const as appC
from vidtuber.vdms_utils.utils import del_filecontents

# add translation macro to builtin similar to what gettext does
builtins.__dict__['_'] = wx.GetTranslation


class Vidtuber(wx.App):
    """
    bootstrap the wxPython GUI toolkit before
    starting the main_frame.

    """

    def __init__(self, redirect=True, filename=None, **kwargs):
        """
        - redirect=False will send print statements to a console
          window (in use)
        - redirect=True will be sent to a little textbox window.
        - filename=None Redirect sys.stdout and sys.stderr
          to a popup window.
        - filename='path/to/file.txt' Redirect sys.stdout
          and sys.stderr to file

        See main() function below to settings it.

        """
        self.locale = None
        self.appset = {'DISPLAY_SIZE': None,
                       'IS_DARK_THEME': None,
                       'GETLANG': None,
                       # short name for the locale
                       'SUPP_LANGs': ['it_IT', 'en_US', 'ru_RU'],
                       # supported langs for online help (user guide)
                       }
        self.data = DataSource(kwargs)  # instance data
        self.appset.update(self.data.get_fileconf())  # data system
        self.iconset = None

        wx.App.__init__(self, redirect, filename)  # constructor
        wx.SystemOptions.SetOption("osx.openfiledialog.always-show-types", "1")
    # -------------------------------------------------------------------

    def OnInit(self):
        """Bootstrap interface."""

        if self.appset.get('ERROR'):
            wx.MessageBox(f"FATAL: {self.appset['ERROR']}\n\nSorry, unable "
                          f"to continue...", 'Vidtuber - ERROR', wx.ICON_STOP)
            return False

        self.appset['DISPLAY_SIZE'] = wx.GetDisplaySize()  # get monitor res
        if hasattr(wx.SystemSettings, 'GetAppearance'):
            appear = wx.SystemSettings.GetAppearance()
            self.appset['IS_DARK_THEME'] = appear.IsDark()

        self.iconset = self.data.icons_set(self.appset['icontheme'][0])

        # locale
        wx.Locale.AddCatalogLookupPathPrefix(self.appset['localepath'])
        self.update_language(self.appset['locale_name'])

        ytdlp = self.check_youtube_dl()
        if ytdlp is False:
            return False

        noffmpeg = self.check_ffmpeg()
        if noffmpeg:
            self.wizard(self.iconset['vidtuber'])
            return True

        from vidtuber.vdms_main.main_frame import MainFrame
        main_frame = MainFrame()
        main_frame.Show()
        self.SetTopWindow(main_frame)
        return True
    # -------------------------------------------------------------------

    def check_youtube_dl(self):
        """
        Check for `yt_dlp` python module.
        """
        if self.appset['downloader'] == 'yt_dlp':
            try:
                import yt_dlp
            except ModuleNotFoundError as err:
                wx.MessageBox(f"ERROR: {err}\n\nyt-dlp is missing, "
                              f"please install it.", 'Vidtuber - ERROR',
                              wx.ICON_STOP)
                return False
        return None
    # -------------------------------------------------------------------

    def check_ffmpeg(self):
        """
        Get the FFmpeg's executables. A permission check
        is also performed on Unix/Unix-like systems.
        """
        for link in [self.appset['ffmpeg_cmd'],
                     self.appset['ffprobe_cmd'],
                     ]:
            if self.appset['ostype'] == 'Windows':  # check for exe
                # HACK use even for unix, if not permission is equal
                # to not binaries
                if not which(link, mode=os.F_OK | os.X_OK, path=None):
                    return True
            else:
                if not os.path.isfile(f"{link}"):
                    return True

        if not self.appset['ostype'] == 'Windows':
            # check for permissions when linked locally
            for link in [self.appset['ffmpeg_cmd'],
                         self.appset['ffprobe_cmd'],
                         ]:
                if which(link, mode=os.F_OK | os.X_OK, path=None):
                    permissions = True
                else:
                    wx.MessageBox(_('Permission denied: {}\n\n'
                                    'Check execution permissions.').format
                                  (link), 'Vidtuber', wx.ICON_STOP)
                    permissions = False
                    break

            return False if not permissions else None
        return None
    # -------------------------------------------------------------------

    def wizard(self, wizardicon):
        """
        Show an initial dialog to setup the application
        during the first start-up.

        """
        from vidtuber.vdms_dialogs.wizard_dlg import Wizard
        main_frame = Wizard(wizardicon)
        main_frame.Show()
        self.SetTopWindow(main_frame)
        return True
    # ------------------------------------------------------------------

    def update_language(self, lang=None):
        """
        Update the language to the requested one.
        Make *sure* any existing locale is deleted before the new
        one is created.  The old C++ object needs to be deleted
        before the new one is created, and if we just assign a new
        instance to the old Python variable, the old C++ locale will
        not be destroyed soon enough, likely causing a crash.

        :param string `lang`: one of the supported language codes
        https://docs.wxpython.org/wx.Language.enumeration.html#wx-language

        """
        # if an unsupported language is requested, default to English
        selectlang = appC.supLang.get(lang, wx.LANGUAGE_ENGLISH)

        if self.locale:
            assert sys.getrefcount(self.locale) <= 2
            del self.locale

        # create a locale object for this language
        self.locale = wx.Locale(selectlang[0])

        if self.locale.IsOk():
            self.locale.AddCatalog(appC.langDomain)
            self.appset['GETLANG'] = self.locale.GetName()
        else:
            self.locale = None
            self.appset['GETLANG'] = "en_US"
    # -------------------------------------------------------------------

    def OnExit(self):
        """
        OnExit provides an interface for exiting the application.
        The ideal place to run the last few things before completely
        exiting the application, eg. delete temporary files etc.
        """
        if self.appset['clearcache']:
            tmp = os.path.join(self.appset['cachedir'], 'tmp')
            if os.path.exists(tmp):
                for cache in os.listdir(tmp):
                    fcache = os.path.join(tmp, cache)
                    if os.path.isfile(fcache):
                        os.remove(fcache)
                    elif os.path.isdir:
                        rmtree(fcache)

        if self.appset['clearlogfiles']:
            logdir = self.appset['logdir']
            if os.path.exists(logdir):
                flist = os.listdir(logdir)
                if flist:
                    for logname in flist:
                        logfile = os.path.join(logdir, logname)
                        try:
                            del_filecontents(logfile)
                        except Exception as err:
                            wx.MessageBox(_("Unexpected error while deleting "
                                            "file contents:\n\n"
                                            "{0}").format(err),
                                          'Vidtuber', wx.ICON_STOP)
                            return False
        return True
    # -------------------------------------------------------------------


def main():
    """
    Without command line arguments starts the
    wx.App mainloop with default keyword arguments.
    """
    if not sys.argv[1:]:
        kwargs = {'make_portable': None}
    else:
        kwargs = arguments()

    app = Vidtuber(redirect=False, **kwargs)
    app.MainLoop()
