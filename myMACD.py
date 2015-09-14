 # -*- encoding:UTF-8 -*-
#计算macd 函数

from WindPy import *
import xlrd
import numpy as np
import datetime
import time


class MACDApi:
    # (登陆的ID，第一个合约条款，第二个选填合约)
    def __init__(self,wapi,LogonID,var1,var2=None):
        dayOfWeek = date.today().weekday()
#         if dayOfWeek == 5 or dayOfWeek ==6:
#             self.__start_date = datetime.datetime.today() - datetime.timedelta(days=3)
#         else:
#             self.__start_date = datetime.datetime.today() - datetime.timedelta(days=1)
        self.__start_date = datetime.datetime(2015,9,9,9,0)
        self.__wapi = wapi
        self.__LogonID = LogonID
        self.__var1 = var1
        self.__var2 = var2
        self.__date_now = datetime.datetime.today()
        self.__long_term = 26
        self.__short_term = 12
        self.__standard_term = 9

     # 获得想要的收盘价(将一些脏数据过滤掉，例如'nan')
    def get_temp_close_value(self,path):
        data = xlrd.open_workbook(path).sheets()[0]
        time_col = data.col_values(0)[1:]                                   #获得时间列，返回一个数组
        time_value = []                                                      #将excel格式的时间转为datetime格式
        for i in range(len(time_col)):
            temp_time = xlrd.xldate_as_tuple(time_col[i],0)
            time_value.append(datetime.datetime(temp_time[0],temp_time[1],temp_time[2],temp_time[3],temp_time[4]))
        close_col = data.col_values(4)[1:]
        time_close_dict = {}                                             #声明一个时间和收盘价的对照表，用字典储存
        for i in range(len(time_value)):
            time_close_dict[time_value[i]] = close_col[i]
        return time_close_dict

    #筛选出开始时间之后的值
    def filter_value_by_time(self,date):
        return date >= self.__start_date

    # 对excel表格的数据进行处理
    def get_close_value(self):
        if self.__var2 == None:
            time_value = filter(self.filter_value_by_time,self.get_temp_close_value('data/'+self.__var1.split('.')[0] + '.xlsx').keys())
            time_value.sort()
            print time_value
            time_close_dict = self.get_temp_close_value('data/'+self.__var1.split('.')[0] + '.xlsx')
            result_list = []
            for item in time_value:
                result_list.append(time_close_dict[item])
            return result_list
        else:
            time_close_dict1 = self.get_temp_close_value('data/'+self.__var1.split('.')[0] + '.xlsx')
            time_close_dict2 = self.get_temp_close_value('data/'+self.__var2.split('.')[0] + '.xlsx')
            time_value1 = time_close_dict1.keys()
            time_value2 = time_close_dict2.keys()
            time_value_in_common = list(set(time_value1).intersection(set(time_value2)))
            time_value_in_common = filter(self.filter_value_by_time,time_value_in_common)
            time_value_in_common.sort()
            result_list = []
            for item in time_value_in_common:
                result_list.append(round(time_close_dict1[item] - time_close_dict2[item] , 2))
            return result_list

    # 得到当前时间（分钟）的价格
    def get_price(self):
        return self.get_close_value()[-1:]

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

    # 得出交易的大小
    def do_operate(self):
        m_DIF = self.cal_DIF()
        m_DEA = self.cal_DEA()
        m_MACD = self.cal_MACD()
        # 金叉信号，DIF向上突破DEA，买入信号
        # 死叉信号，DIF向下跌破DEA，卖出信号
        if m_DIF[-1:] > m_DEA[-1:] :
            if self.__var2 == None:
                price = w.wsq([self.__var1],'rt_last').Data[0]
                self.__wapi.tOrder([self.__var1],'buy',price,10,logonId=self.__LogonID)
            else:
                price = w.wsq([self.__var1,self.__var2],'rt_last').Data[0]
                self.__wapi.tOrder([self.__var1,self.__var2],'buy',price,10,logonId=self.__LogonID)
        if m_DIF[-1:] < m_DEA[-1:] :
            if self.__var2 == None:
                price = w.wsq([self.__var1],'rt_last').Data[0]
                self.__wapi.tOrder([self.__var1],'sale',price,10,logonId=self.__LogonID)
            else:
                price = w.wsq([self.__var1,self.__var2],'rt_last').Data[0]
                self.__wapi.tOrder([self.__var1,self.__var2],'sale',price,10,logonId=self.__LogonID)

    # 判断是否是交易日的交易时间
    def is_trade_time(self):
        dayOfWeek = datetime.datetime.today().weekday()
        current_hour = datetime.datetime.now().hour
        if dayOfWeek == 5 or dayOfWeek == 6:
            return False
        elif (current_hour < 11 and current_hour > 9) or (current_hour>13 and current_hour<15):
            return True
        else:
            return False

    # 做出交易
    def make_trade(self):
        while True:
            #if self.is_trade_time():
            print 'make trade'
            self.do_operate()
            time.sleep(60)




