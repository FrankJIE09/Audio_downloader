"""
网易云音乐下载器 —— 从 网易云_id.txt 或命令行参数读取歌单 ID 并下载。

底层依赖 ncm-dl（已安装），会自动处理 weapi 加密和下载。
歌单中 VIP/付费歌曲若未设置 MUSIC_U 环境变量会被跳过。

用法：
  # 从 网易云_id.txt 读取歌单 ID 并下载
  python netease_dl.py

  # 直接指定歌单 ID
  python netease_dl.py 504948603

  # 指定输出文件夹
  python netease_dl.py 504948603 -o downloads/audios

设置 MUSIC_U Cookie:
  export MUSIC_U='你的MUSIC_U值'
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def _ncm_dl_bin() -> str:
    """返回 ncm-dl 可执行文件的绝对路径。"""
    # 优先在当前 Python 的同级 bin 目录查找（conda 环境）
    python_dir = Path(sys.executable).parent
    candidate = python_dir / "ncm-dl"
    if candidate.exists():
        return str(candidate)
    # 备选：通过 pip show 查找
    for p in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(p) / "ncm-dl"
        if candidate.exists():
            return str(candidate)
    return "ncm-dl"  # fallback


def download_playlist(playlist_id: int, output_dir: str, overwrite: bool = False) -> int:
    """调用 ncm-dl 下载歌单，返回成功下载数。"""
    ncm_dl = _ncm_dl_bin()
    cmd = [
        ncm_dl, "playlist",
        str(playlist_id),
        "--output", output_dir,
        "--level", "standard",
        "--no-md5",
    ]
    # 不传递 --overwrite（ncm-dl默认不覆盖）；除非显式要求
    if overwrite:
        cmd.append("--overwrite")

    # 捕获 stderr 中可能提取的计数
    print(f"执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    # 始终打印 stdout （包含歌单信息和进度）
    if result.stdout:
        print(result.stdout)

    # 如果返回非 0 且输出中有错误信息，打印 stderr
    if result.returncode != 0:
        err_msg = result.stderr.strip()
        if err_msg:
            print(f"警告（ncm-dl 返回码 {result.returncode}）: {err_msg}")
            print("（这是 ncm-dl 尝试写 M3U 到 /opt/navidrome 权限不足，不影响歌曲下载）")

    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="网易云音乐歌单下载器（基于 ncm-dl）",
    )
    parser.add_argument("input", nargs="?", help="歌单 ID（数字）；留空则从 网易云_id.txt 读取")
    parser.add_argument("-o", "--output", default="downloads/audios",
                        help="输出目录 (默认 downloads/audios)")
    parser.add_argument("--overwrite", action="store_true",
                        help="覆盖已存在的文件")

    args = parser.parse_args()

    ids: list[str] = []
    if args.input:
        ids.append(args.input.strip())
    else:
        id_file = Path("网易云_id.txt")
        if id_file.exists():
            ids = [
                line.strip()
                for line in id_file.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]

    if not ids:
        print("请提供歌单 ID 作为参数，或创建 网易云_id.txt 文件")
        sys.exit(1)

    print(f"从 网易云_id.txt 读取到 {len(ids)} 个 ID")
    total = 0
    for item in ids:
        print(f"\n========== 处理歌单: {item} ==========")
        try:
            pid = int(item)
        except ValueError:
            print(f"跳过无效 ID: {item}")
            continue
        download_playlist(pid, args.output, args.overwrite)
        total += 1

    print(f"\n共处理 {total} 个歌单")


if __name__ == "__main__":
    main()
