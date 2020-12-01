# 简单百分比量化模型回测-使用说明
# Author: SkyStar
# 2020.12.01
#
# 调取方法顺序：
# 1. 初始化对象。
# 2. 以自然数为index输入所需要的回测历史数据。(均以npArray形式传入，价格dType默认为float)
# 3. 以自然数为标志传入对应的买/卖位置。
# 4. 更新模型。
# 5. 调取所需回测数据。
#
# 注：
# 返回为收益结果(npArray数组形式)、收益结果(收益曲线图)、最大回撤(float)、最终收益(float)。
# 每次购买和出售需要提供量(正数)



# 依赖库导入
import numpy as np
import sys
sys.path.append('..')
from MathUtils import Math_Utils



class Simple_Model_Testing:

    #相关类变量
    isBuy = True


    def __init__(self):

        # list形式记录历史价格，dType默认为float
        self.history_price = []
        # list形式记录选择买卖位置，dType默认为True(isBuy)/False
        self.choose_position = []
        # self.hold记录所持有的仓位
        self.hold=0



    def add_history(self, price: float):

        self.history_price.append(price)



    def add_choose_position(self, is_buy: bool, position: int, amount: float):

        # 若为卖出而持仓不够则拒绝标记为sell
        if (not is_buy):
            if (Math_Utils.double_compare(self.hold-amount,0)<0):
                print("Error! Hold is not enough, can't sell!")
                return



