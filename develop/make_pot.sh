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
"../vdms_dialogs/wizard_dlg.py" \
"../vdms_dialogs/infoprg.py" \
"../vdms_dialogs/playlist_indexing.py" \
"../vdms_dialogs/preferences.py" \
"../vdms_dialogs/vidtuber_check_version.py" \
"../vdms_dialogs/ydl_mediainfo.py" \
"../vdms_dialogs/widget_utils.py" \
"../vdms_dialogs/showlogs.py" \
"../vdms_io/io_tools.py" \
"../vdms_main/main_frame.py" \
"../vdms_panels/youtubedl_ui.py" \
"../vdms_panels/long_processing_task.py" \
"../vdms_panels/textdrop.py" \

if [ $? != 0 ]; then
    echo 'Failed!'
else
    mv vidtuber.po vidtuber.pot
    echo "A new 'vidtuber.pot' was created on: '${target}'"
    echo "Done!"
fi
