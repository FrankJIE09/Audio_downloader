import argparse
import os
import sys
from main import download_media

try:
    import yt_dlp
except ImportError:
    print("错误：yt-dlp 未安装。请在 conda 环境中运行 'conda install -c conda-forge yt-dlp' 来安装。")
    sys.exit(1)

def batch_download(
    file_path,
    output_dir,
    download_video,
    download_audio,
    browser_cookies=None,
    cookie_file=None,
    force_overwrites=False,
):
    """
    从文本文件中读取 URL 列表并批量下载。

    :param file_path: 包含 URL 的文本文件路径。
    :param output_dir: 输出的根目录。
    :param download_video: 是否下载视频。
    :param download_audio: 是否提取音频。
    :param browser_cookies: 从哪个浏览器加载 cookies。
    :param cookie_file: Cookie 文件的路径。
    :param force_overwrites: 是否强制覆盖已存在的文件。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 未找到。")
        sys.exit(1)

    if not urls:
        print(f"文件 '{file_path}' 为空或不包含有效的 URL。")
        return

    print(f"从 '{file_path}' 中找到 {len(urls)} 个 URL。开始批量下载...")

    for i, url in enumerate(urls):
        print(f"\n--- [{i+1}/{len(urls)}] 正在处理 URL: {url} ---")
        
        # 默认行为：如果不是强制覆盖，则预先检查音频文件是否存在
        if not force_overwrites and download_audio:
            check_opts = {
                'quiet': True,
                'ignoreerrors': True,
                'extract_flat': 'in_playlist', # 快速获取播放列表信息而不深入
            }
            if cookie_file:
                check_opts['cookiefile'] = cookie_file
            elif browser_cookies:
                check_opts['cookiesfrombrowser'] = (browser_cookies,)
            
            try:
                with yt_dlp.YoutubeDL(check_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    # 仅对单个视频进行检查，播放列表由下载器内部处理
                    if info and info.get('_type') != 'playlist':
                        audio_info = info.copy()
                        audio_info['ext'] = 'mp3'
                        
                        # 构建预期的音频文件路径
                        audio_path_template = os.path.join(output_dir, 'audios', '%(title)s [%(id)s].%(ext)s')
                        expected_audio_path = ydl.prepare_filename(audio_info, outtmpl=audio_path_template)
                        
                        if os.path.exists(expected_audio_path):
                            print(f"音频文件已存在，跳过：{os.path.basename(expected_audio_path)}")
                            continue # 继续下一个 URL
            except Exception:
                # 如果预检查失败，没关系，继续执行下载，让下载器自己处理
                pass

        try:
            download_media(
                url,
                output_dir,
                download_video,
                download_audio,
                browser_cookies,
                cookie_file,
                force_overwrites
            )
        except Exception as e:
            print(f"处理 URL {url} 时发生未知严重错误: {e}")
        except KeyboardInterrupt:
            print("\n下载被用户中断。")
            sys.exit(0)
    
    print("\n--- 批量下载完成 ---")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="从文本文件中批量下载媒体文件 (视频和/或音频)。",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
使用方法:
  - 提供一个包含URL列表的文本文件。
  - 文件中每行一个URL。
  - 以 '#' 开头的行将被视为注释并忽略。

示例:
  # 只下载音频
  python batch_download.py links.txt --no-video

  # 同时下载视频和音频到 'my_collection' 目录
  python batch_download.py links.txt -o my_collection
"""
    )
    parser.add_argument("file", help="包含 URL 列表的文本文件路径。")
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

    batch_download(
        args.file,
        args.output,
        should_download_video,
        should_download_audio,
        args.cookies_from_browser,
        args.cookies,
        args.force_overwrites
    )
