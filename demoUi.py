# encoding: UTF-8

"""
该文件中包含的是交易平台的上层UI部分，
通过图形界面调用中间层的主动函数，并监控相关数据更新。

Monitor主要负责监控数据，有部分包含主动功能。
Widget主要用于调用主动功能，有部分包含数据监控。
"""

from __future__ import division

import time
import sys
import shelve
from collections import OrderedDict

import time
import sip
from PyQt4 import QtCore, QtGui

from eventEngine import *
from matplotlib.transforms import offset_copy



########################################################################
class LogMonitor(QtGui.QTableWidget):
    """用于显示日志"""
    signal = QtCore.pyqtSignal(type(Event()))

    #----------------------------------------------------------------------
    def __init__(self, eventEngine, parent=None):
        """Constructor"""
        super(LogMonitor, self).__init__(parent)
        self.__eventEngine = eventEngine

        self.initUi()
        self.registerEvent()

    #----------------------------------------------------------------------
    def initUi(self):
        """初始化界面"""
        self.setWindowTitle(u'日志')

        self.setColumnCount(2)                     
        self.setHorizontalHeaderLabels([u'时间', u'日志'])

        self.verticalHeader().setVisible(False)                 # 关闭左边的垂直表头
        self.setEditTriggers(QtGui.QTableWidget.NoEditTriggers) # 设为不可编辑状态

        # 自动调整列宽
        self.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)        

    #----------------------------------------------------------------------
    def registerEvent(self):
        """注册事件监听"""
        # Qt图形组件的GUI更新必须使用Signal/Slot机制，否则有可能导致程序崩溃
        # 因此这里先将图形更新函数作为Slot，和信号连接起来
        # 然后将信号的触发函数注册到事件驱动引擎中
        self.signal.connect(self.updateLog)
        self.__eventEngine.register(EVENT_LOG, self.signal.emit)

    #----------------------------------------------------------------------
    def updateLog(self, event):
        """更新日志"""
        # 获取当前时间和日志内容
        t = time.strftime('%H:%M:%S',time.localtime(time.time()))   
        log = event.dict_['log']                                    

        # 在表格最上方插入一行
        self.insertRow(0)              

        # 创建单元格
        cellTime = QtGui.QTableWidgetItem(t)    
        cellLog = QtGui.QTableWidgetItem(log)

        # 将单元格插入表格
        self.setItem(0, 0, cellTime)            
        self.setItem(0, 1, cellLog)


########################################################################
class AccountMonitor(QtGui.QTableWidget):
    """用于显示账户"""
    signal = QtCore.pyqtSignal(type(Event()))

    dictLabels = OrderedDict()
    dictLabels['AssetAccount'] = u'投资者账户'
    dictLabels['AvailableFund'] = u'可用资金'
    dictLabels['BalanceFund'] = u'资金余额'
    dictLabels['FetchFund'] = u'可取资金'
    dictLabels['ExerciseMargin'] = u'履约保证金'
    dictLabels['RealFrozenMarginA'] = u'开仓预冻结金额'
    dictLabels['RealFrozenMarginB'] = u'开仓预冻结保证金和费用'
    dictLabels['FrozenFare'] = u'冻结费用'
    dictLabels['CustomerMargin'] = u'客户保证金'
    dictLabels['Interest'] = u'预计利息'

    #----------------------------------------------------------------------
    def __init__(self, eventEngine, parent=None):
        """Constructor"""
        super(AccountMonitor, self).__init__(parent)
        self.__eventEngine = eventEngine

        self.dictAccount = {}	    # 用来保存账户对应的单元格

        self.initUi()
        self.registerEvent()

    #----------------------------------------------------------------------
    def initUi(self):
        """"""
        self.setWindowTitle(u'账户')

        self.setColumnCount(len(self.dictLabels))
        self.setHorizontalHeaderLabels(self.dictLabels.values())

        self.verticalHeader().setVisible(False)                 # 关闭左边的垂直表头
        self.setEditTriggers(QtGui.QTableWidget.NoEditTriggers) # 设为不可编辑状态	

    #----------------------------------------------------------------------
    def registerEvent(self):
        """"""
        self.signal.connect(self.updateAccount)
        self.__eventEngine.register(EVENT_ACCOUNT, self.signal.emit)

    #----------------------------------------------------------------------
    def updateAccount(self, event):
        """"""
        data = event.dict_['data']
        fields = data.Fields
        datas = data.Data
        
        accountid = datas[fields.index('AssetAccount')][0]

        # 如果之前已经收到过这个账户的数据, 则直接更新
        if accountid in self.dictAccount:
            d = self.dictAccount[accountid]

            for label, cell in d.items():
                if label in fields:
                    cell.setText(unicode(datas[fields.index(label)][0]))
        # 否则插入新的一行，并更新
        else:
            self.insertRow(0)
            d = {}

            for col, label in enumerate(self.dictLabels.keys()):
                if label in fields:
                    cell = QtGui.QTableWidgetItem(unicode(datas[fields.index(label)][0]))
                    self.setItem(0, col, cell)
                    d[label] = cell

            self.dictAccount[accountid] = d


