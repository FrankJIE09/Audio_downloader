@echo off
chcp 65001 >nul
echo ========================================
echo 网易云音乐歌单批量下载脚本
echo ========================================
echo.

:: 检查必要文件是否存在
if not exist "网易云_id.txt" (
    echo 错误：未找到 网易云_id.txt 文件
    pause
    exit /b 1
)

if not exist "yun.cookie.txt" (
    echo 错误：未找到 yun.cookie.txt 文件
    pause
    exit /b 1
)

:: 创建music文件夹
if not exist "music" (
    mkdir music
    echo 已创建 music 文件夹
)

echo 开始下载歌单...
echo.

:: 读取歌单ID并逐个下载
for /f "tokens=* delims=" %%i in (网易云_id.txt) do (
    echo ========================================
    echo 正在下载歌单: %%i
    echo ========================================
    
    :: 进入music文件夹
    cd music
    
    :: 下载歌单（使用默认格式，yun工具会自动创建歌单文件夹）
    yun --cookie ..\yun.cookie.txt -c 5 -q 320 --cover %%i
    
    :: 返回上级目录
    cd ..
    
    echo.
    echo 歌单 %%i 处理完成
    echo.
)

echo ========================================
echo 所有歌单下载完成！
echo 文件保存在 music 文件夹的各个歌单子文件夹中
echo ========================================
pause 