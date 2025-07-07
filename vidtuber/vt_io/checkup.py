# -*- coding: UTF-8 -*-
"""
File Name: checkup.py
Porpose: input/output file check
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: April.17.2023
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


def check_destination_dir(file_dest):
    """
    Check output destination directory only.
    return `None` if it meets the condition requirements,
    otherwise an error dialog will be shown and the function
    will return the boolean value `True`.

    """
    drn = os.path.abspath(file_dest)
    if os.path.exists(drn) and os.path.isdir(drn):
        return None

    wx.MessageBox(_('Output folder does not exist:\n\n"{}"\n').format(drn),
                  _('Vidtuber - Error!'), wx.ICON_ERROR)
    return True
