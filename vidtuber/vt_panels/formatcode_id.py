# -*- coding: UTF-8 -*-
"""
Name: formatcode_id.py
Purpose: user interface panel for format codes tasks
Compatibility: Python3, wxPython Phoenix
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
import wx
from vidtuber.vt_utils.get_bmpfromsvg import get_bmp


class FormatCodeList(wx.Panel):
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
    # -----------------------------------------------------------------#

    def __init__(self, parent, format_codeid, controller=None):
        """
        Note that most of the objects defined here are
        always reset for any change to the URLs list.
        """
        self.parent = parent
        self.controller = controller  # DLoad_Gui's phone number :-)
        self.urllist = []
        self.format_codeid = format_codeid  # format codes order
        bmpreload = get_bmp(FormatCodeList.icons['reload'], ((16, 16)))

        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL)
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        # -------------listctrl
        self.labfcode = wx.StaticText(self, wx.ID_ANY,
                                      _('Format Code Properties'))
        sizer_base.Add(self.labfcode, 0, wx.ALL | wx.CENTRE, 5)
        sizer_base.Add((0, 20))

        sizeropt = wx.BoxSizer(wx.HORIZONTAL)
        sizer_base.Add(sizeropt, 0)
        msg = _("Merge files into one file")
        self.ckbx_mrg = wx.CheckBox(self, wx.ID_ANY, msg)
        sizeropt.Add(self.ckbx_mrg, 0, wx.ALL | wx.EXPAND, 5)
        self.ckbx_mrg.SetValue(FormatCodeList.appdata['merge_single_file'])
        msg = _("Download only the best selected qualities")
        self.ckbx_best = wx.CheckBox(self, wx.ID_ANY, msg)
        sizeropt.Add(self.ckbx_best, 0, wx.ALL | wx.EXPAND, 5)
        self.ckbx_best.SetValue(FormatCodeList.appdata['only_best_quality'])
        self.btn_reload = wx.Button(self, wx.ID_ANY, _("Load"),
                                    size=(-1, -1))
        self.btn_reload.SetBitmap(bmpreload, wx.LEFT)
        self.btn_reload.SetToolTip(_('Reload format codes if needed'))
        sizeropt.Add(self.btn_reload, 0, wx.LEFT | wx.CENTRE, 10)
        sizer_base.Add((0, 20))
        self.fcode = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT
                                 | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL
                                 )
        self.fcode.EnableCheckBoxes(enable=True)
        colw = FormatCodeList.appdata['frmtcode_column_width']
        columns = ('Id', 'Url', _('Title'), _('Extension'),
                   _('Resolution'), _('Video Codec'), 'Fps',
                   _('Audio Codec'), _('Language'), _('Size'))

        for index, title in enumerate(columns):
            self.fcode.InsertColumn(index, title, width=colw[index])

        sizer_base.Add(self.fcode, 1, wx.ALL | wx.EXPAND, 5)

        # ----- Properties
        if FormatCodeList.appdata['ostype'] == 'Darwin':
            self.labfcode.SetFont(wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        else:
            self.labfcode.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        # -----------------------
        self.SetSizer(sizer_base)
        self.Layout()

        # ----------------------Binder (EVT)----------------------#
        self.btn_reload.Bind(wx.EVT_BUTTON, self.reload_format_codes)
        self.fcode.Bind(wx.EVT_LIST_ITEM_CHECKED, self.on_checkbox)
        self.fcode.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.on_checkbox)

    def reload_format_codes(self, event):
        """
        Clear all data and Reload format codes when required
        e.g changing some user option as use of cookies etc.
        """
        self.format_codeid.clear()
        self.fcode.DeleteAllItems()
        if self.controller:
            self.controller.on_format_codes()
    # ---------------------------------------------------------------------

    def on_checkbox(self, event):
        """
        Takes data from the checked columns in the list control
        and maps it to the corresponding URL on the dict object.
        This method set `self.format_codeid` attribute.

            `key=url: values=[mhtml: fcode, Audio: fcode, Video: fcode]`
        """
        check = self.fcode.IsItemChecked
        num = self.fcode.GetItemCount()

        for url in self.urllist:
            self.format_codeid[url] = []
            for i in range(num):
                if check(i):
                    if (self.fcode.GetItemText(i, 1)) == url:
                        if 'audio only' in self.fcode.GetItemText(i, 4):
                            dispa = self.fcode.GetItemText(i, 0)
                            self.format_codeid[url].append('Audio: ' + dispa)
                        elif self.fcode.GetItemText(i, 3) == 'mhtml':
                            disph = self.fcode.GetItemText(i, 0)
                            self.format_codeid[url].append('mhtml: ' + disph)
                        else:
                            # everything else could also be audio
                            # it depends on the video site (not youtube)
                            dispv = self.fcode.GetItemText(i, 0)
                            self.format_codeid[url].append('Video: ' + dispv)
    # ----------------------------------------------------------------------

    def set_formatcode(self, data_url):
        """
        Set list control with format code items.
        This method is only called by `on_format_codes`
        parent method.
        """
        del self.urllist[:]
        index = 0
        for listurl in data_url:
            for url, value in listurl.items():
                if not value.get('formats'):
                    break
                self.urllist.append(url)

                for num, frmts in enumerate(value['formats']):
                    self.fcode.InsertItem(index, frmts['id'])

                    row_data = (
                        (1, url),
                        (2, listurl[url]['title']),
                        (3, frmts['ext']),
                        (4, frmts['resolution']),
                        (5, frmts['vcodec']),
                        (6, frmts['fps']),
                        (7, frmts['acodec']),
                        (8, frmts['lang']),
                        (9, frmts['size'])
                    )

                    for col, text in row_data:
                        self.fcode.SetItem(index, col, text)

                    if num == 0:
                        green = FormatCodeList.GREEN
                        self.fcode.SetItemBackgroundColour(index, green)
                    index += 1
    # ----------------------------------------------------------------------

    def get_formatcode(self):
        """
        Build a list of format code arguments for each URL .
        This method is only called by `on_Start` parent method.

        Return a format code list. None type otherwise.
        """
        format_code = []
        sep = ',' if not self.ckbx_mrg.GetValue() else '+'
        sepany = '/' if self.ckbx_best.GetValue() else sep
        amerge = '' if not self.ckbx_mrg.GetValue() else '--audio-multistreams'
        vmerge = '' if not self.ckbx_mrg.GetValue() else '--video-multistreams'

        for url in self.urllist:
            if url in self.format_codeid:
                val = self.format_codeid[url]
                video, audio, mhtml = self.fcode_concatenate(val, sepany)

                if audio or video or mhtml:
                    format_code.append(self.finalize_urlcodes(video,
                                                              audio,
                                                              mhtml,
                                                              sep
                                                              ))
        if len(format_code) != len(self.urllist):
            return None, amerge, vmerge
        return format_code, amerge, vmerge
    # -----------------------------------------------------------------#

    def fcode_concatenate(self, val, sepany):
        """
        Concatenate the selected format codes appropriately
        """
        v_list, a_list, h_list = [], [], []

        for idx in val:
            if idx.startswith('Video: '):
                v_list.append(idx.split('Video: ', 1)[1])
            elif idx.startswith('Audio: '):
                a_list.append(idx.split('Audio: ', 1)[1])
            elif idx.startswith('mhtml: '):
                h_list.append(idx.split('mhtml: ', 1)[1])

        video = sepany.join(v_list) if v_list else None
        audio = sepany.join(a_list) if a_list else None
        mhtml = ','.join(h_list) if h_list else None

        return video, audio, mhtml
    # -----------------------------------------------------------------#

    def finalize_urlcodes(self, video, audio, mhtml, sep):
        """
        Finalizes the passed format codes for each URL, if any.
        Return a string with appropriate separators.
        If no audio, video or mhtml, return None type.
        """
        media_parts = [p for p in (video, audio) if p]
        codes = sep.join(media_parts) if media_parts else None

        if mhtml:
            codes = f'{codes},{mhtml}' if codes else mhtml

        return codes
