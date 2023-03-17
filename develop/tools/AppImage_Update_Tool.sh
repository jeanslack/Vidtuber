#!/usr/bin/env bash
#
# Description:
# ------------
#   Updates pip, certifi, yt-dlp and youtube-dl packages inside
#   Vidtuber*.AppImage.
#
# Usage:
# ------
#   - Place this script in your preferred location with execute permissions.
#   - Call this script from a terminal window (not root!)
#   - Make sure you give it the Vidtuber AppImage location as argument.
#   - Then run it and wait for the task to finish.
#
#   EXAMPLE:
#         ~$ ./VidtuberAppImage_updater.sh /some/other/dir/Vidtuber*.AppImage
#
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
# Update: Nov.27.2022
#
# please visit <https://misc.flogisoft.com/bash/tip_colors_and_formatting>
# for colors code.

set -e  # stop if error

# check for $1
if [ -z "$1" ] ; then
    echo "ERROR: missing argument: provide a valid pathname to Vidtuber*.AppImage"
    exit 1
fi

SITEPKG="squashfs-root/opt/python3.9/lib/python3.9/site-packages"
APPIMAGE=$(readlink -f $1)  # selected vidtuber appimage pathname (absolute path)
BASENAME="$(basename $APPIMAGE)"  # vidtuber name
DIRNAME="$(dirname $APPIMAGE)"  # vidtuber directory

# check for proper filename
if [[ "${BASENAME}" != Vidtuber-*-x86_64.AppImage ]] ; then
    echo "ERROR: requires a Vidtuber AppImage"
    exit 1
fi

# building in temporary directory to keep system clean.
# Don't use /dev/shm as on some Linux distributions it may have noexec set
TEMP_BASE=/tmp

BUILD_DIR=$(mktemp -d -p "$TEMP_BASE" vidtuber-AppImage-update-XXXXXX)

# make sure to clean up build dir, even if errors occur
cleanup () {
    if [ -d "$BUILD_DIR" ]; then
    rm -rf "$BUILD_DIR"
    fi
    }
trap cleanup EXIT

# switch to build dir
pushd "$BUILD_DIR"

# extract appimage inside BUILD_DIR/
$APPIMAGE --appimage-extract

# export squashfs-root
export PATH="$(pwd)/squashfs-root/usr/bin:$PATH"

# update pip
./squashfs-root/opt/python3.9/bin/python3.9 -m pip install -U --target=$SITEPKG pip
# update certifi
./squashfs-root/opt/python3.9/bin/python3.9 -m pip install -U --target=$SITEPKG certifi
# update youtube_dl package
./squashfs-root/opt/python3.9/bin/python3.9 -m pip install -U --target=$SITEPKG youtube_dl
# update youtube_dl package
./squashfs-root/opt/python3.9/bin/python3.9 -m pip install -U --target=$SITEPKG yt_dlp

# retrieve the Vidtuber version from the package metadata
export VERSION=$(cat $SITEPKG/vidtuber-*.dist-info/METADATA | \
    grep "^Version:.*" | cut -d " " -f 2)

# Download appimagetool for re-building AppImage
wget -c https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# Convert back into an AppImage
./appimagetool-x86_64.AppImage squashfs-root/

# move built AppImage back into original DIRNAME
mv -f Vidtuber*x86_64.AppImage "$DIRNAME/"  # overwrites existent appimage
echo
echo -e '\e[5m\e[92m**Successfully updated**\e[25m\e[39m'  # keyword for a successful exit status
echo -e '\e[1m\e[92m...To apply the update, restart Vidtuber AppImage now.\e[21m\e[39m'
