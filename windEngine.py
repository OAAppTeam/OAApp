__author__ = 'Justin'
import sys
from datetime import date
from time import sleep

from windApi import WindApi
from eventEngine import EventEngine

from PyQt4 import QtCore
import shelve

import eventType
class MainEngine:

    def __init__(self):
        self.ee = EventEngine()
        self.wa = WindApi(self.ee)
        self.wa.start()
        self.ee.start()
        
    def exit(self):
        self.wa.stop()
        self.ee.stop()
        
        
        