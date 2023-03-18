# -*- coding: UTF-8 -*-
"""
Name: textdrop.py
Porpose: Allows you to add text URLs
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
import wx


class TextDnD(wx.Panel):
    """
    Text control with text drag ability, accept one or
    more urls separated by a white space or newline.

    """
    def __init__(self, parent):
        """

        """
        self.parent = parent  # parent is the MainFrame
        self.file_dest = self.parent.appdata['dirdownload']

        wx.Panel.__init__(self, parent=parent)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((0, 10))
        infomsg = _("Enter URLs below")
        lbl_info = wx.StaticText(self, wx.ID_ANY, label=infomsg)
        sizer.Add(lbl_info, 0, wx.ALL | wx.EXPAND, 2)
        self.textCtrl = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_MULTILINE
                                    | wx.TE_DONTWRAP,
                                    )
        sizer.Add(self.textCtrl, 1, wx.EXPAND | wx.ALL, 2)
        sizer.Add((0, 10))
        sizer_ctrl = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizer_ctrl, 0, wx.ALL | wx.EXPAND, 0)
        self.text_path_save = wx.TextCtrl(self, wx.ID_ANY, "",
                                          style=wx.TE_PROCESS_ENTER
                                          | wx.TE_READONLY,
                                          )
        sizer_ctrl.Add(self.text_path_save, 1, wx.ALL | wx.EXPAND, 2)

        self.btn_save = wx.Button(self, wx.ID_OPEN, "...", size=(35, -1))
        sizer_ctrl.Add(self.btn_save, 0, wx.ALL
                       | wx.ALIGN_CENTER_HORIZONTAL
                       | wx.ALIGN_CENTER_VERTICAL, 2,
                       )
        self.SetSizer(sizer)

        if self.parent.appdata['ostype'] == 'Darwin':
            lbl_info.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        else:
            lbl_info.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.text_path_save.SetValue(self.file_dest)

        # Tooltip
        tip = _("Set up a temporary folder for downloads")
        self.btn_save.SetToolTip(tip)
        self.text_path_save.SetToolTip(_("Destination folder"))

        # Binding
        self.Bind(wx.EVT_TEXT, self.on_emptyText, self.textCtrl)
    # ---------------------------------------------------------

    def on_emptyText(self, event):
        """
        Text event, if empty set parent.data_url
        """
        if not self.textCtrl.GetValue().strip():
            self.parent.data_url = None
            self.parent.destroy_orphaned_window()
    # ----------------------------------------------------------

    def topic_Redirect(self):
        """
        Redirects data to specific panel
        """
        if not self.textCtrl.GetValue():
            return None

        data = (self.textCtrl.GetValue().split())
        return data
    # -----------------------------------------------------------

    def delete_all(self, event):
        """
        clear all text lines of the TxtCtrl
        """
        self.textCtrl.Clear()
        self.parent.destroy_orphaned_window()
    # -----------------------------------------------------------

    def on_file_save(self, path):
        """
        Set a specific directory for files saving

        """
        self.text_path_save.SetValue("")
        self.text_path_save.AppendText(path)
        self.file_dest = path
    # ------------------------------------------------------------

    def statusbar_msg(self, mess, bcolor, fcolor=None):
        """
        Set a status bar message of the parent method.
        bcolor: background, fcolor: foreground
        """
        self.parent.statusbar_msg(mess, bcolor, fcolor)
