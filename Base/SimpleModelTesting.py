# 简单百分比量化模型回测-使用说明
# Author: SkyStar
# 2020.12.01
#
# 调取方法顺序：
# 1. 初始化对象。
# 2. 以自然数为index输入所需要的回测历史数据。(均以npArray形式传入，价格dType默认为float)
# 3. 以自然数为index传入对应的买/卖位置，最终的买卖位置不能超过历史数据的max。
# 4. 更新模型。
# 5. 调取所需回测数据。
#
# 注：
# 返回为收益结果(npArray数组形式)、收益结果(收益曲线图)、最大回撤(float)、最终收益(float)、持仓情况(投入的原始资金的总数变化情况)、总买卖额。
# 每次购买和出售需要提供量(正数)


# 依赖库导入
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append('..')
from MathUtils import MathUtils


class SimpleModelTesting:

    def __init__(self):

        # list形式记录历史价格，dType默认为float
        self.history_price = []
        # list形式记录选择买卖位置，dType默认为 0 , 1(isBuy) , 2(not isBuy)
        self.choose_position = []
        # list形式记录买卖量，dType默认为float
        self.choose_amount = []
        # npArray形式记录持仓额(会被整体覆盖)
        self.capital = np.array([])
        # npArray形式记录累计收益额(会被整体覆盖)
        self.sum_return = np.array([])
        # npArray形式记录收益额(会被整体覆盖)
        self.capital_return = np.array([])
        # 记录最大回撤及最终收益(会被覆盖)
        self.max_draw_down = 0
        self.final_return = 0
        # float记录总买卖额(会被整体覆盖)
        self.total_amount = 0

    # 清理现存的数据，重新开始
    def clear(self):

        # list形式记录历史价格，dType默认为float
        self.history_price = []
        # list形式记录选择买卖位置，dType默认为 0 , 1(isBuy) , 2(not isBuy)
        self.choose_position = []
        # list形式记录买卖量，dType默认为float
        self.choose_amount = []
        # npArray形式记录持仓额(会被整体覆盖)
        self.capital = np.array([])
        # npArray形式记录累计收益额(会被整体覆盖)
        self.sum_return = np.array([])
        # npArray形式记录收益额(会被整体覆盖)
        self.capital_return = np.array([])
        # 记录最大回撤及最终收益(会被覆盖)
        self.max_draw_down = 0
        self.final_return = 0
        # float记录总买卖额(会被整体覆盖)
        self.total_amount = 0

    # 添加一条历史数据，按顺序添加
    def add_history(self, price: float):

        self.history_price.append(price)

    # 添加一条买卖标志，index可跳跃或改变顺序，亦可覆盖
    def add_choose_position(self, is_buy: bool, position: int, amount: float):

        # 不检查hold是否充足，在update时再进行检查，但检查amount是否为非负数
        if MathUtils.double_compare(amount, 0) < 0:
            print("Error! Amount can't be smaller than 0!")
            return

        # 若两数组长度不够，则用 0 补齐长度
        if len(self.choose_position) <= position:
            for i in range(position - len(self.choose_position) + 1):
                self.choose_position.append(0)
                self.choose_amount.append(0)

        # 在对应的位置上加上标记及amount
        if is_buy:
            self.choose_position[position] = 1
        else:
            self.choose_position[position] = 2
        self.choose_amount[position] = amount

    def update(self):

        # 若标记的长度比历史数据更长，则无法回测并报错
        if len(self.history_price) < len(self.choose_position):
            print('Error! The length of choose_position is larger than that of history_price!')
            return

        # 若标记的长度比历史数据更短，则用0补齐标记数组及amount数组使之与历史数据长度一致
        if len(self.history_price) > len(self.choose_position):
            for i in range(len(self.history_price) - len(self.choose_position)):
                self.choose_position.append(0)
                self.choose_amount.append(0)

        real_capital = 0
        now_hold = 0
        capital = []
        capital_return = []

        for t in range(len(self.history_price)):
            if t > 0:
                capital_return.append(now_hold * (self.history_price[t] - self.history_price[t - 1]))
            if t == 0:
                capital_return.append(0)

            self.total_amount = self.total_amount + self.choose_amount[t]

            if self.choose_position[t] == 1:
                now_hold = now_hold + self.choose_amount[t]
                real_capital = real_capital + self.choose_amount[t] * self.history_price[t]
            if self.choose_position[t] == 2:
                real_capital = real_capital * ((now_hold - self.choose_amount[t]) / now_hold)
                if MathUtils.double_compare(now_hold - self.choose_amount[t], 0) < 0:
                    print("Error! Hold can't be smaller than 0!")
                now_hold = now_hold - self.choose_amount[t]
            capital.append(real_capital)

        max_draw_down = -float("inf")
        temp_sum_return = [capital_return[0]]

        for i in range(1, len(capital_return)):
            temp = temp_sum_return[i - 1] + capital_return[i]
            if MathUtils.double_compare(-temp, max_draw_down) > 0:
                max_draw_down = -temp
            temp_sum_return.append(temp)

        self.sum_return = np.array(temp_sum_return)
        self.capital = np.array(capital)
        self.capital_return = np.array(capital_return)
        self.max_draw_down = max_draw_down
        self.final_return = self.sum_return[-1]

    def get_sum_return_array(self) -> np.ndarray:
        return self.sum_return

    def plot_sum_return(self):
        plt.plot(self.sum_return)
        plt.xlabel("time")
        plt.ylabel("return")
        plt.grid(True)
        plt.axis('tight')
        plt.title("cumulative return")
        plt.show()
        plt.close()

    def get_max_draw_down(self) -> float:
        return self.max_draw_down

    def get_final_return(self) -> float:
        return self.final_return

    def get_total_amount(self) -> float:
        return self.total_amount

    def plot_self_capital(self):
        plt.plot(self.capital)
        plt.xlabel("time")
        plt.ylabel("capital")
        plt.grid(True)
        plt.axis('tight')
        plt.title("original investment fund")
        plt.show()
        plt.close()


# 测试用例
'''
# 设定输入的模拟数据
price = [4.5, 3.5, 3.3, 3.7, 4.2, 4.3, 3.6, 4.0, 4.5, 5.0]
choose_pos = [1, 2, 4, 6, 9]
choose_buy = [True, True, False, False, False]
choose_amount = [200, 300, 100, 200, 200]

# 初始化对象并传入模拟数据回测
stock = SimpleModelTesting()
for i in range(len(price)):
    stock.add_history(price[i])
for i in range(len(choose_pos)):
    stock.add_choose_position(choose_buy[i],choose_pos[i],choose_amount[i])
stock.update()

# 获得回测结果并输出
stock.plot_sum_return()
stock.plot_self_capital()
print("最终收益 = "+str(stock.get_final_return()))
print("最大回撤 = "+str(stock.get_max_draw_down()))
print("总买卖量 = "+str(stock.get_total_amount()))
'''
