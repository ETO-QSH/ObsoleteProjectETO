import os
import json
from tqdm import tqdm
from glob import glob

rpg_dir = r'D:\Desktop\Desktop\mfsn'
bgm_type = 'ogg_'  # rpgmvo


class Decrypt:
    def __init__(self, rpg_dir, bgm_type):
        self.bgm_type = bgm_type
        in_file_addr = rpg_dir + r'\audio\*'
        print(in_file_addr)
        self.json_file = rpg_dir + r'\data\System.json'  # 保证是UTF-8编码，不是UTF-8 BOM，可以用记事本改
        self.in_file = glob(in_file_addr)  # 存放bgm的几个文件夹

    def get_key(self):
        with open(self.json_file, 'r', encoding='utf-8') as f:
            load_dict = json.load(f)
        if ('hasEncryptedAudio' not in load_dict):
            return 0, 0
        load_dict['hasEncryptedAudio'] = False
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(load_dict, f, ensure_ascii=False)
        key = load_dict['encryptionKey']
        _key = []
        for i in range(0, len(key), 2):
            _key.append(int(key[i:i+2], 16))
        return _key, int(len(key) / 2)

    def decrypt(self, content):
        content = content[self.headerLen:]
        _content = []
        for i in content:
            _content.append(i)
        for i in range(self.headerLen):
            _content[i] ^= self.key[i]
        return bytes(_content)

    def run(self):
        # get key
        self.key, self.headerLen = self.get_key()
        # decrypt
        if self.headerLen > 0:
            print('start decrypting...')
            for i in tqdm(self.in_file, ncols=100):
                os.chdir(i)
                encrypted_file = glob('*.{}'.format(self.bgm_type))
                for j in tqdm(encrypted_file, leave=0, ncols=100):
                    with open(j, 'rb') as f:
                        decrypted_file = self.decrypt(f.read())
                    with open(j[:-len(self.bgm_type)] + 'ogg', 'wb') as f:
                        f.write(decrypted_file)
        # convert by ffmpeg
        print('start converting...')
        for i in tqdm(self.in_file, ncols=100):
            os.chdir(i)
            ogg_music = glob('*.ogg')
            for j in tqdm(ogg_music, leave=0, ncols=100):
                os.system(f'ffmpeg -i "{j}" -acodec aac "{j[:-4]}.m4a" >/dev/null 2>&1')


if __name__ == '__main__':
    d = Decrypt(rpg_dir, bgm_type)
    d.run()
