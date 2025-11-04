import re


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


filter_func = make_training_filter()

logs = [
    "Training progress:  21%|██▎       | 7000/30000 [02:56<13:21, 28.69it/s, Loss=0.0839446]",
    "Training progress:  39%|███▉      | 12000/30000 [05:00<08:00, 35.00it/s, Loss=0.0623]",
    "Training progress:  41%|████▏     | 12500/30000 [05:20<07:40, 34.50it/s, Loss=0.0591]"
]

for line in logs:
    if filter_func(line):
        print(line)

print("--- 重置后 ---")
filter_func.reset()

for line in logs:
    if filter_func(line):
        print(line)
