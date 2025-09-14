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
import wx
from vidtuber.vt_dialogs.widget_utils import NormalTransientPopup


class PlayListCtrl(wx.ListCtrl):
    """
    This class inherits is the ListCtrl object.
    Note that this object has PlaylistIndexing parented.
    """
    def __init__(self, parent):
        """
        Constructor, style must be wx.LC_SINGLE_SEL .
        """
        self.parent = parent  # parent is PlaylistIndexing class
        wx.ListCtrl.__init__(self,
                             parent,
                             wx.ID_ANY,
                             style=wx.LC_REPORT
                             | wx.SUNKEN_BORDER
                             | wx.LC_SINGLE_SEL
                             | wx.LC_HRULES
                             | wx.LC_VRULES
                             )
        self.populate()

    def populate(self):
        """
        populate with default colums
        """
        self.EnableCheckBoxes(enable=True)
        self.InsertColumn(0, _('Selection'), width=120)
        self.InsertColumn(1, _('URL'), width=150)
        self.InsertColumn(2, _('Title'), width=200)
        self.InsertColumn(3, _('Type'), width=100)
        self.InsertColumn(4, _('Indexes'), width=230)


class PlaylistIndexing(wx.Dialog):
    """
    Dialog box for setting playlist indexing.

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
        See ``downloader_gui.py`` -> ``on_playlist_idx`` method for
        how to use this class.
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
        self.plctrl = PlayListCtrl(self)  # ListCtrl instance
        sizer_1.Add(self.plctrl, 1, wx.ALL | wx.EXPAND, 5)
        self.plctrl.SetMinSize((800, 200))
        sizer_1.Add((0, 15), 0)
        griditem = wx.FlexGridSizer(1, 3, 0, 0)
        labstr = _('Add item:')
        labitem = wx.StaticText(self, label=labstr)
        griditem.Add(labitem, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.spin_item = wx.SpinCtrl(self, wx.ID_ANY,
                                     "0", min=0,
                                     max=1000, size=(-1, -1),
                                     style=wx.TE_PROCESS_ENTER,
                                     )
        griditem.Add(self.spin_item, 0, wx.LEFT | wx.CENTRE, 5)

        self.btn_item = wx.Button(self, wx.ID_ANY, _("Add"), size=(-1, -1))
        self.btn_item.SetToolTip(_('Add item to the selected playlist. Can '
                                   'be used multiple times.'))
        griditem.Add(self.btn_item, 0, wx.LEFT | wx.CENTRE, 20)
        sizer_1.Add(griditem, 0, wx.ALL | wx.CENTER, 0)

        sizer_1.Add((0, 15), 0)

        gridrange = wx.FlexGridSizer(1, 5, 0, 0)
        labstr = _('Add range')
        labfrom = wx.StaticText(self, label=labstr)
        gridrange.Add(labfrom, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.spin_from = wx.SpinCtrl(self, wx.ID_ANY,
                                     "0", min=0,
                                     max=1000, size=(-1, -1),
                                     style=wx.TE_PROCESS_ENTER,
                                     )
        gridrange.Add(self.spin_from, 0, wx.LEFT | wx.CENTRE, 5)

        labstr = _('To')
        labto = wx.StaticText(self, label=labstr)
        gridrange.Add(labto, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 10)

        self.spin_to = wx.SpinCtrl(self, wx.ID_ANY,
                                   "0", min=0,
                                   max=1000, size=(-1, -1),
                                   style=wx.TE_PROCESS_ENTER,
                                   )
        gridrange.Add(self.spin_to, 0, wx.LEFT | wx.CENTRE, 10)

        self.btn_range = wx.Button(self, wx.ID_ANY, _("Add"), size=(-1, -1))
        self.btn_range.SetToolTip(_('Add range to the selected playlist. '
                                    'Can be used multiple times.'))
        gridrange.Add(self.btn_range, 0, wx.LEFT | wx.CENTRE, 20)
        sizer_1.Add(gridrange, 0, wx.ALL | wx.CENTER, 0)
        sizer_1.Add((0, 15), 0)
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

        if PlaylistIndexing.OS == 'Darwin':
            self.plctrl.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
        else:
            self.plctrl.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL))
            # lab.SetLabelMarkup(f"<b>{labtstr}</b>")

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_readme)

        self.Bind(wx.EVT_LIST_ITEM_CHECKED, self.on_check, self.plctrl)
        self.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.on_uncheck, self.plctrl)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.plctrl)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselect, self.plctrl)

        self.Bind(wx.EVT_BUTTON, self.on_items, self.btn_item)
        self.Bind(wx.EVT_BUTTON, self.on_range, self.btn_range)

        self.Bind(wx.EVT_BUTTON, self.on_close, btn_cancel)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_reset, btn_reset)

        self.on_deselect(None)
        self.setdefault()

    def setdefault(self):
        """
        clear log messages and set text style on textctrl box
        """
        index = 0
        for item in self.urls:
            for link, dictdata in item.items():
                self.plctrl.InsertItem(index, str(index + 1))
                # self.plctrl.InsertItem(index, '')  # do not add srt indx
                self.plctrl.SetItem(index, 1, link)
                self.plctrl.SetItem(index, 2, dictdata['title'])
                self.plctrl.SetItem(index, 3, dictdata['urltype'])
                index += 1

        for row in range(self.plctrl.GetItemCount()):  # total number of rows
            line = self.data.get(self.plctrl.GetItem(row, 1).GetText(), False)
            if line:
                self.plctrl.SetItem(row, 4, line[0])
                self.plctrl.CheckItem(row, check=line[1])
                # self.plctrl.SetItemBackgroundColour(row,
                #                                     PlaylistIndexing.GREEN)
            else:
                self.plctrl.SetItem(row, 4, '')
                self.plctrl.CheckItem(row, check=line)
    # ------------------------------------------------------------------#

    def getvalue(self):
        """
        This method return values via the interface getvalue()
        by the caller. See the caller for more info and usage.
        """
        diz = {}
        num = self.plctrl.GetItemCount()  # n° total items
        for i in range(num):
            if self.plctrl.IsItemChecked(i):
                url = self.plctrl.GetItem(i, 1).GetText()
                plidx = self.plctrl.GetItem(i, 4).GetText()
                diz[url] = [''.join(plidx.split()), True]

        return diz
    # ----------------------Event handler (callback)----------------------#

    def on_help(self, event):
        """
        event on button help
        """
        msg = (_("To enable a playlist, check the box in the «Selection» "
                 "column for each desired row.\nThis "
                 "will download the title and the playlist containing it. "
                 "If not any title is present,\nthe playlist will still be "
                 "downloaded only if the URL refers to a playlist.\n\n"
                 "To index the playlist, use the «Add Item» and «Add Range» "
                 "controls and then click\nthe «Add» button. You "
                 "can use these controls multiple times for the same "
                 "selected\nplaylist.\n\n"
                 "To remove a playlist, uncheck the box in the «Selection» "
                 "column.\nTo remove all settings, click the "
                 "«Clear» button.\nTo confirm everything, click the «OK» "
                 "button.\n\n"
                 "Examples:\n"
                 "Add item 8 to download only the index 8 of the playlist.\n"
                 "Add the range 10-13 to download the playlist's videos "
                 "within that range.\nAdd 1-3,7,10-13 with which the media at "
                 "index 1, 2, 3, 7, 10, 11, 12 and 13 will be\ndownloaded."))

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

    def on_uncheck(self, event):
        """
        Event on checkbox disabled
        """
        row_id = event.GetIndex()
        self.plctrl.Select(row_id, on=0)  # default event selection
        self.plctrl.SetItem(row_id, 4, '', imageId=-1)
    # --------------------------------------------------------------#

    def on_check(self, event):
        """
        Event on checkbox enabled
        """
        row_id = event.GetIndex()
        self.plctrl.Focus(row_id)
        self.plctrl.Select(row_id, on=1)  # default event selection
    # --------------------------------------------------------------#

    def on_items(self, event):
        """
        Event on press btn_item
        """
        newval = self.spin_item.GetValue()
        sel = self.plctrl.GetFocusedItem()
        if newval and sel != -1:
            currv = self.plctrl.GetItem(sel, 4).GetText()
            setval = f'{currv},{newval}' if currv else f'{newval}'
            self.plctrl.SetItem(sel, 4, setval, imageId=-1)

            if not self.plctrl.IsItemChecked(sel):
                self.plctrl.CheckItem(sel, check=True)
    # --------------------------------------------------------------#

    def on_range(self, event):
        """
        Event on press btn_range
        """
        newfrom = self.spin_from.GetValue()
        newto = self.spin_to.GetValue()
        sel = self.plctrl.GetFocusedItem()
        if newfrom and newto and sel != -1:
            currv = self.plctrl.GetItem(sel, 4).GetText()
            setval = (f'{currv},{newfrom}-{newto}'
                      if currv else f'{newfrom}-{newto}')
            self.plctrl.SetItem(sel, 4, setval, imageId=-1)

            if not self.plctrl.IsItemChecked(sel):
                self.plctrl.CheckItem(sel, check=True)
    # --------------------------------------------------------------#

    def on_select(self, event):
        """
        Selecting line with mouse or up/down keyboard buttons
        """
        self.spin_item.Enable(), self.btn_item.Enable()
        self.spin_from.Enable(), self.spin_to.Enable()
        self.btn_range.Enable()
    # ----------------------------------------------------------------------

    def on_deselect(self, event):
        """
        Event to deselect a line when clicking
        in an empty space of the control list
        """
        self.spin_item.Disable(), self.btn_item.Disable()
        self.btn_range.Disable(), self.spin_from.Disable(),
        self.spin_to.Disable()

        self.spin_item.SetValue(0), self.spin_from.SetValue(0),
        self.spin_to.SetValue(0)
    # ----------------------------------------------------------------------

    def on_reset(self, event):
        """
        Reset all items on editable columns and clear log messages
        """
        rows = self.plctrl.GetItemCount()  # Get the total number of rows
        for row in range(rows):
            self.plctrl.SetItem(row, 4, '')
            self.plctrl.CheckItem(self, row, check=False)
    # --------------------------------------------------------------#

    def on_close(self, event):
        """
        Close this dialog without saving anything
        """
        event.Skip()
    # --------------------------------------------------------------#

    def on_ok(self, event):
        """
        Don't use self.Destroy() in this dialog
        """
        event.Skip()
