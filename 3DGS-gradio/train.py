import os
import sys
import time
import argparse


parser = argparse.ArgumentParser(description="Demo-train: 睡觉流式日志")
parser.add_argument("-s", "--source_path", required=True, help="视频/图片目录")
parser.add_argument("-m", "--model_path",  required=True, help="输出目录")
parser.add_argument("--iterations", type=int, default=60, help="总步数")
parser.add_argument("--quiet", action="store_true", help="静默模式")
parser.add_argument("--port", type=int, default=0, help="运行端口")
args = parser.parse_args()

os.makedirs(args.model_path, exist_ok=True)

total = args.iterations
step = total // 20

for i in range(0, total + 1, step):
    time.sleep(0.1)
    print(f"[{i:>6}/{total}]  loss={0.9 - i/total*0.8:.4f}")
    sys.stdout.flush()


final_ply = r"D:\Desktop\Desktop\gradio-test\res\point_cloud.ply"

print("\nTraining complete.")
print(f"__FINAL_MODEL_PATH__|{os.path.abspath(final_ply)}")
sys.stdout.flush()
