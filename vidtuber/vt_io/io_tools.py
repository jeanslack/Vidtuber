# -*- coding: UTF-8 -*-
"""
Name: io_tools.py
Porpose: input/output redirection to processes (aka threads)
Compatibility: Python3, wxPython4 Phoenix
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
import requests
import wx
from vidtuber.vt_threads.check_bin import subp
from vidtuber.vt_utils.utils import open_default_application
from vidtuber.vt_dialogs.widget_utils import PopupDialog
from vidtuber.vt_threads.ydl_get_formatcode import YdlExtractInfo


def youtubedl_getstatistics(url, args, logfile, parent=None):
    """
    Call `YdlExtractInfo` thread to extract data info.
    During this process a wait pop-up dialog is shown.

    Returns a generator.

    Usage example without pop-up dialog:
        thread = YdlExtractInfo(url)
        thread.join()
        data = thread.data
        yield data
    """
    thread = YdlExtractInfo(url, args, logfile)
    dlgload = PopupDialog(parent,
                          _("Vidtuber - Loading..."),
                          _("Wait....\nRetrieving required data."))
    dlgload.ShowModal()
    # thread.join()
    data = thread.data
    dlgload.Destroy()
    yield data
# --------------------------------------------------------------------------#


def youtubedl_get_executable_version(execpath):
    """
    Call `check_bin.subp` to get yt-dlp executable version.
    """
    get = wx.GetApp()
    res = subp([execpath, '--version'], get.appset['ostype'])
    return res[1] if res[0] == 'None' else f'{res[0]} [ERROR]\n'
# --------------------------------------------------------------------------#


def openpath(where):
    """
    Call `vdms_threads.opendir.open_default_application`.
    """
    ret = open_default_application(where)
    if ret:
        wx.MessageBox(ret, _('Vidtuber - Error!'), wx.ICON_ERROR, None)
# -------------------------------------------------------------------------#


def get_github_releases(url, keyname):
    """
    Check for releases data on github page using github API:
        https://developer.github.com/v3/repos/releases/#get-the-latest-release

    see keyname examples here:
    <https://api.github.com/repos/jeanslack/Vidtuber/releases>
    """
    try:
        response = requests.get(url, timeout=15)
        not_found = None, None
    except Exception as err:
        not_found = 'request error:', err
    else:
        try:
            version = response.json()[f"{keyname}"]
        except Exception as err:
            not_found = 'response error:', err

    if not_found[0]:
        return not_found

    return version, None
# --------------------------------------------------------------------------#
