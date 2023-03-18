#!/bin/bash

# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyleft - 2018/2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: March.17.2023
#
# Make a new `vidtuber.po` file on '../../vidtuber/locale'.
# The previus vidtuber.po file will be overwrite with the new
# one incoming which will update latest strings for traslation .

PLATFORM=$(uname)  # command to show platform
self="$(readlink -f -- $0)"  # this file
here="${self%/*}"  # dirname of this file
rootdir=$(dirname $here)  # base sources directory
target="$rootdir/vidtuber/locale"  # location to store new incoming

cd $target

if [ "$PLATFORM" = "Darwin" ]; then
    # On my Macos xgettext is in '/usr/local/Cellar/gettext/0.20.1/bin/xgettext'
    # which is't in $PATH
    XGETTEXT="/usr/local/Cellar/gettext/0.20.1/bin/xgettext"

elif [ "$PLATFORM" = "Linux" ]; then
    XGETTEXT="xgettext"
fi

$XGETTEXT -d vidtuber "../gui_app.py" \
"../vt_dialogs/wizard_dlg.py" \
"../vt_dialogs/infoprg.py" \
"../vt_dialogs/playlist_indexing.py" \
"../vt_dialogs/preferences.py" \
"../vt_dialogs/vidtuber_check_version.py" \
"../vt_dialogs/ydl_mediainfo.py" \
"../vt_dialogs/widget_utils.py" \
"../vt_dialogs/showlogs.py" \
"../vt_io/io_tools.py" \
"../vt_main/main_frame.py" \
"../vt_panels/youtubedl_ui.py" \
"../vt_panels/long_processing_task.py" \
"../vt_panels/textdrop.py" \

if [ $? != 0 ]; then
    echo 'Failed!'
else
    mv vidtuber.po vidtuber.pot
    echo "A new 'vidtuber.pot' was created on: '${target}'"
    echo "Done!"
fi
