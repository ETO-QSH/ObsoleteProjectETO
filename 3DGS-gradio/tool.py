import os
import re
import sys
import json
import time
import queue
import threading
import subprocess
import gradio as gr

MODEL_PATHS = {}
FLAG_LOCK = False
TRAIN_PROC = None
FINAL_MODEL_PATH = None
LOG_QUEUE = queue.Queue()

with open("external.json", "r", encoding="utf-8") as ex:
    external = json.load(ex)


def extract_frames(video_path, fps):
    global TRAIN_PROC

    if not os.path.isfile(video_path):
        gr.Warning("视频文件不存在")
        raise FileNotFoundError(f"视频文件不存在：{video_path}")

    images_path = os.path.join("./data", 'split')
    os.makedirs(images_path, exist_ok=True)

    ffmpeg_exe = external["ffmpeg"]["PATH"]
    if not os.path.isfile(ffmpeg_exe):
        gr.Warning("ffmpeg 未找到")
        raise FileNotFoundError(f"ffmpeg 未找到：{ffmpeg_exe}")

    cmd = [
        ffmpeg_exe, "-i", video_path, "-qscale:v", "1", "-qmin", "1",
        "-vf", f"fps={fps}", os.path.join(images_path, "%04d.jpg")
    ]
    log_line(str(cmd))

    try:
        TRAIN_PROC = subprocess.Popen(cmd)
        TRAIN_PROC.wait()
        frame_count = len(os.listdir(images_path))
        return images_path, frame_count
    except Exception as e:
        gr.Error("视频抽帧出错")
        raise RuntimeError(f"视频抽帧出错：{e}")


def convert_frames(images_path):
    global TRAIN_PROC

    try:
        cmd = [sys.executable, "convert.py", "-s", images_path]
        # cmd = [
        #     os.path.join(external["3DGS"]["ROOT"], "convert.bat"),
        #     external["3DGS"]["ENVS"],
        #     os.path.abspath(images_path)
        # ]
        log_line(str(cmd))

        TRAIN_PROC = subprocess.Popen(cmd)
        TRAIN_PROC.wait()

    except Exception as e:
        gr.Error("特征提取出错")
        raise RuntimeError(f"特征提取出错：{e}")


def log_line(text):
    line = f"[{time.strftime("%H:%M:%S")}]   {text}\n"
    print(line.rstrip())
    LOG_QUEUE.put(line)


def make_training_filter():
    printed_thresholds = set()
    pattern = re.compile(r'^Training progress:\s*(\d+(?:\.\d+)?)%')

    def should_output(line: str) -> bool:
        nonlocal printed_thresholds
        match = pattern.match(line)
        if not match:
            return False
        try:
            percent = float(match.group(1))
        except ValueError:
            return False

        threshold = int(percent // 20) * 20
        if 0 <= threshold <= 80 and threshold not in printed_thresholds:
            printed_thresholds.add(threshold)
            return True
        return False

    def reset():
        nonlocal printed_thresholds
        printed_thresholds.clear()

    should_output.reset = reset
    return should_output


def run_train_3dgs(source_video, fps, rounds, exp_name, json):
    global TRAIN_PROC, FINAL_MODEL_PATH, FLAG_LOCK
    log_line("开始进行视频转3D高斯模型")

    images_folder, n_frames = extract_frames(source_video, fps)
    if FLAG_LOCK:
        FLAG_LOCK = not FLAG_LOCK
        log_line(f"视频抽帧进程中断")
        raise RuntimeWarning(f"视频抽帧进程中断")
    log_line(f"抽帧完成，共 {n_frames} 帧")

    convert_frames(images_folder)
    if FLAG_LOCK:
        FLAG_LOCK = not FLAG_LOCK
        log_line(f"特征提取进程中断")
        raise RuntimeWarning(f"特征提取进程中断")
    log_line(f"特征提取完成")

    cmd = [
        sys.executable, "train.py", "-s", images_folder, "-m", os.path.join("output", "3dgs", exp_name),
        "--iterations", str(int(rounds)), "--quiet", "--port", "0"
    ]
    # cmd = [
    #     os.path.join(external["3DGS"]["ROOT"], "train.bat"),
    #     external["3DGS"]["ENVS"],
    #     os.path.abspath(images_folder),
    #     os.path.abspath(os.path.join("output", "3dgs", exp_name)),
    #     str(int(rounds))
    # ]
    # if json:
    #     cmd += ["--json", os.path.abspath("config.json"), "--key", "3DGS"]
    log_line(str(cmd))

    TRAIN_PROC = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
    filter_func = make_training_filter()
    for line in TRAIN_PROC.stdout:
        print(">>> 原始行:", repr(line))

        if re.search(r'Exhaustive feature matching', line.strip()):
            log_line(f"特征匹配开始")
        if re.search(r'Reading reconstruction', line.strip()):
            log_line(f"稀疏重建开始")
        if re.search(r'Image undistortion', line.strip()):
            log_line(f"去除畸变开始")
        if re.search(r'Optimizing', line.strip()):
            log_line(f"正式开始高斯泼溅训练")
        if filter_func(line.strip()):
            log_line(line.strip())

        final_model_path_catch = re.search(r'__FINAL_MODEL_PATH__\|(.+?)$', line.strip())
        if final_model_path_catch:
            FINAL_MODEL_PATH = final_model_path_catch.group(1).strip()
            log_line(f"最终模型输出：{FINAL_MODEL_PATH}")
            MODEL_PATHS["SfM-Free"] = FINAL_MODEL_PATH

    TRAIN_PROC.wait()
    filter_func.reset()
    if FLAG_LOCK:
        FLAG_LOCK = not FLAG_LOCK
        log_line(f"模型训练进程中断")
        raise RuntimeWarning(f"模型训练进程中断")
    log_line("模型训练结束")


def _start_train(video, fps, rounds, exp, json):
    global FINAL_MODEL_PATH

    if not video:
        gr.Warning("请先上传视频")
        return None

    if "3DGS" in MODEL_PATHS:
        del MODEL_PATHS["3DGS"]
    FINAL_MODEL_PATH = None

    LOG_QUEUE.queue.clear()
    LOG_QUEUE.put("CLEAR_TOKEN")
    threading.Thread(target=run_train_3dgs, args=(video, fps, rounds, exp, json), daemon=True).start()


def _stop_train():
    global TRAIN_PROC, FLAG_LOCK
    try:
        if TRAIN_PROC and TRAIN_PROC.poll() is None:
            TRAIN_PROC.terminate()
            TRAIN_PROC.wait(timeout=15)

            FLAG_LOCK = True
            while FLAG_LOCK:
                time.sleep(1)
            log_line("进程已强行结束")
            return True

        elif TRAIN_PROC is None:
            log_line("进程已强行结束")
            return True

    except Exception as e:
        gr.Error("无法结束训练")
        raise RuntimeError(f"无法结束训练：{e}")
