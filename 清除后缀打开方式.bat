@echo off
set /p ext=������Ҫ����ĺ�׺������.����
 
echo.ϣ������ĺ�׺Ĭ��ֵ��.%ext%
pause
 
::ʹ���������
assoc .%ext%=
 
::������ע�����
echo.Windows Registry Editor Version 5.00>edit.reg
echo.[-HKEY_CLASSES_ROOT\.%ext%]>>edit.reg
echo.[-HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.%ext%]>>edit.reg
 
start edit.reg
echo.ȷ�ϵ�����������������
pause >nul
del edit.reg
 
::������Դ������
taskkill /f /im explorer.exe
start explorer.exe