########################################################################
class TradeMonitor(QtGui.QTableWidget):
    """用于显示成交记录"""
    signal = QtCore.pyqtSignal(type(Event()))

    dictLabels = OrderedDict()
    dictLabels['InstrumentID'] = u'合约代码'
    dictLabels['ExchangeInstID'] = u'交易所合约代码'
    dictLabels['ExchangeID'] = u'交易所'
    dictLabels['Direction'] = u'方向'   
    dictLabels['OffsetFlag'] = u'开平'
    dictLabels['TradeID'] = u'成交编号'
    dictLabels['TradeTime'] = u'成交时间'
    dictLabels['Volume'] = u'数量'
    dictLabels['Price'] = u'价格'
    dictLabels['OrderRef'] = u'报单号'
    dictLabels['OrderSysID'] = u'报单系统号'

    dictDirection = {}
    dictDirection['0'] = u'买'
    dictDirection['1'] = u'卖'
    dictDirection['2'] = u'ETF申购'
    dictDirection['3'] = u'ETF赎回'
    dictDirection['4'] = u'ETF现金替代'
    dictDirection['5'] = u'债券入库'
    dictDirection['6'] = u'债券出库'
    dictDirection['7'] = u'配股'
    dictDirection['8'] = u'转托管'
    dictDirection['9'] = u'信用账户配股'
    dictDirection['A'] = u'担保品买入'
    dictDirection['B'] = u'担保品卖出'
    dictDirection['C'] = u'担保品转入'
    dictDirection['D'] = u'担保品转出'
    dictDirection['E'] = u'融资买入'
    dictDirection['F'] = u'融资卖出'
    dictDirection['G'] = u'卖券还款'
    dictDirection['H'] = u'买券还券'
    dictDirection['I'] = u'直接还款'
    dictDirection['J'] = u'直接换券'
    dictDirection['K'] = u'余券划转'
    dictDirection['L'] = u'OF申购'    
    dictDirection['M'] = u'OF赎回'
    dictDirection['N'] = u'SF拆分'
    dictDirection['O'] = u'SF合并'
    dictDirection['P'] = u'备兑'
    dictDirection['Q'] = u'证券冻结/解冻'
    dictDirection['R'] = u'行权'      

    dictOffset = {}
    dictOffset['0'] = u'开仓'
    dictOffset['1'] = u'平仓'
    dictOffset['2'] = u'强平'
    dictOffset['3'] = u'平今'
    dictOffset['4'] = u'平昨'
    dictOffset['5'] = u'强减'
    dictOffset['6'] = u'本地强平'
    
    contractItem = {}
    contractItem['0'] = u'开仓'
    contractItem['1'] = u'平仓'
    contractItem['2'] = u'强平'
    contractItem['3'] = u'平今'
    contractItem['4'] = u'平昨'
    contractItem['5'] = u'强减'
    contractItem['6'] = u'本地强平'

    #----------------------------------------------------------------------
    def __init__(self, eventEngine, mainEngine, parent=None):
        """Constructor"""
        super(TradeMonitor, self).__init__(parent)
        self.__eventEngine = eventEngine
        self.__mainEngine = mainEngine
        self.dictTrade={}
        self.initUi()
        self.registerEvent()	

    #----------------------------------------------------------------------
    def initUi(self):
        """"""
        self.setWindowTitle(u'成交')

        self.setColumnCount(len(self.dictLabels))
        self.setHorizontalHeaderLabels(self.dictLabels.values())

        self.verticalHeader().setVisible(False)                 # 关闭左边的垂直表头
        self.setEditTriggers(QtGui.QTableWidget.NoEditTriggers) # 设为不可编辑状态	

    #----------------------------------------------------------------------
    def registerEvent(self):
        """"""
        self.signal.connect(self.updateTrade)
        self.__eventEngine.register(EVENT_TRADE, self.signal.emit)

    #----------------------------------------------------------------------
    def updateTrade(self):
        """"""       
        logonID = str(self.__mainEngine.wa.tQuery('LogonID').Data[0][0])
        tradeinfo = self.__mainEngine.wa.tQuery('Trade','LogonID='+logonID)
        print u'成交'
        print tradeinfo
        data = tradeinfo.Data
        field = tradeinfo.Fields
        ordernum = tradeinfo.Data[0]
        for i in range(0,len(ordernum)):
            onum  = ordernum[i]
            if onum in self.dictTrade:
                d = self.dictTrade[onum]
                for label, cell in d.items():
                    value=''
                    if label == 'InstrumentID'and 'SecurityCode' in field:
                        try:
                            k = field.index('SecurityCode')
                            value = data[k][i]
                        except KeyError:
                            value = u'未知类型'
                    elif label == 'ExchangeInstID'and 'SecurityName' in field:
                        try:
                            k = field.index('SecurityName')
                            value = data[k][i]
                        except KeyError:
                            value = u'未知类型'
                    elif label == 'ExchangeID':
                        try:
                            value = ''
                        except KeyError:
                            value = u'未知类型'
                    elif label == 'Direction'and 'TradeSide' in field:
                        try:
                            k = field.index('TradeSide')
                            value = data[k][i]
                            if value == 'BUY':
                                value = u'买'
                            elif value == 'SHORT':
                                value = u'卖'
                            elif value == 'COVER':
                                value = u'买'
                            elif value == 'SELL':
                                value = u'卖'
                            elif value == 'COVERTODAY':
                                value = u'买'
                            elif value == 'SELLTODAY':
                                value = u'卖'
                            else:
                                value = ''
                        except KeyError:
                            value = u'未知类型'
                    elif label == 'OffsetFlag'and 'TradeSide' in field:
                        try:
                            k = field.index('TradeSide')
                            value = data[k][i]
                            if value == 'BUY':
                                value = u'开仓'
                            elif value == 'SHORT':
                                value = u'开仓'
                            elif value == 'COVER':
                                value = u'平仓'
                            elif value == 'SELL':
                                value = u'平仓'
                            elif value == 'COVERTODAY':
                                value = u'平今仓'
                            elif value == 'SELLTODAY':
                                value = u'平今仓'
                            else:
                                value = ''
                        except KeyError:
                            value = u'未知类型'
                    elif label == 'TradeID'and 'TradedNumber' in field:
                        try:
                            k = field.index('TradedNumber')
                            value = data[k][i]
                        except KeyError:
                            value = u'未知类型'        
                    elif label == 'TradeTime'and 'TradedTime' in field:
                        try:
                            k = field.index('TradedTime')
                            value = str(data[k][i])
                        except KeyError:
                            value = u'未知类型'
                    elif label == 'Volume'and 'TradedVolume' in field:
                        try:
                            k = field.index('TradedVolume')
                            value = data[k][i]

                        except KeyError:
                            value = u'未知类型'
                    elif label == 'Price'and 'TradedPrice' in field:
                        try:
                            k = field.index('TradedPrice')
                            value = data[k][i]
                        except KeyError:
                            value = u'未知类型'        
                    elif label == 'OrderRef'and 'OrderNumber' in field:
                        try:
                            k = field.index('OrderNumber')
                            value = data[k][i]
                        except KeyError:
                            value = u'未知类型'
                    elif label == 'OrderSysID':
                        try:
                            value =''
                        except KeyError:
                            value = u'未知类型'
                 
                    cell.setText(value)   
            else:
                self.insertRow(0)
                d={}
                for col, label in enumerate(self.dictLabels.keys()):
                    value=''
                    if label == 'InstrumentID'and 'SecurityCode' in field:
                        try:
                            k = field.index('SecurityCode')
                            value = data[k][i]
                        except KeyError:
                            value = u'未知类型'
                    elif label == 'ExchangeInstID' and 'SecurityName' in field:
                        try:
                            
                            k = field.index('SecurityName')
                            value = data[k][i]
                            
                        except KeyError:
                            value = u'未知类型'
                    elif label == 'ExchangeID'and 'SecurityName' in field:
                        try:
                            value = ''
                        except KeyError:
                            value = u'未知类型'
                    elif label == 'Direction'and 'TradeSide' in field:
                        try:
                            
                            k = field.index('TradeSide')
                            value = data[k][i]
                            if value == 'Buy':
                                value = u'买'
                            elif value == 'Short':
                                value = u'卖'
                            elif value == 'Cover':
                                value = u'买'
                            elif value == 'SELL':
                                value = u'卖'
                            elif value == 'CoverToday':
                                value = u'买'
                            elif value == 'SellToday':
                                value = u'卖'
                            else:
                                value = ''
                        except KeyError:
                            value = u'未知类型'
                    elif label == 'OffsetFlag'and 'TradeSide' in field:
                        try:
                            
                            k = field.index('TradeSide')
                            value = data[k][i]
                            if value == 'Buy':
                                value = u'开仓'
                            elif value == 'Short':
                                value = u'开仓'
                            elif value == 'Cover':
                                value = u'平仓'
                            elif value == 'Sell':
                                value = u'平仓'
                            elif value == 'CoverToday':
                                value = u'平今仓'
                            elif value == 'SellToday':
                                value = u'平今仓'
                            else:
                                value = ''
                        except KeyError:
                            value = u'未知类型'
                    elif label == 'TradeID'and 'TradedNumber' in field:
                        try:                           
                            k = field.index('TradedNumber')
                            value = data[k][i]
                        except KeyError:
                            value = u'未知类型'        
                    elif label == 'TradeTime'and 'TradedTime' in field:
                        try:
                            k = field.index('TradedTime')
                            value = str(data[k][i])
                                
                        except KeyError:
                            value = u'未知类型'
                    elif label == 'Volume'and 'TradedVolume' in field:
                        try:
                            k = field.index('TradedVolume')
                            value = str(data[k][i])
                        except KeyError:
                            value = u'未知类型'
                    elif label == 'Price'and 'TradedPrice' in field:
                        try:
                            
                            k = field.index('TradedPrice')
                            value = str(data[k][i])
                            
                        except KeyError:
                            value = u'未知类型'        
                    elif label == 'OrderRef'and 'OrderNumber' in field:
                        try:
                            k = field.index('OrderNumber')
                            value = data[k][i]
                        except KeyError:
                            value = u'未知类型'
                    elif label == 'OrderSysID':
                        try:
                            value =''
                        except KeyError:
                            value = u'未知类型'
                    else:
                        value=''
        
                    cell = QtGui.QTableWidgetItem(value)
                    self.setItem(0, col, cell)
                    d[label] = cell
                    self.dictTrade[onum] = d

