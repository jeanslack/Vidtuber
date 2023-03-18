# -*- coding: UTF-8 -*-
"""
Name: showlogs.py
Porpose: show logs data
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
import wx
from pubsub import pub


class ShowLogs(wx.Dialog):
    """
    View log data from files within the log directory

    """
    # list of logs files to include
    LOGNAMES = ('yt_dlp.log')

    def __init__(self, parent, dirlog, OS):
        """
        Attributes defined here:
        self.dirlog > log location directory (depends from OS)
        self.logdata > dict object {KEY=file name.log: VAL=log data, ...}
        self.selected > None if item on listctrl is not selected

        """
        self.dirlog = dirlog
        self.logdata = {}
        self.selected = None
        get = wx.GetApp()  # get data from bootstrap
        colorscheme = get.appset['icontheme'][1]
        appicon = get.iconset['vidtuber']

        wx.Dialog.__init__(self, None,
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
                           )
        # ----------------------Layout----------------------#
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        self.log_select = wx.ListCtrl(self,
                                      wx.ID_ANY,
                                      style=wx.LC_REPORT
                                      | wx.SUNKEN_BORDER
                                      | wx.LC_SINGLE_SEL,
                                      )
        self.log_select.SetMinSize((600, 200))
        self.log_select.InsertColumn(0, _('Log file list'), width=300)
        sizer_base.Add(self.log_select, 0, wx.ALL | wx.EXPAND, 5)
        lablog = wx.StaticText(self, label=_('Log messages'))
        sizer_base.Add(lablog, 0, wx.ALL, 5)
        self.textdata = wx.TextCtrl(self,
                                    wx.ID_ANY, "",
                                    style=wx.TE_MULTILINE
                                    | wx.TE_READONLY
                                    | wx.TE_RICH2,
                                    )
        self.textdata.SetMinSize((600, 200))
        self.textdata.SetBackgroundColour(colorscheme['BACKGRD'])
        self.textdata.SetDefaultStyle(wx.TextAttr(colorscheme['TXT3']))

        if OS == 'Darwin':
            self.textdata.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL,
                                          wx.NORMAL))
        else:
            self.textdata.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))

        sizer_base.Add(self.textdata, 1, wx.ALL | wx.EXPAND, 5)
        # ------ btns bottom
        grdBtn = wx.GridSizer(1, 2, 0, 0)
        grid_funcbtn = wx.BoxSizer(wx.HORIZONTAL)
        button_update = wx.Button(self, wx.ID_REFRESH,
                                  _("Refresh all log files"))
        grid_funcbtn.Add(button_update, 0, wx.ALL
                         | wx.ALIGN_CENTER_VERTICAL, 5
                         )
        button_clear = wx.Button(self, wx.ID_CLEAR,
                                 _("Clear selected log")
                                 )
        grid_funcbtn.Add(button_clear, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        grdBtn.Add(grid_funcbtn)
        grdexit = wx.BoxSizer(wx.HORIZONTAL)
        button_close = wx.Button(self, wx.ID_CLOSE, "")
        grdexit.Add(button_close, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        grdBtn.Add(grdexit, flag=wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, border=0)
        sizer_base.Add(grdBtn, 0, wx.ALL | wx.EXPAND, 0)
        # set caption and min size
        self.SetTitle(_('Showing log messages'))
        self.SetMinSize((700, 500))
        # ------ set sizer
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(appicon, wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        self.SetSizer(sizer_base)
        self.Fit()
        self.Layout()

        # populate ListCtrl and set self.logdata dict
        self.on_update(self)

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.log_select)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselect,
                  self.log_select)
        self.Bind(wx.EVT_BUTTON, self.on_update, button_update)
        self.Bind(wx.EVT_BUTTON, self.on_clear, button_clear)
        self.Bind(wx.EVT_BUTTON, self.on_close, button_close)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    # ----------------------Event handler (callback)----------------------#

    def on_clear(self, event):
        """
        clear data logging from selected log file

        """
        if not self.selected:
            wx.MessageBox(_('Select a log file'),
                          'Vidtuber', wx.ICON_INFORMATION)
            return

        index = self.log_select.GetFocusedItem()
        name = self.log_select.GetItemText(index, 0)

        if wx.MessageBox(_('Are you sure you want to clear the selected '
                           'log file?'), "Vidtuber",
                         wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
            return

        with open(os.path.join(self.dirlog, name),
                  'w', encoding='utf8') as log:
            log.write('')

        self.on_update(self)
    # --------------------------------------------------------------------#

    def on_update(self, event):
        """
        update data with new incoming

        """
        sel = self.log_select.GetFocusedItem()
        selitem = sel if sel != -1 else 0

        self.logdata.clear()
        self.log_select.DeleteAllItems()
        index = 0
        for f in os.listdir(self.dirlog):
            if os.path.basename(f) in ShowLogs.LOGNAMES:  # append listed only
                with open(os.path.join(self.dirlog, f),
                          'r', encoding='utf8') as log:
                    self.logdata[f] = log.read()  # set value
                    self.log_select.InsertItem(index, f)
                index += 1

        if index:
            self.log_select.Focus(selitem)  # make the line the current line
            self.log_select.Select(selitem, on=1)  # default event selection
            self.on_select(self)
    # --------------------------------------------------------------------#

    def on_deselect(self, event):
        """
        Reset on de-selected

        """
        self.textdata.Clear()
        self.selected = None
    # ------------------------------------------------------------------#

    def on_select(self, event):
        """
        show data during items selection

        """
        self.textdata.Clear()  # delete previous append:
        index = self.log_select.GetFocusedItem()
        name = self.log_select.GetItemText(index, 0)
        self.selected = name
        self.textdata.AppendText(self.logdata.get(name))
    # ------------------------------------------------------------------#

    def on_close(self, event):
        """
        Destroy this dialog
        """
        pub.sendMessage("DESTROY_ORPHANED_WINDOWS", msg='ShowLogs')
