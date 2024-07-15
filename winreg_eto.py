import winreg

def menuSet_0(self):
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'Software\\Microsoft\\Windows\\CurrentVersion\\Run', 0, access=winreg.KEY_ALL_ACCESS)
    winreg.SetValueEx(key, 'DeskpetETO', 0, winreg.REG_SZ, path)
    winreg.CloseKey(key)
    
def menuSet_1(self):
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'Software\\Microsoft\\Windows\\CurrentVersion\\Run', 0, access=winreg.KEY_ALL_ACCESS)
    winreg.DeleteValue(key, 'DeskpetETO')
    winreg.CloseKey(key)
    