########################################################################
class PositionMonitor(QtGui.QTableWidget):
    """用于显示持仓"""
    signal = QtCore.pyqtSignal(type(Event()))

    dictLabels = OrderedDict()
    dictLabels['SecurityName'] = u'交易品种名称'
    dictLabels['CostPrice'] = u'成本价'
    dictLabels['LastPrice'] = u'最新价'
    dictLabels['TradeSide'] = u'买/卖'
    dictLabels['BeginVolume'] = u'期初数量'
    dictLabels['EnableVolume'] = u'可用数量'
    dictLabels['TodayRealVolume'] = u'当日可平仓数量'
    dictLabels['TodayOpenVolume'] = u'当日开仓可用数量'
    dictLabels['HoldingProfit'] = u'盯市盈亏'
    dictLabels['TotalFloatProfit'] = u'持仓浮动盈亏'
    dictLabels['PreMargin'] = u'上交易日保证金'

    #----------------------------------------------------------------------
    def __init__(self, eventEngine, parent=None):
        """Constructor"""
        super(PositionMonitor, self).__init__(parent)
        self.__eventEngine = eventEngine

        self.dictPosition = {}	    # 用来保存持仓对应的单元格

        self.initUi()
        self.registerEvent()

    #----------------------------------------------------------------------
    def initUi(self):
        """"""
        self.setWindowTitle(u'持仓')

        self.setColumnCount(len(self.dictLabels))
        self.setHorizontalHeaderLabels(self.dictLabels.values())

        self.verticalHeader().setVisible(False)                 # 关闭左边的垂直表头
        self.setEditTriggers(QtGui.QTableWidget.NoEditTriggers) # 设为不可编辑状态	

    #----------------------------------------------------------------------
    def registerEvent(self):
        """"""
        self.signal.connect(self.updatePosition)
        self.__eventEngine.register(EVENT_POSITION, self.signal.emit)

    #----------------------------------------------------------------------
    def updatePosition(self, event):
        """"""
        data = event.dict_['data']
        fields = data.Fields
        datas = data.Data
        # 过滤返回值为空的情况
        posid = datas[fields.index('SecurityName')][0] + '.' + datas[fields.index('TradeSide')][0]

        # 如果之前已经收到过这个账户的数据, 则直接更新
        if posid in self.dictPosition:
            d = self.dictPosition[posid]

            for label, cell in d.items():
                if label in fields:
                    value = unicode(datas[fields.index(label)][0])
                    cell.setText(value)
        # 否则插入新的一行，并更新
        else:
            self.insertRow(0)
            d = {}

            for col, label in enumerate(self.dictLabels.keys()):
                if label in fields:
                    cell = QtGui.QTableWidgetItem(datas[fields.index(label)][0])
                    self.setItem(0, col, cell)
                    d[label] = cell

            self.dictPosition[posid] = d


########################################################################
class OrderMonitor(QtGui.QTableWidget):
    """用于显示所有报单"""
    signal = QtCore.pyqtSignal(type(Event()))

    dictLabels = OrderedDict()
    dictLabels['OrderRef'] = u'报单号'
    dictLabels['OrderSysID'] = u'系统编号'
    dictLabels['InstrumentID'] = u'合约代码'
    dictLabels['ExchangeInstID'] = u'交易所合约代码'   
    dictLabels['Direction'] = u'方向'
    dictLabels['CombOffsetFlag'] = u'开平'
    dictLabels['LimitPrice'] = u'价格'
    dictLabels['VolumeTotalOriginal'] = u'委托数量'
    dictLabels['VolumeTraded'] = u'成交数量'
    dictLabels['InsertTime'] = u'委托时间'
    dictLabels['CancelTime'] = u'撤销时间'
    dictLabels['StatusMsg'] = u'状态信息'

    dictDirection = {}
    dictDirection['0'] = u'买'
    dictDirection['1'] = u'卖'
    dictDirection['2'] = u'ETF申购'
    dictDirection['3'] = u'ETF赎回'
    dictDirection['4'] = u'ETF现金替代'
    dictDirection['5'] = u'债券入库'
    dictDirection['6'] = u'债券出库'
    dictDirection['7'] = u'配股'
    dictDirection['8'] = u'转托管'
    dictDirection['9'] = u'信用账户配股'
    dictDirection['A'] = u'担保品买入'
    dictDirection['B'] = u'担保品卖出'
    dictDirection['C'] = u'担保品转入'
    dictDirection['D'] = u'担保品转出'
    dictDirection['E'] = u'融资买入'
    dictDirection['F'] = u'融资卖出'
    dictDirection['G'] = u'卖券还款'
    dictDirection['H'] = u'买券还券'
    dictDirection['I'] = u'直接还款'
    dictDirection['J'] = u'直接换券'
    dictDirection['K'] = u'余券划转'
    dictDirection['L'] = u'OF申购'    
    dictDirection['M'] = u'OF赎回'
    dictDirection['N'] = u'SF拆分'
    dictDirection['O'] = u'SF合并'
    dictDirection['P'] = u'备兑'
    dictDirection['Q'] = u'证券冻结/解冻'
    dictDirection['R'] = u'行权'          

    dictOffset = {}
    dictOffset['0'] = u'开仓'
    dictOffset['1'] = u'平仓'
    dictOffset['2'] = u'强平'
    dictOffset['3'] = u'平今'
    dictOffset['4'] = u'平昨'
    dictOffset['5'] = u'强减'
    dictOffset['6'] = u'本地强平'    

    #----------------------------------------------------------------------
    def __init__(self, eventEngine, mainEngine, parent=None):
        """Constructor"""
        super(OrderMonitor, self).__init__(parent)
        self.__eventEngine = eventEngine
        self.__mainEngine = mainEngine

        self.dictOrder = {}	    # 用来保存报单号对应的单元格对象
        self.dictOrderData = {}	    # 用来保存报单数据

        self.initUi()
        self.registerEvent()

    #----------------------------------------------------------------------
    def initUi(self):
        """"""
        self.setWindowTitle(u'报单')

        self.setColumnCount(len(self.dictLabels))
        self.setHorizontalHeaderLabels(self.dictLabels.values())

        self.verticalHeader().setVisible(False)                 # 关闭左边的垂直表头
        self.setEditTriggers(QtGui.QTableWidget.NoEditTriggers) # 设为不可编辑状态

    #----------------------------------------------------------------------
    def registerEvent(self):
        """"""
        self.signal.connect(self.updateOrder)
        self.__eventEngine.register(EVENT_ORDER, self.signal.emit)

        self.itemDoubleClicked.connect(self.cancelOrder)

    #----------------------------------------------------------------------
    def updateOrder(self, event):
        """"""
        data = event.dict_['data']
        orderSysID = data[0][0]
        options = 'LogonID='+str(self.__mainEngine.wa.tQuery('LogonID').Data[0][0])+';RequestID='+str(orderSysID)+';showfields=OrderNumber,OrderStatus,TradedVolume,OrderTime,SecurityName'
        message = self.__mainEngine.wa.tQuery('Order', options)
        print u'报单'
        print message
        orderref = message.Data[0][0]
        #options = 'LogonID='+str(self.__mainEngine.wa.tQuery('LogonID').Data[0][0])+';WindCode='+str(event.dict_['code'])
        #ReOrder = self.__mainEngine.wa.tQuery('Order', options)
        #print ReOrder
        
        self.dictOrderData[orderref] = data

        # 如果之前已经收到过这个账户的数据, 则直接更新
        if orderref in self.dictOrder:
            d = self.dictOrder[orderref]

            for label, cell in d.items():
                if label == 'OrderRef':
                    try:
                        value = str(message.Data[0][0])
                    except KeyError:
                        value = u'未知类型'
                elif label == 'OrderSysID':
                    try:
                        value = str(orderSysID)
                    except KeyError:
                        value = u'未知类型'
                        
                elif label == 'InstrumentID':
                    try:
                        value = data[1][0]
                    except KeyError:
                        value = u'未知类型'  
                elif label == 'ExchangeInstID':
                    try:
                        value = message.Data[4][0]
                    except KeyError:
                        value = u'未知类型'  
                elif label == 'Direction':
                    try:
                        value = data[2][0]
                        if value == 'BUY':
                            value = u'买'
                        elif value == 'SHORT':
                            value = u'卖'
                        elif value == 'COVER':
                            value = u'买'
                        elif value == 'SELL':
                            value = u'卖'
                        elif value == 'COVERTODAY':
                            value = u'买'
                        elif value == 'SELLTODAY':
                            value = u'卖'
                    except KeyError:
                        value = u'未知类型'        
                elif label == 'CombOffsetFlag':
                    try:
                        value = data[2][0]
                        if value == 'BUY':
                            value = u'开仓'
                        elif value == 'SHORT':
                            value = u'开仓'
                        elif value == 'COVER':
                            value = u'平仓'
                        elif value == 'SELL':
                            value = u'平仓'
                        elif value == 'COVERTODAY':
                            value = u'平今仓'
                        elif value == 'SELLTODAY':
                            value = u'平今仓'
                    except KeyError:
                        value = u'未知类型'
                elif label == 'LimitPrice':
                    value = data[3][0]
                
                elif label == 'VolumeTotalOriginal':
                    value = data[4][0]
                
                elif label == 'VolumeTraded':
                    value = str(message.Data[2][0])
                 
                elif label == 'InsertTime':
                    value = str(message.Data[3][0])
                 
                elif label == 'CancelTime':
                    value = ''
                 
                elif label == 'StatusMsg':
                    value = str(message.Data[1][0])
                cell.setText(value)
                
           # 否则插入新的一行，并更新

        else:
            self.insertRow(0)
            d = {}

            for col, label in enumerate(self.dictLabels.keys()):
                if label == 'OrderRef':
                    try:
                        
                        value = str(message.Data[0][0])
                    except KeyError:
                        value = u'未知类型'
                elif label == 'OrderSysID':
                    try:
                        value = str(orderSysID)
                    except KeyError:
                        value = u'未知类型'
                        
                elif label == 'InstrumentID':
                    try:
                        value = data[1][0]
                    except KeyError:
                        value = u'未知类型'  
                elif label == 'ExchangeInstID':
                    try:
                        value = message.Data[4][0]
                    except KeyError:
                        value = u'未知类型'  
                elif label == 'Direction':
                    try:
                        value = data[2][0]
                        if value == 'BUY':
                            value = u'买'
                        elif value == 'SHORT':
                            value = u'卖'
                        elif value == 'COVER':
                            value = u'买'
                        elif value == 'SELL':
                            value = u'卖'
                        elif value == 'COVERTODAY':
                            value = u'买'
                        elif value == 'SELLTODAY':
                            value = u'卖'
                    except KeyError:
                        value = u'未知类型'        
                elif label == 'CombOffsetFlag':
                    try:
                        value = data[2][0]
                        if value == 'BUY':
                            value = u'开仓'
                        elif value == 'SHORT':
                            value = u'开仓'
                        elif value == 'COVER':
                            value = u'平仓'
                        elif value == 'SELL':
                            value = u'平仓'
                        elif value == 'COVERTODAY':
                            value = u'平今仓'
                        elif value == 'SELLTODAY':
                            value = u'平今仓'
                    except KeyError:
                        value = u'未知类型'
                elif label == 'LimitPrice':
                    value = data[3][0]
                
                elif label == 'VolumeTotalOriginal':
                    value = data[4][0]
                

                elif label == 'VolumeTraded':
                    value = str(message.Data[2][0])
                 
                elif label == 'InsertTime':
                    value =str( message.Data[3][0])
                 
                elif label == 'CancelTime':
                    value = ''
                 
                elif label == 'StatusMsg':
                    value = str(message.Data[1][0])
                if value == None:
                    value =''
                cell = QtGui.QTableWidgetItem(value)
                self.setItem(0, col, cell)
                d[label] = cell

                cell.orderref =	message.Data[0][0]   # 动态绑定报单号到单元格上

            self.dictOrder[orderref] = d
    
    #----------------------------------------------------------------------
    def cancelOrder(self, cell):
        """双击撤单"""
        logonID = self.__mainEngine.wa.tQuery('LogonID').Data[0][0]
        options1 = 'LogonID='+str(logonID)+';OrderType=Withdrawable'
        withOrder = self.__mainEngine.wa.tQuery('Order',options1)
        print 'withOrder'
        print withOrder
        
        orderref = str(cell.orderref)
        # 撤单前检查报单是否已经撤销或者全部成交
        print u'可撤',orderref,withOrder.Data[0]
        if orderref in withOrder.Data[0]:
            self.__mainEngine.wa.tCancel(orderref,'LogonID='+str(logonID))
        
        #options =   "LogonId=" + str(self.__mainEngine.wa.tQuery('LogonID').Data[0][0])+';OrderNumber='+orderref
        #ReOrder = self.__mainEngine.wa.tQuery('Order',options)
        #print ReOrder
        #k = ReOrder.Fields.index('OrderStatus')
        
        d = self.dictOrder[cell.orderref]
    
        for label, cell in d.items():
            value =''
            if label == 'CancelTime':
                try:
                    value = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                    cell.setText(value) 
                except KeyError:
                    value = u'未知类型'
                    cell.setText(value)
            elif label == 'StatusMsg':
                try:
                    value = 'Cancelled'
                    cell.setText(value)
                except KeyError:
                    value = u'未知类型'
                    cell.setText(value)      
            
    #----------------------------------------------------------------------
    def cancelAll(self):
        """全撤"""
        pass	

    

