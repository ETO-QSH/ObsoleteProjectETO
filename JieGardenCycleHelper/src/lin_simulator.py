import random
from typing import Dict, List, Optional

from smart_policy import SmartPolicy


class LiveState:
    def __init__(self, candle, originium, tickets, flower_money, balance_money, fierce_money,
                 throw_count, ticket_cost, silk_cocoon, prize_count, stay_prob):

        self.candle = candle
        self.originium = originium
        self.tickets = tickets
        self.flower_money = flower_money
        self.balance_money = balance_money
        self.fierce_money = fierce_money
        self.throw_count = throw_count
        self.ticket_cost = ticket_cost
        self.silk_cocoon = silk_cocoon
        self.prize_count = prize_count
        self.stay_prob = stay_prob

        self.money_box = ['花'] * flower_money + ['衡'] * balance_money + ['厉'] * fierce_money
        self.standard = 0

        self.ACTIONS = [
            ('衡如常', None),
            ('厉如锋', '要兵器一对'),
            ('厉如锋', '要书一卷'),
            ('厉如锋', '要酒一壶'),
            ('花如簇', None),
            ('茧成绢', None)
        ]

        self.rewards = {
            '衡如常': {10: ('originium', 15), 20: ('originium', 30), 50: ('originium', 65)},
            '厉如锋': {
                '要兵器一对': {10: ('prize_count', 2), 20: ('prize_count', 3), 50: ('prize_count', 6)},
                '要书一卷': {10: ('tickets', 4), 20: ('tickets', 8), 50: ('tickets', 12)},
                '要酒一壶': {10: ('candle', 2), 20: ('candle', 3), 50: ('candle', 6)},
            },
            '花如簇': {10: ('prize_count', 2), 20: ('prize_count', 3), 50: ('prize_count', 6)},
        }

    @staticmethod
    def get_payment_standard(originium: int):
        standards = [50, 20, 10]
        for standard in standards:
            if originium >= standard:
                return standard
        return None

    @staticmethod
    def silk_cocoon_return(originium: int):
        return min(originium // 4, 99)


class EventSimulator:
    def __init__(self):
        self.candle = 0              # 烛火
        self.originium = 0           # 源石锭
        self.tickets = 0             # 票券
        self.flower_money = 0        # 花钱数量
        self.balance_money = 0       # 衡钱数量
        self.fierce_money = 0        # 厉钱数量
        self.throw_count = 0         # 投掷个数
        self.ticket_cost = 0         # 票券消耗
        self.silk_cocoon = False     # 茧成绢
        self.prize_count = 0         # 藏品数量
        self.stay_prob = 0.0         # 停留概率
        self.money_box = []          # 初始化空钱盒
        self.standard = 0            # 支付缓存

        self.ACTIONS = [
            ('衡如常', None),
            ('厉如锋', '要兵器一对'),
            ('厉如锋', '要书一卷'),
            ('厉如锋', '要酒一壶'),
            ('花如簇', None),
            ('茧成绢', None)
        ]

        self.rewards = {
            '衡如常': {10: ('originium', 15), 20: ('originium', 30), 50: ('originium', 65)},
            '厉如锋': {
                '要兵器一对': {10: ('prize_count', 2), 20: ('prize_count', 3), 50: ('prize_count', 6)},
                '要书一卷': {10: ('tickets', 4), 20: ('tickets', 8), 50: ('tickets', 12)},
                '要酒一壶': {10: ('candle', 2), 20: ('candle', 3), 50: ('candle', 6)},
            },
            '花如簇': {10: ('prize_count', 2), 20: ('prize_count', 3), 50: ('prize_count', 6)},
        }

    def set_initial_state(self, **kwargs):
        """设置初始状态"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @staticmethod
    def get_payment_standard(originium: int) -> Optional[int]:
        """根据源石锭数量确定支付标准"""
        standards = [50, 20, 10]
        for standard in standards:
            if originium >= standard:
                return standard
        return None

    @staticmethod
    def silk_cocoon_return(originium: int) -> int:
        """ 茧成绢返还规则 """
        return min(originium // 4, 99)

    def throw_money(self) -> List[str]:
        """模拟投钱过程，返回投钱结果列表"""
        self.money_box = ['花'] * self.flower_money + ['衡'] * self.balance_money + ['厉'] * self.fierce_money
        return random.sample(self.money_box, self.throw_count)

    @staticmethod
    def check_success(choice: str, throw_result: List[str]) -> bool:
        """检查是否成功"""
        if choice == '衡如常':
            return '衡' in throw_result
        elif choice == '厉如锋':
            return throw_result.count('厉') >= 2
        elif choice == '花如簇':
            return throw_result.count('花') >= 2
        return False

    def apply_reward(self, choice: str, standard: int, sub_choice: Optional[str] = None):
        """根据成功结果发放奖励，厉如锋支持三选一"""
        if choice == '衡如常':
            attr, val = self.rewards[choice][standard]
            setattr(self, attr, getattr(self, attr) + val)
            return attr, val
        elif choice == '厉如锋' and sub_choice:
            attr, val = self.rewards[choice][sub_choice][standard]
            setattr(self, attr, getattr(self, attr) + val)
            return attr, val
        elif choice == '花如簇':
            attr, val = self.rewards[choice][standard]
            setattr(self, attr, getattr(self, attr) + val)
            return attr, val
        return None, 0

    def run_event_cycle(self, ai_policy) -> Dict[str, any]:
        round_no = 0
        rethrow = False
        self.throw_money()

        while True:
            choice, sub_choice = ai_policy(sim)  # AI决策选择
            round_no += 1

            if choice != '茧成绢':
                if not rethrow:
                    print(f"Round_{round_no}:")
                    print(f"    剩余烛火：{self.candle}, 源石锭数量：{self.originium}, 票券数量：{self.tickets}, 藏品数量：{self.prize_count}")

                    # 1. 检查烛火
                    if self.candle < 1:
                        print(f"Round_{round_no}: 烛火不足，事件结束")
                        return {'success': False, 'reason': '烛火不足'}

                    # 2. 消耗烛火
                    self.candle -= 1

                    # 3. 确定并支付源石锭
                    self.standard = self.get_payment_standard(self.originium)

                    if self.standard is None:
                        print(f"Round_{round_no}: 源石锭不足最低标准，事件结束")
                        return {'success': False, 'reason': '源石锭不足支付最低标准'}

                else:
                    if self.originium >= self.standard:
                        self.standard = self.standard
                        rethrow = False
                    else:
                        rethrow = False
                        continue

                self.originium -= self.standard

                # 4. 投钱 & 判定
                throw_result = self.throw_money()
                success = self.check_success(choice, throw_result)
                print(f"    上缴 = {self.standard}, 选择 = {choice} · {sub_choice}, 投钱 = {throw_result}")

                if success:
                    reward_text = {
                        '衡如常': "源石锭", '花如簇': "藏品", '厉如锋': {
                            '要兵器一对': "藏品", '要书一卷': "票券", '要酒一壶': "烛火", None: None
                        }[sub_choice]
                    }[choice]

                    reward = self.apply_reward(choice, self.standard, sub_choice)
                    print(f"    天随人愿！返还 {reward[1]} {reward_text}")

                    # 达到300藏品直接退出
                    if self.prize_count >= 300:
                        return {'success': True, 'reason': '藏品达标'}

                else:
                    # 失败：是否继续
                    if random.random() < self.stay_prob and self.originium >= self.standard:
                        rethrow = True
                        print(f"    失败但触发停留，重新支付 {self.standard} 源石锭")
                    else:
                        print(f"    失败且未继续，事件结束")

            else:
                print(f"Round_{round_no}:")
                print(f"    剩余烛火：{self.candle}, 源石锭数量：{self.originium}, 票券数量：{self.tickets}, 藏品数量：{self.prize_count}")

                self.tickets -= self.ticket_cost
                print(f"    茧成绢事件：消耗 {self.ticket_cost} 票券")

                if random.random() < self.throw_count / len(self.money_box):
                    res = self.silk_cocoon_return(self.originium)
                    self.originium += res
                    print(f"    天随人愿！返还 {res} 源石锭")

                else:
                    print(f"    不尽人意！事件结束。。。")

    def simulate_once(self, ai_policy) -> Dict[str, any]:
        return self.run_event_cycle(ai_policy)


if __name__ == "__main__":
    sim = EventSimulator()
    sim.set_initial_state(
        candle=5, originium=100, tickets=0,
        flower_money=1, balance_money=5, fierce_money=6,
        throw_count=5, ticket_cost=2, silk_cocoon=True,
        prize_count=0, stay_prob=0.6
    )

    policy = SmartPolicy()
    result = sim.simulate_once(policy)

    print("\n最终资源:")
    print(f"    烛火: {sim.candle}")
    print(f"    票券: {sim.tickets}")
    print(f"    源石锭: {sim.originium}")
    print(f"    藏品: {sim.prize_count}")
