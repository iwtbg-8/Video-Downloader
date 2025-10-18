#!/usr/bin/env python3
"""
Ultimate Universal Video Downloader
Download videos from ANY website supported by yt-dlp, with advanced features.
"""

#!/usr/bin/env python3
"""
CLI-only Ultimate Universal Video Downloader
Supports any site yt-dlp supports.
Features:
- Download videos/audio from any supported site
- List available formats for a URL
- Search YouTube from CLI
- Concurrent downloads
- Subtitles and thumbnail downloading
- Batch download from file
- Config file support
- Logging to file
- Retry mechanism
"""

import argparse
import sys
import os
import json
import logging
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from yt_dlp import YoutubeDL


def setup_logging(log_file):
    if log_file:
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.WARNING)  # Suppress unless log file specified


def progress_hook(d):
    status = d.get('status')
    if status == 'downloading':
        percent = d.get('_percent_str', '0%').strip()
        speed = d.get('_speed_str', 'N/A')
        eta = d.get('_eta_str', 'N/A')
        filename = os.path.basename(d.get('filename', ''))
        msg = f"Downloading {filename}: {percent} at {speed}, ETA {eta}"
        print(msg)
        logging.info(msg)
    elif status == 'finished':
        filename = os.path.basename(d.get('filename', ''))
        msg = f"Finished: {filename}"
        print(msg)
        logging.info(msg)


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def load_config(config_file):
    if config_file and Path(config_file).exists():
        with open(config_file, 'r') as f:
            return json.load(f)
    return {}


def save_config(config_file, config):
    if config_file:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)


