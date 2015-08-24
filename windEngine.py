__author__ = 'Justin'

from windApi import WindApi
from eventEngine import EventEngine

class MainEngine:

    def __init__(self):
        self.ee = EventEngine()
        self.wa = WindApi(self.ee)
        self.wa.start()
        self.ee.start()