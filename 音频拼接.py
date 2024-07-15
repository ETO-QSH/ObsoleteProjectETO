
import subprocess

def execute_ffmpeg_command(command):
    try:
        subprocess.check_output(command, shell=True)
        print("\033[1;32m" + "FFmpeg command executed successfully." + "\033[0m")
    except subprocess.CalledProcessError as e:
        print("\033[1;31m" + "Error executing FFmpeg command: {}".format(e) + "\033[0m")
    finally:
        return 'command: {}'.format(command)

def get_command(number, interval, velocity):
    command = 'ffmpeg {} -filter_complex "[0:a]apad=pad_dur={}[s0];{}[out]atempo={}[out_speed]" -map "[out_speed]" -metadata title="ETO.mp3" output.mp3'.format(
        ' '.join(['-i {}.mp3'.format(i+1) for i in range(number)]), interval,
        ''.join(['[0:a][1:a]concat=n=2:v=0:a=1[s1];[s0][s1]concat=n=2:v=0:a=1[s2];'] + [('[s{}][{}:a]concat=n=2:v=0:a=1[out];'.format(i, i) if i == (number-1) else ('[s{}][{}:a]concat=n=2:v=0:a=1[s{}];'.format(i, i, i+1) if i > 1 else '')) for i in range(number)]), velocity
    )
    return command

print(execute_ffmpeg_command(get_command(number=10, interval=10, velocity=1.2)))
