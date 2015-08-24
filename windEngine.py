__author__ = 'Justin'

from windApi import WindApi
from eventEngine import EventEngine

class MainEngine:

    def __init__(self):
        self.wa = WindApi()
        self.wa.start()