########################################################################
class MarketDataMonitor(QtGui.QTableWidget):
    """用于显示行情 """
    signal = QtCore.pyqtSignal(type(Event()))

    dictLabels = OrderedDict()
#     dictLabels['Name'] = u'合约名称'
    dictLabels['InstrumentID'] = u'合约代码'
    dictLabels['ExchangeInstID'] = u'合约交易所代码'

    dictLabels['BidPrice1'] = u'买一价'
    dictLabels['BidVolume1'] = u'买一量'
    dictLabels['AskPrice1'] = u'卖一价'
    dictLabels['AskVolume1'] = u'卖一量'    

    dictLabels['LastPrice'] = u'最新价'
    dictLabels['Volume'] = u'成交量'

    dictLabels['UpdateTime'] = u'更新时间'


    #----------------------------------------------------------------------
    def __init__(self, eventEngine, mainEngine, parent=None):
        """Constructor"""
        super(MarketDataMonitor, self).__init__(parent)
        self.__eventEngine = eventEngine
        self.__mainEngine = mainEngine

        self.dictData = {}

        self.initUi()
        self.registerEvent()

    #----------------------------------------------------------------------
    def initUi(self):
        """"""
        self.setWindowTitle(u'行情')

        self.setColumnCount(len(self.dictLabels))
        self.setHorizontalHeaderLabels(self.dictLabels.values())

        self.verticalHeader().setVisible(False)                 # 关闭左边的垂直表头
        self.setEditTriggers(QtGui.QTableWidget.NoEditTriggers) # 设为不可编辑状态

    #----------------------------------------------------------------------
    def registerEvent(self):
        """"""
        self.signal.connect(self.updateData)
        self.__eventEngine.register(EVENT_MARKETDATA, self.signal.emit)

    #----------------------------------------------------------------------
    def updateData(self, event):
        """"""
        data = event.dict_['data']
        time = event.dict_['time'][0]
        instrumentid = event.dict_['code'][0]
        field = event.dict_['field']

        # 如果之前已经收到过这个账户的数据, 则直接更新
        if instrumentid in self.dictData:
            d = self.dictData[instrumentid]

            for label, cell in d.items():
                if label == 'InstrumentID':
                    
                    value = str(instrumentid)                    
                    
#                 elif label=='Name':
#                     value = ''                
                    
                                
                    
                elif label=='BidPrice1':
                    for k in range(0,len(field)):
                        if field[k] == 'RT_BID1':
                            value = str(data[k][0])                    
                    
                    
                elif label=='BidVolume1':
                    for k in range(0,len(field)):
                        if field[k] == 'RT_BSIZE1':
                            value = str(data[k][0])                       
                    
                elif label=='AskPrice1':
                    for k in range(0,len(field)):
                        if field[k] == 'RT_ASK1':
                            value = str(data[k][0])                        
                    
                elif label=='AskVolume1':
                    for k in range(0,len(field)):
                        if field[k] == 'RT_ASIZE1':
                            value = str(data[k][0])                        
                    
                elif label=='Volume':
                    for k in range(0,len(field)):
                        if field[k] == 'RT_VOL':
                            value = str(data[k][0])                        
                    
                elif label=='LastPrice':
                    for k in range(0,len(field)):
                        if field[k] == 'LATEST':
                            value = str(data[k][0])                        
                                      
                    
                elif label=='UpdateTime':
                    value = str(time)                    
                    
                cell.setText(value)
        # 否则插入新的一行，并更新
        else:
            row = self.rowCount()
            self.insertRow(row)
            d = {}

            for col, label in enumerate(self.dictLabels.keys()):
                
                if label == 'InstrumentID':
                    value = str(instrumentid)				    
                    cell = QtGui.QTableWidgetItem(value)
                    self.setItem(row, col, cell)
                    d[label] = cell
