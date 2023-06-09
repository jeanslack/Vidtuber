#!/bin/bash

# Convert a 1024x1024 png to the required icns file. only for MacOs.
# Before proceeding make sure you have image named `Icon1024.png' with
# 1024x1024 pixel (px) at 72 pixel-per-inch (ppi) .

cd $PWD
mkdir MyIcon.iconset
sips -z 16 16     Icon1024.png --out MyIcon.iconset/icon_16x16.png
sips -z 32 32     Icon1024.png --out MyIcon.iconset/icon_16x16@2x.png
sips -z 32 32     Icon1024.png --out MyIcon.iconset/icon_32x32.png
sips -z 64 64     Icon1024.png --out MyIcon.iconset/icon_32x32@2x.png
sips -z 128 128   Icon1024.png --out MyIcon.iconset/icon_128x128.png
sips -z 256 256   Icon1024.png --out MyIcon.iconset/icon_128x128@2x.png
sips -z 256 256   Icon1024.png --out MyIcon.iconset/icon_256x256.png
sips -z 512 512   Icon1024.png --out MyIcon.iconset/icon_256x256@2x.png
sips -z 512 512   Icon1024.png --out MyIcon.iconset/icon_512x512.png
cp Icon1024.png MyIcon.iconset/icon_512x512@2x.png
iconutil -c icns MyIcon.iconset -o vidtuber.icns
rm -R MyIcon.iconset
