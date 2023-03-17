# -*- coding: UTF-8 -*-
"""
Name: settings_manager.py
Porpose: Read and write the configuration file
Compatibility: Python3
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
import json


class ConfigManager:
    """
    It represents the setting of the user parameters
    of the program and the configuration file in its
    read and write aspects.

    Usage:

    write a new conf.json :
        >>> from settings_manager import ConfigManager
        >>> confmng = ConfigManager('fileconfpath.json')
        >>> confmng.write_options()

    read the current fileconf.json :
        >>> settings = confmng.read_options()

    example of modify data into current file conf.json:
        >>> settings['outputfile'] = '/home/user/MyVideos'
        >>> confmng.write_options(**settings)
    ------------------------------------------------------

    Options description:

    confversion (float):
        current version of this configuration file

    dirdownload (str):
        file destination path used by the downloader

    ffmpeg_cmd, ffprobe_cmd, (str):
        Absolute or relative path name of the executable.
        If an empty ("") string is found, starts the wizard.

    ffmpeg_islocal, ffprobe_islocal, (bool):
        With True the user enables the executable locally

    warnexiting (bool):
        with True displays a message dialog before exiting the app

    icontheme (str):
        Icon theme Name (see art folder)

    toolbarsize (int):
        Set toolbar icon size, one of 16, 24, 32, 64 default is 24 px.

    toolbarpos (int):
        Set toolbar positioning. 0 placed on top side;
        1 placed at the bottom side; 2 placed at the rigth side;
        3 is placed at the left side. default is 0 .

    toolbartext (bool):
        True, enables text alongside toolbar buttons. Default is False.

    window_size (list):
        [int(Height), int(Width)] last current window dimension before
        exiting the application.

    window_position (list):
        [int(x), in(y)] last current window position on monitor screen
        before exiting the application.

    clearcache (bool):
        with True, clear the cache before exiting the application,
        default is False

    clearlogfiles (bool):
        with True, erases all log files content before exiting the
        application, default is False.

    downloader (bool, str):
        sets the downloader to use when application startup.
        one of `disabled`,` youtube_dl`, `yt_dlp` or False
        Where `disabled` means not load anything, `youtube_dl`
        means load/use youtube-dl on sturtup, `yt_dlp` means load/use
        yt_dl on sturtup, `false` means *not set at all* then
        a wizard dialog will be displayed.

    playlistsubfolder (bool):
        Auto-create subfolders when download the playlists,
        default value is True.

    locale_name (str):
        "Default", set system language to vidtuber message catalog
        if available, set to English otherwise.
        It supports canonical form of locale names as used on UNIX systems,
        eg. xx or xx_YY format, where xx is ISO 639 code of language and
        YY is ISO 3166 code of the country. Examples are "en", "en_GB",
        "en_US" or "fr_FR".

    """
    VERSION = 1.1
    DEFAULT_OPTIONS = {"confversion": VERSION,
                       "dirdownload": f"{os.path.expanduser('~')}",
                       "ffmpeg_cmd": "",
                       "ffmpeg_islocal": False,
                       "ffprobe_cmd": "",
                       "ffprobe_islocal": False,
                       "warnexiting": True,
                       "icontheme": "Vidtuber-Colours",
                       "toolbarsize": 24,
                       "toolbarpos": 0,
                       "toolbartext": False,
                       "window_size": [850, 560],
                       "window_position": [0, 0],
                       "clearcache": False,
                       "clearlogfiles": False,
                       "downloader": False,
                       "playlistsubfolder": True,
                       "locale_name": "Default"
                       }

    def __init__(self, filename, makeportable=None):
        """
        Accepts an existing `filename` on the file system paths
        suffixed by `.json`. If `makeportable` is `True`, some
        paths on the `DEFAULT_OPTIONS` class attribute will be
        set as relative paths.
        """
        self.filename = filename

        if makeportable:
            path = os.path.join(makeportable, "My_Files")
            outputdir = os.path.relpath(path)
            ConfigManager.DEFAULT_OPTIONS['dirdownload'] = outputdir

    def write_options(self, **options):
        """
        Writes options to configuration file. If **options is
        given, writes the new changes to filename, writes the
        DEFAULT_OPTIONS otherwise.
        """
        if options:
            set_options = options
        else:
            set_options = ConfigManager.DEFAULT_OPTIONS

        with open(self.filename, "w", encoding='utf-8') as settings_file:

            json.dump(set_options,
                      settings_file,
                      indent=4,
                      separators=(",", ": ")
                      )

    def read_options(self):
        """
        Reads options from the current configuration file.
        Returns: current options, `None` otherwise.
        Raise: json.JSONDecodeError
        """
        with open(self.filename, 'r', encoding='utf-8') as settings_file:
            try:
                options = json.load(settings_file)
            except json.JSONDecodeError:
                return None

        return options
