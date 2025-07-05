# YouTube/Bilibili/Douyin 音频和视频下载器

一个简单的 Python 脚本，用于从 YouTube、Bilibili、抖音等网站下载视频和/或音频。

## 功能

- 支持 YouTube, Bilibili, 抖音 (TikTok) 等众多网站的链接。
- **[新]** 可以同时下载视频和提取音频，并保存到不同目录 (`downloads/videos`, `downloads/audios`)。
- **[新]** 可以选择只下载视频，或只下载音频。
- **[新]** 支持从文本文件进行批量下载。
- **[新]** 支持中文文件名: 文件名会保留原始标题中的中文字符。
- **[新]** 智能文件名: 自动在文件名中加入唯一的视频ID (`标题 [ID].mp4`)，防止重名文件被覆盖或跳过。
- **[新]** 默认跳过重复: 批量下载时，默认会检查并跳过在 `audios` 文件夹中已存在的音频文件。
- **[新]** 强制覆盖: 提供 `--force-overwrites` 选项，可以覆盖默认的跳过行为，强制重新下载。
- **[新]** 错误忽略: 批量下载时，单个链接失败不会中断整个任务。
- 可自定义输出目录。

## 安装与使用 (使用 Conda)

本项目推荐使用 [Conda](https://docs.conda.io/en/latest/miniconda.html) 来管理环境和依赖。

### 1. 创建并激活 Conda 环境

```bash
conda create -n media-downloader python=3.9 -y
conda activate media-downloader
```

### 2. 安装依赖

此项目依赖 `yt-dlp` 和 `ffmpeg`。在激活的环境中，从 `conda-forge` 频道安装它们：

```bash
conda install -c conda-forge yt-dlp ffmpeg -y
```

### 3. 如何使用

#### 单个链接下载

使用 `main.py` 脚本下载单个链接。

- **下载视频和音频 (默认):**
  ```bash
  python main.py "视频的URL"
  ```

- **只下载音频:**
  ```bash
  python main.py "视频的URL" --no-video
  ```

- **只下载视频:**
  ```bash
  python main.py "视频的URL" --no-audio
  ```

- **指定输出目录:**
  ```bash
  python main.py "视频的URL" -o "my_collection"
  ```

- **[重要] 如何下载需要 Cookie 的网站 (如抖音)**

  对于抖音这类网站，服务器需要验证浏览器的 Cookie 信息。我们提供两种方式来加载 Cookie，**强烈推荐使用方法1**。

  #### 方法 1: (推荐) 使用 `cookies.txt` 文件
  
  这是最稳定可靠的方法，可以绕过所有浏览器文件锁定和加密问题。
  
  1.  **安装浏览器扩展**:
      *   **Chrome/Edge**: 在应用商店搜索并安装 [**Get cookies.txt-LOCALLY**](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelhbljzzaogicljgnmkjfkpbafeag) 扩展。
      *   **Firefox**: 在应用商店搜索并安装 [**cookies.txt**](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/) 扩展。
  
  2.  **导出 Cookie**:
      *   在浏览器中打开 **抖音网站** (douyin.com)。
      *   点击刚刚安装的扩展图标。
      *   点击 "Export" 或 "Download" 按钮，将 Cookie 保存为 `cookies.txt` 文件，并将其放置在本项目根目录下。
  
  3.  **运行脚本**:
      在命令中使用 `--cookies` 参数指向刚刚导出的文件。
      ```bash
      # 使用 cookies.txt 文件下载抖音视频
      python main.py "抖音的分享URL" --cookies cookies.txt
      ```
  
  #### 方法 2: (备用) 直接从浏览器读取
  
  此方法更便捷，但可能会因系统权限或加密问题而失败。

  **注意：** 运行脚本前，请**完全关闭**您指定的浏览器（包括后台进程），否则 `yt-dlp` 可能无法读取 Cookie 文件。

  ```bash
  # 尝试从 Chrome 浏览器自动加载 Cookie 来下载抖音视频
  python main.py "抖音的分享URL" --cookies-from-browser chrome
  ```

#### 批量下载

使用 `batch_download.py` 脚本从一个文本文件批量下载。

1.  创建一个文本文件 (例如 `links.txt`)，每行放入一个视频 URL。
2.  运行脚本，并将文件名作为参数传入。

- **批量下载视频和音频:**
  ```bash
  python batch_download.py links.txt
  ```

- **批量只下载音频:**
  ```bash
  python batch_download.py links.txt --no-video
  ```

- **使用 `cookies.txt` 文件批量下载:**
  ```bash
  python batch_download.py links.txt --cookies cookies.txt
  ```

- **强制重新下载所有文件 (覆盖默认的跳过行为):**
  ```bash
  python batch_download.py links.txt --force-overwrites
  ```

#### [新] 仅批量下载音频 (简化版)

如果您只关心音频，可以使用 `batch_audio_only.py` 脚本，它的用法更简单。
**此脚本会自动将下载的音频音量增加50%。**

- **批量下载音频 (默认跳过已存在文件):**
  ```bash
  python batch_audio_only.py links.txt
  ```

- **使用 Cookie 下载并强制覆盖:**
  ```bash
  python batch_audio_only.py links.txt --cookies cookies.txt --force-overwrites
  ```

下载的文件将默认保存在项目根目录下的 `downloads` 文件夹中，视频和音频会分目录存放。