#                 elif label=='Name':
#                     name = ''			    
#                     cell = QtGui.QTableWidgetItem(name)	
#                     self.setItem(row, col, cell)
#                     d[label] = cell
                
                elif label=='BidPrice1':
                    for k in range(0,len(field)):
                        if field[k] == 'RT_BID1':
                            value = str(data[k][0])                    
                    cell = QtGui.QTableWidgetItem(value)
                    self.setItem(row, col, cell)
                    d[label] = cell
                elif label=='BidVolume1':
                    for k in range(0,len(field)):
                        if field[k] == 'RT_BSIZE1':
                            value = str(data[k][0])                       
                    cell = QtGui.QTableWidgetItem(value)
                    self.setItem(row, col, cell)
                    d[label] = cell
                elif label=='AskPrice1':
                    for k in range(0,len(field)):
                        if field[k] == 'RT_ASK1':
                            value = str(data[k][0])                        
                    cell = QtGui.QTableWidgetItem(value)
                    self.setItem(row, col, cell)
                    d[label] = cell
                elif label=='AskVolume1':
                    for k in range(0,len(field)):
                        if field[k] == 'RT_ASIZE1':
                            value = str(data[k][0])                        
                    cell = QtGui.QTableWidgetItem(value)
                    self.setItem(row, col, cell)
                    d[label] = cell
                elif label=='Volume':
                    for k in range(0,len(field)):
                        if field[k] == 'RT_VOL':
                            value = str(data[k][0])                        
                    cell = QtGui.QTableWidgetItem(value)
                    self.setItem(row, col, cell)
                    d[label] = cell
                elif label=='LastPrice':
                    for k in range(0,len(field)):
                        if field[k] == 'LATEST':
                            value = str(data[k][0])                        
                    cell = QtGui.QTableWidgetItem(value)
                    self.setItem(row, col, cell)
                    d[label] = cell
                elif label=='UpdateTime':
                    value = str(time)                    
                    cell = QtGui.QTableWidgetItem(value)
                    self.setItem(row, col, cell)
                    d[label] = cell
                
            self.dictData[instrumentid] = d
            

    #----------------------------------------------------------------------
    def getName(self, instrumentid):
        """获取名称"""
        instrument = self.__mainEngine.selectInstrument(instrumentid)
        if instrument:
            return instrument['InstrumentName'].decode('GBK')
        else:
            return ''


########################################################################
class LoginWidget(QtGui.QDialog):
    """登录"""
    accountType = OrderedDict()
    
    accountType['SHSZ'] = u'沪深A股'
    accountType['SZB'] = u'深市B股'
    accountType['SHB'] = u'沪市B股'
    accountType['CFE'] = u'中金所期货'
    accountType['SHF'] = u'上期所期货'
    accountType['DCE'] = u'大商所期货'
    accountType['CZE'] = u'郑商所期货'
    accountType['SHO'] = u'上交所期权'
    
    accountTypeReverse = {value:key for key,value in accountType.items()}
    #----------------------------------------------------------------------
    def __init__(self, mainEngine, parent=None):
        """Constructor"""
        super(LoginWidget, self).__init__()
        self.__mainEngine = mainEngine

        self.initUi()
        self.loadData()

    #----------------------------------------------------------------------
    def initUi(self):
        """初始化界面"""
        self.setWindowTitle(u'登录')

        # 设置组件
        labelUserID = QtGui.QLabel(u'账号：')
        labelPassword = QtGui.QLabel(u'密码：')
     #   labelMdAddress = QtGui.QLabel(u'行情服务器：')
      #  labelTdAddress = QtGui.QLabel(u'交易服务器：')
        labelBrokerID = QtGui.QLabel(u'经纪商代码')
        labelDepartmentID = QtGui.QLabel(u'营业部代码')
        accountType = QtGui.QLabel(u'账户类型')

        self.editUserID = QtGui.QLineEdit()
        self.editPassword = QtGui.QLineEdit()
        self.editPassword.setEchoMode(QtGui.QLineEdit.Password) 
#         self.editMdAddress = QtGui.QLineEdit()
#         self.editTdAddress = QtGui.QLineEdit()
        self.editBrokerID = QtGui.QLineEdit()
        self.editDepartmentID = QtGui.QLineEdit()
        self.editAccountType = QtGui.QComboBox()
        self.editAccountType.addItems(self.accountType.values())
        self.editUserID.setMinimumWidth(200)

        buttonLogin = QtGui.QPushButton(u'登录')
        buttonCancel = QtGui.QPushButton(u'取消')
        buttonLogin.clicked.connect(self.login)
        buttonCancel.clicked.connect(self.close)

        # 设置布局
        buttonHBox = QtGui.QHBoxLayout()
        buttonHBox.addStretch()
        buttonHBox.addWidget(buttonLogin)
        buttonHBox.addWidget(buttonCancel)

        grid = QtGui.QGridLayout()
        grid.addWidget(labelUserID, 0, 0)
        grid.addWidget(labelPassword, 1, 0)
#         grid.addWidget(labelMdAddress, 2, 0)
#         grid.addWidget(labelTdAddress, 3, 0)
        grid.addWidget(labelBrokerID, 4, 0)
        grid.addWidget(labelDepartmentID, 5, 0)
        grid.addWidget(accountType, 6, 0)
        grid.addWidget(self.editUserID, 0, 1)
        grid.addWidget(self.editPassword, 1, 1)
#         grid.addWidget(self.editMdAddress, 2, 1)
#         grid.addWidget(self.editTdAddress, 3, 1)
        grid.addWidget(self.editBrokerID, 4, 1)
        grid.addWidget(self.editDepartmentID, 5, 1)
        grid.addWidget(self.editAccountType, 6, 1)
        grid.addLayout(buttonHBox, 7, 0, 1, 2)
        self.setLayout(grid)

    #----------------------------------------------------------------------
    def login(self):
        """登录"""
        userid = str(self.editUserID.text())
        password = str(self.editPassword.text())
#         mdAddress = str(self.editMdAddress.text())
#         tdAddress = str(self.editTdAddress.text())
        brokerid = str(self.editBrokerID.text())
        departmentid = str(self.editDepartmentID.text())
        accountType = self.accountTypeReverse[unicode(self.editAccountType.currentText())]
        print userid,password,brokerid,accountType
        #self.__mainEngine.wa.tLogon('00000010', '0' , "M:1585078833901", '111111','SHSZ')
        logonId = self.__mainEngine.wa.tLogon(brokerid, departmentid , userid, password,accountType)
        self.__mainEngine.initLogonId(logonId)
        
        self.close()

    #----------------------------------------------------------------------
    def loadData(self):
        """读取数据"""
        f = shelve.open('setting.vn')

        try:
            setting = f['login']
            userid = setting['userid']
            password = setting['password']
#             mdAddress = setting['mdAddress']
#             tdAddress = setting['tdAddress']
            brokerid = setting['brokerid']
            departmentid = setting['departmentid']
            accountType = setting['accountType']



            self.editUserID.setText(userid)
            self.editPassword.setText(password)
            self.editBrokerID.setText(brokerid)
            self.editDepartmentID.setText(departmentid)
        except KeyError:
            pass

        f.close()

    #----------------------------------------------------------------------
    def saveData(self):
        """保存数据"""
        setting = {}
        setting['userid'] = str(self.editUserID.text())
        setting['password'] = str(self.editPassword.text())
        setting['brokerid'] = str(self.editBrokerID.text())
        setting['departmentid'] = str(self.editDepartmentID.text())
        setting['accountType'] = self.accountTypeReverse[unicode(self.editAccountType.currentText())]
        f = shelve.open('setting.vn')
        f['login'] = setting
        f.close()	

    #----------------------------------------------------------------------
    def closeEvent(self, event):
        """关闭事件处理"""
        # 当窗口被关闭时，先保存登录数据，再关闭
        self.saveData()
        event.accept()  	
 

########################################################################
class ControlWidget(QtGui.QWidget):
    """调用查询函数"""

    #----------------------------------------------------------------------
    def __init__(self, mainEngine, parent=None):
        """Constructor"""
        super(ControlWidget, self).__init__()
        self.__mainEngine = mainEngine

        self.initUi()

    #----------------------------------------------------------------------
    def initUi(self):
        """"""
        self.setWindowTitle(u'测试')

        buttonAccount = QtGui.QPushButton(u'查询账户')
        buttonInvestor = QtGui.QPushButton(u'查询投资者')
        buttonPosition = QtGui.QPushButton(u'查询持仓')

        buttonAccount.clicked.connect(self.__mainEngine.getAccount)
        buttonInvestor.clicked.connect(self.__mainEngine.getInvestor)
        buttonPosition.clicked.connect(self.__mainEngine.getPosition)

        hBox = QtGui.QHBoxLayout()
        hBox.addWidget(buttonAccount)
        hBox.addWidget(buttonInvestor)
        hBox.addWidget(buttonPosition)

        self.setLayout(hBox)


