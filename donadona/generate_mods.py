#!/usr/bin/env python3

import random
import subprocess
from pathlib import Path

from sample_and_verify import sampling


ROOT = Path(__file__).parent
ARK, MOD = ROOT / 'ark', ROOT / 'User'
TEMPLATE = (ROOT / 'template.txt').read_text(encoding='shift_jis')


def make_txt(name: str, attrs):
    lines = TEMPLATE.splitlines()
    lines[0] = f'画像={name}.png'
    lines[1] = f'名前={name}'

    attr_idx = [i for i, line in enumerate(lines) if line.startswith('属性=')]
    for i, attr in zip(attr_idx, attrs):
        lines[i] = f'属性={attr}'

    return '\n'.join(lines) + '\n'


def main():
    MOD.mkdir(exist_ok=True)

    for png in ARK.glob('*.png'):
        name = png.stem
        out_png = MOD / f'{name}.png'
        out_txt = MOD / f'{name}.txt'

        try:
            attrs = list(sampling(ROOT / 'row_weights.csv', 1, False).keys())
            random.shuffle(attrs)
            txt_content = make_txt(name, attrs)
            txt_encoded = txt_content.encode('shift_jis')
            out_txt.write_bytes(txt_encoded)

            subprocess.run(
                ['ffmpeg', '-y', '-i', str(png), '-vf', 'scale=360:720:flags=lanczos,pad=1024:1024:(ow-iw)/2:(oh-ih)/2:color=0x00000000', str(out_png)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        except Exception as e:
            print(e, name)


if __name__ == '__main__':
    main()
