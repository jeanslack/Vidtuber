# **Vidtuber** is a simple, open-source and cross-platform GUI for [yt-dlp](https://github.com/yt-dlp/yt-dlp)

Vidtuber is written in Python3 using the wxPython-Phoenix GUI toolkit.

# Installing and Dependencies

### Requirements
- **[Python >= 3.7.0](https://www.python.org/)**
- **[wxPython-Phoenix >= 4.0.7](https://wxpython.org/)**
- **[PyPubSub >= 4.0.3](https://pypi.org/project/PyPubSub/)**
- **[requests >= 2.21.0](https://pypi.org/project/requests/)**
- **[ffmpeg >=4.3](https://ffmpeg.org/)**
- **[ffprobe >=4.3](https://ffmpeg.org/ffprobe.html)** (usually bundled with ffmpeg)
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)**

### Optionals
- **[atomicparsley](http://atomicparsley.sourceforge.net/)**

# Start Vidtuber manually from source code

Vidtuber can be run without installing it, just executing the "launcher" 
script inside the source directory:

`python3 launcher`

> First, make sure you have installed at least all the above required
dependencies.

Vidtuber can also be run in interactive mode with the Python interpreter,
always within the same unpacked directory:

```Python
>>> from vidtuber import gui_app
>>> gui_app.main()
```