########################################################################
class TradingWidget(QtGui.QWidget):
    """交易"""
    signal = QtCore.pyqtSignal(type(Event()))

    dictDirection = OrderedDict()
    dictDirection['0'] = u'买'
    dictDirection['1'] = u'卖'  

    dictOffset = OrderedDict()
    dictOffset['0'] = u'开仓'
    dictOffset['1'] = u'平仓' 
    dictOffset['3'] = u'平今'

    dictPriceType = OrderedDict()
    
    dictPriceType['0'] = u'限价委托'
    dictPriceType['4'] = u'最优五档剩余撤销'
    dictPriceType['6'] = u'最优五档剩余转限价'
    

    
    contractItem = OrderedDict()
    contractItem['0'] = u''
    contractItem['1'] = u'IF1509.CFE'
    contractItem['2'] = u'IF1510.CFE'
    contractItem['3'] = u'IF1512.CFE'
    contractItem['4'] = u'IF1603.CFE'
    contractItem['6'] = u'10000031.SH'
    contractItem['7'] = u'10000032.SH'
    contractItem['8'] = u'10000033.SH'
    contractItem['9'] = u'10000034.SH'
    contractItem['10'] = u'10000035.SH'
    contractItem['11'] = u'10000047.SH'
    contractItem['12'] = u'10000055.SH'
    contractItem['13'] = u'10000063.SH'
    contractItem['14'] = u'10000071.SH'
    contractItem['15'] = u'10000079.SH'
    contractItem['16'] = u'10000087.SH'
    contractItem['17'] = u'10000095.SH'
    contractItem['18'] = u'10000103.SH'
    contractItem['19'] = u'10000125.SH'
    contractItem['20'] = u'10000139.SH'
    contractItem['21'] = u'10000140.SH'
    contractItem['22'] = u'10000149.SH'
    contractItem['23'] = u'10000157.SH'
    contractItem['24'] = u'10000165.SH'
    contractItem['25'] = u'10000173.SH'
    contractItem['26'] = u'10000181.SH'
    contractItem['27'] = u'10000197.SH'
    contractItem['28'] = u'10000225.SH'
    contractItem['29'] = u'10000339.SH'
    contractItem['30'] = u'10000357.SH'
    contractItem['31'] = u'10000358.SH'
    contractItem['32'] = u'10000359.SH'
    contractItem['33'] = u'10000360.SH'
    contractItem['34'] = u'10000387.SH'
    contractItem['35'] = u'10000388.SH'
    contractItem['36'] = u'10000389.SH'
    
    # 反转字典
    dictDirectionReverse = {value:key for key,value in dictDirection.items()}
    dictOffsetReverse = {value:key for key, value in dictOffset.items()}
    dictPriceTypeReverse = {value:key for key, value in dictPriceType.items()}

    #----------------------------------------------------------------------
    def __init__(self, eventEngine, mainEngine, orderMonitor, parent=None):
        """Constructor"""
        super(TradingWidget, self).__init__()
        self.__eventEngine = eventEngine
        self.__mainEngine = mainEngine
        self.__orderMonitor = orderMonitor

        self.instrumentid = ''

        self.initUi()
        self.registerEvent()

    #----------------------------------------------------------------------
    def initUi(self):
        """初始化界面"""
        self.setWindowTitle(u'交易')

        # 左边部分
#         labelID = QtGui.QLabel(u'代码')
#         labelName =  QtGui.QLabel(u'名称')
        labelDirection = QtGui.QLabel(u'委托类型')
        labelOffset = QtGui.QLabel(u'开平')
        labelContract = QtGui.QLabel(u'合约')
        labelPrice = QtGui.QLabel(u'价格')
        labelVolume = QtGui.QLabel(u'数量')
        labelPriceMargin = QtGui.QLabel(u'价差')
        labelPriceType = QtGui.QLabel(u'价格类型')
        labelOperation = QtGui.QLabel(u'操作')

        self.lineID = QtGui.QLineEdit()

        self.comboDirection = QtGui.QComboBox()
        self.comboDirection.addItems(self.dictDirection.values())

        self.comboOffset = QtGui.QComboBox()
        self.comboOffset.addItems(self.dictOffset.values())

        self.contract = QtGui.QComboBox()
        self.contract.addItems(self.contractItem.values())

        self.spinPrice = QtGui.QDoubleSpinBox()
        self.spinPrice.setDecimals(4)
        self.spinPrice.setMinimum(0)
        self.spinPrice.setMaximum(10000)

        self.spinVolume = QtGui.QSpinBox()
        self.spinVolume.setMinimum(0)
        self.spinVolume.setMaximum(1000000)

        self.priceMargin = QtGui.QLineEdit()

        self.comboPriceType = QtGui.QComboBox()
        self.comboPriceType.addItems(self.dictPriceType.values())
        
        self.lineID1 = QtGui.QLineEdit()

        self.comboDirection1 = QtGui.QComboBox()
        self.comboDirection1.addItems(self.dictDirection.values())

        self.comboOffset1 = QtGui.QComboBox()
        self.comboOffset1.addItems(self.dictOffset.values())
        
        self.contract1 = QtGui.QComboBox()
        self.contract1.addItems(self.contractItem.values())

        self.spinPrice1 = QtGui.QDoubleSpinBox()
        self.spinPrice1.setDecimals(4)
        self.spinPrice1.setMinimum(0)
        self.spinPrice1.setMaximum(10000)

        self.spinVolume1 = QtGui.QSpinBox()
        self.spinVolume1.setMinimum(0)
        self.spinVolume1.setMaximum(1000000)

        self.priceMargin1 = QtGui.QLineEdit()

        self.comboPriceType1 = QtGui.QComboBox()
        self.comboPriceType1.addItems(self.dictPriceType.values())

        gridleft = QtGui.QGridLayout()
#         gridleft.addWidget(labelID, 0, 0)
        gridleft.addWidget(labelDirection, 2, 0)
        gridleft.addWidget(labelOffset, 3, 0)
        gridleft.addWidget(labelContract, 4, 0)
        gridleft.addWidget(labelPrice, 5, 0)
        gridleft.addWidget(labelVolume, 6, 0)
        gridleft.addWidget(labelPriceMargin, 7, 0)
        gridleft.addWidget(labelPriceType, 8, 0)
#         gridleft.addWidget(self.lineID, 0, 1)
#          gridleft.addWidget(self.lineName, 1, 1)
#         gridleft.addWidget(self.comboDirection, 2, 1)
#         gridleft.addWidget(self.comboOffset, 3, 1)
#         gridleft.addWidget(self.contract, 4, 1)
#         gridleft.addWidget(self.spinPrice, 5, 1)
#         gridleft.addWidget(self.spinVolume, 6, 1)
#         gridleft.addWidget(self.priceMargin, 7, 1)
#         gridleft.addWidget(self.comboPriceType, 8, 1)	
#         gridleft.addWidget(self.lineID1, 0, 2)
#         gridleft.addWidget(self.comboDirection1, 2, 2)
#         gridleft.addWidget(self.comboOffset1, 3, 2)
#         gridleft.addWidget(self.contract1, 4, 2)
#         gridleft.addWidget(self.spinPrice1, 5, 2)
#         gridleft.addWidget(self.spinVolume1, 6, 2)
#         gridleft.addWidget(self.priceMargin1, 7, 1)
#         gridleft.addWidget(self.comboPriceType1, 8, 2)    

        gridmiddle1 = QtGui.QGridLayout()
#         gridmiddle1.addWidget(self.lineID, 0, 2)
        gridmiddle1.addWidget(self.comboDirection, 2, 2)
        gridmiddle1.addWidget(self.comboOffset, 3, 2)
        gridmiddle1.addWidget(self.contract, 4, 2)
        gridmiddle1.addWidget(self.spinPrice, 5, 2)
        gridmiddle1.addWidget(self.spinVolume, 6, 2)
        gridmiddle1.addWidget(self.priceMargin, 7, 2)
        gridmiddle1.addWidget(self.comboPriceType, 8, 2)    

        gridmiddle2 = QtGui.QGridLayout()
