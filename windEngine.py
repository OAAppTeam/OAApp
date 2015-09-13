# encoding: UTF-8
__author__ = 'Justin'

import shelve
from windApi import *

class MainEngine:

    def __init__(self):
        self.ee = EventEngine()
        self.wa = WindApi(self.ee)
        self.wa.start()
        self.ee.start()

        # 循环查询持仓和账户相关
        self.countGet = 0               # 查询延时计数
        self.lastGet = 'Account'        # 上次查询的性质
        self.ee.register(EVENT_TLOGON, self.initGet)  # 登录成功后开始初始化查询

        # 合约储存相关
        self.dictInstrument = {}        # 字典（保存合约查询数据）
        # self.ee.register(EVENT_INSTRUMENT, self.insertInstrument)

    def getLogonId(self):
        data = self.wa.tQuery('LogonID')
        return str(data.Data[0][0])

    def getAccount(self):
        '''查询账户'''
        LogonId = self.getLogonId()
        self.wa.tQuery("Account","LogonId=" + LogonId)

    def getCapital(self):
        '''查询资金'''
        LogonId = self.getLogonId()
        self.wa.tQuery("Capital","LogonId=" + LogonId)

    def getPosition(self):
        '''查询持仓'''
        LogonId = self.getLogonId()
        self.wa.tQuery("Position","LogonId=" + LogonId)

    def getAccountPosition(self, event):
        """循环查询账户和持仓"""
        self.countGet = self.countGet + 1

        # 每5秒发一次查询
        if self.countGet > 5:
            self.countGet = 0   # 清空计数

            if self.lastGet == 'Account':
                self.getPosition()#查询持仓
                self.lastGet = 'Position'
            else:
                self.getAccount() #查询账户
                self.lastGet = 'Account'

    #----------------------------------------------------------------------
    def initGet(self, event):
        """在交易服务器登录成功后，开始初始化查询"""
        # 如果本地保存的合约数据是今日的，则载入，否则发出查询请求

        # 开始循环查询
        self.ee.register(EVENT_TIMER, self.getAccountPosition)

        event = Event(type_=EVENT_LOG)
        log = u'合约信息查询'
        event.dict_['log'] = log
        self.ee.put(event)
        
    def exit(self):
        """退出"""
        # 销毁API对象
        self.wa = None

        # 停止事件驱动引擎
        self.ee.stop()

    def saveInstrument(self):
        """保存合约属性数据"""
        f = shelve.open('setting.vn')
        d = {}
        d['dictInstrument'] = self.dictInstrument
        d['date'] = date.today()
        f['instrument'] = d
        f.close()
        
        
        