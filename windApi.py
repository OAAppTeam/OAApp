# encoding: UTF-8
__author__ = 'Justin'

from WindPy import *
from eventEngine import *

class WindApi:

    def __init__(self, eventEngine):
        self.__eventEngine = eventEngine

    # 开启
    def start(self):
        w.start()

    # 停止
    def stop(self):
        w.stop()

    # 判断是否连接
    def isConnected(self):
        return w.isconnected()

    # 取消订阅
    def cancelSubscribe(self, id):
        w.cancelRequest(id)

    # 获取历史序列数据
    def getHistorySequenceData(self, security, fields, startDate, endDate, **option):
        data = w.wsd(security, fields, startDate, endDate, **option)
        event = Event(type_=EVENT_HISTORYSEQUENCEDATA)
        event.dict_['data'] = data
        self.__eventEngine.put(event)

    # 获取分钟数据
    def getMinuteData(self, security, fields, startTime, endTime, **option):
        data = w.wsi(security, fields, startTime, endTime, **option)
        event = Event(type_=EVENT_MINUTEDATA)
        event.dict_['data'] = data
        self.__eventEngine.put(event)

    # 获取日内tick级别数据
    def getTickData(self, security, fields, startTime, endTime, **option):
        data = w.wst(security, fields, startTime, endTime, **option)
        event = Event(type_=EVENT_TICKDATA)
        event.dict_['data'] = data
        self.__eventEngine.put(event)

    # 获取历史截面数据
    def getHistorySectionData(self, security, fields, **option):
        data = w.wss(security, fields, **option)
        event = Event(type_=EVENT_HISTORYSECTIONDATA)
        event.dict_['data'] = data
        self.__eventEngine.put(event)

    # 获取和订阅实时行情数据
    def subscribe(self, security, fields):
        w.wsq(security, fields, func=self.onSubscribe)

    def onSubscribe(self, indata):
        event = Event(type_=EVENT_MARKETDATA)
        event.dict_['data'] = indata
        self.__eventEngine.put(event)

    # 获取板块、指数等成分数据
    def getMemberData(self):
        pass

    # 获取条件选股结果
    def getConditionalSelectStock(self):
        pass

    # 获取资产管理、组合管理数据
    def getManageData(self):
        pass

    # 交易相关函数

    #交易登录
    def tLogon(self, brokerId, departmentId, accountId, password, accountType):
        w.tlogon(brokerId, departmentId, accountId, password, accountType)

    # 交易登出
    def tLogout(self):
        w.tlogout()

    # 委托下单
    def tOrder(self, securityCode, tradeSide, orderPrice, orderVolume, **option):
        w.torder(securityCode, tradeSide, orderPrice, orderVolume, **option)

    # 撤销委托
    def tCancel(self, orderNum, **option):
        w.tcancel(orderNum, **option)

    # 交易查询
    def tQuery(self, qryCode, **option):
        w.tquery(qryCode, **option)

    # 日期函数

    # 返回区间内日期序列
    def getDateSequence(self):
        pass

    # 返回偏移值对应日期
    def getDateOffset(self):
        pass

    # 返回某个区间内日期数量
    def getDateNum(self):
        pass

