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
        # self.ee.register(EVENT_TLOGON, self.initGet)  # 登录成功后开始初始化查询

        # 合约储存相关
        self.dictInstrument = {}        # 字典（保存合约查询数据）
        # self.ee.register(EVENT_INSTRUMENT, self.insertInstrument)

    def getAccount(self):
        '''查询账户'''
        self.wa.tQuery(5)

    def getCapital(self):
        '''查询资金'''
        self.wa.tQuery(0)

    def getPosition(self):
        '''查询持仓'''
        self.wa.tQuery(1)

    #----------------------------------------------------------------------
    def initGet(self, event):
        """在交易服务器登录成功后，开始初始化查询"""
        # 打开设定文件setting.vn
        f = shelve.open('setting.vn')

        # 尝试读取设定字典，若该字典不存在，则发出查询请求
        try:
            d = f['instrument']

            # 如果本地保存的合约数据是今日的，则载入，否则发出查询请求
            today = date.today()
            if d['date'] == today:
                self.dictInstrument = d['dictInstrument']

                event = Event(type_=EVENT_LOG)
                log = u'合约信息读取完成'
                event.dict_['log'] = log
                self.ee.put(event)

                self.getInvestor()

                # 开始循环查询
                self.ee.register(EVENT_TIMER, self.getAccountPosition)
            else:
                self.getInstrument()
        except KeyError:
            self.getInstrument()

        f.close()
        
    def exit(self):
        self.wa.stop()
        self.ee.stop()
        
        
        