def menuAdd(self):
    try:
        directory, _ = QFileDialog.getOpenFilNames(self, '选择文件', './headshots', 'PNG Files(.png)')
        for dir in directory:
            if os.getcwd()+'\\headshots' == os.path.dirname(dir) and os.path.splitext(os.path.split(dir)[1])[0] in os.listdir('./saves') and os.path.splitext(os.path.split(dir)[1])[1] == '.png':
                copyfile(dir, os.path.abspath(os.path.dirname(os.path.dirname(dir)))+'\\images\\'+'{}'.format(dir.split('/')[-1]))
    except:
        #QSound('./waves/发生错误.wav', self).play()
        pass

def menuRemove(self):
    try:
        directory, _ = QFileDialog.getOpenFilNames(self, '选择文件', './headshots', 'PNG Files(.png)')
        for dir in directory:
            if os.getcwd()+'\\images' == os.path.dirname(dir) and os.path.splitext(os.path.split(dir)[1])[0] in os.listdir('./saves') and os.path.splitext(os.path.split(dir)[1])[1] == '.png':
                copyfile(dir, os.path.abspath(os.path.dirname(os.path.dirname(dir)))+'\\headshots\\'+'{}'.format(dir.split('/')[-1]))
    except:
        #QSound('./waves/发生错误.wav', self).play()
        pass
    