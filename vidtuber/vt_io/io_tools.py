# -*- coding: UTF-8 -*-
"""
Name: io_tools.py
Purpose: input/output redirection to processes (aka threads)
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Oct.27.2026
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
from vidtuber.vt_utils.utils import (open_default_application,
                                     format_bytes,
                                     integer_to_time)
from vidtuber.vt_io.make_filelog import make_log_template
from vidtuber.vt_dialogs.widget_utils import PopupDialog
from vidtuber.vt_threads.get_output_thread import (FetchOutputDataProcess,
                                                   logerror)


def dump_formats(datadict, jdata):
    """
    Called by `ytdlp_dump_single_json` function.
    Performs some data manipulation steps to make
    datadict mapping more compact.
    Return a dict object with formats values.
    """
    for frmts in jdata.get('formats', []):
        format_res = frmts.get('format', 'N/A')
        res_parts = format_res.split()
        resolution = (' '.join(res_parts[1:]).replace('-', '').strip()
                      if len(res_parts) > 1 else 'N/A')

        # RIFATTORIZZATO: Compattazione pulita delle stringhe "None"
        raw_vcodec = str(frmts.get('vcodec', ''))
        raw_fps = str(frmts.get('fps', ''))
        raw_acodec = str(frmts.get('acodec', ''))
        raw_lang = str(frmts.get('language', ''))

        size = (format_bytes(float(frmts['filesize']))
                if frmts.get('filesize') else '')

        dictf = {
            'id': frmts.get('format_id', 'None'),
            'ext': frmts.get('ext', 'N/A'),
            'resolution': resolution,
            'vcodec': '' if raw_vcodec.lower() in ('none', '') else raw_vcodec,
            'fps': '' if raw_fps.lower() in ('none', '') else raw_fps,
            'acodec': '' if raw_acodec.lower() in ('none', '') else raw_acodec,
            'lang': '' if raw_lang.lower() in ('none', '') else raw_lang,
            'size': size,
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
                          thread
                          )
    dlgload.ShowModal()

    data = thread.data
    dlgload.Destroy()

    if thread.stop_work_thread:
        return None, 'stop work thread'
    if data[1]:
        return data

    try:
        jdata = json.loads(data[0])
    except json.decoder.JSONDecodeError as err:
        logerror(f"[VIDTUBER]: JSON Decoding ERROR: {err}",
                 logfile, usesep=False)
        return None, 'error'

    newdata = {
        'title': jdata.get('title', 'Unknown Title'),
        'domain': jdata.get('webpage_url_domain', 'Unknown Domain'),
        'urltype': jdata.get('webpage_url_basename', 'Unknown Type'),
        'duration': 'N/A',
        'formats': [],
    }

    duration = jdata.get('duration')
    if duration and isinstance(duration, (float, int)):
        duration = round(duration) * 1000
        newdata['duration'] = integer_to_time(duration, mills=False)

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
# --------------------------------------------------------------------------#


def get_github_releases(url, keyname):
    """
    Check for releases data on github page using github API.
    """
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        version = response.json()[f"{keyname}"]
        return version, None
    except requests.RequestException as err:
        return None, err
    except (KeyError, ValueError, TypeError) as err:
        return None, err
