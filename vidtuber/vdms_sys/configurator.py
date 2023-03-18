# -*- coding: UTF-8 -*-
"""
Name: configurator.py
Porpose: Set Vidtuber configuration on startup
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
import sys
import site
import shutil
import platform
from vidtuber.vdms_utils.utils import copydir_recursively
from vidtuber.vdms_sys.settings_manager import ConfigManager


def msg(arg):
    """
    print logging messages during startup
    """
    print('Info:', arg)


def create_dirs(dirname, fconf):
    """
    This function is responsible for the recursive creation
    of directories required for Vidtuber if they do not exist.
    Returns dict:
        key == 'R'
        key == ERROR (if any errors)
    """
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname, mode=0o777)
        except FileExistsError as err:
            return {'ERROR': err}
        except OSError as err:
            os.remove(fconf)  # force to restart on deleting
            thismsg = ('Please try restarting Vidtuber to '
                       'restore default settings now.')
            return {'ERROR': f'{err}\n{thismsg}'}

    return {'R': None}


def get_options(dirconf, fileconf, srcpath, makeportable):
    """
    Check the application options. Reads the `settings.json`
    file; if it does not exist or is unreadable try to restore
    it. If `dirconf` does not exist try to restore both `dirconf`
    and `settings.json`. If VERSION is not the same as the version
    readed, it adds new missing items while preserving the old ones
    with the same values.

    Returns dict:
        key == 'R'
        key == ERROR (if any errors)
    """
    conf = ConfigManager(fileconf, makeportable)
    version = ConfigManager.VERSION

    if os.path.exists(dirconf):  # i.e ~/.conf/vidtuber dir
        if os.path.isfile(fileconf):
            data = {'R': conf.read_options()}
            if not data['R']:
                conf.write_options()
                data = {'R': conf.read_options()}
            if float(data['R']['confversion']) != version:  # conf version
                data['R']['confversion'] = version
                new = ConfigManager.DEFAULT_OPTIONS  # model
                data = {'R': {**new, **data['R']}}
                conf.write_options(**data['R'])
        else:
            conf.write_options()
            data = {'R': conf.read_options()}

    else:  # try to restore entire configuration directory
        dconf = copydir_recursively(srcpath,
                                    os.path.dirname(dirconf),
                                    "vidtuber",
                                    )
        if dconf:
            data = {'ERROR': dconf}
        else:
            conf.write_options()
            data = {'R': conf.read_options()}

    return data


def get_pyinstaller():
    """
    Get pyinstaller-based package attributes to determine
    how to use sys.executable
    When a bundled app starts up, the bootloader sets the sys.frozen
    attribute and stores the absolute path to the bundle folder
    in sys._MEIPASS.
    For a one-folder bundle, this is the path to that folder.
    For a one-file bundle, this is the path to the temporary folder
    created by the bootloader.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        frozen, meipass = True, True
        this = getattr(sys, '_MEIPASS', os.path.abspath(__file__))
        data_locat = this

    else:
        frozen, meipass = False, False
        this = os.path.realpath(os.path.abspath(__file__))
        data_locat = os.path.dirname(os.path.dirname(this))

    return frozen, meipass, this, data_locat


def conventional_paths():
    """
    Establish the conventional paths based on OS

    """
    user_name = os.path.expanduser('~')

    if platform.system() == 'Windows':
        fpath = "\\AppData\\Roaming\\vidtuber\\settings.json"
        file_conf = os.path.join(user_name + fpath)
        dir_conf = os.path.join(user_name + "\\AppData\\Roaming\\vidtuber")
        log_dir = os.path.join(dir_conf, 'log')  # logs
        cache_dir = os.path.join(dir_conf, 'cache')  # updates executable

    elif platform.system() == "Darwin":
        fpath = "Library/Application Support/vidtuber/settings.json"
        file_conf = os.path.join(user_name, fpath)
        dir_conf = os.path.join(user_name, os.path.dirname(fpath))
        log_dir = os.path.join(user_name, "Library/Logs/vidtuber")
        cache_dir = os.path.join(user_name, "Library/Caches/vidtuber")

    else:  # Linux, FreeBsd, etc.
        fpath = ".config/vidtuber/settings.json"
        file_conf = os.path.join(user_name, fpath)
        dir_conf = os.path.join(user_name, ".config/vidtuber")
        log_dir = os.path.join(user_name, ".local/share/vidtuber/log")
        cache_dir = os.path.join(user_name, ".cache/vidtuber")

    return file_conf, dir_conf, log_dir, cache_dir


