import itertools
from collections import Counter

GEM_VALUE = {
    "Nesre_iner_0": 1, "Nesre_iner_1": 2, "Nesre_iner_2": 10, "Nesre_iner_3": 35, "Nesre_iner_4": 85,
    "Gabe_iner_0": 1, "Gabe_iner_1": 5, "Gabe_iner_2": 50, "Gabe_iner_3": 500,
    "Pet_iner_0": 1, "Pet_iner_1": 3, "Pet_iner_2": 22, "Pet_iner_3": 105,
    "Shay_iner_0": 1,
}

ALL_GEMS = list(GEM_VALUE.keys())
r_int = lambda x: int(round(x))


class GameState:
    def __init__(self, workspace: int, initial: Counter):
        self.workspace = workspace
        self.gems = Counter(initial)
        self.score = 0
        self.pet_bonus = 0
        self.shay_bonus = 0
        self.used_cards = set()
        self.log = []

    def copy(self):
        new = GameState.__new__(GameState)
        new.workspace = self.workspace
        new.gems = Counter(self.gems)
        new.score = self.score
        new.pet_bonus = self.pet_bonus
        new.shay_bonus = self.shay_bonus
        new.used_cards = set(self.used_cards)
        new.log = list(self.log)
        return new

    def value(self, gem: str):
        if gem.startswith("Pet_iner"):
            return GEM_VALUE[gem] + self.pet_bonus
        if gem == "Shay_iner_0":
            return GEM_VALUE[gem] + self.shay_bonus
        return GEM_VALUE[gem]

    def total_value(self):
        val = sum(self.value(k) * v for k, v in self.gems.items())

        if "淬雕_4" in self.used_cards:
            remaining = self.workspace - len(self.used_cards)
            bonus = remaining * 5000
            self.score += bonus
            self.log.append(f"  剩余工作台 {remaining} → 得分 +{bonus}")

        if "交糅_3" in self.used_cards:
            non_zero = [k for k in ALL_GEMS if self.gems[k]]
            if len(non_zero) == 1:
                bonus = self.gems["Pet_iner_3"] * 100
                self.score += bonus
                self.log.append(f"  唯一宝石奖励：{bonus}")

        return val + self.score

    def apply_card(self, card: str):
        """玩家主动把 card 放进工作台，才会调用这里"""
        self.used_cards.add(card)  # 标记已用
        self.execute_card(card)  # 真正执行效果

    def execute_card(self, card: str):
        """真正执行卡片效果；默认卡片也复用此函数"""
        self.log.append(f"执行：{card}")
        g = self.gems

        if card == "淬雕_1":
            n = g["Nesre_iner_0"]
            if n:
                g["Nesre_iner_0"] = 0
                g["Nesre_iner_1"] += 2 * n
                self.log.append(f"  转换 {n} Nesre_iner_0 → {2 * n} Nesre_iner_1")

        elif card == "淬雕_2":
            n = g["Nesre_iner_1"]
            if n:
                g["Nesre_iner_1"] = 0
                g["Nesre_iner_2"] += 2 * n
                self.log.append(f"  转换 {n} Nesre_iner_1 → {2 * n} Nesre_iner_2")

        elif card == "淬雕_3":
            n = g["Nesre_iner_2"]
            if n:
                g["Nesre_iner_2"] = 0
                g["Nesre_iner_3"] += r_int(2.4 * n)
                self.log.append(f"  转换 {n} Nesre_iner_2 → {r_int(2.4 * n)} Nesre_iner_3")

        elif card == "淬雕_4":
            n = g["Nesre_iner_3"]
            if n:
                g["Nesre_iner_3"] = 0
                g["Nesre_iner_4"] += n
                self.log.append(f"  转换 {n} Nesre_iner_3 → {n} Nesre_iner_4")

        elif card == "滤纯_1":
            n = g["Gabe_iner_0"]
            if n:
                g["Gabe_iner_0"] = 0
                g["Gabe_iner_1"] += n
                g["Shay_iner_0"] += n
                self.log.append(f"  转换 {n} Gabe_iner_0 → {n} Gabe_iner_1 + {n} Shay_iner_0")

        elif card == "滤纯_2":
            n = g["Gabe_iner_1"]
            if n:
                g["Gabe_iner_1"] = 0
                g2 = r_int(0.8 * n)
                g["Gabe_iner_2"] += g2
                g["Shay_iner_0"] += n + 2 * g2
                self.log.append(f"  转换 {n} Gabe_iner_1 → {g2} Gabe_iner_2 + {n + 2 * g2} Shay_iner_0")

        elif card == "滤纯_3":
            n = g["Gabe_iner_1"]
            if n:
                g["Gabe_iner_1"] = 0
                g3 = r_int(0.7 * n)
                g["Gabe_iner_3"] += g3
                g["Shay_iner_0"] += n + 2 * g3
                self.log.append(f"  转换 {n} Gabe_iner_1 → {g3} Gabe_iner_3 + {n + 2 * g3} Shay_iner_0")

        elif card == "交糅_1":
            total = g["Pet_iner_0"] + g["Shay_iner_0"]
            convert = r_int(0.5 * total)
            if convert:
                g["Pet_iner_0"] = g["Shay_iner_0"] = 0
                g["Pet_iner_1"] += convert
                self.pet_bonus += 5
                self.log.append(f"  交糅_1：{convert} Pet_iner_1，Pet系列价值+5")

        elif card == "交糅_2":
            total = g["Pet_iner_1"] + g["Gabe_iner_1"]
            convert = r_int(0.5 * total)
            if convert:
                g["Pet_iner_1"] = g["Gabe_iner_1"] = 0
                g["Pet_iner_2"] += convert
                self.pet_bonus += 15
                self.log.append(f"  交糅_2：{convert} Pet_iner_2，Pet系列价值+15")

        elif card == "交糅_3":
            total = g["Pet_iner_2"] + g["Nesre_iner_3"]
            convert = r_int(0.5 * total)
            if convert:
                g["Pet_iner_2"] = g["Nesre_iner_3"] = 0
                g["Pet_iner_3"] += convert
                self.log.append(f"  交糅_3：{convert} Pet_iner_3")

        elif card == "落晶_1":
            n = g["Shay_iner_0"]
            if n:
                g["Shay_iner_0"] *= 5
                self.log.append(f"  落晶_1：Shay_iner_0 *= 5 → {g['Shay_iner_0']}")

        elif card == "落晶_2":
            n = g["Shay_iner_0"]
            if n:
                g["Shay_iner_0"] *= 8
                self.log.append(f"  落晶_2：Shay_iner_0 *= 8 → {g['Shay_iner_0']}")

        elif card == "落晶_3":
            n = g["Shay_iner_0"]
            if n:
                g["Shay_iner_0"] *= 9
                self.shay_bonus += 1
                self.log.append(f"  落晶_3：Shay_iner_0 *= 9 → {g['Shay_iner_0']}，价值+1")

        else:
            raise ValueError(card)


