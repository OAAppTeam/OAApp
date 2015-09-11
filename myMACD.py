 # -*- encoding:UTF-8 -*-
#计算macd 函数

import xlrd
from WindPy import *
import datetime
import numpy as np
import matplotlib as plt
import math

def is_nan(x):
    return math.isnan(float(x))


class MACDApi:
    # 传入一个起始时间参数,一个合约条款，一个选填合约，excel表格的路径
    def __init__(self,start_date,var1,var2=None):
        # w.start()
        self.__start_date = datetime.datetime.strptime(start_date,"%Y-%m-%d %H:%M:%S")
        self.__var1 = var1
        self.__var2 = var2
        self.__date_now = date.today()
        self.__long_term = 26
        self.__short_term = 12
        self.__standard_term = 9

     # 获得想要的收盘价(将一些脏数据过滤掉，例如'nan')
    def get_close_value(self):
        table = xlrd.open_workbook(self.__var1+".xlsx").sheets()[0]
        result_list = []
        time_col = table.col_values(0)[1:]
        close_col = table.col_values(4)[1:]
        time = []
        for i in range(len(time_col)):
            temp = xlrd.xldate_as_tuple(time_col[i],0)
            time.append(datetime.datetime(temp[0],temp[1],temp[2],temp[3],temp[4]))
        # 根据时间来筛选数据
        for j in range(len(time_col)):
            if self.__start_date > time[j]:
                j = j + 1
            else:
                break
        return close_col[j:]

    # 获得到今天为止长期（26）天的 ema
    def cal_longterm_EMA(self):
        close_value_list = self.get_close_value()
        result_list = []
        avg = np.average(close_value_list[:26])
        result_list.append(avg)
        for i in range(len(close_value_list) - 26):
            temp = float(close_value_list[i+26]*2/27) + float(result_list[i]*25/27)
            result_list.append(temp)
        return result_list

    # 获得到今天为止的短期（12）天的 ema
    def cal_shortterm_EMA(self):
        close_value_list = self.get_close_value()
        result_list = []
        avg = np.average(close_value_list[:12])
        result_list.append(round(avg,2))
        for i in range(len(close_value_list) - 12):
            temp = float(close_value_list[i+12])*2/13 + float(result_list[i])*11/13
            result_list.append(temp)
        return result_list

    # 获得今天为止的 macd 值
    def cal_DIF(self):
        short_term_EMA = self.cal_shortterm_EMA()
        long_term_EMA = self.cal_longterm_EMA()
        result_list = []
        for i in range(len(long_term_EMA)):
            result_list.append(short_term_EMA[i+14] - long_term_EMA[i])
        return result_list

    # 获得今天为止的DEA
    def cal_DEA(self):
        DEA_value = self.cal_DIF()
        result_list = []
        avg = np.average(DEA_value[:9])
        result_list.append(avg)
        for i in range(len(DEA_value) - 9):
            temp = DEA_value[i+9]*2/10 + result_list[i]*8/10
            result_list.append(temp)
        return result_list

     # 计算单个期货的macd值
    def cal_MACD(self):
        DIF_value = self.cal_DIF()
        DEA_value = self.cal_DEA()
        result_list = []
        for i in range(len(DEA_value)):
            temp = DIF_value[i+8] - DEA_value[i]
            result_list.append(temp)
        return result_list

    # 做出交易决定
    def do_operate(self):
        operate = 0
        m_DIF = self.cal_DIF()
        m_DEA = self.cal_DEA()
        m_MACD = self.cal_MACD()
        # 金叉信号，DIF向上突破DEA，买入信号
        # 死叉信号，DIF向下跌破DEA，卖出信号
        for i in range(len(m_MACD)):
            if m_DIF[i] > 0 and m_DEA[i] > 0 and m_DIF[i] > m_DEA[i] :
                operate = operate + 10
            if m_DIF[i] < 0 and m_DEA[i] < 0 and m_DIF[i] < m_DEA[i] :
                operate = operate - 10
        return operate

macd = MACDApi("2015-09-11 9:00:00","IF1509")
print macd.get_close_value()