def portable_paths(portdirname):
    """
    Make portable-data paths based on OS

    """
    dir_conf = portdirname
    file_conf = os.path.join(dir_conf, "settings.json")
    log_dir = os.path.join(dir_conf, 'log')  # logs
    cache_dir = os.path.join(dir_conf, 'cache')  # updates executable

    if not os.path.exists(dir_conf):
        os.makedirs(dir_conf, mode=0o777)

    return file_conf, dir_conf, log_dir, cache_dir


def get_color_scheme(theme):
    """
    Returns the corrisponding colour scheme according to
    chosen theme in ("Videomass-Light",
                     "Videomass-Dark",
                     "Videomass-Colours",
                     "Ubuntu-Light-Aubergine",
                     "Ubuntu-Dark-Aubergine",
                     )
    """
    if theme == 'Vidtuber-Colours':
        c_scheme = {'BACKGRD': '#8dc6c2',  # Ciano: background color
                    'TXT0': '#d01d7a',  # Magenta: titles & end messages)
                    'TXT1': '#ae11db',  # Purple for debug and others
                    'ERR0': '#FF4A1B',  # ORANGE: errors 1 and others
                    'WARN': '#7b6e01',  # YELLOW: warnings
                    'ERR1': '#EA312D',  # LIGHTRED: errors 2
                    'SUCCESS': '#017001',  # Light GREEN: successful
                    'TXT3': '#333333',  # Dark grey: standard text
                    'INFO': '#194c7e',  # Blue: other info messages
                    'DEBUG': '#333333',  # light green
                    'FAILED': '#D21814',  # RED_DEEP if failed
                    'ABORT': '#D21814',  # RED_DEEP if abort
                    }
    elif theme == 'Vidtuber-Dark':
        c_scheme = {'BACKGRD': '#232424',  # DARK Grey background color
                    'TXT0': '#FFFFFF',  # WHITE for title or URL in progress
                    'TXT1': '#959595',  # GREY for all other text messages
                    'ERR0': '#FF4A1B',  # ORANGE for error text messages
                    'WARN': '#dfb72f',  # YELLOW for warning text messages
                    'ERR1': '#EA312D',  # LIGHTRED for errors 2
                    'SUCCESS': '#30ec30',  # Light GREEN when it is successful
                    'TXT3': '#11b584',  # medium green
                    'INFO': '#118db5',  # AZURE
                    'DEBUG': '#0ce3ac',  # light green
                    'FAILED': '#D21814',  # RED_DEEP if failed
                    'ABORT': '#A41EA4',  # VIOLET the user stops the processes
                    }
    elif theme == 'Vidtuber-Light':
        c_scheme = {'BACKGRD': '#ced0d1',  # WHITE background color
                    'TXT0': '#1f1f1f',  # BLACK for title or URL in progress
                    'TXT1': '#576470',  # LIGHT_SLATE for all other text msg
                    'ERR0': '#d25c07',  # ORANGE for error text messages
                    'WARN': '#988313',  # YELLOW for warning text messages
                    'ERR1': '#c8120b',  # LIGHTRED for errors 2
                    'SUCCESS': '#35a735',  # DARK_GREEN when it is successful
                    'TXT3': '#005c00',  # Light Green
                    'INFO': '#3298FB',  # AZURE
                    'DEBUG': '#005c00',  # Light Green
                    'FAILED': '#D21814',  # RED_DEEP if failed
                    'ABORT': '#A41EA4',  # VIOLET the user stops the processes
                    }
    elif theme in ('Ubuntu-Dark-Aubergine', 'Ubuntu-Light-Aubergine'):
        c_scheme = {'BACKGRD': '#2C001E',  # Dark-Aubergine background color
                    'TXT0': '#FFFFFF',  # WHITE for titles
                    'TXT1': '#8AB8E6',  # light Blue
                    'ERR0': '#E95420',  # ORANGE for error text messages
                    'WARN': '#DFB72F',  # YELLOW for warning messages
                    'ERR1': '#F90808',  # RED_DEEP
                    'SUCCESS': '#ABD533',  # Light GREEN when it is successful
                    'TXT3': '#AEA79F',  # Ubuntu warm grey (base foreground)
                    'INFO': '#F7C3B1',  # Ubuntu orange light 30%
                    'DEBUG': '#8AB8E6',  # light Blue
                    'FAILED': '#F90808',  # RED_DEEP
                    'ABORT': '#F90808',  # RED_DEEP
                    }
    else:
        c_scheme = {'ERROR': f'Unknow theme "{theme}"'}

    return c_scheme


