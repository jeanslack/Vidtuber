#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Name: setup.py
Porpose: script to setup Vidtuber.
Compatibility: Python3
Platform: all
Writer: Gianluca Pernigotto <jeanlucperni@gmail.com>
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
import sys
import platform
from setuptools import setup, find_packages
from vidtuber.vdms_sys.msg_info import current_release
from vidtuber.vdms_sys.msg_info import descriptions_release


def source_build():
    """
    Source/Build distributions

    """
    # Get info data
    crel = current_release()
    drel = descriptions_release()

    if 'sdist' in sys.argv or 'bdist_wheel' in sys.argv:

        inst_req = ["wxpython>=4.0.7; platform_system=='Windows' or "
                    "platform_system=='Darwin'",
                    "PyPubSub>=4.0.3",
                    "yt_dlp>=2021.9.2",
                    "requests>=2.21.0",
                    ]
        setup_req = ["setuptools>=47.1.1",
                     "wheel>=0.34.2",
                     "twine>=3.1.1"
                     ]
        with open('README.md', 'r', encoding='utf8') as readme:
            long_descript = readme.read()

        long_description_ct = 'text/markdown'

    else:  # e.g. to make a Debian source package, include wxpython.
        inst_req = ["wxpython>=4.0.7",
                    "PyPubSub>=4.0.3",
                    "requests>=2.21.0",
                    ]
        setup_req = []
        long_descript = drel[1]
        long_description_ct = 'text'

    excluded = ['']
    # pathnames must be relative-path
    if platform.system() == 'Windows':
        data_f = [('share/pixmaps', ['vidtuber/art/icons/vidtuber.png'])]

    elif platform.system() == 'Darwin':
        data_f = [('share/pixmaps', ['vidtuber/art/icons/vidtuber.png']),
                  ('share/man/man1', ['docs/man/man1/vidtuber.1.gz']),
                  ]
    else:
        data_f = [('share/applications',
                   ['vidtuber/art/io.github.jeanslack.vidtuber.desktop']),
                  ('share/metainfo',
                   ['io.github.jeanslack.vidtuber.appdata.xml']),
                  ('share/pixmaps', ['vidtuber/art/icons/vidtuber.png']),
                  ('share/icons/hicolor/48x48/apps',
                   ['vidtuber/art/icons/hicolor/48x48/apps/vidtuber.png',
                    'vidtuber/art/icons/hicolor/48x48/apps/vidtuber.xpm']),
                  ('share/icons/hicolor/256x256/apps',
                   ['vidtuber/art/icons/hicolor/256x256/apps/vidtuber.png']
                   ),
                  ('share/icons/hicolor/scalable/apps',
                   ['vidtuber/art/icons/hicolor/scalable/apps/'
                    'vidtuber.svg']),
                  ('share/man/man1', ['docs/man/man1/vidtuber.1.gz']),
                  ]
    setup(name=crel[1],
          version=crel[2],
          description=drel[0],
          long_description=long_descript,
          long_description_content_type=long_description_ct,
          author=crel[6][0],
          author_email=crel[7],
          url=crel[5],
          license=drel[2],
          platforms=["All"],
          packages=find_packages(exclude=excluded),
          data_files=data_f,
          package_data={"vidtuber": ["art/icons/*", "locale/*"]
                        },
          exclude_package_data={"vidtuber": ["art/vidtuber.icns",
                                              "art/vidtuber.ico",
                                              "locale/README",
                                              "locale/vidtuber.pot"
                                              ]
                                },
          include_package_data=True,
          zip_safe=False,
          python_requires=">=3.7.0, <4.0.0",
          install_requires=inst_req,
          setup_requires=setup_req,
          entry_points={'gui_scripts':
                        ['vidtuber = vidtuber.gui_app:main']},
          classifiers=[
        'Environment :: X11 Applications :: GTK',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: Dutch',
        'Natural Language :: English',
        'Natural Language :: French',
        'Natural Language :: Italian',
        'Natural Language :: Portuguese (Brazilian)',
        'Natural Language :: Russian',
        'Natural Language :: Spanish',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia :: Video :: Conversion',
        'Topic :: Multimedia :: Sound/Audio :: Conversion',
    ],
    )


if __name__ == '__main__':
    source_build()
