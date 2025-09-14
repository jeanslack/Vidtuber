# -*- coding: UTF-8 -*-
"""
Name: playlist_indexing.py
Porpose: shows a dialog box for setting playlist indexing
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: July.17.2022
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
import re
import wx
import wx.lib.mixins.listctrl as listmix
from vidtuber.vt_dialogs.widget_utils import NormalTransientPopup


class ListCtrl(wx.ListCtrl,
               listmix.ListCtrlAutoWidthMixin,
               listmix.TextEditMixin):
    """
    A listctrl with the ability to be editable.
    """
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.populate()
        listmix.TextEditMixin.__init__(self)

    def populate(self):
        """populate with default colums"""
        self.InsertColumn(0, '#', width=30)
        self.InsertColumn(1, _('URL'), width=150)
        self.InsertColumn(2, _('Title'), width=200)
        self.InsertColumn(3, _('Playlist Items'), width=200)


class PlaylistIndexing(wx.Dialog):
    """
    Shows a dialog box for setting playlist indexing.
    See ``downloader_gui.py`` -> ``on_playlist_idx`` method for
    how to use this class.

    """
    get = wx.GetApp()  # get data from bootstrap
    OS = get.appset['ostype']
    appdata = get.appset
    if appdata['IS_DARK_THEME'] is True:
        GREEN = '#136322'
    elif appdata['IS_DARK_THEME'] is False:
        GREEN = '#4CDD67'
    else:
        GREEN = '#40804C'
    appicon = get.iconset['vidtuber']

    LGREEN = '#52ee7d'
    BLACK = '#1f1f1f'

    def __init__(self, parent, url, data):
        """
        NOTE Use 'parent, -1' param. to make parent, use 'None' otherwise

        """
        self.clrs = PlaylistIndexing.appdata['colorscheme']
        self.listurl = [list(k.keys())[0] for k in url]
        self.urls = url
        self.data = data

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE
                           | wx.RESIZE_BORDER)

        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        btn_readme = wx.Button(self, wx.ID_ANY, _("Read me"), size=(-1, -1))
        btn_readme.SetBackgroundColour(wx.Colour(PlaylistIndexing.LGREEN))
        btn_readme.SetForegroundColour(wx.Colour(PlaylistIndexing.BLACK))
        sizer_1.Add(btn_readme, 0, wx.ALL, 5)
        sizer_1.Add((0, 15), 0)
        self.lctrl = ListCtrl(self,
                              wx.ID_ANY,
                              style=wx.LC_REPORT
                              | wx.SUNKEN_BORDER
                              | wx.LC_SINGLE_SEL
                              | wx.LC_HRULES
                              | wx.LC_VRULES
                              )
        sizer_1.Add(self.lctrl, 1, wx.ALL | wx.EXPAND, 5)
        self.lctrl.SetMinSize((800, 200))
        sizer_1.Add((0, 15), 0)
        labtstr = _('Messages')
        lab = wx.StaticText(self, label=labtstr)
        sizer_1.Add(lab, 0, wx.LEFT, 5)
        self.tctrl = wx.TextCtrl(self,
                                 wx.ID_ANY, "",
                                 style=wx.TE_MULTILINE
                                 | wx.TE_CENTRE
                                 | wx.HSCROLL
                                 | wx.TE_READONLY
                                 | wx.TE_RICH2
                                 )
        sizer_1.Add(self.tctrl, 0, wx.ALL | wx.EXPAND, 5)
        self.tctrl.SetMinSize((800, 50))

        # ------ bottom layout for buttons
        grid_btn = wx.GridSizer(1, 2, 0, 0)
        gridexit = wx.BoxSizer(wx.HORIZONTAL)
        btn_reset = wx.Button(self, wx.ID_CLEAR, "")
        grid_btn.Add(btn_reset, 0, wx.ALL, 5)
        btn_cancel = wx.Button(self, wx.ID_CANCEL, "")
        gridexit.Add(btn_cancel, 0)
        btn_ok = wx.Button(self, wx.ID_OK)
        gridexit.Add(btn_ok, 0, wx.LEFT, 5)
        grid_btn.Add(gridexit, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, 5)

        # ------ final settings:
        sizer_1.Add(grid_btn, 0, wx.EXPAND)
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(PlaylistIndexing.appicon,
                                      wx.BITMAP_TYPE_ANY))
        self.SetTitle(_('Playlist Editor'))
        self.SetMinSize((800, 400))
        self.SetIcon(icon)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()

        index = 0
        for item in self.urls:
            for link, dictdata in item.items():
                self.lctrl.InsertItem(index, str(index + 1))
                self.lctrl.SetItem(index, 1, link)
                self.lctrl.SetItem(index, 2, dictdata['title'])

                if dictdata['urltype'] == 'playlist':
                    self.lctrl.SetItemBackgroundColour(index,
                                                       PlaylistIndexing.GREEN)

                if not self.data == {'': ''}:
                    for key, val in self.data.items():
                        if key == link:
                            self.lctrl.SetItem(index, 3, val)
                index += 1

        if PlaylistIndexing.OS == 'Darwin':
            self.lctrl.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
            self.tctrl.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.BOLD))
        else:
            self.lctrl.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL))
            self.tctrl.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))
            # lab.SetLabelMarkup(f"<b>{labtstr}</b>")

        self.tctrl.SetBackgroundColour(self.clrs['BACKGRD'])

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_readme)
        self.lctrl.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.on_edit_begin)
        self.lctrl.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.on_edit_end)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_cancel)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_reset, btn_reset)

        self.textstyle()

    def textstyle(self):
        """
        clear log messages and set text style on textctrl box
        """
        self.tctrl.Clear()
        self.tctrl.SetDefaultStyle(wx.TextAttr(self.clrs['TXT1']))
        self.tctrl.SetValue('Ready')
    # ------------------------------------------------------------------#

    def getvalue(self):
        """
        This method return values via the interface getvalue()
        by the caller. See the caller for more info and usage.
        """
        diz = {}
        for row, url in enumerate(self.listurl):
            txt = self.lctrl.GetItem(row, 3).GetText()
            if txt:
                diz[url] = ''.join(txt.split())

        return diz

    # ----------------------Event handler (callback)----------------------#

    def on_help(self, event):
        """
        event on button help
        """
        msg = (_('To index the media of a playlist, click on the "Playlist\n'
                 'Items" column of each corresponding URL and specify the\n'
                 'numerical indexes separated by commas, e.g. "1,2,5,8" if\n'
                 'you want to download the indexed media at 1, 2, 5, 8\n'
                 'of the playlist. It is also possible to specify intervals, '
                 'e.g.\n"1-3,7,10-13" with which the media at index 1, 2, 3, '
                 '7, 10,\n11, 12 and 13 will be downloaded.\n'))

        win = NormalTransientPopup(self,
                                   wx.SIMPLE_BORDER,
                                   msg,
                                   PlaylistIndexing.LGREEN,
                                   PlaylistIndexing.BLACK)

        # Show the popup right below or above the button
        # depending on available screen space...
        btn = event.GetEventObject()
        pos = btn.ClientToScreen((0, 0))
        sz = btn.GetSize()
        win.Position(pos, (0, sz[1]))

        win.Popup()
    # --------------------------------------------------------------#

    def on_edit_end(self, event):
        """
        Checking event-entered strings using REGEX:

            Allows min 0 to max 999 digits and does not allow
            numbers with leading zeroes like 07 or 005, allows
            a number separated by hyphen like 22-33 and supports
            comma followed by a white space. Note that all white
            spaces are stripped before come to parsing by REGEX:
            see `string` var below.

        Some event examples:

        row_id = event.GetIndex()  # Get the current row
        col_id = event.GetColumn()  # Get the current column
        new_data = event.GetLabel()  # Get the changed data
        cols = self.lctrl.GetColumnCount()  # Get the total number of col
        rows = self.lctrl.GetItemCount()  # Get the total number of rows

        """
        # wxd = wx.DateTime.Now()
        # date = wxd.Format('%H:%M:%S')
        new_data = event.GetLabel()  # Get the changed data
        errbeg = _('ERROR: Invalid option')
        # errend = _('please try again.')
        assign = _('OK: Indexes to download')
        string = ''.join(new_data.split())

        if string == '':
            event.Veto()
            return
        check = bool(re.search(r"^(?:[1-9]\d\d|[1-9]?\d)(?:-(?:[1-9]\d\d"
                               r"|[1-9]?\d))?(?:,\s?(?:[1-9]\d\d|[1-9]?\d)"
                               r"(?:-(?:[1-9]\d\d|[1-9]?\d))?)*$", string))
        if check is not True:
            self.tctrl.SetDefaultStyle(wx.TextAttr(self.clrs['ERR1']))
            self.tctrl.SetValue(f'{errbeg}: "{new_data}"')
            event.Veto()
            return

        self.tctrl.SetDefaultStyle(wx.TextAttr(self.clrs['TXT3']))
        self.tctrl.SetValue(f'{assign}: "{string}"')
    # ------------------------------------------------------------------#

    def on_edit_begin(self, event):
        """
        Columns 0 and 1 must not be editable for
        link without playlist.
        """
        row_id = event.GetIndex()

        # wxd = wx.DateTime.Now()
        # date = wxd.Format('%H:%M:%S')
        invalidmsg = _('The selected URL does not refer to an individual '
                       'playlist. Only lines marked green can be indexed.')

        # invalidmsg = _('WARNING: The selected URL does not refer to a '
        #                'playlist. Only lines marked green can be indexed.')

        colour = PlaylistIndexing.GREEN

        if event.GetColumn() in (0, 1, 2):
            event.Veto()
        elif event.GetColumn() == 3:
            # It looks like the HTML color codes are translated to RGB here
            if self.lctrl.GetItemBackgroundColour(row_id) != colour:
                self.tctrl.SetDefaultStyle(wx.TextAttr(self.clrs['WARN']))
                self.tctrl.SetValue(f'{invalidmsg}')
                event.Veto()
            else:
                event.Skip()  # or event.Allow()
        else:
            event.Skip()  # or event.Allow()
    # ------------------------------------------------------------------#

    def on_reset(self, event):
        """
        Reset all items on editable columns and clear log messages
        """
        rows = self.lctrl.GetItemCount()  # Get the total number of rows
        for row in range(rows):
            self.lctrl.SetItem(row, 3, '')

        self.textstyle()
    # ------------------------------------------------------------------#

    def on_close(self, event):
        """
        Close this dialog without saving anything
        """
        event.Skip()
    # ------------------------------------------------------------------#

    def on_ok(self, event):
        """
        Don't use self.Destroy() in this dialog
        """
        event.Skip()
