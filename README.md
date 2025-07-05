 # 多媒体下载工具 (YouTube/Bilibili/网易云音乐)

这是一个功能强大的多媒体下载工具，支持从YouTube、Bilibili、网易云音乐等多个平台下载视频和音频文件。

## 功能特性

- 🎥 **视频下载**：支持从YouTube、Bilibili等平台下载高质量视频
- 🎵 **音频提取**：从视频中提取音频，转换为MP3格式
- 📝 **批量下载**：支持从文本文件批量下载多个链接
- 🎶 **网易云音乐**：支持网易云音乐歌单批量下载
- 🍪 **Cookie支持**：支持浏览器Cookie和Cookie文件，突破登录限制
- ⚡ **智能跳过**：自动跳过已存在的文件，避免重复下载
- 🔊 **音量调节**：支持下载时调整音频音量

## 环境要求

- Python 3.6+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [yun](https://github.com/nondanee/ncm-api) (用于网易云音乐下载)
- FFmpeg (用于音频/视频处理)

## 安装依赖

```bash
# 使用conda安装yt-dlp
conda install -c conda-forge yt-dlp

# 或使用pip安装
pip install yt-dlp

# 安装FFmpeg (Windows)
# 下载FFmpeg并添加到系统PATH中
```

## 文件结构

```
youtube_download/
├── main.py                    # 主程序 - 单个链接下载
├── batch_download.py          # 批量下载程序
├── batch_audio_only.py        # 批量音频下载程序
├── download_playlists.bat     # 网易云音乐歌单下载脚本
├── links.txt                  # 下载链接列表
├── yun.cookie.txt            # 网易云音乐Cookie文件
├── 网易云_id.txt             # 网易云音乐歌单ID列表
├── downloads/                 # 下载文件输出目录
│   ├── videos/               # 视频文件
│   └── audios/               # 音频文件
└── music/                    # 网易云音乐下载目录
    ├── 我喜欢的音乐/
    ├── 夜曲/
    └── 别让时间非礼了梦喜欢的音乐/
```

## 使用方法

### 1. 单个链接下载

```bash
# 下载视频和音频
python main.py "https://www.youtube.com/watch?v=VIDEO_ID"

# 只下载音频
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" --no-video

# 只下载视频
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" --no-audio

# 指定输出目录
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" -o "my_downloads"

# 使用Cookie文件
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" --cookies cookie.txt

# 从浏览器加载Cookie
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" --cookies-from-browser chrome

# 强制覆盖已存在的文件
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" --force-overwrites
```

### 2. 批量下载

首先在 `links.txt` 文件中添加要下载的链接，每行一个：

```
https://www.youtube.com/watch?v=VIDEO_ID1
https://www.bilibili.com/video/BV1234567890
# 这是注释行，会被忽略
https://www.youtube.com/watch?v=VIDEO_ID2
```

然后运行批量下载：

```bash
# 批量下载视频和音频
python batch_download.py links.txt

# 批量下载音频
python batch_download.py links.txt --no-video

# 指定输出目录
python batch_download.py links.txt -o "my_collection"
```

### 3. 仅音频批量下载

```bash
# 专门用于批量下载音频的简化版本
python batch_audio_only.py links.txt

# 强制覆盖已存在的文件
python batch_audio_only.py links.txt --force-overwrites
```

### 4. 网易云音乐歌单下载

1. 在 `网易云_id.txt` 文件中添加歌单ID，每行一个：
```
504948603
123456789
```

2. 配置 `yun.cookie.txt` 文件（包含网易云音乐的Cookie）

3. 运行批处理脚本：
```bash
download_playlists.bat
```

## 配置文件说明

### links.txt
包含要下载的URL列表，每行一个链接。支持的格式：
- YouTube: `https://www.youtube.com/watch?v=VIDEO_ID`
- Bilibili: `https://www.bilibili.com/video/BV1234567890`
- 其他yt-dlp支持的网站

### yun.cookie.txt
网易云音乐的Cookie文件，用于访问需要登录的歌单。

### 网易云_id.txt
网易云音乐歌单ID列表，每行一个ID。

### .gitignore
项目的Git忽略文件，包含以下忽略规则：
- 日志文件 (`*.log`)
- 临时文件 (`*.tmp`, `*.swp`, `*.bak`)
- 下载文件 (`downloads/`, `*.mp3`)
- 开发环境文件 (`.env`, `.vscode/`, `__pycache__/`)

## 支持的网站

### 通过yt-dlp支持的网站
- YouTube
- Bilibili
- 抖音/TikTok
- Twitter
- Instagram
- Facebook
- 以及其他1000+个网站

### 通过yun工具支持
- 网易云音乐

## 高级功能

### Cookie支持
对于需要登录的网站，可以通过两种方式使用Cookie：

1. **Cookie文件**：
   ```bash
   python main.py URL --cookies cookie.txt
   ```

2. **浏览器Cookie**：
   ```bash
   python main.py URL --cookies-from-browser chrome
   ```

### 音量调节
在 `batch_audio_only.py` 中，音频音量会自动增加200%（`audio_volume_multiplier=3`）。

### 文件命名
下载的文件会自动使用以下命名格式：
- 视频：`视频标题 [视频ID].mp4`
- 音频：`音频标题 [视频ID].mp3`

这样可以避免文件名冲突，确保每个文件都有唯一的标识符。

## 常见问题

### Q: 下载失败怎么办？
A: 检查网络连接，确保URL有效，对于某些网站可能需要使用Cookie。

### Q: 如何获取Cookie？
A: 可以使用浏览器开发者工具导出Cookie，或者直接使用 `--cookies-from-browser` 参数。

### Q: 支持下载播放列表吗？
A: 是的，yt-dlp支持YouTube播放列表和Bilibili合集的下载。

### Q: 如何跳过已下载的文件？
A: 程序会自动检查已存在的文件并跳过，除非使用 `--force-overwrites` 参数。

## 注意事项

1. **版权**：请确保您有权下载和使用这些媒体文件
2. **网络**：某些网站可能需要稳定的网络连接
3. **更新**：定期更新yt-dlp以支持最新的网站变化
4. **存储**：确保有足够的磁盘空间存储下载的文件

## 许可证

本项目仅供学习和个人使用。请遵守相关网站的服务条款和版权法律。

## 贡献

欢迎提交问题和改进建议！

---

*最后更新：2024年*