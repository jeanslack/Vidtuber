# -*- coding: UTF-8 -*-
"""
Name: formatcodelist.py
Porpose: user interface panel for format codes tasks
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: March.19.2023
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
from vidtuber.vt_io import io_tools
from vidtuber.vt_utils.utils import format_bytes


if not hasattr(wx, 'EVT_LIST_ITEM_CHECKED'):
    import wx.lib.mixins.listctrl as listmix

    class TestListCtrl(wx.ListCtrl,
                       listmix.CheckListCtrlMixin,
                       listmix.ListCtrlAutoWidthMixin
                       ):
        """
        This class is responsible for maintaining backward
        compatibility of wxPython which do not have a `ListCtrl`
        module with checkboxes feature:

        Examples of errors raised using a ListCtrl with checkboxes
        not yet implemented:

        AttributeError:
            - 'ListCtrl' object has no attribute 'EnableCheckBoxes'
            - module 'wx' has no attribute `EVT_LIST_ITEM_CHECKED`
            - module 'wx' has no attribute `EVT_LIST_ITEM_UNCHECKED`
        """
        def __init__(self,
                     parent,
                     ID,
                     pos=wx.DefaultPosition,
                     size=wx.DefaultSize,
                     style=0
                     ):
            self.parent = parent
            wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
            listmix.CheckListCtrlMixin.__init__(self)
            listmix.ListCtrlAutoWidthMixin.__init__(self)
            # self.setResizeColumn(3)

        def OnCheckItem(self, index, flag):
            """
            Send to parent (class FormatCode) index and flag.
            index = int(num) of checked item.
            flag = boolean True or False of the checked or un-checked item
            """
            self.parent.on_checkbox(self)


class FormatCode(wx.Panel):
    """
    This panel is responsible to execute format codes tasks

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
    BACKGRD = get.appset['icontheme'][1]['BACKGRD']  # help viewer backgrd
    DONE = get.appset['icontheme'][1]['TXT3']  # code text done
    WARN = get.appset['icontheme'][1]['WARN']  # code text warn
    RED = get.appset['icontheme'][1]['ERR1']   # code text err + sb error

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
        self.oldwx = None  # test result of hasattr EVT_LIST_ITEM_CHECKED

        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL)
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        # -------------listctrl
        if hasattr(wx, 'EVT_LIST_ITEM_CHECKED'):
            self.oldwx = False
            self.fcode = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT
                                     | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL
                                     )
        else:
            self.oldwx = True
            t_id = wx.ID_ANY
            self.fcode = TestListCtrl(self, t_id, style=wx.LC_REPORT
                                      | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL
                                      )
        if not self.oldwx:
            self.fcode.EnableCheckBoxes(enable=True)
        self.fcode.InsertColumn(0, (_('Format Code')), width=120)
        self.fcode.InsertColumn(1, (_('Url')), width=60)
        self.fcode.InsertColumn(2, (_('Title')), width=200)
        self.fcode.InsertColumn(3, (_('Extension')), width=80)
        self.fcode.InsertColumn(4, (_('Resolution')), width=160)
        self.fcode.InsertColumn(5, (_('Video Codec')), width=110)
        self.fcode.InsertColumn(6, (_('fps')), width=80)
        self.fcode.InsertColumn(7, (_('Audio Codec')), width=110)
        self.fcode.InsertColumn(8, (_('Size')), width=100)

        sizer_base.Add(self.fcode, 1, wx.ALL | wx.EXPAND, 5)
        # -------------textctrl
        labtstr = _('Help viewer')
        self.labtxt = wx.StaticText(self, label=labtstr)
        sizer_base.Add(self.labtxt, 0, wx.LEFT, 5)
        self.cod_text = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_MULTILINE
                                    | wx.TE_READONLY
                                    | wx.TE_RICH2,
                                    size=(-1, 100)
                                    )
        sizer_base.Add(self.cod_text, 0, wx.ALL | wx.EXPAND, 5)
        # -----------------------
        self.SetSizer(sizer_base)
        self.Layout()
        # ----------------------- Properties

        self.cod_text.SetBackgroundColour(FormatCode.BACKGRD)
        if FormatCode.appdata['ostype'] != 'Darwin':
            self.labtxt.SetLabelMarkup(f"<b>{labtstr}</b>")

        # ----------------------Binder (EVT)----------------------#
        if not self.oldwx:
            self.fcode.Bind(wx.EVT_LIST_ITEM_CHECKED, self.on_checkbox)
            self.fcode.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.on_checkbox)

    def on_checkbox(self, event):
        """
        get data from the enabled checkbox and set the values
        on corresponding key e.g.:

            `key=url: values=[Audio: code, Video: code]`
        """
        viddisp, auddisp = 'video', 'audio only'

        if not self.oldwx:
            check = self.fcode.IsItemChecked
        else:
            check = self.fcode.IsChecked

        num = self.fcode.GetItemCount()
        for url in self.urls:
            self.format_dict[url] = []
            for i in range(num):
                if check(i):
                    if (self.fcode.GetItemText(i, 1)) == url:
                        if viddisp in self.fcode.GetItemText(i, 4):
                            dispv = self.fcode.GetItemText(i, 0)
                            self.format_dict[url].append('Video: ' + dispv)
                        elif auddisp in self.fcode.GetItemText(i, 4):
                            dispa = self.fcode.GetItemText(i, 0)
                            self.format_dict[url].append('Audio: ' + dispa)
                        else:
                            dispv = self.fcode.GetItemText(i, 0)
                            self.format_dict[url].append('Video: ' + dispv)

        self.cod_text.Clear()

        for key, val in self.format_dict.items():
            if not val:
                self.cod_text.SetDefaultStyle(wx.TextAttr(FormatCode.WARN))
                self.cod_text.AppendText(f'- {key} :\n')
            elif val[0].split(': ')[1] == 'UNSUPPORTED':
                self.cod_text.SetDefaultStyle(wx.TextAttr(FormatCode.RED))
                self.cod_text.AppendText(f'- {key} :  '
                                         f'Unable to get format code\n')
            else:
                self.cod_text.SetDefaultStyle(wx.TextAttr(FormatCode.DONE))
                self.cod_text.AppendText(f'- {key} :  {val}\n')
    # ----------------------------------------------------------------------

    def set_formatcode(self, data_url, ssl):
        """
        Get URLs data and format codes by generator object
        `youtubedl_getstatistics`. Return `True` if `meta[1]`
        (error), otherwise return None as exit status.
        """
        self.cod_text.Clear()
        self.urls = data_url.copy()
        meta = None, None
        index = 0
        for link in data_url:
            data = io_tools.youtubedl_getstatistics(link, ssl)
            for meta in data:
                if meta[1]:
                    return meta[1]

            formats = iter(meta[0].get('formats', [meta[0]]))
            for n, f in enumerate(formats):
                if f.get('vcodec'):
                    vcodec, fps = f['vcodec'], f"{f.get('fps')}fps"
                else:
                    vcodec, fps = '', ''
                if f.get('acodec'):
                    acodec = f['acodec']
                else:
                    acodec = 'Video only'
                if f.get('filesize'):
                    size = format_bytes(float(f['filesize']))
                else:
                    size = 'N/A'

                formatid = f.get('format_id', 'UNSUPPORTED')
                self.fcode.InsertItem(index, formatid)
                self.fcode.SetItem(index, 1, link)
                self.fcode.SetItem(index, 2, meta[0].get('title', 'N/A'))
                self.fcode.SetItem(index, 3, f.get('ext', 'N/A'))
                self.fcode.SetItem(index, 4, f.get('format',
                                                   '-N/A').split('-')[1])
                self.fcode.SetItem(index, 5, vcodec)
                self.fcode.SetItem(index, 6, fps)
                self.fcode.SetItem(index, 7, acodec)
                self.fcode.SetItem(index, 8, size)
                if n == 0:
                    if formatid == 'UNSUPPORTED':
                        return _("ERROR: Unable to get format codes.\n\n"
                                 "Unsupported URL:\n'{0}'").format(link)

                    self.fcode.SetItemBackgroundColour(index, FormatCode.GREEN)
                index += 1
        return None
    # ----------------------------------------------------------------------

    def getformatcode(self):
        """
        Called by `on_Start` parent method. Return format code list.
        """
        format_code = []

        for url, key, val in zip(self.urls,
                                 self.format_dict.keys(),
                                 self.format_dict.values()
                                 ):
            if key == url:
                video, audio = '', ''
                if len(val) == 1:
                    if val[0].startswith('Audio: '):
                        audio = val[0].split('Audio: ')[1]
                    elif val[0].startswith('Video: '):
                        video = val[0].split('Video: ')[1]
                    else:
                        video = val[0].split('Video: ')[1]
                else:
                    index_1, index_2 = 0, 0
                    for i in val:
                        if i.startswith('Video: '):
                            index_1 += 1
                            if index_1 > 1:
                                video += f"/{i.split('Video: ')[1]}"
                            else:
                                video = i.split('Video: ')[1]

                        elif i.startswith('Audio: '):
                            index_2 += 1
                            if index_2 > 1:
                                audio += f"/{i.split('Audio: ')[1]}"
                            else:
                                audio = i.split('Audio: ')[1]
                        else:
                            index_1 += 1
                            if index_1 > 1:
                                video += f"/{i.split('Video: ')[1]}"
                            else:
                                video = i.split('Video: ')[1]

                if video and audio:
                    format_code.append(f'{video}+{audio}')
                elif video:
                    format_code.append(f'{video}')
                elif audio:
                    format_code.append(f'{audio}')

        if len(format_code) != len(self.urls):
            return None
        return format_code
