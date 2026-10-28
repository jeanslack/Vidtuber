# -*- coding: UTF-8 -*-
"""
Name: downloader_gui.py
Purpose: youtube-dl user interface
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Oct.26.2026
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
import shutil
import itertools
import wx
from vidtuber.vt_utils.get_bmpfromsvg import get_bmp
from vidtuber.vt_dialogs.playlist_indexing import PlaylistIndexing
from vidtuber.vt_dialogs.confirm_dialog import Confirmation_Dlg
from vidtuber.vt_dialogs.list_warning import ListWarning
from vidtuber.vt_dialogs.subtitles_editor import SubtitleEditor
from vidtuber.vt_panels.formatcode_id import FormatCodeList
from vidtuber.vt_sys.settings_manager import ConfigManager


def from_api_to_cli(data, execpath):
    """
    Revert API arguments to command line options
    """
    args = [f'"{execpath}"']

    if data.get("format"):
        fmt_str = f'--format "{data["format"]}"'
        if data.get("audio-multistreams"):
            fmt_str += f' {data["audio-multistreams"]}'
        if data.get("video-multistreams"):
            fmt_str += f' {data["video-multistreams"]}'
        args.append(fmt_str)

    # default yt-dlp arguments
    args.extend([
        '--progress-template "download-title:%(info.id)s-%(progress.eta)s"',
        '--newline',
        f'--compat-options "{data["compat_opts"]}"',
        '--ignore-errors',
        '--ignore-config',
        '--no-color'
    ])
    if data.get('extractaudio'):
        args.append('--extract-audio')

    if data.get('postprocessors'):
        for pp in data['postprocessors']:
            for key, val in pp.items():
                if 'preferredcodec' in key:
                    args.append(f'--audio-format {val}')
                if 'EmbedThumbnail' in val:
                    args.append('--embed-thumbnail')
                if 'FFmpegEmbedSubtitle' in val:
                    args.append('--embed-subs')

    if data.get('addmetadata'):
        args.append('--embed-metadata')

    if data.get('external_downloader'):
        args.append(f'--downloader "{data["external_downloader"]}"')
        if data.get('external_downloader_args'):
            extdl = os.path.basename(data["external_downloader"])
            args.append(f'--downloader-args '
                        f'"{extdl}:{data["external_downloader_args"]}"')

    if data.get('yesplaylist') is True:
        args.append('--yes-playlist')
        if data.get('playlist_items'):
            args.append(f'--playlist-items "{data["playlist_items"]}"')
    else:
        args.append('--no-playlist')

    if data.get('writesubtitles'):
        args.append('--write-subs')
        if data.get('subtitleslangs') and data['subtitleslangs'][0]:
            sublang = ','.join(data["subtitleslangs"])
            args.append(f'--sub-langs "{sublang}"')
        if data.get('writeautomaticsub'):
            args.append('--write-auto-subs')
        if data.get('skip_download'):
            args.append('--skip-download')

    if data.get('restrictfilenames'):
        args.append('--restrict-filenames')
    if data.get('writethumbnail'):
        args.append('--write-thumbnail')
    if data.get('overwrites'):
        args.append('--force-overwrites')
    if data.get('nocheckcertificate'):
        args.append('--no-check-certificates')

    if data.get("proxy"):
        args.append(f'--proxy "{data["proxy"]}"')

    args.extend([
        f'--socket-timeout {data.get("socket_timeout", 30)}',
        f'--retries {data.get("retries", 10)}',
        f'--fragment-retries {data.get("fragment_retries", 10)}'
    ])

    if data.get('geo_verification_proxy'):
        args.append(f'--geo-verification-proxy '
                    f'"{data["geo_verification_proxy"]}"')

    geo = (f'{data.get("geo_bypass", "")} '
           f'{data.get("geo_bypass_country", "")} '
           f'{data.get("geo_bypass_ip_block", "")}'.strip()
           )
    if geo:
        args.append(f'--xff "{geo}"')

    if data.get('username'):
        args.append(f'--username {data["username"]}')
        args.append(f'--password {data["password"]}')

    if data.get('videopassword'):
        args.append(f'--video-password {data["videopassword"]}')

    if data.get("cookiefile"):
        args.append(f'--cookies "{data["cookiefile"]}"')

    if data.get("webbrowser"):
        cfb_val = data['webbrowser'] + data['webbrowserOPT']
        args.append(f'--cookies-from-browser "{cfb_val}"')

    args.append(f'--ffmpeg-location "{data["ffmpeg_location"]}"')
    args.append(f'--output "{data["outtmpl"]}"')

    return ' '.join(args) + ' '


class DLoad_Gui(wx.Panel):
    """
    This panel represents the main interface to yt-dlp
    """
    WHITE = '#fbf4f4'  # sb foreground
    VIOLET = '#D64E93'  # activated buttons

    # video resolution
    VRES = {('p1080'): ('best*[height=1080]'),
            ('p720'): ('best*[height=720]'),
            ('p480'): ('best*[height=480]'),
            ('p360'): ('best*[height=360]'),
            ('p240'): ('best*[height=240]'),
            ('p144'): ('best*[height=144]'),
            }
    AFORMATS = {("Auto"): ("best"),
                ("wav"): ("wav"),
                ("mp3"): ("mp3"),
                ("aac"): ("aac"),
                ("m4a"): ("m4a"),
                ("vorbis"): ("vorbis"),
                ("opus"): ("opus"),
                ("flac"): ("flac"),
                }
    # -----------------------------------------------------------------#

    def __init__(self, parent):
        """
        Initialization: the parent is the main frame
        """
        get = wx.GetApp()  # get data from bootstrap
        icons = get.iconset
        self.appdata = get.appset
        self.parent = parent
        self.red = self.appdata['colorscheme']['ERR1']  # code err + sb error
        confmanager = ConfigManager(self.appdata['fileconfpath'])
        sett = confmanager.read_options()
        # video qualities best or worst
        self.VQUAL = {_('Best quality video'): 'bestvideo',
                      _('Worst quality video'): 'worstvideo'}
        # precompiled videos
        self.VPCOMP = {_('Best available quality'): '',
                       _('Format 18 (youtube.com only)'): '18',
                       _('Worst available quality'):
                           'worstvideo+worstaudio/worst'}
        # audio qualities best or wors
        self.AQUAL = {_('Best quality audio'): 'bestaudio',
                      _('Worst quality audio'): 'worstaudio'}
        self.choices_list = [_('Combined Videos'),
                             _('Videos by Resolution'),
                             _('Split Audio and Video'),
                             _('Audio Only'),
                             _('Format Codes')]

        bmplistindx = get_bmp(icons['playlist'], ((16, 16)))
        bmpsubtitles = get_bmp(icons['subtitles'], ((16, 16)))

        self.opt = {("V_QUALITY"): list(self.VPCOMP)[0],
                    ("A_FORMAT"): "best",
                    ("A_QUALITY"): "bestaudio",
                    ("SUBS"): sett['subtitles_options'],
                    }
        self.playlist_indx = {}  # playlist indexes data
        self.format_codeid = {}  # format codes order with URL matching
        self.quality = 'best'

        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL)
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        # ------------- choice and comboboxes
        fgs1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_base.Add(fgs1, 0, wx.ALL | wx.CENTRE, 5)
        self.choice = wx.Choice(self, wx.ID_ANY,
                                choices=self.choices_list,
                                size=(-1, -1),
                                )
        self.choice.SetSelection(sett['download_mode'])
        txtdmode = wx.StaticText(self, wx.ID_ANY, _('Download Mode:'))
        fgs1.Add(txtdmode, 0, wx.LEFT | wx.CENTRE, 20)
        fgs1.Add(self.choice, 0, wx.LEFT | wx.CENTRE, 5)
        self.btn_plidx = wx.Button(self, wx.ID_ANY, "Playlist", size=(-1, -1))
        self.btn_plidx.SetToolTip(_('Playlist Editor'))
        self.btn_plidx.SetBitmap(bmplistindx, wx.LEFT)
        fgs1.Add(self.btn_plidx, 0, wx.LEFT | wx.CENTRE, 20)
        self.btn_subeditor = wx.Button(self, wx.ID_ANY, "Subtitles",
                                       size=(-1, -1))
        self.btn_subeditor.SetBitmap(bmpsubtitles, wx.LEFT)
        self.btn_subeditor.SetToolTip(_('Subtitles Editor'))
        fgs1.Add(self.btn_subeditor, 0, wx.LEFT | wx.CENTRE, 20)
        if sett['subtitles_options']['writesubtitles']:
            self.btn_subeditor.SetBackgroundColour(
                wx.Colour(DLoad_Gui.VIOLET))

        # ------------- quality pref
        box = wx.StaticBox(self, wx.ID_ANY, _('Quality settings'))
        boxoptions = wx.StaticBoxSizer(box, wx.VERTICAL)
        sizer_base.Add(boxoptions, 0, wx.ALL | wx.EXPAND, 5)
        fgs2 = wx.BoxSizer(wx.HORIZONTAL)
        boxoptions.Add(fgs2, 0, wx.ALL | wx.EXPAND, 0)
        self.cmbx_vq = wx.ComboBox(box, wx.ID_ANY,
                                   choices=(sett['video_quality'], ''),
                                   size=(-1, -1), style=wx.CB_DROPDOWN
                                   | wx.CB_READONLY
                                   )
        self.cmbx_vq.SetSelection(0)
        # grid_v.Add((20, 20), 0,)
        fgs2.Add(self.cmbx_vq, 0, wx.ALL | wx.CENTRE, 5)
        txtvformat = wx.StaticText(box, wx.ID_ANY, _('Video format:'))
        fgs2.Add(txtvformat, 0, wx.LEFT | wx.CENTRE, 5)
        self.cmbx_vformat = wx.ComboBox(box, wx.ID_ANY,
                                        choices=['Auto', 'webm', 'mp4'],
                                        size=(-1, -1), style=wx.CB_DROPDOWN
                                        | wx.CB_READONLY
                                        )
        self.cmbx_vformat.SetSelection(sett['video_format'])
        fgs2.Add(self.cmbx_vformat, 0, wx.ALL | wx.CENTRE, 5)
        fgs2.Add((20, 20), 0,)
        self.cmbx_aq = wx.ComboBox(box, wx.ID_ANY,
                                   choices=list(self.AQUAL.keys()),
                                   size=(-1, -1),
                                   style=wx.CB_DROPDOWN
                                   | wx.CB_READONLY
                                   )
        self.cmbx_aq.SetSelection(0)
        # grid_v.Add((20, 20), 0,)
        fgs2.Add(self.cmbx_aq, 0, wx.ALL | wx.CENTRE, 5)

        txtaformat = wx.StaticText(box, wx.ID_ANY, _('Audio format:'))
        fgs2.Add(txtaformat, 0, wx.LEFT | wx.CENTRE, 5)
        self.cmbx_af = wx.ComboBox(box, wx.ID_ANY,
                                   choices=list(DLoad_Gui.AFORMATS.keys()),
                                   size=(-1, -1),
                                   style=wx.CB_DROPDOWN
                                   | wx.CB_READONLY
                                   )
        self.cmbx_af.SetSelection(sett['audio_format'])
        fgs2.Add(self.cmbx_af, 0, wx.ALL | wx.CENTRE, 5)

        # ------------- simple listctrl
        box1 = wx.StaticBox(self, wx.ID_ANY, '')
        boxpanel = wx.StaticBoxSizer(box1, wx.VERTICAL)
        sizer_base.Add(boxpanel, 1, wx.ALL | wx.EXPAND, 5)
        self.panel_cod = FormatCodeList(box1,
                                        self.format_codeid,
                                        controller=self
                                        )
        boxpanel.Add(self.panel_cod, 1, wx.EXPAND)
        self.SetSizer(sizer_base)
        self.Layout()

        # ----------------------Binder (EVT)----------------------#
        self.choice.Bind(wx.EVT_CHOICE, self.on_choicebox)
        self.cmbx_vq.Bind(wx.EVT_COMBOBOX, self.on_vquality)
        self.cmbx_vformat.Bind(wx.EVT_COMBOBOX, self.on_quality)
        self.cmbx_af.Bind(wx.EVT_COMBOBOX, self.on_aformat)
        self.cmbx_aq.Bind(wx.EVT_COMBOBOX, self.on_aquality)
        self.btn_plidx.Bind(wx.EVT_BUTTON, self.on_playlist_idx)
        self.btn_subeditor.Bind(wx.EVT_BUTTON, self.on_subtitles_editor)

    # ----------------------------------------------------------------------
    def on_subtitles_editor(self, event):
        """
        Event by clicking on the subtitles button
        """
        with SubtitleEditor(self, self.opt["SUBS"]) as subeditor:
            if subeditor.ShowModal() == wx.ID_OK:
                data = subeditor.getvalue()
                self.opt["SUBS"] = data
        if not self.opt["SUBS"]["writesubtitles"]:
            self.btn_subeditor.SetBackgroundColour(wx.NullColour)
        else:
            self.btn_subeditor.SetBackgroundColour(
                wx.Colour(DLoad_Gui.VIOLET))
    # ----------------------------------------------------------------------

    def clear_data_list(self, changed):
        """
        Reset all required data if `changed` arg is True,
        delete data and set to Disable otherwise.
        """
        if not self.parent.data_url:
            self.format_codeid.clear()
            self.panel_cod.fcode.DeleteAllItems()
            self.on_choicebox(self, statusmsg=False)
        else:
            if changed:
                self.btn_plidx.SetBackgroundColour(wx.NullColour)
                self.playlist_indx.clear()
                self.panel_cod.fcode.DeleteAllItems()
                self.format_codeid.clear()
                self.on_choicebox(self, statusmsg=False)
    # -----------------------------------------------------------------#

    def on_format_codes(self):
        """
        Check data given from `self.panel_cod.set_formatcode()` method
        which allow to enabling download by "Format Code".
        If GetItemCount == 0 (False) and forcereload == False
        it Return None (i.e the format codes list is already set).
        """
        if self.panel_cod.fcode.GetItemCount():
            return None

        unsuppurls = []
        for url in self.parent.data_url:
            for key, value in url.items():
                if not value.get('formats'):
                    unsuppurls.append(f'"{key}"')
        if unsuppurls:
            msg = _('Unable to get format codes for playlists, '
                    'channels and/or multiple videos.\nPlease list '
                    'only individual video URLs or choose another '
                    'download mode.')
            with ListWarning(self,
                             dict.fromkeys(unsuppurls, _('Unsupported')),
                             caption='Unsupported URLs',
                             header=msg,
                             buttons='OK',
                             ) as log:
                log.ShowModal()
            return True

        self.panel_cod.set_formatcode(self.parent.data_url)
        return None
    # -----------------------------------------------------------------#

    def on_choicebox(self, event, statusmsg=True):
        """
        Set widgets on switching choice box
        """
        if statusmsg and self.parent.sb.GetStatusText() != 'Ready':
            self.parent.statusbar_msg(_('Ready'), None)

        mode = self.choice.GetSelection()

        # Disable all first
        self.cmbx_vq.Disable()
        self.cmbx_vformat.Disable()
        self.cmbx_aq.Disable()
        self.cmbx_af.Disable()

        if mode == 0:
            self.cmbx_vq.Enable()
            self.cmbx_vq.Clear()
            self.cmbx_vq.Append(list(self.VPCOMP.keys()))
            self.cmbx_vq.SetSelection(0)
            self.on_vquality(self)

        elif mode == 1:
            self.cmbx_vq.Enable()
            self.cmbx_vformat.Enable()
            self.cmbx_vq.Clear()
            self.cmbx_vq.Append(list(DLoad_Gui.VRES.keys()))
            self.cmbx_vq.SetSelection(0)
            self.on_vquality(self)

        elif mode == 2:
            self.cmbx_vq.Enable()
            self.cmbx_aq.Enable()
            self.cmbx_vq.Clear()
            self.cmbx_vq.Append(list(self.VQUAL.keys()))
            self.cmbx_vq.SetSelection(0)
            self.on_vquality(self)

        elif mode == 3:
            self.cmbx_aq.Enable()
            self.cmbx_af.Enable()
            self.on_aformat(self)

        elif mode == 4:
            if self.on_format_codes():
                return

        self.Layout()
    # -----------------------------------------------------------------#

    def on_vquality(self, event):
        """
        Set video qualities during combobox event
        """
        mode = self.choice.GetSelection()
        val = self.cmbx_vq.GetValue()

        if mode == 0:
            self.opt["V_QUALITY"] = self.VPCOMP[val]
        elif mode == 1:
            self.opt["V_QUALITY"] = DLoad_Gui.VRES[val]
        elif mode == 2:
            self.opt["V_QUALITY"] = self.VQUAL[val]

        self.on_quality(self)
    # -----------------------------------------------------------------#

    def on_quality(self, event):
        """
        Set preferring video and audio format on combobox event
        """
        mode = self.choice.GetSelection()
        vformat = self.cmbx_vformat.GetValue()
        quality = self.quality

        if mode == 0:
            quality = self.opt["V_QUALITY"]
            qbar = quality if quality != '' else 'Default best quality'
            self.parent.statusbar_msg(f'Quality: {qbar}', None)

        elif mode == 1:
            vf = '' if vformat == 'Auto' else f'[ext={vformat}]'
            quality = self.opt["V_QUALITY"] + vf
            self.parent.statusbar_msg(f'Quality: {quality}', None)

        elif mode == 2:
            quality = f'{self.opt["V_QUALITY"]},{self.opt["A_QUALITY"]}'
            self.parent.statusbar_msg(f'Quality: {quality}', None)

        elif mode == 3:
            quality = f'{self.opt["A_QUALITY"]}/worst'
            msg = f'Quality: {quality} (format={self.cmbx_af.GetValue()})'
            self.parent.statusbar_msg(msg, None)

        self.quality = quality
    # -----------------------------------------------------------------#

    def on_aformat(self, event):
        """
        Set audio format extension to exporting on combobox event.
        This is related to "Download Audio only" choice.
        """
        self.opt["A_FORMAT"] = DLoad_Gui.AFORMATS.get(self.cmbx_af.GetValue())
        self.on_quality(None)
    # -----------------------------------------------------------------#

    def on_aquality(self, event):
        """
        Set audio qualities on combobox event.
        This is related to "Download spilt audio and video" and
        "Download Audio only" choices.
        """
        self.opt["A_QUALITY"] = self.AQUAL.get(self.cmbx_aq.GetValue())
        self.on_quality(self)
    # -----------------------------------------------------------------#

    def on_playlist_idx(self, event):
        """
        Dialog for setting playlist indexing
        """
        with PlaylistIndexing(self,
                              self.parent.data_url,
                              self.playlist_indx) as idxdialog:
            if idxdialog.ShowModal() == wx.ID_OK:
                data = idxdialog.getvalue()
                if not data:
                    self.btn_plidx.SetBackgroundColour(wx.NullColour)
                    self.playlist_indx.clear()
                else:
                    self.btn_plidx.SetBackgroundColour(
                        wx.Colour(DLoad_Gui.VIOLET))
                    self.playlist_indx = data
    # -----------------------------------------------------------------#

    def default_download_options(self):
        """
        default_options
        Main mapping for download options.
        return a type dict object.
        """
        data = {}
        postprocessors = []
        if self.choice.GetSelection() == 3:
            postprocessors.append({'key': 'FFmpegExtractAudio',
                                   'preferredcodec': self.opt["A_FORMAT"],
                                   })
        if self.appdata['add_metadata']:
            postprocessors.append({'key': 'FFmpegMetadata'})
        if self.appdata["embed_thumbnails"]:
            postprocessors.append({'key': 'EmbedThumbnail'})
        if self.opt["SUBS"]["embedsubtitle"]:
            postprocessors.append({'key': 'FFmpegEmbedSubtitle'})
        if (self.appdata["select_cookie_file"]
                and self.appdata["cookiefile"].strip()):
            data["cookiefile"] = self.appdata["cookiefile"]
        if self.appdata["autogen_cookie_file"]:
            data["webbrowser"] = self.appdata["webbrowser"]
            data["webbrowserOPT"] = self.appdata.get("webbrowserOPT", "")
        data['compat_opts'] = 'youtube-dl'
        data['external_downloader'] = (
            self.appdata["external_downloader"])
        data['external_downloader_args'] = (
            self.appdata["external_downloader_args"])
        # data['noplaylist'] = self.opt["NO_PLAYLIST"]
        data['writesubtitles'] = self.opt["SUBS"]["writesubtitles"]
        data['subtitleslangs'] = self.opt["SUBS"]["subtitleslangs"]
        data['writeautomaticsub'] = self.opt["SUBS"]["writeautomaticsub"]
        data['skip_download'] = self.opt["SUBS"]["skip_download"]
        data['addmetadata'] = self.appdata['add_metadata']
        data['restrictfilenames'] = self.appdata["restrict_fname"]
        data['ignoreerrors'] = True
        data['no_warnings'] = False
        data['writethumbnail'] = self.appdata["embed_thumbnails"]
        data['overwrites'] = self.appdata["overwr_dl_files"]
        data['no_color'] = True
        data['nocheckcertificate'] = self.appdata["ssl_certificate"]
        data['proxy'] = self.appdata["proxy"]
        data['socket_timeout'] = self.appdata["timeoutDL"]
        data['retries'] = self.appdata["retriesDL"]
        data['fragment_retries'] = self.appdata["retriesfragDL"]
        data['username'] = self.appdata["username"]
        data['password'] = self.appdata["password"]
        data['videopassword'] = self.appdata["videopassword"]
        data["geo_verification_proxy"] = self.appdata["geo_verification_proxy"]
        data["geo_bypass"] = self.appdata["geo_bypass"]
        data["geo_bypass_country"] = self.appdata["geo_bypass_country"]
        data["geo_bypass_ip_block"] = self.appdata["geo_bypass_ip_block"]
        data['ffmpeg_location'] = f'{self.appdata["ffmpeg_cmd"]}'
        data['postprocessors'] = postprocessors
        data["audio-multistreams"] = ''
        data["video-multistreams"] = ''

        return data
    # -----------------------------------------------------------------#

    def build_args(self, outtmpl, format_quality, codes, **data):
        """
        Build the options list for yt_dlp,
        return a type list object.
        """
        datalist = []
        urlslist = [list(k.keys())[0] for k in self.parent.data_url]

        subdir = ('%(uploader)s/%(playlist_title)s/%(playlist_index)s - '
                  if self.appdata['playlistsubfolder'] else '')

        if not isinstance(codes, (list, tuple)):
            codes = [codes] if codes else []

        for url, code in itertools.zip_longest(urlslist,
                                               codes,
                                               fillvalue=''):
            if self.playlist_indx.get(url):
                template = subdir + outtmpl
                playlistitems = self.playlist_indx[url][0]
                yesplaylist = self.playlist_indx[url][1]
            else:
                template = outtmpl
                playlistitems = None
                yesplaylist = False

            format_code = code if code else format_quality
            datalist.append({
                'format': format_code,
                'extractaudio': data.get('extractaudio', False),
                'outtmpl': f"{self.appdata['dirdownload']}/{template}",
                'yesplaylist': yesplaylist,
                'playlist_items': playlistitems,
                'postprocessors': data.get('postprocessors', []),
                **data
            })
        return datalist
    # -----------------------------------------------------------------#

    def on_start(self):
        """
        Pass options list to processing.
        """
        data = self.default_download_options()
        mode = self.choice.GetSelection()

        # Configurazione di base del template dell'ID
        _id = ('%(title).100s-%(id)s' if self.appdata["include_ID_name"]
               else '%(title).100s')

        formatquality = self.quality
        outtmpl = f'{_id}.%(ext)s'
        code = []
        data['extractaudio'] = False

        if mode == 2:  # audio and video splitted
            outtmpl = f'{_id}.f%(format_id)s.%(ext)s'

        elif mode == 3:  # audio only
            data['extractaudio'] = True

        elif mode == 4:  # format code
            if self.panel_cod.fcode.GetItemCount() == 0:
                msg = _('Click the Reload Format Codes button.')
                wx.MessageBox(msg, _('Format Code List Missing'),
                              wx.ICON_INFORMATION, self
                              )
                return

            res_code = self.panel_cod.get_formatcode()
            if not res_code or not res_code[0]:
                msg = _('At least one "Format Code" must be checked for '
                        'each URL selected in green.')
                wx.MessageBox(msg, _('Incomplete Format Code Selection'),
                              wx.ICON_INFORMATION, self
                              )
                return

            formatquality = ''
            outtmpl = f'{_id}.f%(format_id)s.%(ext)s'
            code = res_code[0]
            data['audio-multistreams'] = res_code[1]
            data['video-multistreams'] = res_code[2]

        args_list = self.build_args(outtmpl,
                                    formatquality,
                                    code,
                                    **data
                                    )
        self.to_processing(args_list)
    # -----------------------------------------------------------------#

    def to_processing(self, datalist, getcmd=False):
        """
        Call `main_ytdlp.switch_to_processing`
        """
        execlist = []
        execpath = self.appdata['yt-dlp_cmd']
        if not shutil.which(execpath):
            wx.MessageBox(_('Missing «yt-dlp» executable. Please check the '
                            'execution permissions and be sure to make the '
                            'correct settings in the preferences dialog.'),
                          _('Vidtuber - Error!'), wx.ICON_ERROR, self)
            return

        for args in datalist:
            execlist.append(from_api_to_cli(args, execpath))

        with Confirmation_Dlg(self,
                              execlist,
                              [list(k.keys())[0] for k in self.parent.data_url]
                              ) as epilogue:
            if epilogue.ShowModal() == wx.ID_OK:
                newdata = epilogue.getvalue()
                if not newdata == execlist:
                    if wx.MessageBox(_('Changes have been made to the command '
                                       'arguments.\n\nAre you sure you want '
                                       'to apply them?'), _('Apply changes?'),
                                     wx.ICON_QUESTION | wx.CANCEL
                                     | wx.YES_NO, self) != wx.YES:
                        return
                    self.parent.switch_to_processing('Download Process',
                                                     newdata)
                else:
                    self.parent.switch_to_processing('Download Process',
                                                     execlist)
    # -----------------------------------------------------------------#