def list_formats(url, retries=3):
    for attempt in range(retries):
        try:
            with YoutubeDL({'listformats': True, 'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'formats' in info:
                    for f in info['formats']:
                        size = f.get('filesize') or f.get('filesize_approx') or 0
                        size_str = f"{size/1024/1024:.1f}MB" if size else 'unknown'
                        note = f.get('format_note') or ''
                        print(f"{f['format_id']} - {f.get('ext','')} - {note} ({size_str})")
                else:
                    print('No format list available for this URL')
            break
        except Exception as e:
            if attempt == retries - 1:
                print(f"Error listing formats after {retries} attempts: {e}")
            else:
                print(f"Attempt {attempt+1} failed, retrying...")


def search_youtube(query, max_results=10, retries=3):
    search_url = f"ytsearch{max_results}:{query}"
    for attempt in range(retries):
        try:
            with YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                info = ydl.extract_info(search_url, download=False)
                results = []
                if 'entries' in info:
                    for entry in info['entries']:
                        results.append({'title': entry.get('title'), 'url': entry.get('webpage_url'), 'duration': entry.get('duration')})
                return results
        except Exception as e:
            if attempt == retries - 1:
                print(f"Search failed after {retries} attempts: {e}")
                return []
            else:
                print(f"Search attempt {attempt+1} failed, retrying...")
    return []


def download_one(options):
    url = options['url']
    outdir = options.get('outdir', 'downloads')
    fmt = options.get('format', 'best')
    audio = options.get('audio', False)
    playlist = options.get('playlist', False)
    subtitles = options.get('subtitles', False)
    thumbnail = options.get('thumbnail', False)
    dry_run = options.get('dry_run', False)
    no_overwrites = options.get('no_overwrites', False)
    retries = int(options.get('retries', 3))
    timeout = int(options.get('timeout', 15))
    user_agent = options.get('user_agent')
    proxy = options.get('proxy')

    ensure_dir(outdir)

    ydl_opts = {
        'outtmpl': f"{outdir}/%(title)s.%(ext)s",
        'noplaylist': not playlist,
        'progress_hooks': [progress_hook],
        'quiet': False,
        'socket_timeout': timeout,
    }

    if no_overwrites:
        ydl_opts['nooverwrites'] = True
    if user_agent:
        # set HTTP header User-Agent
        ydl_opts['http_headers'] = {'User-Agent': user_agent}
    if proxy:
        ydl_opts['proxy'] = proxy

    if subtitles:
        ydl_opts['writesubtitles'] = True
        ydl_opts['subtitleslangs'] = ['en']

    if thumbnail:
        ydl_opts['writethumbnail'] = True

    if audio:
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        ydl_opts['format'] = fmt

    # Dry run: only show what would be downloaded
    if dry_run:
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info is None:
                    print(f"[DRY RUN] No info for {url}")
                    return
                if 'entries' in info and info['entries']:
                    for e in info['entries']:
                        try:
                            name = ydl.prepare_filename(e)
                        except Exception:
                            name = e.get('title') or '<unknown>'
                        print(f"[DRY RUN] {e.get('title')} -> {name}")
                else:
                    try:
                        name = ydl.prepare_filename(info)
                    except Exception:
                        name = info.get('title') or '<unknown>'
                    print(f"[DRY RUN] {info.get('title')} -> {name}")
            return
        except Exception as e:
            print(f"Dry-run failed for {url}: {e}")
            logging.error(f"Dry-run failed for {url}: {e}")
            return

    attempt = 0
    while attempt < retries:
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            logging.info(f"Successfully downloaded {url}")
            return
        except Exception as e:
            attempt += 1
            msg = f"Download failed for {url} (attempt {attempt}/{retries}): {e}"
            print(msg)
            logging.error(msg)
            if attempt < retries:
                sleep_time = 2 ** attempt
                print(f"Retrying in {sleep_time}s...")
                time.sleep(sleep_time)
            else:
                print(f"Giving up on {url} after {retries} attempts")


def cli_mode(args, config):
    # Merge config with args
    if 'output_dir' in config and not args.dir:
        args.dir = config['output_dir']
    if 'concurrent' in config and args.concurrent == 1:
        args.concurrent = config['concurrent']

    # Load URLs from batch file if provided
    urls = args.urls
    if args.batch_file:
        if not Path(args.batch_file).exists():
            print(f"Batch file {args.batch_file} not found")
            return
        with open(args.batch_file, 'r') as f:
            urls.extend([line.strip() for line in f if line.strip()])

    # Handle list-formats and search as separate commands
    if args.list_formats:
        if not urls:
            print('Provide a URL to list formats for')
            return
        list_formats(urls[0])
        return

    if args.search:
        results = search_youtube(args.search_query, max_results=args.max_results)
        for i, r in enumerate(results, 1):
            dur = r['duration']
            dur_str = f"{dur//60}:{dur%60:02d}" if dur else 'unknown'
            print(f"{i}. {r['title']} ({dur_str})\n   {r['url']}\n")
        return

    if not urls:
        print('No URLs provided for download')
        return

    with ThreadPoolExecutor(max_workers=args.concurrent) as ex:
        futures = []
        for url in urls:
            options = {
                'url': url,
                'outdir': args.dir,
                'format': args.format,
                'audio': args.audio,
                'playlist': args.playlist,
                'subtitles': args.subtitles,
                'thumbnail': args.thumbnail,
                'dry_run': args.dry_run,
                'no_overwrites': args.no_overwrites,
                'retries': args.retries,
                'timeout': args.timeout,
                'user_agent': args.user_agent,
                'proxy': args.proxy,
            }
            futures.append(ex.submit(download_one, options))

        for f in as_completed(futures):
            try:
                f.result()
            except Exception as e:
                print(f"Error in download task: {e}")


def build_parser():
    p = argparse.ArgumentParser(description='Ultimate Universal Video Downloader - CLI only')
    p.add_argument('urls', nargs='*', help='Video URLs to download (any yt-dlp supported site)')
    p.add_argument('-d', '--dir', default='downloads', help='Output directory')
    p.add_argument('-f', '--format', default='best', help='Video format')
    p.add_argument('-a', '--audio', action='store_true', help='Download audio only (converts to MP3)')
    p.add_argument('-p', '--playlist', action='store_true', help='Download entire playlist')
    p.add_argument('-c', '--concurrent', type=int, default=1, help='Number of concurrent downloads')
    p.add_argument('-s', '--subtitles', action='store_true', help='Download subtitles')
    p.add_argument('-t', '--thumbnail', action='store_true', help='Download thumbnail')
    p.add_argument('--dry-run', dest='dry_run', action='store_true', help='Show what would be downloaded without saving files')
    p.add_argument('--no-overwrites', dest='no_overwrites', action='store_true', help='Do not overwrite existing files')
    p.add_argument('--retries', dest='retries', type=int, default=3, help='Number of download retries on failure')
    p.add_argument('--timeout', dest='timeout', type=int, default=15, help='Socket timeout in seconds')
    p.add_argument('--user-agent', dest='user_agent', help='Custom User-Agent header')
    p.add_argument('--proxy', dest='proxy', help='Proxy URL (e.g., socks5://127.0.0.1:9050)')
    p.add_argument('--list-formats', dest='list_formats', action='store_true', help='List available formats for the first URL')
    p.add_argument('--search', dest='search', action='store_true', help='Search YouTube (use --search-query)')
    p.add_argument('--search-query', dest='search_query', help='Query for YouTube search')
    p.add_argument('--max-results', dest='max_results', type=int, default=10, help='Max results for search')
    p.add_argument('--batch-file', dest='batch_file', help='File containing URLs to download (one per line)')
    p.add_argument('--config', dest='config_file', default='downloader_config.json', help='Config file path')
    p.add_argument('--log-file', dest='log_file', help='Log file path')
    p.add_argument('--version', action='version', version='Ultimate Downloader v1.0')

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    # Load config
    config = load_config(args.config_file)

    # Setup logging
    setup_logging(args.log_file)

    if args.search and not args.search_query:
        print('Provide --search-query for searching')
        sys.exit(1)

    if not args.urls and not args.search and not args.list_formats and not args.batch_file:
        parser.print_help()
        sys.exit(0)

    cli_mode(args, config)

    # Save config if changed
    if args.dir != 'downloads' or args.concurrent != 1:
        config['output_dir'] = args.dir
        config['concurrent'] = args.concurrent
        save_config(args.config_file, config)


if __name__ == '__main__':
    main()