#         gridmiddle2.addWidget(self.lineID1, 0, 2)
        gridmiddle2.addWidget(self.comboDirection1, 2, 2)
        gridmiddle2.addWidget(self.comboOffset1, 3, 2)
        gridmiddle2.addWidget(self.contract1, 4, 2)
        gridmiddle2.addWidget(self.spinPrice1, 5, 2)
        gridmiddle2.addWidget(self.spinVolume1, 6, 2)
        gridmiddle2.addWidget(self.priceMargin1, 7, 2)
        gridmiddle2.addWidget(self.comboPriceType1, 8, 2)    

        # 右边部分
        labelBid1 = QtGui.QLabel(u'买一')
        labelBid2 = QtGui.QLabel(u'买二')
        labelBid3 = QtGui.QLabel(u'买三')
        labelBid4 = QtGui.QLabel(u'买四')
        labelBid5 = QtGui.QLabel(u'买五')

        labelAsk1 = QtGui.QLabel(u'卖一')
        labelAsk2 = QtGui.QLabel(u'卖二')
        labelAsk3 = QtGui.QLabel(u'卖三')
        labelAsk4 = QtGui.QLabel(u'卖四')
        labelAsk5 = QtGui.QLabel(u'卖五')

        self.labelBidPrice1 = QtGui.QLabel()
        self.labelBidPrice2 = QtGui.QLabel()
        self.labelBidPrice3 = QtGui.QLabel()
        self.labelBidPrice4 = QtGui.QLabel()
        self.labelBidPrice5 = QtGui.QLabel()
        self.labelBidVolume1 = QtGui.QLabel()
        self.labelBidVolume2 = QtGui.QLabel()
        self.labelBidVolume3 = QtGui.QLabel()
        self.labelBidVolume4 = QtGui.QLabel()
        self.labelBidVolume5 = QtGui.QLabel()	

        self.labelAskPrice1 = QtGui.QLabel()
        self.labelAskPrice2 = QtGui.QLabel()
        self.labelAskPrice3 = QtGui.QLabel()
        self.labelAskPrice4 = QtGui.QLabel()
        self.labelAskPrice5 = QtGui.QLabel()
        self.labelAskVolume1 = QtGui.QLabel()
        self.labelAskVolume2 = QtGui.QLabel()
        self.labelAskVolume3 = QtGui.QLabel()
        self.labelAskVolume4 = QtGui.QLabel()
        self.labelAskVolume5 = QtGui.QLabel()	

        labelLast = QtGui.QLabel(u'最新')
        self.labelLastPrice = QtGui.QLabel()
        self.labelReturn = QtGui.QLabel()

        self.labelLastPrice.setMinimumWidth(60)
        self.labelReturn.setMinimumWidth(60)

        gridRight = QtGui.QGridLayout()
        gridRight.addWidget(labelAsk5, 0, 0)
        gridRight.addWidget(labelAsk4, 1, 0)
        gridRight.addWidget(labelAsk3, 2, 0)
        gridRight.addWidget(labelAsk2, 3, 0)
        gridRight.addWidget(labelAsk1, 4, 0)
        gridRight.addWidget(labelLast, 5, 0)
        gridRight.addWidget(labelBid1, 6, 0)
        gridRight.addWidget(labelBid2, 7, 0)
        gridRight.addWidget(labelBid3, 8, 0)
        gridRight.addWidget(labelBid4, 9, 0)
        gridRight.addWidget(labelBid5, 10, 0)

        gridRight.addWidget(self.labelAskPrice5, 0, 1)
        gridRight.addWidget(self.labelAskPrice4, 1, 1)
        gridRight.addWidget(self.labelAskPrice3, 2, 1)
        gridRight.addWidget(self.labelAskPrice2, 3, 1)
        gridRight.addWidget(self.labelAskPrice1, 4, 1)
        gridRight.addWidget(self.labelLastPrice, 5, 1)
        gridRight.addWidget(self.labelBidPrice1, 6, 1)
        gridRight.addWidget(self.labelBidPrice2, 7, 1)
        gridRight.addWidget(self.labelBidPrice3, 8, 1)
        gridRight.addWidget(self.labelBidPrice4, 9, 1)
        gridRight.addWidget(self.labelBidPrice5, 10, 1)	

        gridRight.addWidget(self.labelAskVolume5, 0, 2)
        gridRight.addWidget(self.labelAskVolume4, 1, 2)
        gridRight.addWidget(self.labelAskVolume3, 2, 2)
        gridRight.addWidget(self.labelAskVolume2, 3, 2)
        gridRight.addWidget(self.labelAskVolume1, 4, 2)
        gridRight.addWidget(self.labelReturn, 5, 2)
        gridRight.addWidget(self.labelBidVolume1, 6, 2)
        gridRight.addWidget(self.labelBidVolume2, 7, 2)
        gridRight.addWidget(self.labelBidVolume3, 8, 2)
        gridRight.addWidget(self.labelBidVolume4, 9, 2)
        gridRight.addWidget(self.labelBidVolume5, 10, 2)

        # 发单按钮
        buttonSendOrder = QtGui.QPushButton(u'发单')
        buttonArbitrage = QtGui.QPushButton(u'套利')
        buttonAuto = QtGui.QPushButton(u'自动套利')

        # 整合布局
        hbox = QtGui.QHBoxLayout()
        hbox.addLayout(gridleft)
        hbox.addLayout(gridmiddle1)
        hbox.addLayout(gridmiddle2)
        hbox.addLayout(gridRight)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(buttonSendOrder)
        vbox.addWidget(buttonArbitrage)
        vbox.addWidget(buttonAuto)

        self.setLayout(vbox)

        # 关联更新
        buttonSendOrder.clicked.connect(self.sendOrder)
#         buttonCancelAll.clicked.connect(self.__orderMonitor.cancelAll)
        buttonAuto.clicked.connect(self.autoArbitrage)
#         self.lineID.returnPressed.connect(self.updateID)
        QtGui.QWidget.connect(self.contract, QtCore.SIGNAL('activated(int)'), self.updateID)
        QtGui.QWidget.connect(self.contract1, QtCore.SIGNAL('activated(int)'), self.updateID1)
    #----------------------------------------------------------------------
    def updateID(self):
        """合约变化"""
        instrumentid = str(self.contract.currentText())
        # 获取合约
        instrument = self.__mainEngine.wa.subscribe(instrumentid, "rt_bid1,rt_bsize1,rt_ask1,rt_asize1,rt_latest,rt_vol,rt_time,rt_pre_close")
        if instrument.ErrorCode==0:

            # 清空价格数量
            self.spinPrice.setValue(0)
            self.spinVolume.setValue(0)

            # 清空行情显示
            self.labelBidPrice1.setText('')
            self.labelBidPrice2.setText('')
            self.labelBidPrice3.setText('')
            self.labelBidPrice4.setText('')
            self.labelBidPrice5.setText('')
            self.labelBidVolume1.setText('')
            self.labelBidVolume2.setText('')
            self.labelBidVolume3.setText('')
            self.labelBidVolume4.setText('')
            self.labelBidVolume5.setText('')	
            self.labelAskPrice1.setText('')
            self.labelAskPrice2.setText('')
            self.labelAskPrice3.setText('')
            self.labelAskPrice4.setText('')
            self.labelAskPrice5.setText('')
            self.labelAskVolume1.setText('')
            self.labelAskVolume2.setText('')
            self.labelAskVolume3.setText('')
            self.labelAskVolume4.setText('')
            self.labelAskVolume5.setText('')
            self.labelLastPrice.setText('')
            self.labelReturn.setText('')

            # 更新目前的合约
            self.instrumentid = instrumentid
            
    def updateID1(self):
        """合约变化"""
        instrumentid = str(self.contract1.currentText())
        # 获取合约
        instrument = self.__mainEngine.wa.subscribe(instrumentid, "rt_bid1,rt_bsize1,rt_ask1,rt_asize1,rt_latest,rt_vol,rt_time,rt_pre_close")
        if instrument.ErrorCode==0:

            # 清空价格数量
            self.spinPrice.setValue(0)
            self.spinVolume.setValue(0)

            # 清空行情显示
            self.labelBidPrice1.setText('')
            self.labelBidPrice2.setText('')
            self.labelBidPrice3.setText('')
            self.labelBidPrice4.setText('')
            self.labelBidPrice5.setText('')
            self.labelBidVolume1.setText('')
            self.labelBidVolume2.setText('')
            self.labelBidVolume3.setText('')
            self.labelBidVolume4.setText('')
            self.labelBidVolume5.setText('')    
            self.labelAskPrice1.setText('')
            self.labelAskPrice2.setText('')
            self.labelAskPrice3.setText('')
            self.labelAskPrice4.setText('')
            self.labelAskPrice5.setText('')
            self.labelAskVolume1.setText('')
            self.labelAskVolume2.setText('')
            self.labelAskVolume3.setText('')
            self.labelAskVolume4.setText('')
            self.labelAskVolume5.setText('')
            self.labelLastPrice.setText('')
            self.labelReturn.setText('')

            # 更新目前的合约
            self.instrumentid = instrumentid    
            
    def autoArbitrage(self):
        name = unicode(self.contract.currentText())
        name1 = unicode(self.contract1.currentText())
        self.__mainEngine.autoArbitrageEngine(name, name1)
            

    #----------------------------------------------------------------------
    def updateMarketData(self, event):
        """更新行情"""
        data = event.dict_['data']
        time = event.dict_['time'][0]
        instrumentid = event.dict_['code'][0]
        field = event.dict_['field']
        latest = 0
        if instrumentid == self.instrumentid:
            for k in range(0,len(field)):
                if field[k] == 'RT_BID1':
                    self.labelBidPrice1.setText(str(data[k][0]))
                elif field[k] == 'RT_ASK1':
                    self.labelAskPrice1.setText(str(data[k][0]))
                elif field[k] == 'RT_BSIZE1':
                    self.labelBidVolume1.setText(str(data[k][0]))
                elif field[k] == 'RT_ASIZE1':
                    self.labelAskVolume1.setText(str(data[k][0]))
                elif field[k] == 'RT_LATEST':
                    self.labelLastPrice.setText(str(data[k][0]))
                    latest=data[k][0]
                elif field[k] == 'RT_PRE_CLOSE':
                    rt = (float(latest)/float(data[k][0]))-1
                    self.labelReturn.setText(('%.2f' %(rt*100))+'%')

    #----------------------------------------------------------------------
    def registerEvent(self):
        """注册事件监听"""
        self.signal.connect(self.updateMarketData)
        self.__eventEngine.register(EVENT_MARKETDATA_CONTRACT, self.signal.emit)

    #----------------------------------------------------------------------
    def sendOrder(self):
        """发单"""
        instrumentid = str(self.lineID.text())
        
        direction = self.dictDirectionReverse[unicode(self.comboDirection.currentText())]
        offset = self.dictOffsetReverse[unicode(self.comboOffset.currentText())]
        tradeside = self.getTradeSide(direction,offset)
        price = str(self.spinPrice.value())
        volume = str(self.spinVolume.value())
        pricetype = self.dictPriceTypeReverse[unicode(self.comboPriceType.currentText())]
        self.__mainEngine.wa.tOrder(instrumentid, tradeside, price, volume, OrderType=pricetype)

    def getTradeSide(self, dir, offset):
        if dir== '0' and offset == '0':
            return 'Buy'
        elif dir== '1' and offset == '0':
            return 'Short'
        elif dir== '0' and offset == '1':
            return 'Cover'
        elif dir== '1' and offset == '1':
            return 'Sell'
        elif dir== '0' and offset == '3':
            return 'CoverToday'
        elif dir== '1' and offset == '3':
            return 'SellToday'
            
        