def data_location(args):
    """
    Determines data location and modes to make the app
    portable, fully portable or using conventional paths.
    return data location.
    """
    frozen, meipass, this, locat = get_pyinstaller()
    workdir = os.path.dirname(os.path.dirname(os.path.dirname(this)))

    if args['make_portable']:
        portdir = args['make_portable']
        conffile, confdir, logdir, cachedir = portable_paths(portdir)
    else:
        conffile, confdir, logdir, cachedir = conventional_paths()

    return {"conffile": conffile,
            "confdir": confdir,
            "logdir": logdir,
            "cachedir": cachedir,
            "this": this,
            "frozen": frozen,
            "meipass": meipass,
            "locat": locat,
            "localepath": os.path.join(locat, 'locale'),
            "workdir": workdir,
            "srcpath": os.path.join(locat, 'share'),
            "icodir": os.path.join(locat, 'art', 'icons'),
            "ffmpeg_pkg": os.path.join(locat, 'FFMPEG'),
            }


class DataSource():
    """
    DataSource class determines the Vidtuber's configuration
    according to the used Operating System (Linux/*BSD, MacOS, Windows).
    Remember that all specifications defined in this class refer
    only to the following packaging methods:

        - Vidtuber Python package by PyPi (cross-platform, multiuser/user)
        - Linux's distributions packaging (multiuser)
        - Bundled app by pyinstaller (windowed for MacOs and Windows)
        - AppImage for Linux (user)

        * multiuser: system installation
        * user: local installation

    """
    # -------------------------------------------------------------------

    def __init__(self, kwargs):
        """
        Having the pathnames returned by `dataloc` it
        performs the initialization described in DataSource.

        """
        self.dataloc = data_location(kwargs)
        self.relativepaths = bool(kwargs['make_portable'])
        self.makeportable = kwargs['make_portable']
        self.apptype = None  # appimage, pyinstaller on None
        launcher = os.path.isfile(f"{self.dataloc['workdir']}/launcher")

        if self.dataloc['frozen'] and self.dataloc['meipass'] or launcher:
            msg(f"frozen={self.dataloc['frozen']} "
                f"meipass={self.dataloc['meipass']} "
                f"launcher={launcher}")

            self.apptype = 'pyinstaller' if not launcher else None
            self.prg_icon = f"{self.dataloc['icodir']}/vidtuber.png"

        elif ('/tmp/.mount_' in sys.executable or os.path.exists(
              os.path.dirname(os.path.dirname(os.path.dirname(
                  sys.argv[0])))
              + '/AppRun')):
            # embedded on python appimage
            msg('Embedded on python appimage')
            self.apptype = 'appimage'
            userbase = os.path.dirname(os.path.dirname(sys.argv[0]))
            pixmaps = '/share/pixmaps/vidtuber.png'
            self.prg_icon = os.path.join(userbase + pixmaps)

        else:
            binarypath = shutil.which('vidtuber')
            if platform.system() == 'Windows':  # any other packages
                exe = binarypath if binarypath else sys.executable
                msg(f'Win32 executable={exe}')
                # HACK check this
                # dirname = os.path.dirname(sys.executable)
                # pythonpath = os.path.join(dirname, 'Script', 'vidtuber')
                # self.icodir = dirname + '\\share\\vidtuber\\icons'
                self.prg_icon = self.dataloc['icodir'] + "\\vidtuber.png"

            elif binarypath == '/usr/local/bin/vidtuber':
                msg(f'executable={binarypath}')
                # pip as super user, usually Linux, MacOs, Unix
                share = '/usr/local/share/pixmaps'
                self.prg_icon = share + '/vidtuber.png'

            elif binarypath == '/usr/bin/vidtuber':
                msg(f'executable={binarypath}')
                # installed via apt, rpm, etc, usually Linux
                share = '/usr/share/pixmaps'
                self.prg_icon = share + "/vidtuber.png"

            else:
                msg(f'executable={binarypath}')
                # pip as normal user, usually Linux, MacOs, Unix
                if binarypath is None:
                    # need if user $PATH is not set yet
                    userbase = site.getuserbase()
                else:
                    userbase = os.path.dirname(os.path.dirname(binarypath))
                pixmaps = '/share/pixmaps/vidtuber.png'
                self.prg_icon = os.path.join(userbase + pixmaps)
    # ---------------------------------------------------------------------

    def get_fileconf(self):
        """
        Get settings.json configuration data and returns a dict object
        with current data-set for bootstrap.

        Note: If returns a dict key == ERROR it will raise a windowed
        fatal error in the gui_app bootstrap.
        """
        # handle configuration file
        userconf = get_options(self.dataloc['confdir'],
                               self.dataloc['conffile'],
                               self.dataloc['srcpath'],
                               self.makeportable,
                               )
        if userconf.get('ERROR'):
            return userconf
        userconf = userconf['R']

        # create required directories if them not exist
        requiredirs = (os.path.join(self.dataloc['cachedir'], 'tmp'),
                       self.dataloc['logdir'],
                       userconf['dirdownload']
                       )
        for dirs in requiredirs:
            create = create_dirs(dirs, self.dataloc['conffile'],)
            if create.get('ERROR'):
                return create

        # set color scheme
        theme = get_color_scheme(userconf['icontheme'])
        userconf['icontheme'] = (userconf['icontheme'], theme)
        if theme.get('ERROR'):
            return theme

        def _relativize(path, relative=self.relativepaths):
            """
            Returns a relative pathname if *relative* param is True.
            If not, it returns the given pathname. Also return the given
            pathname if `ValueError` is raised. This function is called
            several times during program execution.
            """
            try:
                return os.path.relpath(path) if relative else path
            except (ValueError, TypeError):
                # return {'ERROR': f'{error}'}  # use `as error` here
                return path

        return ({'ostype': platform.system(),
                 'srcpath': _relativize(self.dataloc['srcpath']),
                 'localepath': _relativize(self.dataloc['localepath']),
                 'fileconfpath': _relativize(self.dataloc['conffile']),
                 'workdir': _relativize(self.dataloc['workdir']),
                 'confdir': _relativize(self.dataloc['confdir']),
                 'logdir': _relativize(self.dataloc['logdir']),
                 'cachedir': _relativize(self.dataloc['cachedir']),
                 'FFMPEG_vidtuber_pkg':
                     _relativize(self.dataloc['ffmpeg_pkg']),
                 'app': self.apptype,
                 'relpath': self.relativepaths,
                 'getpath': _relativize,
                 'ffmpeg_cmd': _relativize(userconf['ffmpeg_cmd']),
                 'ffprobe_cmd': _relativize(userconf['ffprobe_cmd']),
                 **userconf
                 })
    # --------------------------------------------------------------------

    def icons_set(self, icontheme):
        """
        Determines icons set assignment defined on the configuration
        file (see `Set icon themes map:`, on paragraph `6- GUI setup`
        in the settings.json file).
        Returns a icontheme dict object.

        """
        keys = ('vidtuber', 'previous', 'next', 'download', 'statistics',
                'playlist', 'logpanel', 'stop', 'clear',
                )  # must match with items on `iconset` tuple, see following

        ext = 'svg' if 'wx.svg' in sys.modules else 'png'
        icodir = self.dataloc['icodir']
        iconames = {'Vidtuber-Light':  # Vidtuber icons for light themes
                    {'x16': f'{icodir}/Vidtuber-Light/16x16',
                     'x22': f'{icodir}/Vidtuber-Light/24x24'},
                    'Vidtuber-Dark':  # Vidtuber icons for dark themes
                    {'x16': f'{icodir}/Vidtuber-Dark/16x16',
                     'x22': f'{icodir}/Vidtuber-Dark/24x24'},
                    'Vidtuber-Colours':  # Vidtuber icons for all themes
                    {'x16': f'{icodir}/Vidtuber-Colours/16x16',
                     'x22': f'{icodir}/Vidtuber-Colours/24x24'},
                    'Ubuntu-Dark-Aubergine':  # Videomass icons for all themes
                    {'x16': f'{icodir}/Vidtuber-Dark/16x16',
                     'x22': f'{icodir}/Vidtuber-Dark/24x24'},
                    'Ubuntu-Light-Aubergine':  # Videomass icons for all themes
                    {'x16': f'{icodir}/Vidtuber-Light/16x16',
                     'x22': f'{icodir}/Vidtuber-Light/24x24'},
                    }
        choose = iconames.get(icontheme)  # set appropriate icontheme

        iconset = (self.prg_icon,
                   f"{choose.get('x22')}/go-previous.{ext}",
                   f"{choose.get('x22')}/go-next.{ext}",
                   f"{choose.get('x22')}/download.{ext}",
                   f"{choose.get('x22')}/statistics.{ext}",
                   f"{choose.get('x16')}/playlist-append.{ext}",
                   f"{choose.get('x22')}/logpanel.{ext}",
                   f"{choose.get('x22')}/stop.{ext}",
                   f"{choose.get('x22')}/clear.{ext}",
                   )
        values = [os.path.join(norm) for norm in iconset]  # normalize pathns

        return dict(zip(keys, values))
