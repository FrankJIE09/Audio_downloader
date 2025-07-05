import argparse
import os
import sys

try:
    import yt_dlp
except ImportError:
    print("错误：yt-dlp 未安装。请在 conda 环境中运行 'conda install -c conda-forge yt-dlp' 来安装。")
    sys.exit(1)


def download_media(
    url,
    output_dir='downloads',
    download_video=True,
    download_audio=True,
    browser_cookies=None,
    cookie_file=None,
    force_overwrites=False,
    audio_volume_multiplier=1.0
):
    """
    使用 yt-dlp 从给定的 URL 下载媒体文件。

    :param url: 视频的 URL.
    :param output_dir: 输出的根目录。
    :param download_video: 是否下载视频。
    :param download_audio: 是否提取音频。
    :param browser_cookies: 从哪个浏览器加载 cookies (例如, 'chrome', 'firefox').
    :param cookie_file: Cookie 文件的路径。
    :param force_overwrites: 是否强制覆盖已存在的文件。
    :param audio_volume_multiplier: 音频音量乘数 (例如 1.5 代表音量增加50%)。
    """
    base_ydl_opts = {
        'quiet': True,
        'progress_hooks': [progress_hook],
        'force_overwrites': force_overwrites,
        # --ignore-errors: 继续处理播放列表中的其他视频，即使某个视频下载失败
        'ignoreerrors': True,
    }

    if cookie_file:
        base_ydl_opts['cookiefile'] = cookie_file
    elif browser_cookies:
        base_ydl_opts['cookiesfrombrowser'] = (browser_cookies,)

    # 1. 下载视频
    if download_video:
        video_dir = os.path.join(output_dir, 'videos')
        os.makedirs(video_dir, exist_ok=True)
        
        video_opts = base_ydl_opts.copy()
        video_opts.update({
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            # 使用包含唯一ID的文件名模板，防止冲突
            'outtmpl': os.path.join(video_dir, '%(title)s [%(id)s].%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        })
        
        try:
            print(f"开始从 {url} 下载视频...")
            with yt_dlp.YoutubeDL(video_opts) as ydl:
                ydl.download([url])
        except yt_dlp.utils.DownloadError as e:
            print(f"\n下载视频时出错: {e}")
        except Exception as e:
            print(f"发生未知错误: {e}")

    # 2. 下载音频
    if download_audio:
        audio_dir = os.path.join(output_dir, 'audios')
        os.makedirs(audio_dir, exist_ok=True)
        
        audio_opts = base_ydl_opts.copy()
        audio_opts.update({
            'format': 'bestaudio/best',
            # 使用包含唯一ID的文件名模板，防止冲突
            'outtmpl': os.path.join(audio_dir, '%(title)s [%(id)s].%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
        
        # 如果指定了音量调节，添加 ffmpeg 参数
        if audio_volume_multiplier and audio_volume_multiplier != 1.0:
            audio_opts['postprocessor_args'] = ['-af', f'volume={audio_volume_multiplier}']

        try:
            print(f"开始从 {url} 提取音频...")
            with yt_dlp.YoutubeDL(audio_opts) as ydl:
                ydl.download([url])
        except yt_dlp.utils.DownloadError as e:
            print(f"\n提取音频时出错: {e}")
        except Exception as e:
            print(f"发生未知错误: {e}")


def progress_hook(d):
    if d['status'] == 'finished':
        # 文件名可能包含路径，我们只取文件名部分
        filename = os.path.basename(d['filename'])
        print(f"处理完成: {filename}")
    elif d['status'] == 'error':
        print(f"处理 {d.get('filename', '未知文件')} 时出错")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="从 YouTube, Bilibili, Douyin 等网站下载视频和/或音频。",
        epilog="示例: python main.py <URL> --no-video  (只下载音频)"
    )
    parser.add_argument("url", help="视频的 URL")
    parser.add_argument("-o", "--output", default="downloads", help="输出文件的根目录 (默认为 'downloads')")
    parser.add_argument("--no-video", action="store_true", help="不下载视频文件")
    parser.add_argument("--no-audio", action="store_true", help="不提取音频文件")
    parser.add_argument(
        "--force-overwrites",
        action="store_true",
        help="强制覆盖并重新下载已存在的文件。"
    )
    parser.add_argument(
        "--cookies",
        metavar="FILE",
        help="指定包含 Cookies 的文本文件路径 (Netscape 格式)。这是最可靠的方法。"
    )
    parser.add_argument(
        "--cookies-from-browser",
        metavar="BROWSER",
        help="从指定浏览器加载 Cookies (例如: chrome, firefox, edge, opera)。对抖音等网站可能需要此选项。"
    )

    args = parser.parse_args()

    should_download_video = not args.no_video
    should_download_audio = not args.no_audio

    if not should_download_video and not should_download_audio:
        print("错误: 您必须选择下载视频或音频中的至少一项。")
        sys.exit(1)

    download_media(
        args.url,
        args.output,
        should_download_video,
        should_download_audio,
        args.cookies_from_browser,
        args.cookies,
        args.force_overwrites
    )
