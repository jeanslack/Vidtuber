#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Name: pyinstaller_setup.py
Porpose: Setup the vidtuber.spec and build bundle via Pyinstaller
Compatibility: Python3
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: March.17.2023
########################################################
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
import shutil
import platform
import argparse
import time
import subprocess

this = os.path.realpath(os.path.abspath(__file__))
HERE = os.path.dirname(os.path.dirname(os.path.dirname(this)))
sys.path.insert(0, HERE)
try:
    from vidtuber.vdms_sys.msg_info import current_release
except ModuleNotFoundError as modulerror:
    sys.exit(modulerror)

SCRIPT = 'launcher'
NAME = 'vidtuber'
BINARY = os.path.join(HERE, SCRIPT)
SPECFILE = os.path.join(HERE, f'{NAME}.spec')


def vidtuber_data_source(here=HERE, name=NAME):
    """
    Returns a dict object of the Vidtuber data
    and pathnames needed to spec file.
    """
    release = current_release()  # Gets data list

    return dict(RLS_NAME=release[0],  # first letter is Uppercase
                PRG_NAME=release[1],  # first letter is lower
                NAME=name,
                VERSION=release[2],
                RELEASE=release[3],
                COPYRIGHT=release[4],
                WEBSITE=release[5],
                AUTHOR=release[6],
                EMAIL=release[7],
                COMMENT=release[8],
                ART=os.path.join(here, 'vidtuber', 'art'),
                LOCALE=os.path.join(here, 'vidtuber', 'locale'),
                SHARE=os.path.join(here, 'vidtuber', 'share'),
                FFMPEG=os.path.join(here, 'vidtuber', 'FFMPEG'),
                NOTICE=os.path.join(here, 'vidtuber',
                                    'FFMPEG', 'NOTICE.rtf'),
                AUTH=os.path.join(here, 'AUTHORS'),
                BUGS=os.path.join(here, 'BUGS'),
                CHANGELOG=os.path.join(here, 'CHANGELOG'),
                COPYING=os.path.join(here, 'LICENSE'),
                INSTALL=os.path.join(here, 'INSTALL'),
                README=os.path.join(here, 'README.md'),
                TODO=os.path.join(here, 'TODO'),
                ICNS=os.path.join(here, 'vidtuber',
                                  'art', 'vidtuber.icns'),
                ICO=os.path.join(here, 'vidtuber', 'art', 'vidtuber.ico'),
                )


class PyinstallerSpec():
    """
    This class structures the information data flow,
    arranges the paths of the files and directories
    and manages the options to generate a vidtuber.spec
    file based to the operating system in use.

    """

    def __init__(self, onedf='--onedir'):
        """
        The following OS's are supported:
        Linux, MacOS and MS-Windows
        """
        self.onedf = onedf  # is None if --start_build option is given
        self.getdata = vidtuber_data_source()
        sep = ';' if platform.system() == 'Windows' else ':'

        self.datas = (f"--add-data {self.getdata['ART']}{sep}art "
                      f"--add-data {self.getdata['LOCALE']}{sep}locale "
                      f"--add-data {self.getdata['SHARE']}{sep}share "
                      f"--add-data {self.getdata['FFMPEG']}{sep}FFMPEG "
                      f"--add-data {self.getdata['AUTH']}{sep}DOC "
                      f"--add-data {self.getdata['BUGS']}{sep}DOC "
                      f"--add-data {self.getdata['CHANGELOG']}{sep}DOC "
                      f"--add-data {self.getdata['COPYING']}{sep}DOC "
                      f"--add-data {self.getdata['INSTALL']}{sep}DOC "
                      f"--add-data {self.getdata['README']}{sep}DOC "
                      f"--add-data {self.getdata['TODO']}{sep}DOC "
                      )
    # ---------------------------------------------------------#

    def windows_platform(self):
        """
        Set options flags and spec file pathname
        on MS-Windows platform.
        """
        options = (f"--name {self.getdata['RLS_NAME']} {self.onedf} "
                   f"--windowed --noconsole --icon {self.getdata['ICO']} "
                   # f"--exclude-module youtube_dl --exclude-module 'yt_dlp' "
                   f"{self.datas} ")

        return options
    # ---------------------------------------------------------#

    def darwin_platform(self):
        """
        Set options flags and spec file pathname
        on MacOS platform.
        FIXME : use codesign identity when pyinstaller is fixed to v.4.5.2
        """
        rlsname = self.getdata['RLS_NAME']
        version = self.getdata['VERSION']
        cright = self.getdata['COPYRIGHT']

        opts = (f"--name '{rlsname}' {self.onedf} "
                f"--windowed --noconsole --icon "
                f"'{self.getdata['ICNS']}' --osx-bundle-identifier "
                f"'com.jeanslack.vidtuber' "
                # f"--codesign-identity IDENTITY "
                # f"--osx-entitlements-file FILENAME "
                # f"--exclude-module 'youtube_dl' --exclude-module 'yt_dlp' "
                f"{self.datas} ")

        plist = (
            f"""             info_plist={{# 'LSEnvironment': '$0',
             'NSPrincipalClass': 'NSApplication',
             'NSAppleScriptEnabled': False,
             'CFBundleName': '{rlsname}',
             'CFBundleDisplayName': '{rlsname}',
             'CFBundleGetInfoString': "Making {rlsname}",
             'CFBundleIdentifier': "com.jeanslack.vidtuber",
             'CFBundleVersion': '{version}',
             'CFBundleShortVersionString': '{version}',
             'NSHumanReadableCopyright':'Copyright {cright}, '
                                        'Gianluca Pernigotto, '
                                        'All Rights Reserved',}})
""")

        return opts, plist
    # ---------------------------------------------------------#

    def linux_platform(self):
        """
        Set options flags and spec file pathname
        on Linux platform.
        """
        options = (f"--name {self.getdata['NAME']} {self.onedf} "
                   f"--windowed --noconsole {self.datas}"
                   )

        return options
