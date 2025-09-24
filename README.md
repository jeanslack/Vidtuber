# **Vidtuber**
[![Image](https://img.shields.io/static/v1?label=python&logo=python&message=3.9%20|%203.10%20|%203.11%20|%203.12%20|%203.13&color=blue)](https://www.python.org/downloads/)
[![Image](https://img.shields.io/badge/license-GPLv3-orange)](https://github.com/jeanslack/Vidtuber/blob/master/LICENSE)
[![Python application](https://github.com/jeanslack/Vidtuber/actions/workflows/python-package.yml/badge.svg)](https://github.com/jeanslack/Vidtuber/actions/workflows/python-package.yml)

A simple yet comprehensive, cross-platform graphical user interface for [yt-dlp](https://github.com/yt-dlp/yt-dlp). 
This project is a partial fork of [Videomass](https://github.com/jeanslack/Videomass), which has now dropped support for yt-dlp and the GUI for audio/video download.

Vidtuber is [Free (libre) Software](https://en.wikipedia.org/wiki/Free_software),
written in [Python3](https://www.python.org/) using the
[wxPython Phoenix](https://www.wxpython.org/) toolkit; it works on Linux, MacOs, Windows and FreeBSD.

## INSTALLATION

### Ubuntu PPA

>#### Important notes for Ubuntu 22.04 Jammy users
>This PPA does not provide support to recent versions of Vidtuber for Ubuntu 22.04 due to compatibility issues with the official version of wxPython provided on Jammy. 
>To overcome this, please download the archive containing the standalone application: [Vidtuber-2.0.1-ubuntu-22.04_x86_64.tar.xz](https://github.com/jeanslack/Vidtuber/releases/download/v2.0.1/Vidtuber-2.0.1-ubuntu-22.04_x86_64.tar.xz)

This PPA currently publishes packages for [Ubuntu](https://ubuntu.com/), including official and
derivative distributions such as Ubuntu, Xubuntu, Kubuntu, Lubuntu, LinuxMint,
etc.

To install Vidtuber add this [PPA](https://launchpad.net/~jeanslack/+archive/ubuntu/vidtuber) to your system:

```
sudo add-apt-repository ppa:jeanslack/vidtuber
sudo apt update
sudo apt install vidtuber
```

### Slackware

Vidtuber is available on the [SlackBuilds.org](https://slackbuilds.org/) ("Sbo") repository, a collection of third-party SlackBuild scripts to build Slackware packages from sources.

### Devuan / Debian

No arch deb package: [Latest Releases](https://github.com/jeanslack/Vidtuber/releases/latest)

Tested on:

- Devuan Daedalus
- Debian12 bookworm

### MS Windows

Portable edition: [Latest releases](https://github.com/jeanslack/Vidtuber/releases/latest)

Minimum requirements:

- Microsoft Windows 10
- x86_64 Architecture

For space reasons, this portable edition does not include the FFmpeg nor yt-dlp executables. 
Please read the README.txt file included in the 7-zip archive for more information about
downloading and installing these additional dependencies.

### Other installation and execution methods

[INSTALL](https://github.com/jeanslack/Vidtuber/blob/main/INSTALL)

## DOCUMENTATION

[docs/UserGuide](https://github.com/jeanslack/Vidtuber/tree/main/docs/UserGuide)

## TRANSLATIONS

### Help translate the program into other languages
DISCLAIMER: By sending a translation you agree to publish your work under the GPL3 license!
- [Localization_Guidelines](https://github.com/jeanslack/Vidtuber/blob/main/docs/Localization_Guidelines.md)

