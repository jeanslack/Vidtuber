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


def check_duplicated_indexes(string, entry):
    """
    Check for duplicates. Return None if no duplicates,
    a message string otherwise.

    """
    if not string or not entry:
        return None

    rangestr = []
    itemstr = []
    for x in string.split(','):
        if not x.isdigit():
            rangestr.append(x.split('-'))
        else:
            itemstr.append(x)

    totalrange = []
    for x in rangestr:
        for r in range(int(x[0]), int(x[1]) + 1):
            totalrange.append(r)

    alreadyexists = totalrange + [int(x) for x in itemstr if x.isdigit()]

    if '-' in entry:  # entry is a range
        start, end = int(entry.split('-')[0]), int(entry.split('-')[1])

        if start > end:
            return f'ERROR: Invalid range: "{start}" is > "{end}"'

        entrylist = list(range(start, end + 1))
        duplicates = alreadyexists + entrylist
        if [i for i in set(duplicates) if duplicates.count(i) > 1]:

            return (_('Items in Range "{0}" already included in '
                      'this row').format(entry))
        return None

    if int(entry) in alreadyexists:
        return _('Index "{0}" already included in this row').format(entry)

    return None


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
        self.InsertColumn(4, _('Index/Range'), width=230)


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
        self.labstatus = wx.StaticText(self, label='')
        msg = _('Add Index/Range')
        self.labstatus.SetLabelMarkup(f"<b>{msg}</b>")
        sizer_1.Add(self.labstatus, 0, wx.CENTRE)
        sizer_1.Add((0, 20), 0)
        griditem = wx.FlexGridSizer(1, 6, 0, 0)
        labstr = _('Index')
        labitem = wx.StaticText(self, label=labstr)
        griditem.Add(labitem, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.spin_index = wx.SpinCtrl(self, wx.ID_ANY,
                                      "1", min=1,
                                      max=999, size=(-1, -1),
                                      style=wx.TE_PROCESS_ENTER,
                                      )
        griditem.Add(self.spin_index, 0, wx.LEFT | wx.CENTRE, 5)

        self.btn_add_indx = wx.Button(self, wx.ID_ANY, _("Add"), size=(-1, -1))
        self.btn_add_indx.SetToolTip(_('Add index to the selected playlist. '
                                       'Can be used multiple times.'))
        griditem.Add(self.btn_add_indx, 0, wx.LEFT | wx.CENTRE, 5)

        labstr = _('Range')
        labto = wx.StaticText(self, label=labstr)
        griditem.Add(labto, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 30)

        self.spin_range = wx.SpinCtrl(self, wx.ID_ANY,
                                      "2", min=2,
                                      max=1000, size=(-1, -1),
                                      style=wx.TE_PROCESS_ENTER,
                                      )
        griditem.Add(self.spin_range, 0, wx.LEFT | wx.CENTRE, 5)

        self.btn_add_range = wx.Button(self, wx.ID_ANY, _("Add"),
                                       size=(-1, -1))
        self.btn_add_range.SetToolTip(_('Add range to the selected playlist. '
                                        'Can be used multiple times.'))
        griditem.Add(self.btn_add_range, 0, wx.LEFT | wx.CENTRE, 5)
        sizer_1.Add(griditem, 0, wx.ALL | wx.CENTER, 0)
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

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_readme)

        self.Bind(wx.EVT_LIST_ITEM_CHECKED, self.on_check, self.plctrl)
        self.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.on_uncheck, self.plctrl)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.plctrl)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselect, self.plctrl)

        self.Bind(wx.EVT_SPINCTRL, self.on_index, self.spin_index)
        # self.Bind(wx.EVT_SPINCTRL, self.on_range, self.spin_range)

        self.Bind(wx.EVT_BUTTON, self.on_add_index, self.btn_add_indx)
        self.Bind(wx.EVT_BUTTON, self.on_add_range, self.btn_add_range)

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
                 "To index the playlist, use the «Index» and/or «Range» "
                 "controls and then click the\ncorresponding «Add» button. "
                 "You can use these controls multiple times for the\n"
                 "same selected playlist.\n\n"
                 "To remove a playlist, uncheck the box in the «Selection» "
                 "column.\nTo remove all settings, click the "
                 "«Clear» button.\nTo confirm everything, click the «OK» "
                 "button.\n\n"
                 "Examples:\n"
                 "Add item 8 to download only the index 8 of the playlist.\n"
                 "Add the range 10-13 to download the playlist's videos "
                 "within that range.\nAdd 1-3,7,10-13 with which the media "
                 "at index 1, 2, 3, 7, 10, 11, 12 and 13 will\n"
                 "be downloaded."))

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
        msg = _('Add Index/Range')
        self.labstatus.SetLabelMarkup(f"<b>{msg}</b>")
        self.Layout()
    # --------------------------------------------------------------#

    def on_check(self, event):
        """
        Event on checkbox enabled
        """
        row_id = event.GetIndex()
        self.plctrl.Focus(row_id)
        self.plctrl.Select(row_id, on=1)  # default event selection
        msg = _('Add Index/Range')
        self.labstatus.SetLabelMarkup(f"<b>{msg}</b>")
        self.Layout()
    # --------------------------------------------------------------#

    def on_index(self, event):
        """
        Event on spin_index control
        """
        idxitem = self.spin_index.GetValue()
        self.spin_range.SetMin(idxitem + 1)
    # --------------------------------------------------------------#

    # def on_range(self, event):
    #     """
    #     Event on spin_range control
    #     """
    #     pass
    # --------------------------------------------------------------#

    def on_add_index(self, event):
        """
        Event on press btn_item
        """
        idxitem = self.spin_index.GetValue()
        sel = self.plctrl.GetFocusedItem()
        if idxitem and sel != -1:
            curidx = self.plctrl.GetItem(sel, 4).GetText()
            ret = check_duplicated_indexes(str(curidx), str(idxitem))
            if ret:
                self.labstatus.SetLabelMarkup(f"<b><span foreground="
                                              f"'red'>{ret}</span></b>")
                self.Layout()
                return

            newitem = f'{curidx},{idxitem}' if curidx else f'{idxitem}'
            self.plctrl.SetItem(sel, 4, newitem, imageId=-1)

            if not self.plctrl.IsItemChecked(sel):
                self.plctrl.CheckItem(sel, check=True)

            msg = _('Added index: "{0}"').format(idxitem)
            self.labstatus.SetLabelMarkup(f"<b>{msg}</b>")
            self.Layout()
    # --------------------------------------------------------------#

    def on_add_range(self, event):
        """
        Event on press btn_range
        """
        idxfrom = self.spin_index.GetValue()
        idxto = self.spin_range.GetValue()
        sel = self.plctrl.GetFocusedItem()
        if idxfrom and idxto and sel != -1:
            curidx = self.plctrl.GetItem(sel, 4).GetText()

            ret = check_duplicated_indexes(str(curidx), f'{idxfrom}-{idxto}')
            if ret:
                self.labstatus.SetLabelMarkup(f"<b><span foreground="
                                              f"'red'>{ret}</span></b>")
                self.Layout()
                return

            newrange = (f'{curidx},{idxfrom}-{idxto}'
                        if curidx else f'{idxfrom}-{idxto}')

            self.plctrl.SetItem(sel, 4, newrange, imageId=-1)

            # if not checked, auto check the corrisponding checkbox
            if not self.plctrl.IsItemChecked(sel):
                self.plctrl.CheckItem(sel, check=True)

            msg = _('Added range indexes: "{0}-{1}"').format(idxfrom, idxto)
            self.labstatus.SetLabelMarkup(f"<b>{msg}</b>")
            self.Layout()
    # --------------------------------------------------------------#

    def on_select(self, event):
        """
        Selecting line with mouse or up/down keyboard buttons
        """
        self.spin_index.Enable(), self.btn_add_indx.Enable()
        self.spin_range.Enable(), self.btn_add_range.Enable()
    # ----------------------------------------------------------------------

    def on_deselect(self, event):
        """
        Event to deselect a line when clicking
        in an empty space of the control list
        """
        self.spin_index.Disable(), self.btn_add_indx.Disable()
        self.btn_add_range.Disable(), self.spin_range.Disable()
    # ----------------------------------------------------------------------

    def on_reset(self, event):
        """
        Reset all items on editable columns and clear log messages
        """
        rows = self.plctrl.GetItemCount()  # Get the total number of rows
        for row in range(rows):
            self.plctrl.SetItem(row, 4, '')
            self.plctrl.CheckItem(row, check=False)

        self.spin_index.SetValue(1)
        self.spin_range.SetMin(self.spin_index.GetValue() + 1)
        self.spin_range.SetValue(2)
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