# --------------------------------------------------------#


def onefile_onedir():
    """
    Pyinstaller offer two options to generate stand-alone executables.
    The `--onedir` option is the default.
    """
    text = ('\nChoose from the following options:\n'
            '[1] Create a one-folder bundle containing an '
            'executable (default)\n'
            '[2] Create a one-file bundled executable\n'
            '(1/2) ')

    while True:
        onedf = input(text)
        if onedf.strip() in ('1', '2', ''):
            break
        print(f"\nInvalid option '{onedf}'")
        continue

    return '--onefile' if onedf == '2' else '--onedir'
# --------------------------------------------------------#


def fetch_exec(binary=BINARY):
    """
    fetch the vidtuber binary on bin folder
    """
    if not os.path.exists(binary):  # binary
        sys.exit(f"ERROR: no file found named '{binary}'")
# --------------------------------------------------------#


def genspec(options, specfile=SPECFILE, addplist=None, script=SCRIPT):
    """
    Generate a vidtuber.spec file for platform in use.
    Support for the following platforms is expected:
            [Windows, Darwin, Linux]
    The vidtuber.spec file will be saved in the root directory
    of the vidtuber sources.
    To running vidtuber.spec is required ``pyinstaller``.
    To use vidtuber.spec type:
        `pyinstaller vidtuber.spec`
    or use this script with option -s to start the building by
    an existing vidtuber.spec file.
    """
    try:
        subprocess.run(f'pyi-makespec {options} {script}',
                       shell=True, check=True)
    except subprocess.CalledProcessError as err:
        sys.exit(f'\nERROR: {err}\n')

    if platform.system() == 'Darwin' and addplist is not None:
        with open(specfile, 'r', encoding='utf8') as specf:
            arr = specf.readlines()

        idx = arr.index("             bundle_identifier='com."
                        "jeanslack.vidtuber')\n")
        arr[idx] = ("             bundle_identifier='com."
                    "jeanslack.vidtuber',\n")
        newspec = ''.join(arr) + addplist
        with open(specfile, 'w', encoding='utf8') as specf:
            specf.write(newspec)
# --------------------------------------------------------#


def clean_buildingdirs(here=HERE, name=NAME):
    """
    Asks the user if they want to clean-up building
    directories, usually "dist", "build", "*.egg-info" dirs.
    """
    target = ('dist', 'build', f'{NAME}.egg-info')
    aredirs = [x for x in os.listdir(HERE) if os.path.isdir(x)]
    toremove = [t for t in aredirs if t in target]

    if toremove:
        while True:
            clean = input('\nDo you want to clean build folders? (y/n)? ')
            if clean.strip() in ('Y', 'y', 'n', 'N'):
                break
            print(f"\nInvalid option '{clean}'")
            continue

        if clean in ('y', 'Y'):
            for names in toremove:
                dirname = os.path.join(HERE, names)
                print('Removing: ', dirname)
                shutil.rmtree(os.path.join(HERE, dirname), ignore_errors=True)
            print('\n')

# --------------------------------------------------------#


