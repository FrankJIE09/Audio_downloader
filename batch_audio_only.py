import argparse
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from main import download_media

try:
    import yt_dlp
except ImportError:
    print("错误：yt-dlp 未安装。请在 conda 环境中运行 'conda install -c conda-forge yt-dlp' 来安装。")
    sys.exit(1)


# 创建线程锁用于线程安全的打印
print_lock = threading.Lock()


def safe_print(*args, **kwargs):
    """线程安全的打印函数"""
    with print_lock:
        print(*args, **kwargs)


def download_single_url(url, output_dir, cookie_file=None, force_overwrites=False):
    """
    下载单个 URL 的音频文件。这个函数将在线程池中被调用。
    
    :param url: 要下载的 URL
    :param output_dir: 输出目录
    :param cookie_file: Cookie 文件路径
    :param force_overwrites: 是否强制覆盖已存在的文件
    :return: 包含 URL 和下载结果的元组
    """
    start_time = time.time()
    
    try:
        # 如果不是强制覆盖，检查音频文件是否已存在
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
                            return (url, "已存在", os.path.basename(expected_audio_path), 0)
            except Exception:
                pass

        # 下载音频
        download_media(
            url,
            output_dir,
            download_video=False,  # 固定为只下载音频
            download_audio=True,
            cookie_file=cookie_file,
            force_overwrites=force_overwrites,
            audio_volume_multiplier=3  # 音量增加50%
        )
        
        elapsed_time = time.time() - start_time
        return (url, "成功", None, elapsed_time)
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        return (url, "错误", str(e), elapsed_time)


def batch_download_audio_only(
    file_path,
    output_dir,
    cookie_file=None,
    force_overwrites=False,
    max_workers=4
):
    """
    从文本文件中读取 URL 列表，并使用多线程批量下载音频。

    :param file_path: 包含 URL 的文本文件路径。
    :param output_dir: 输出的根目录。
    :param cookie_file: Cookie 文件的路径。
    :param force_overwrites: 是否强制覆盖已存在的文件。
    :param max_workers: 最大线程数。
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

    print(f"从 '{file_path}' 中找到 {len(urls)} 个 URL。使用 {max_workers} 个线程开始批量下载音频...")
    print(f"输出目录: {os.path.abspath(output_dir)}")
    print("-" * 80)

    # 创建输出目录
    os.makedirs(os.path.join(output_dir, 'audios'), exist_ok=True)

    # 统计变量
    completed = 0
    skipped = 0
    failed = 0
    total_time = 0

    # 记录开始时间
    batch_start_time = time.time()

    # 使用线程池执行下载
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        try:
            # 提交所有下载任务
            future_to_url = {
                executor.submit(download_single_url, url, output_dir, cookie_file, force_overwrites): url
                for url in urls
            }

            # 处理完成的任务
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    url, status, extra_info, elapsed_time = future.result()
                    total_time += elapsed_time
                    
                    if status == "成功":
                        completed += 1
                        safe_print(f"✓ [{completed + skipped + failed}/{len(urls)}] 下载成功 ({elapsed_time:.1f}s): {url}")
                    elif status == "已存在":
                        skipped += 1
                        safe_print(f"- [{completed + skipped + failed}/{len(urls)}] 文件已存在，跳过: {extra_info}")
                    else:  # 错误
                        failed += 1
                        safe_print(f"✗ [{completed + skipped + failed}/{len(urls)}] 下载失败 ({elapsed_time:.1f}s): {url}")
                        safe_print(f"  错误信息: {extra_info}")
                        
                except Exception as e:
                    failed += 1
                    safe_print(f"✗ [{completed + skipped + failed}/{len(urls)}] 处理失败: {url}")
                    safe_print(f"  错误信息: {e}")

        except KeyboardInterrupt:
            safe_print("\n下载被用户中断。正在停止所有线程...")
            executor.shutdown(wait=True)
            sys.exit(0)

    # 计算总时间
    batch_elapsed_time = time.time() - batch_start_time
    
    # 显示最终统计
    safe_print("-" * 80)
    safe_print(f"批量音频下载完成！")
    safe_print(f"总计: {len(urls)} 个 URL")
    safe_print(f"成功: {completed} 个")
    safe_print(f"跳过: {skipped} 个")
    safe_print(f"失败: {failed} 个")
    safe_print(f"总用时: {batch_elapsed_time:.1f} 秒")
    if completed > 0:
        safe_print(f"平均下载时间: {total_time/completed:.1f} 秒/个")
    safe_print(f"并发效率: {max_workers} 个线程")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="[仅音频] 从文本文件中批量下载音频。支持多线程下载。",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
这是一个简化版脚本，专门用于批量下载音频。
默认会跳过 'audios' 文件夹中已存在的同名文件。
支持多线程下载以提高效率。

示例:
  # 从 links.txt 批量下载音频（使用默认 8 个线程）
  python batch_audio_only.py links.txt

  # 使用 8 个线程下载
  python batch_audio_only.py links.txt --max-workers 8

  # 下载并强制覆盖已存在的文件
  python batch_audio_only.py links.txt --force-overwrites

  # 使用 cookie 文件并指定输出目录
  python batch_audio_only.py links.txt --cookies cookies.txt --output my_downloads
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
    parser.add_argument(
        "--max-workers",
        type=int,
        default=8,
        help="最大线程数 (默认为 8)。增加线程数可以提高下载速度，但也会增加系统负载。"
    )

    args = parser.parse_args()

    # 验证线程数
    if args.max_workers < 1:
        print("错误: 最大线程数必须大于 0。")
        sys.exit(1)
    elif args.max_workers > 20:
        print("警告: 使用过多线程可能会导致系统不稳定或被网站限制。建议使用 1-20 个线程。")

    batch_download_audio_only(
        args.file,
        args.output,
        args.cookies,
        args.force_overwrites,
        args.max_workers
    ) 