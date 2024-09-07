@echo off
set /p ext=请输入要清除的后缀（不加.）：
 
echo.希望清除的后缀默认值：.%ext%
pause
 
::使用命令清除
assoc .%ext%=
 
::清除相关注册表项
echo.Windows Registry Editor Version 5.00>edit.reg
echo.[-HKEY_CLASSES_ROOT\.%ext%]>>edit.reg
echo.[-HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.%ext%]>>edit.reg
 
start edit.reg
echo.确认导入后按任意键继续……
pause >nul
del edit.reg
 
::重启资源管理器
taskkill /f /im explorer.exe
start explorer.exe