def run_pyinst(specfile=SPECFILE):
    """
    wrap `pyinstaller --clean vidtuber.spec`
    """
    if os.path.exists(specfile) and os.path.isfile(specfile):
        fetch_exec()  # fetch vidtuber binary
        time.sleep(1)
        try:
            subprocess.run(f'pyinstaller --clean {specfile}',
                           shell=True, check=True)
        except subprocess.CalledProcessError as err:
            sys.exit(f'\nERROR: {err}\n')

        print("\nSUCCESS: pyinstaller_setup.py: Build finished.\n")
    else:
        sys.exit(f"ERROR: no such file {specfile}")
# --------------------------------------------------------#


def make_portable(here=HERE):
    """
    If you plan to make definively fully portable the application
    bundled, use this function to implements this feature.

    Note:
       with `--onedir` option, the 'portable_data' directory should
       be inside the vidtuber standalone directory.
        with `--onefile` option, the 'portable_data' directory should
        be next to the vidtuber standalone executable.
    """
    while True:
        portable = input('Do you want to keep all application data inside '
                         'the program folder? (makes stand-alone executable '
                         'fully portable and stealth) (y/N) ')
        if portable.strip() in ('Y', 'y', 'n', 'N'):
            break
        print(f"\nInvalid option '{portable}'")
        continue

    if portable in ('n', 'N'):
        return False

    error = False
    row = "        kwargs = {'make_portable': None}"
    code = ("        data = os.path.join(os.path.dirname(sys.executable), "
            "'portable_data')\n        kwargs = {'make_portable': data}\n")
    filename = os.path.join(here, 'vidtuber', 'gui_app.py')

    with open(filename, 'r+', encoding='utf8') as gui_app:
        data = gui_app.readlines()

        for line in data:
            if line.startswith(row):
                idx = data.index(line)
        if idx:
            gui_app.flush()
            gui_app.seek(0)
            data[idx] = code  # replace `row` line with `code`
            gui_app.writelines(data)
            gui_app.truncate()
        else:
            error = True

    if error:
        sys.exit("\nERROR on writing file `gui_app.py`")

    return True
# --------------------------------------------------------#


def restore_sources(data, here=HERE):
    """
    Restore source file `gui_app.py`
    """
    filename = os.path.join(here, 'vidtuber', 'gui_app.py')
    with open(filename, 'w', encoding='utf8') as bak:
        bak.write(''.join(data))
# --------------------------------------------------------#


def backup_sources(here=HERE):
    """
    Backup source file `gui_app.py`
    """
    data = None
    filename = os.path.join(here, 'vidtuber', 'gui_app.py')
    with open(filename, 'r', encoding='utf8') as gui_app:
        data = gui_app.readlines()
    return data
# --------------------------------------------------------#


def get_data_platform():
    """
    Retrieves data options and generates spec file.
    """
    if not platform.system() in ('Windows', 'Darwin', 'Linux'):
        sys.exit("\nERROR: Unsupported platform.\n"
                 "Try creating a 'spec' file by typing the "
                 "following command:\n"
                 "\"pyi-makespec [options] vidtuber.py\"\n"
                 )
    wrap = PyinstallerSpec(onefile_onedir())

    if platform.system() == 'Linux':
        getopts = wrap.linux_platform()
        genspec(getopts)

    elif platform.system() == 'Darwin':
        getopts = wrap.darwin_platform()
        genspec(getopts[0], addplist=getopts[1])

    elif platform.system() == 'Windows':
        getopts = wrap.windows_platform()
        genspec(getopts)
# ----------------------------------------------#


def main():
    """
    Users inputs parser (positional/optional arguments)
    """
    descr = 'Wrap the pyinstaller setup for Vidtuber application'
    parser = argparse.ArgumentParser(prog=NAME,
                                     description=descr,
                                     add_help=True,
                                     )
    parser.add_argument(
        '-g', '--gen_spec',
        help="Generates a ready-to-use vidtuber.spec file.",
        action="store_true",
    )
    parser.add_argument(
        '-gb', '--genspec_build',
        help="Generate a vidtuber.spec file and start building bundle.",
        action="store_true",
    )
    parser.add_argument(
        '-s', '--start_build',
        help="Start the building bundle by an existing vidtuber.spec file.",
        action="store_true",
    )

    args = parser.parse_args()

    if args.gen_spec:
        get_data_platform()

    elif args.genspec_build:
        get_data_platform()
        clean_buildingdirs()
        backup = backup_sources()
        ret = make_portable()
        run_pyinst()
        if ret:
            restore_sources(backup)

    elif args.start_build:
        clean_buildingdirs()
        backup = backup_sources()
        ret = make_portable()
        run_pyinst()
        if ret:
            restore_sources(backup)
    else:
        print("\nType 'pyinstaller_setup.py -h' for help.\n")
        return


if __name__ == '__main__':
    main()
