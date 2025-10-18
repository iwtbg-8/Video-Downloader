# Ultimate Universal Video Downloader

Download videos from **ANY website** supported by yt-dlp! This powerful tool goes beyond YouTube to handle hundreds of video platforms with advanced features and an intuitive interface.

## 🌐 Universal Support

Supports **1000+ websites** including:
- **YouTube** (videos, playlists, shorts)
- **Vimeo**, **Dailymotion**
- **TikTok**, **Instagram** (Reels, Stories)
- **Twitter/X** (videos)
- **Reddit** (videos)
- **Twitch** (clips, streams)
- **Facebook** (videos)
- **And hundreds more!**

## 🚀 Advanced Features

- **Universal Video Downloads**: Any yt-dlp supported site
- **YouTube Search**: Built-in search with results you can add to queue
- **Format Selection**: Browse and choose from all available qualities
- **Concurrent Downloads**: Download multiple videos simultaneously
- **Queue Management**: Add downloads to queue, pause/resume, stop all
- **Real-time Progress**: Live updates with percentage, speed, and ETA
- **Smart Audio Conversion**: Automatic MP3 extraction
- **Subtitles & Thumbnails**: Download captions and video thumbnails
- **Playlist Support**: Download entire playlists from any site
- **Tabbed Interface**: Organized Download, Search, and Settings tabs

## Installation

1. Ensure Python 3.6+ is installed.
2. Install dependencies: `pip install yt-dlp`
3. FFmpeg is required for audio conversion (usually pre-installed on Linux)

## Usage

### GUI Mode (Recommended)

Run: `python downloader.py`

**Download Tab:**
- Paste URLs from any supported site (one per line)
- Click "List Formats" to see available options
- Select format, enable options (audio, playlist, subtitles, etc.)
- Add to queue and start downloading

**Search Tab:**
- Search YouTube directly
- Select results and add to download queue
- No need to copy/paste URLs manually

**Settings Tab:**
- View all supported websites
- See the full list of 1000+ extractors

### CLI Mode

```bash
python downloader.py [options] URL [URL ...]
```

Options:
- `-d, --dir DIR`: Output directory (default: downloads)
- `-f, --format FORMAT`: Video format (default: best)
- `-a, --audio`: Download audio only (converts to MP3)
- `-p, --playlist`: Download entire playlist
- `-c, --concurrent N`: Number of concurrent downloads (default: 1)
- `-s, --subtitles`: Download subtitles/captions
- `-t, --thumbnail`: Download video thumbnail

Examples:

```bash
# YouTube video
python downloader.py https://www.youtube.com/watch?v=dQw4w9WgXcQ

# TikTok video
python downloader.py https://www.tiktok.com/@user/video/123456789

# Instagram Reel
python downloader.py https://www.instagram.com/reel/ABC123/

# Vimeo video with subtitles
python downloader.py -s https://vimeo.com/123456789

# Playlist with concurrent downloads
python downloader.py -p -c 3 https://www.youtube.com/playlist?list=PLAYLIST_ID

# Audio only from any site
python downloader.py -a https://example.com/video
```

## Supported Sites Examples

The downloader supports virtually any video site. Some popular ones:
- YouTube, YouTube Music
- Vimeo, Vimeo Livestream
- Dailymotion
- TikTok, TikTok Music
- Instagram, Instagram TV
- Twitter/X
- Facebook, Facebook Live
- Reddit
- Twitch, Twitch Clips
- SoundCloud
- Bandcamp
- And 900+ more!

## Advanced Features

- **Format Discovery**: See file sizes and quality options before downloading
- **Queue System**: Manage multiple downloads efficiently
- **Progress Hooks**: Real-time download status
- **Post-processing**: Automatic format conversion
- **Metadata**: Preserve video information
- **Error Handling**: Robust error reporting and recovery

## Requirements

## Troubleshooting

### GUI Won't Start (Segmentation Fault)
If you get a segmentation fault when running the GUI:
- This is common in headless environments (VMs, servers without display)
- The downloader automatically falls back to CLI mode with helpful messages
- Use CLI mode: `python downloader.py --help`
- For GUI on remote systems, use X11 forwarding: `ssh -X user@host`

### Common Issues
- **tkinter not found**: Install python3-tk
- **FFmpeg missing**: Install ffmpeg for audio conversion
- **Permission denied**: Run with proper permissions or change output directory