########################################################################
class AboutWidget(QtGui.QDialog):
    """显示关于信息"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        super(AboutWidget, self).__init__(parent)

        self.initUi()

    #----------------------------------------------------------------------
    def initUi(self):
        """"""
        self.setWindowTitle(u'关于')

        text = u"""
            50ETF 期权与股指期货组合投资交易系统

            完成日期：2015/9/10

            作者：南京大学Friday小组

            Github：github.com/OAAppTeam/OAApp

            参考：vnpy框架   鸣谢作者：用python的交易员

            vnpy框架Github：github.com/vnpy/vnpy


            开发环境

            操作系统：Windows 8.1 专业版 64位

            Python发行版：Python 2.7.9 (Anaconda 1.9.2 Win-32)

            图形库：PyQt4 4.11.3 Py2.7-x32

            交易接口：windApi

            事件驱动引擎：eventEngine

            开发环境：pycharm 4.0.6

            EXE打包：Nuitka 0.5.12.1 Python2.7 32 bit MSI
            """

        label = QtGui.QLabel()
        label.setText(text)
        label.setMinimumWidth(450)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(label)

        self.setLayout(vbox)


########################################################################
class MainWindow(QtGui.QMainWindow):
    """主窗口"""
    signalInvestor = QtCore.pyqtSignal(type(Event()))
    signalLog = QtCore.pyqtSignal(type(Event()))

    #----------------------------------------------------------------------
    def __init__(self, eventEngine, mainEngine):
        """Constructor"""
        super(MainWindow, self).__init__()
        self.__eventEngine = eventEngine
        self.__mainEngine = mainEngine

        self.initUi()
        self.registerEvent()

    #----------------------------------------------------------------------
    def initUi(self):
        """"""
        # 设置名称
        self.setWindowTitle(u'50ETF 期权与股指期货组合投资交易系统')

        # 布局设置
        self.logM = LogMonitor(self.__eventEngine, self)
        self.accountM = AccountMonitor(self.__eventEngine, self)
        self.positionM = PositionMonitor(self.__eventEngine, self)
        self.tradeM = TradeMonitor(self.__eventEngine, self.__mainEngine,self)
        self.orderM = OrderMonitor(self.__eventEngine, self.__mainEngine, self)
        self.marketdataM = MarketDataMonitor(self.__eventEngine, self.__mainEngine, self)
        self.tradingW = TradingWidget(self.__eventEngine, self.__mainEngine, self.orderM, self)

        righttab = QtGui.QTabWidget()
        righttab.addTab(self.positionM, u'持仓')
        righttab.addTab(self.accountM, u'账户')

        lefttab = QtGui.QTabWidget()
        lefttab.addTab(self.orderM, u'报单')
        lefttab.addTab(self.tradeM, u'成交')
        lefttab.addTab(self.logM, u'日志')

        self.tradingW.setMaximumWidth(400)
        tradingVBox = QtGui.QVBoxLayout()
        tradingVBox.addWidget(self.tradingW)
        tradingVBox.addStretch()

        upHBox = QtGui.QHBoxLayout()
        upHBox.addLayout(tradingVBox)
        upHBox.addWidget(self.marketdataM)

        downHBox = QtGui.QHBoxLayout()
        downHBox.addWidget(lefttab)
        downHBox.addWidget(righttab)

        vBox = QtGui.QVBoxLayout()
        vBox.addLayout(upHBox)
        vBox.addLayout(downHBox)

        centralwidget = QtGui.QWidget()
        centralwidget.setLayout(vBox)
        self.setCentralWidget(centralwidget)

        # 设置状态栏
        self.bar = self.statusBar()
        self.bar.showMessage(u'启动Demo')

        # 设置菜单栏
        actionLogin = QtGui.QAction(u'登录', self)
        actionLogin.triggered.connect(self.openLoginWidget)
        actionExit = QtGui.QAction(u'退出', self)
        actionExit.triggered.connect(self.close)

        actionAbout = QtGui.QAction(u'关于', self)
        actionAbout.triggered.connect(self.openAboutWidget)		

        menubar = self.menuBar()
        sysMenu = menubar.addMenu(u'系统')
        sysMenu.addAction(actionLogin)
        sysMenu.addAction(actionExit)

        helpMenu = menubar.addMenu(u'帮助')
        helpMenu.addAction(actionAbout)

    #----------------------------------------------------------------------
    def registerEvent(self):
        """"""
        self.signalInvestor.connect(self.updateInvestor)
        self.signalLog.connect(self.updateLog)

        self.__eventEngine.register(EVENT_INVESTOR, self.signalInvestor.emit)
        self.__eventEngine.register(EVENT_LOG, self.signalLog.emit)

    #----------------------------------------------------------------------
    def updateInvestor(self, event):
        """"""
        data = event.dict_['data']

        self.setWindowTitle(u'50ETF 期权与股指期货组合投资交易系统  ' + data['InvestorName'].decode('GBK'))

    #----------------------------------------------------------------------
    def updateLog(self, event):
        """"""
        log = event.dict_['log']

        self.bar.showMessage(log)

    #----------------------------------------------------------------------
    def openLoginWidget(self):
        """打开登录"""
        try:
            self.loginW.show()
        except AttributeError:
            self.loginW = LoginWidget(self.__mainEngine, self)
            self.loginW.show()

    #----------------------------------------------------------------------
    def openAboutWidget(self):
        """打开关于"""
        try:
            self.aboutW.show()
        except AttributeError:
            self.aboutW = AboutWidget(self)
            self.aboutW.show()

    #----------------------------------------------------------------------
    def closeEvent(self, event):
        """退出事件处理"""
        reply = QtGui.QMessageBox.question(self, u'退出',
                                           u'确认退出?', QtGui.QMessageBox.Yes | 
                                           QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            self.__mainEngine.exit()
            event.accept()
        else:
            event.ignore()       










