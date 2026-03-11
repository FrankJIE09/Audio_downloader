## Audio_downloader（YouTube/Bilibili/抖音等音视频下载）

这个仓库提供一组基于 `yt-dlp` 的脚本，用于从多平台下载视频/音频，并在需要时用 `ffmpeg` 转码。

### 脚本说明

- **`main.py`**：单个链接下载（视频/音频）
- **`batch_download.py`**：按 `links.txt` 批量下载（视频/音频）
- **`batch_audio_only.py`**：按 `links.txt` 批量下载音频，并输出为 **MP3**
- **`download_playlists.bat`**：网易云歌单批量下载（依赖 `yun`，可选）

### 输出目录

- **音频**：`downloads/audios/标题 [视频ID].mp3`
- **视频**：`downloads/videos/标题 [视频ID].mp4`

---

## 环境要求（Windows）

- **conda 环境**：`Audio_downloader`
- **Python**：建议 3.10+
- **依赖**
  - `yt-dlp`
  - `ffmpeg`（没有它就无法稳定转 MP3；可能会只下载到 `.webm/.m4a`）

---

## 安装与运行（推荐：conda）

### 1) 激活环境

```powershell
conda activate Audio_downloader
```

### 2) 安装 yt-dlp（二选一）

```powershell
conda install -c conda-forge yt-dlp
```

或

```powershell
python -m pip install -U yt-dlp
```

### 3) 安装 ffmpeg（强烈推荐）

#### 方案 A：conda-forge（优先）

```powershell
conda install -c conda-forge ffmpeg
```

#### 方案 B：winget（当 conda 安装失败时）

```powershell
winget install --id Gyan.FFmpeg -e
```

如果提示“已修改 PATH，需要重启 shell”，请**关闭并重新打开终端/Cursor**后再运行脚本。

验证是否安装成功：

```powershell
ffmpeg -version
ffprobe -version
```

---

## 使用方法

### 1) 批量：只下载 MP3（推荐）

1. 编辑 `links.txt`，每行一个链接，支持注释（以 `#` 开头）：

```text
https://www.youtube.com/watch?v=xxxx
# 这是一行注释
https://www.bilibili.com/video/BVxxxx
```

2. 运行：

```powershell
python batch_audio_only.py links.txt
```

常用参数：

- 强制覆盖并重新下载：

```powershell
python batch_audio_only.py links.txt --force-overwrites
```

- 指定输出目录（默认 `downloads/`）：

```powershell
python batch_audio_only.py links.txt -o downloads
```

---

### 2) 单个链接下载

- 下载视频 + 音频：

```powershell
python main.py "URL"
```

- 只下载音频（并转 MP3）：

```powershell
python main.py "URL" --no-video
```

- 只下载视频：

```powershell
python main.py "URL" --no-audio
```

---

### 3) Cookie（遇到登录/风控/年龄限制时）

- 使用 cookie 文件（Netscape 格式）：

```powershell
python main.py "URL" --cookies cookies.txt
```

- 从浏览器读取 cookie：

```powershell
python main.py "URL" --cookies-from-browser chrome
```

批量脚本 `batch_audio_only.py` 也支持：

```powershell
python batch_audio_only.py links.txt --cookies cookies.txt
```

---

## 常见问题（FAQ）

### 1) 为什么下载后还是 `.webm/.m4a`，不是 `.mp3`？

几乎都是 **ffmpeg 不可用**导致的：

- 先运行 `ffmpeg -version` 确认
- 若用 winget 安装过，请重启终端/Cursor 让 PATH 生效
- 再用 `--force-overwrites` 重跑

### 2) 控制台乱码/Unicode 报错怎么办？

可以在 PowerShell 里临时指定 UTF-8 输出：

```powershell
$env:PYTHONIOENCODING="utf-8"
python batch_audio_only.py links.txt
```

### 3) 音量为什么更大？

`batch_audio_only.py` 调用 `download_media()` 时默认设置了 `audio_volume_multiplier=3`，会通过 ffmpeg 的 `volume=` 滤镜放大音量。

---

## 免责声明

请遵守目标网站条款与版权法律。本项目仅供学习与个人使用。
