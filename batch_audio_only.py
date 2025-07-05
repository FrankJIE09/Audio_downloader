import argparse
import os
import sys

from main import download_media

try:
    import yt_dlp
except ImportError:
    print("错误：yt-dlp 未安装。请在 conda 环境中运行 'conda install -c conda-forge yt-dlp' 来安装。")
    sys.exit(1)


def batch_download_audio_only(
    file_path,
    output_dir,
    cookie_file=None,
    force_overwrites=False
):
    """
    从文本文件中读取 URL 列表，并只批量下载音频。

    :param file_path: 包含 URL 的文本文件路径。
    :param output_dir: 输出的根目录。
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

    print(f"从 '{file_path}' 中找到 {len(urls)} 个 URL。开始批量下载音频...")

    for i, url in enumerate(urls):
        print(f"\n--- [{i+1}/{len(urls)}] 正在处理 URL: {url} ---")
        
        # 默认行为：如果不是强制覆盖，则预先检查音频文件是否存在
        if not force_overwrites:
            check_opts = {
                'quiet': True,
                'ignoreerrors': True,
                'extract_flat': 'in_playlist',
            }
            if cookie_file:
                check_opts['cookiefile'] = cookie_file
            
            try:
                with yt_dlp.YoutubeDL(check_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info and info.get('_type') != 'playlist':
                        audio_info = info.copy()
                        audio_info['ext'] = 'mp3'
                        
                        audio_path_template = os.path.join(output_dir, 'audios', '%(title)s [%(id)s].%(ext)s')
                        expected_audio_path = ydl.prepare_filename(audio_info, outtmpl=audio_path_template)
                        
                        if os.path.exists(expected_audio_path):
                            print(f"音频文件已存在，跳过：{os.path.basename(expected_audio_path)}")
                            continue
            except Exception:
                pass

        try:
            download_media(
                url,
                output_dir,
                download_video=False, # 固定为只下载音频
                download_audio=True,
                cookie_file=cookie_file,
                force_overwrites=force_overwrites,
                audio_volume_multiplier=3 # 音量增加50%
            )
        except Exception as e:
            print(f"处理 URL {url} 时发生未知严重错误: {e}")
        except KeyboardInterrupt:
            print("\n下载被用户中断。")
            sys.exit(0)
    
    print("\n--- 批量音频下载完成 ---")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="[仅音频] 从文本文件中批量下载音频。",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
这是一个简化版脚本，专门用于批量下载音频。
默认会跳过 'audios' 文件夹中已存在的同名文件。

示例:
  # 从 links.txt 批量下载音频
  python batch_audio_only.py links.txt

  # 下载并强制覆盖已存在的文件
  python batch_audio_only.py links.txt --force-overwrites
"""
    )
    parser.add_argument("file", help="包含 URL 列表的文本文件路径。")
    parser.add_argument("-o", "--output", default="downloads", help="输出文件的根目录 (默认为 'downloads')")
    parser.add_argument(
        "--force-overwrites",
        action="store_true",
        help="强制覆盖并重新下载已存在的文件。"
    )
    parser.add_argument(
        "--cookies",
        metavar="FILE",
        help="指定包含 Cookies 的文本文件路径 (Netscape 格式)。"
    )

    args = parser.parse_args()

    batch_download_audio_only(
        args.file,
        args.output,
        args.cookies,
        args.force_overwrites
    ) 