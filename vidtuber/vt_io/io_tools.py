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
import json
import requests
import wx
from vidtuber.vt_threads.check_bin import subp
from vidtuber.vt_utils.utils import open_default_application
from vidtuber.vt_utils.utils import format_bytes
from vidtuber.vt_io.make_filelog import make_log_template
from vidtuber.vt_dialogs.widget_utils import PopupDialog
from vidtuber.vt_threads.get_output_thread import FetchOutputDataProcess
from vidtuber.vt_threads.get_output_thread import logerror


def dump_formats(datadict, jdata):
    """
    Called by `ytdlp_dump_single_json` function.
    Performs some data manipulation steps to make
    datadict mapping more compact.
    Return a dict object with formats values.
    """
    for frmts in jdata['formats']:
        frmtid = frmts.get('format_id', 'None')
        ext = frmts.get('ext', 'N/A')
        format_res = frmts.get('format', 'N/A')
        res = ' '.join(format_res.split()[1:])
        resolution = res.replace('-', '').strip()
        vcodec = f"{frmts.get('vcodec', '')}"
        vcodec = '' if vcodec in ('None', 'none') else vcodec
        fps = f"{frmts.get('fps', '')}"
        fps = '' if fps in ('None', 'none') else fps
        acodec = f"{frmts.get('acodec', '')}"
        acodec = '' if acodec in ('None', 'none') else acodec
        lang = f"{frmts.get('language', '')}"
        lang = '' if lang in ('None', 'none') else lang

        if frmts.get('filesize'):
            size = format_bytes(float(frmts['filesize']))
        else:
            size = ''
        dictf = {'id': frmtid, 'ext': ext, 'resolution': resolution,
                 'vcodec': vcodec, 'fps': fps, 'acodec': acodec,
                 'lang': lang, 'size': size,
                 }
        datadict['formats'].append(dictf)

    return datadict
# --------------------------------------------------------------------------#


def ytdlp_dump_single_json(url, args, logfile, parent=None):
    """
    Wait for data given by `FetchOutputDataProcess` thread.
    During this process a Modal wait pop-up dialog is shown.

    This function is responsible for converting JSON data from
    `thread.data` class attribute and returning a consistent data
    structure.

    Note that parent is `vt_panels.textdrop.Url_DnD_Panel` here.

    Returns a data tuple.
    """
    logfile = make_log_template(logfile, mode="w")
    thread = FetchOutputDataProcess(url, args, logfile)
    dlgload = PopupDialog(parent,
                          _("Vidtuber - Loading..."),
                          _("Wait....\nRetrieving required data."),
                          thread,
                          )
    dlgload.ShowModal()
    # thread.join()
    data = thread.data
    dlgload.Destroy()
    if data[1]:
        return data
    try:
        jdata = json.loads(data[0])
    except json.decoder.JSONDecodeError as err:
        logerror(f"[VIDTUBER]: JSON Decoding ERROR: {err}",
                 logfile, usesep=False)
        return None, 'error'

    newdata = {'title': jdata.get('title', 'Unknown Title'),
               'domain': jdata.get('webpage_url_domain', 'Unknown Domain'),
               'urltype': jdata.get('webpage_url_basename', 'Unknown Type'),
               'formats': [],
               }
    if url in ('/playlists', '/channels', '/playlist', '/channel', '/videos'):
        newdata['formats'] = []

    elif jdata.get('formats'):
        newdata = dump_formats(newdata, jdata)

    return newdata, None
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
