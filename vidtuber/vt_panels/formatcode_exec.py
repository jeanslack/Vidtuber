# -*- coding: UTF-8 -*-
"""
Name: formatcodelist.py
Porpose: user interface panel for format codes tasks
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Feb.07.2024
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
import wx
from vidtuber.vt_io.io_tools import youtubedl_getstatistics
from vidtuber.vt_io.make_filelog import make_log_template


class FormatCode(wx.Panel):
    """
    This panel implements a kind of wx.ListCtrl for
    the format codes tasks. Format codes are identifier
    codes (ID) used in choosing multimedia contents according
    to the yt-dlp standards.

    """
    get = wx.GetApp()  # get vidtuber wx.App attribute
    appdata = get.appset
    icons = get.iconset

    if appdata['IS_DARK_THEME'] is True:
        GREEN = '#136322'  # formatcode highlighted items
    elif appdata['IS_DARK_THEME'] is False:
        GREEN = '#4CDD67'
    else:
        GREEN = '#40804C'

    BACKGRD = get.appset['colorscheme']['BACKGRD']  # help viewer backgrd
    DONE = get.appset['colorscheme']['TXT3']  # code text done
    WARN = get.appset['colorscheme']['WARN']  # code text warn
    RED = get.appset['colorscheme']['ERR1']   # code text err + sb error

    MSG_1 = _('At least one "Format Code" must be checked for each '
              'URL selected in green.')
    # -----------------------------------------------------------------#

    def __init__(self, parent, format_dict):
        """
        Note that most of the objects defined here are
        always reset for any change to the URLs list.
        """
        self.parent = parent
        self.urls = []
        self.format_dict = format_dict  # format codes order with URL matching

        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL)
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        # -------------listctrl

        self.fcode = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT
                                 | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL
                                 )
        self.fcode.EnableCheckBoxes(enable=True)
        colw = FormatCode.appdata['fcode_column_width']
        self.fcode.InsertColumn(0, (_('Format Code')), width=colw[0])
        self.fcode.InsertColumn(1, (_('Url')), width=colw[1])
        self.fcode.InsertColumn(2, (_('Extension')), width=colw[2])
        self.fcode.InsertColumn(3, (_('Resolution')), width=colw[3])

        sizer_base.Add(self.fcode, 1, wx.ALL | wx.EXPAND, 5)
        sizeropt = wx.BoxSizer(wx.HORIZONTAL)
        sizer_base.Add(sizeropt, 0)
        msg = _("Merge files into one file")
        self.ckbx_mrg = wx.CheckBox(self, wx.ID_ANY, msg)
        sizeropt.Add(self.ckbx_mrg, 0, wx.ALL | wx.EXPAND, 5)
        self.ckbx_mrg.SetValue(FormatCode.appdata['merge_single_file'])
        msg = _("Download only the best selected qualities")
        self.ckbx_best = wx.CheckBox(self, wx.ID_ANY, msg)
        sizeropt.Add(self.ckbx_best, 0, wx.ALL | wx.EXPAND, 5)
        self.ckbx_best.SetValue(FormatCode.appdata['only_best_quality'])
        # -----------------------
        self.SetSizer(sizer_base)
        self.Layout()

        # ----------------------Binder (EVT)----------------------#
        self.fcode.Bind(wx.EVT_LIST_ITEM_CHECKED, self.on_checkbox)
        self.fcode.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.on_checkbox)

    def enable_widgets(self, enable=True):
        """
        Enable if download by format code is used.
        """
        if enable:
            self.fcode.Enable()
            self.ckbx_best.Enable()
            self.ckbx_mrg.Enable()
        else:
            self.fcode.Disable()
            self.ckbx_best.Disable()
            self.ckbx_mrg.Disable()
    # ----------------------------------------------------------------------

    def on_checkbox(self, event):
        """
        get data from the enabled checkbox and set the values
        on corresponding key e.g. Resolution or Extension.

            `key=url: values=[mhtml: fcode, Audio: fcode, Video: fcode]`
        """
        check = self.fcode.IsItemChecked
        num = self.fcode.GetItemCount()
        for url in self.urls:
            self.format_dict[url] = []
            for i in range(num):
                if check(i):
                    if (self.fcode.GetItemText(i, 1)) == url:
                        if 'audio only' in self.fcode.GetItemText(i, 3):
                            dispa = self.fcode.GetItemText(i, 0)
                            self.format_dict[url].append('Audio: ' + dispa)
                        elif self.fcode.GetItemText(i, 2) == 'mhtml':
                            disph = self.fcode.GetItemText(i, 0)
                            self.format_dict[url].append('mhtml: ' + disph)
                        else:
                            # everything else could also be audio
                            # it depends on the video site (not youtube)
                            dispv = self.fcode.GetItemText(i, 0)
                            self.format_dict[url].append('Video: ' + dispv)
    # ----------------------------------------------------------------------

    def set_formatcode(self, data_url, arg):
        """
        Get URLs data and format codes by generator object
        `youtubedl_getstatistics`. Return `True` if `meta[1]`
        (error), otherwise return None as exit status.
        """
        logfile = make_log_template("Format_Codes.log",
                                    FormatCode.appdata['logdir'],
                                    mode="w",
                                    )
        self.urls = data_url.copy()
        meta = None, None
        index = 0
        for link in data_url:
            data = youtubedl_getstatistics(link,
                                           arg,
                                           logfile,
                                           parent=self.GetParent()
                                           )
            for meta in data:
                if meta[1]:
                    return meta[0]
                i = 0
                for count, fc in enumerate(meta[0].split('\n')):
                    if not count > i:
                        i += 1
                    elif fc != '':
                        self.fcode.InsertItem(index, fc.split()[0])
                        self.fcode.SetItem(index, 1, link)
                        self.fcode.SetItem(index, 2, fc.split()[1])
                        note = ' '.join(fc.split()[2:])
                        self.fcode.SetItem(index, 3, note)

                        if i + 1 == count:
                            green = FormatCode.GREEN
                            self.fcode.SetItemBackgroundColour(index, green)
                        index += 1

                    if fc.startswith('format code '):
                        i = count  # limit
        return None
    # -----------------------------------------------------------------#

    def getformatcode(self):
        """
        Called by `on_Start` parent method.
        Return format code list. None type otherwise.
        """
        format_code = []
        sep = ',' if not self.ckbx_mrg.GetValue() else '+'
        sepany = '/' if self.ckbx_best.GetValue() else sep
        amerge = '' if not self.ckbx_mrg.GetValue() else '--audio-multistreams'
        vmerge = '' if not self.ckbx_mrg.GetValue() else '--video-multistreams'

        for url, key, val in zip(self.urls,
                                 self.format_dict.keys(),
                                 self.format_dict.values()
                                 ):
            if key == url:
                video, audio, mhtml = self.fcode_concatenate(val, sepany)

                if audio or video or mhtml:
                    format_code.append(self.finalize_urlcodes(video,
                                                              audio,
                                                              mhtml,
                                                              sep
                                                              ))
        if len(format_code) != len(self.urls):
            return None
        return format_code, amerge, vmerge
    # -----------------------------------------------------------------#

    def fcode_concatenate(self, val, sepany):
        """
        Concatenate the selected format codes appropriately
        """
        video, audio, mhtml = None, None, None
        index_v, index_a, index_h = 0, 0, 0

        for idx in val:
            if idx.startswith('Video: '):
                index_v += 1
                if index_v > 1:
                    video += f"{sepany}{idx.split('Video: ')[1]}"
                else:
                    video = idx.split('Video: ')[1]

            elif idx.startswith('Audio: '):
                index_a += 1
                if index_a > 1:
                    audio += f"{sepany}{idx.split('Audio: ')[1]}"
                else:
                    audio = idx.split('Audio: ')[1]

            elif idx.startswith('mhtml: '):
                index_h += 1
                if index_h > 1:
                    mhtml += f",{idx.split('mhtml: ')[1]}"
                else:
                    mhtml = idx.split('mhtml: ')[1]

        return video, audio, mhtml
    # -----------------------------------------------------------------#

    def finalize_urlcodes(self, video, audio, mhtml, sep):
        """
        Finalizes the passed format codes for each URL, if any.
        Return a string with apropriate separators.
        If no audio, video or mhtml, return None type.
        """
        if video and audio:
            codes = f'{video}{sep}{audio}'
        elif video:
            codes = f'{video}'
        elif audio:
            codes = f'{audio}'
        else:
            codes = None

        if mhtml:
            codes = f'{codes},{mhtml}' if codes else f'{mhtml}'

        return codes