ALL_CARDS = [
    "淬雕_1", "淬雕_2", "淬雕_3", "淬雕_4",
    "滤纯_1", "滤纯_2", "滤纯_3",
    "交糅_1", "交糅_2", "交糅_3",
    "落晶_1", "落晶_2", "落晶_3"
]
DEFAULT_CARDS = {"淬雕_1", "淬雕_2", "淬雕_3"}


def default_cards_effect(state: GameState):
    """默认阶段：仅执行未被玩家选进工作台的淬雕1/2/3"""
    for c in ["淬雕_1", "淬雕_2", "淬雕_3"]:
        if c not in state.used_cards:
            state.execute_card(c)


def simulate(workspace: int, initial: Counter, top_k=3):
    cards_pool = [c for c in ALL_CARDS if c not in DEFAULT_CARDS] + list(DEFAULT_CARDS)
    best = []

    for L in range(0, workspace + 1):
        for seq in itertools.permutations(cards_pool, L):
            state = GameState(workspace, initial)
            default_cards_effect(state)  # 先跑默认
            for c in seq:  # 再跑玩家卡片
                state.apply_card(c)
            best.append((seq, state.gems.copy(), state.total_value(), state))

    best.sort(key=lambda x: (-x[2], x[0]))
    return best[:top_k]


def main(workspace, init):
    """
    Nesre：火焰伊纳
    Gabe：草叶伊纳
    Pet：天空伊纳
    Shay：沙伊纳
    """

    initial = Counter({
        "Nesre_iner_0": init['Nesre'], "Gabe_iner_0": init['Gabe'],
        "Pet_iner_0": init['Pet'], "Shay_iner_0": init['Shay']
    })

    print(f"工作台数量：{workspace}")
    print("初始宝石：", dict(initial))
    print("\n" + "=" * 100 + "\n")

    top3 = simulate(workspace, initial, 3)

    for rank, (seq, final_gems, score, _) in enumerate(top3, 1):
        print(f"第 {rank} 名")
        print("卡片顺序：", list(seq))
        print("最终宝石：", dict(final_gems))
        print("总得分：", score)
        print("-" * 40)

    print("\n第一名详细过程：\n")
    seq, _, _, st = top3[0]
    st = GameState(workspace, initial)
    default_cards_effect(st)

    for c in seq:
        st.apply_card(c)
    for line in st.log:
        print("  " + line)

    print("\n" + "=" * 100 + "\n")
    print("最终宝石：", dict(st.gems))
    print("总得分：", st.total_value())


if __name__ == "__main__":
    main(workspace=2, init={"Nesre": 21, "Gabe": 32, "Pet": 28, "Shay": 19})
