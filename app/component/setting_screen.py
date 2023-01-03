# -*- coding: utf-8 -*-
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen

class SettingScreen(MDScreen):
    def __init__(self, **kw):
        super(SettingScreen, self).__init__(**kw)
        Clock.schedule_once(self.__post_init__)

    def __post_init__(self, *args):
        pass

    def __post_connection__(self, connection):
        pass

    def __post_joined__(self, connection):
        pass
