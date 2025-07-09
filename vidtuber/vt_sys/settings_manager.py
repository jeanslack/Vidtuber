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
    read and write fondamentals.

    Usage:

    write a new conf.json :
        >>> from settings_manager import ConfigManager
        >>> confmng = ConfigManager('fileconfpath.json')
        >>> confmng.write_options()

    read the current fileconf.json :
        >>> settings = confmng.read_options()

    example of modify data into current file conf.json:
        >>> settings['outputdir'] = '/home/user/MyVideos'
        >>> confmng.write_options(**settings)
    ------------------------------------------------------

    Options description:

    shutdown (bool):
        If True turn off the system when operation is finished.
        Name space only, the setting will not be stored in the
        configuration file.

    sudo_password (str):
        SUDO password for the shutdown process if the user does
        not have elevated privileges. Name space only, the setting
        will not be stored in the configuration file.

    auto_exit (bool):
        exit the application programmatically when processing is
        finished. Name space only, the setting will not be stored
        in the configuration file.

    confversion (float):
        current version of this configuration file

    dirdownload (str):
        file destination path

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
        3 is placed at the left side. default is 3 .

    main_window_size (list):
        [int(Height), int(Width)] last current window dimension before
        exiting the application.

    main_window_pos (list):
        [int(x), in(y)] last current window position on monitor screen
        before exiting the application.

    clearcache (bool):
        with True, clear the cache before exiting the application,
        default is True

    clearlogfiles (bool):
        with True, erases all log files content before exiting the
        application, default is False.

    locale_name (str):
        "Default", set system language to vidtuber message catalog
        if available, set to English otherwise.
        It supports canonical form of locale names as used on UNIX systems,
        eg. xx or xx_YY format, where xx is ISO 639 code of language and
        YY is ISO 3166 code of the country. Examples are "en", "en_GB",
        "en_US" or "fr_FR", etc.

    yt-dlp_cmd (str):
        Path to the yt-dlp (yt-dlp.exe on Windows) executable.

    ytdlp_islocal (bool):
        If `True`, the user enables a custom location (pathname) for
        yt-dlp executable. Default is `False`.

    playlistsubfolder (bool):
        Auto-create subfolders when download the playlists,
        default value is True.

    ("ssl_certificate", "add_metadata", "embed_thumbnails",
    "overwr_dl_files", "include_ID_name", "restrict_fname")
    (bool):
        Checkboxes option (see YouTube Downloader)

    subtitles_options (dict):
        (see YouTube Downloader)

    external_downloader (str):
        external downloader used by yt-dlp. Default is None

    external_downloader_args (list):
        args used by external downloader in yt-dlp. Default is None
        List of options should be passed using aria2c:
        ["-j", "1","-x", "1", "-s", "1"]

    proxy (str):
        Use the specified HTTP/HTTPS/SOCKS proxy. To enable SOCKS proxy,
        specify a proper scheme, e.g. socks5://user:pass@127.0.0.1:1080/ .
        Pass in an empty string (--proxy "") for direct connection

    username (str):
        Login with this account ID

    password (str):
        Account password. If this option is left out, yt-dlp will ask
        interactively

    videopassword (str):
        for Video-specific password

    geo-restriction setup options:
        geo_verification_proxy (str)
        geo_bypass (str)
        geo_bypass_country (str)
        geo_bypass_ip_block (str)

    cookie file setup options:
        cookiefile (str)
        autogen_cookie_file (bool)
        webbrowser (str),
        cookiesfrombrowser (list)

    fcode_column_width (list of int)
        column width in the format code panel (ytdownloader).

    """
    VERSION = 1.9
    DEFAULT_OPTIONS = {"confversion": VERSION,
                       "yt-dlp_cmd": "",
                       "ytdlp_islocal": False,
                       "ffmpeg_cmd": "",
                       "ffmpeg_islocal": False,
                       "ffprobe_cmd": "",
                       "ffprobe_islocal": False,
                       "shutdown": False,
                       "sudo_password": "",
                       "auto_exit": False,
                       "dirdownload": "",
                       "warnexiting": True,
                       "icontheme": "Vidtuber-Colours",
                       "toolbarsize": 24,
                       "toolbarpos": 0,
                       "toolbartext": False,
                       "window_size": [850, 560],
                       "window_position": [0, 0],
                       "clearcache": False,
                       "clearlogfiles": False,
                       "locale_name": "Default",
                       "subtitles_options": {"writesubtitles": False,
                                             "subtitleslangs": [],
                                             "writeautomaticsub": False,
                                             "embedsubtitle": False,
                                             "skip_download": False
                                             },
                       "fcode_column_width": [120, 60, 200, 80],
                       "external_downloader": None,
                       "external_downloader_args": None,
                       "proxy": "",
                       "username": "",
                       "password": "",
                       "videopassword": "",
                       "geo_verification_proxy": "",
                       "geo_bypass": "",
                       "geo_bypass_country": "",
                       "geo_bypass_ip_block": "",
                       "use_cookie_file": False,
                       "cookiefile": "",
                       "autogen_cookie_file": False,
                       "webbrowser": "firefox",
                       "cookiesfrombrowser": [None, None, None, None],
                       "playlistsubfolder": True,
                       "ssl_certificate": False,
                       "add_metadata": False,
                       "embed_thumbnails": False,
                       "overwr_dl_files": False,
                       "include_ID_name": False,
                       "restrict_fname": False,
                       }

    def __init__(self, filename, makeportable=None):
        """
        Expects an existing `filename` on the file system paths
        suffixed by `.json`. If `makeportable` is `True`, some
        paths on the `DEFAULT_OPTIONS` class attribute will be
        set as relative paths.
        """
        self.filename = filename
        self.makeportable = makeportable

        if self.makeportable:
            dwldpath = os.path.join(makeportable, "Media", "Downloads")
            outputdir = os.path.relpath(dwldpath)
            ConfigManager.DEFAULT_OPTIONS['dirdownload'] = outputdir
            self.dwlddir = outputdir
        else:
            self.dwlddir = os.path.expanduser('~')

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

    def default_outputdirs(self, **options):
        """
        This method is useful for restoring consistent output
        directories for file destinations, in case they were
        previously set to physically non-existent file system paths
        (such as pendrives, hard drives, etc.) or to deleted directories.
        Returns a dict object.
        """
        dwldpath = options['dirdownload']
        if not os.path.exists(dwldpath) and not os.path.isdir(dwldpath):
            if self.makeportable:
                options['dirdownload'] = self.dwlddir
            else:
                options['dirdownload'] = f"{os.path.expanduser('~')}"

        return options
