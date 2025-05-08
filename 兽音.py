class MeowTranslator:
    def __init__(self, char):
        self.char_map = list(char)
        if not (len(self.char_map) == 4 and len(set(self.char_map)) == 4):
            raise ValueError("需要4个不重复的字符")

    def meow_to_hex(self, str_meow):
        str_hex = ""
        for i in range(0, len(str_meow), 2):
            j = self.char_map.index(str_meow[i])
            k = self.char_map.index(str_meow[i + 1])
            k = (j * 4 + k - i // 2 % 16 + 16) % 16
            str_hex += format(k, 'x')
        return str_hex.upper()

    def hex_to_meow(self, str_hex):
        buffer = ""
        for i in range(len(str_hex)):
            k = (int(str_hex[i], 16) + i % 16) % 16
            buffer += self.char_map[k // 4] + self.char_map[k % 4]
        return buffer

    def hex_to_str(self, str_hex):
        buffer = ""
        for i in range(0, len(str_hex), 4):
            buffer += chr(int(str_hex[i:i+4], 16))
        return buffer

    def str_to_hex(self, str_text):
        str_hex = ""
        for char in str_text:
            str_hex += format(ord(char), '04x')
        return str_hex.upper()

    def set_char_map_from_meow(self, str_meow):
        if len(str_meow) >= 4:
            self.char_map[0] = str_meow[2]
            self.char_map[1] = str_meow[1]
            self.char_map[2] = str_meow[-1]
            self.char_map[3] = str_meow[0]

    def set_char_map(self, str_map):
        if len(str_map) >= 4:
            self.char_map[0] = str_map[0]
            self.char_map[1] = str_map[1]
            self.char_map[2] = str_map[2]
            self.char_map[3] = str_map[-1]

    def get_char_map_str(self):
        return ''.join(self.char_map)

    def get_char_map(self):
        return self.char_map.copy()

    def get_char_map_to_meow(self):
        return [
            self.char_map[3],
            self.char_map[1],
            self.char_map[0],
            self.char_map[2],
        ]

    def parse_to_string(self, str_meow):
        print('输入串', str_meow)
        if len(str_meow) >= 4:
            self.set_char_map_from_meow(str_meow)
            print('设置字典映射', self.get_char_map())
            str_hex = self.meow_to_hex(str_meow[3:-1])
            print('十六进制转换', str_hex)
            str_text = self.hex_to_str(str_hex)
            print('文本转换', str_text)
            return str_text
        return ""

    def parse_to_meow(self, str_text, char_map=None):
        if char_map and len(char_map) >=4:
            self.set_char_map(char_map)
            print('设置字典映射', self.get_char_map())
        print('输入串', str_text)
        str_hex = self.str_to_hex(str_text)
        print('十六进制转换', str_hex)
        str_meow = self.hex_to_meow(str_hex)
        print('文本转换', str_meow)
        char_map_meow = self.get_char_map_to_meow()
        str_meow = f"{char_map_meow[0]}{char_map_meow[1]}{char_map_meow[2]}{str_meow}{char_map_meow[3]}"
        print('字典位追加', str_meow)
        return str_meow


translator = MeowTranslator("明日方舟")

# 加密
str_human = "ETO"
str_meow = translator.parse_to_meow(str_human)
print("加密结果:", str_meow)

# 解密
str_human_decrypted = translator.parse_to_string(str_meow)
print("解密结果:", str_human_decrypted)
