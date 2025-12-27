import math
from functools import lru_cache
from typing import Tuple, Optional


class SmartPolicy:
    """ 根据 EventSimulator 的当前状态返回下一轮应执行的动作 (choice, sub_choice) """
    RICH_CANDLE = 25
    RICH_INGOT = 1250
    RICH_TICKETS = 60

    def __call__(self, sim) -> Tuple[str, Optional[str]]:
        """ 公共入口 -> 返回下一步动作 """
        # ---------- 1. 资源缺口优先级 ----------
        if sim.silk_cocoon and sim.tickets >= sim.ticket_cost and sim.originium < self.RICH_INGOT:
            return sim.ACTIONS[5]
        if sim.originium < self.RICH_INGOT and sim.candle >= self.RICH_CANDLE:
            return sim.ACTIONS[0]
        if sim.candle < self.RICH_CANDLE and sim.originium >= self.RICH_INGOT:
            return sim.ACTIONS[3]
        if sim.originium < self.RICH_INGOT or sim.candle < self.RICH_CANDLE:
            return self.mdp_optimal_action(sim)
        if sim.tickets < self.RICH_TICKETS:
            return sim.ACTIONS[2]
        # ---------- 2. 不缺了，二选一 ----------
        return sim.ACTIONS[4] if sim.flower_money >= sim.fierce_money else sim.ACTIONS[1]

    @staticmethod
    @lru_cache(maxsize=None)
    def _hyper_geometric_success(box: tuple, symbol: str, need: int, k: int) -> float:
        """ 超几何成功概率 -> P(抽中 >= need 个 symbol 的 k 个硬币) """
        total, good = len(box), box.count(symbol)
        return 0.0 if good < need else 1.0 - sum(
            math.comb(good, i) * math.comb(total - good, k - i) / math.comb(total, k)
            for i in range(need)
        )

    def recurse(self, x: int, t: int, p: float, f) -> int:
        if t > 0:
            x = x * (1 - p) + p * (x + f(x))
            return self.recurse(x, t - 1, p, f)
        else:
            return x

    def mdp_optimal_action(self, sim) -> Tuple[str, Optional[str]]:
        """
        以先耗尽为唯一判据的闭式最优策略：
        1. 计算两种动作在无限重试下的期望回合数
        2. 比较耗尽步数，先耗尽谁就先补谁
        3. 若不会先耗尽，选择成功率高的
        """

        # 计算超几何成功概率
        p_heng = self._hyper_geometric_success(tuple(sim.money_box), '衡', 1, sim.throw_count)
        p_li = self._hyper_geometric_success(tuple(sim.money_box), '厉', 2, sim.throw_count)

        if std := sim.get_payment_standard(sim.originium):
            c_ingot = std / (1 - (1 - p_heng) * sim.stay_prob)
            s_ingot = sim.originium // c_ingot - 1

            # 折算衡如常刷取源石锭的价值
            r_ingot = sim.rewards['衡如常'][std][1] * p_heng
            sim.standard = std

            # 折算票券间接刷取源石锭的价值（小除一个方差）
            t, p = (sim.tickets + sim.rewards['厉如锋']['要书一卷'][std][1]) // sim.ticket_cost, sim.throw_count / len(sim.money_box)
            r_silk = self.recurse(sim.originium - std, t, p, sim.silk_cocoon_return) * p_li / (t * p * (1 - p)) - std

        else:
            s_ingot = -1

        c_candle = 1 / (1 - (1 - p_li) * sim.stay_prob)
        s_candle = sim.candle // c_candle - 1

        if s_ingot < s_candle:
            return sim.ACTIONS[2] if s_ingot != -1 and r_ingot < r_silk else sim.ACTIONS[0]
        elif s_candle < s_ingot:
            return sim.ACTIONS[3]
        else:
            return sim.ACTIONS[0] if p_heng > p_li else sim.ACTIONS[3]
