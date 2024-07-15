
import os, subprocess

def batch_convert_files(input_folder, output_folder, input_extension, output_extension):
    files = [f for f in os.listdir(input_folder) if f.endswith(input_extension)]
    for file in files:
        input_file = os.path.join(input_folder, file)
        output_file = os.path.join(output_folder, os.path.splitext(file)[0] + output_extension)
        command = ['ffmpeg', '-i', input_file, output_file]
        subprocess.call(command)

batch_convert_files('D:\\新建文件夹 (3)', 'D:\\新建文件夹 (4)', '.png', '.jpg')
