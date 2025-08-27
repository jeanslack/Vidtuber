# -*- coding: UTF-8 -*-
"""
Name: confirm_dialog.py
Porpose: confirmation dialog for final settings.
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Aug.25.2025
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


class Confirmation_Dlg(wx.Dialog):
    """
    Displays a confirmation dialog before running download processes.
    This dialog allows the user to customize command-line arguments.
    """
    def __init__(self, parent, data, urls):
        """
        Attributes defined here:
        It accept two type list object:
        - data, command-line arguments.
        - urls, a matched URL(s) list.
        """
        self.urls = urls  # list
        self.edited = data.copy()
        get = wx.GetApp()  # get data from bootstrap
        green = '#52ee7d'
        black = '#1f1f1f'

        wx.Dialog.__init__(self, parent, -1,
                           style=wx.DEFAULT_DIALOG_STYLE
                           | wx.RESIZE_BORDER
                           )
        # ----------------------Layout----------------------#
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        self.url_select = wx.ListCtrl(self,
                                      wx.ID_ANY,
                                      style=wx.LC_REPORT
                                      | wx.SUNKEN_BORDER
                                      | wx.LC_SINGLE_SEL,
                                      )
        self.url_select.SetMinSize((600, 200))
        self.url_select.InsertColumn(0, _('URL Summary'), width=700)
        sizer_base.Add(self.url_select, 0, wx.ALL | wx.EXPAND, 5)
        msg = _('Edit command arguments')
        self.ckbx_showcmd = wx.CheckBox(self, wx.ID_ANY, msg)
        sizer_base.Add(self.ckbx_showcmd, 0, wx.ALL | wx.EXPAND, 5)
        self.labcmd = wx.StaticText(self, label=_('Command arguments'))
        sizer_base.Add(self.labcmd, 0, wx.ALL, 5)
        self.labcmd.Hide()
        self.textargs = wx.TextCtrl(self,
                                    wx.ID_ANY, "",
                                    style=wx.TE_MULTILINE | wx.TE_RICH2,
                                    )
        self.textargs.SetMinSize((600, 200))

        if get.appset['ostype'] == 'Darwin':
            self.textargs.SetFont(wx.Font(12, wx.FONTFAMILY_TELETYPE,
                                          wx.NORMAL, wx.NORMAL))
        else:
            self.textargs.SetFont(wx.Font(10, wx.FONTFAMILY_TELETYPE,
                                          wx.NORMAL, wx.NORMAL))
        self.textargs.Hide()
        sizer_base.Add(self.textargs, 1, wx.ALL | wx.EXPAND, 5)
        # ----- confirm buttons layout
        sizbott = wx.BoxSizer(wx.HORIZONTAL)
        btn_cancel = wx.Button(self, wx.ID_CANCEL, "")
        sizbott.Add(btn_cancel, 0)
        self.btn_ok = wx.Button(self, wx.ID_OK, "Run")
        sizbott.Add(self.btn_ok, 0, wx.LEFT, 5)
        sizer_base.Add(sizbott, 0, wx.ALL | wx.ALIGN_RIGHT
                       | wx.RIGHT, border=5)
        # set caption and min size
        self.SetTitle(_('Confirmation Procedure'))
        self.SetMinSize((750, 315))
        # ------ set sizer
        self.SetSizer(sizer_base)
        self.Fit()
        self.Layout()
        self.textargs.SetBackgroundColour(black)
        self.textargs.SetForegroundColour(green)
        # populate ListCtrl and set self.logdata dict
        if not self.edited:
            self.on_deselect(None)
        else:
            self.on_update()

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.url_select)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselect,
                  self.url_select)
        self.Bind(wx.EVT_CHECKBOX, self.on_show_cmd, self.ckbx_showcmd)
        self.Bind(wx.EVT_TEXT, self.on_edit_arg, self.textargs)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_cancel)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)

    # --------------------------------------------------------------------#

    def on_update(self):
        """
        This method is called by __init__ method only the first time
        to update the selected item if any. If no any item available
        the init method call on_deselect method instead.
        """
        sel = self.url_select.GetFocusedItem()
        selitem = sel if sel != -1 else 0
        index = 0
        for url in self.urls:
            self.url_select.InsertItem(index, url)
            index += 1

        if index:
            self.url_select.Focus(selitem)  # make the line the current line
            self.url_select.Select(selitem, on=1)  # default event selection
            self.on_select(self)

    # ----------------------Event handler (callback)----------------------#

    def on_show_cmd(self, event):
        """
        CheckBox event, Show or Hide the text control for
        the command-line arguments.
        """
        if self.ckbx_showcmd.GetValue():
            self.labcmd.Show(), self.textargs.Show()
        else:
            self.textargs.Hide(), self.labcmd.Hide()

        self.Fit()
        self.Layout()
    # --------------------------------------------------------------------#

    def on_edit_arg(self, event):
        """
        Respond to a wxEVT_TEXT event, generated when the text
        is modified by user (changing text on command line
        arguments).
        """
        index = self.url_select.GetFocusedItem()
        if index == -1:
            return

        if self.textargs.IsModified():
            self.edited[index] = self.textargs.GetValue()
    # --------------------------------------------------------------------#

    def on_deselect(self, event):
        """
        on_deselect make the text control not editable
        and clear all text field. See also on_select doc string.
        """
        self.textargs.ChangeValue('')
        self.textargs.SetEditable(False)
    # ------------------------------------------------------------------#

    def on_select(self, event):
        """
        Show text data for the selected index and make
        editable the text control .
        Note that on_select and on_deselect methods use
        ChangeValue() function to reset text control which does
        not generate the wxEVT_TEXT event at all.
        """
        index = self.url_select.GetFocusedItem()
        self.textargs.SetEditable(True)
        self.textargs.ChangeValue(self.edited[index])
    # ------------------------------------------------------------------#

    def getvalue(self):
        """
        This method return values via the getvalue() interface from
        the caller (parent). See the caller for more info and usage.
        """
        return self.edited
    # ------------------------------------------------------------------#

    def on_ok(self, event):
        """
        Don't use self.Destroy() here
        """
        event.Skip()
    # ------------------------------------------------------------------#

    def on_close(self, event):
        """
        Close this dialog without saving anything
        """
        event.Skip()
    # ------------------------------------------------------------------#
