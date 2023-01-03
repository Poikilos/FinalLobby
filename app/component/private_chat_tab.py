# -*- coding: utf-8 -*-
from math import ceil

# from kivy.app import App
from kivymd.app import MDApp
# ^ <https://github.com/HeaTTheatR/KivyMD/blob/master/README.md#api-
#   breaking-changes>

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import ObjectProperty, Logger, NumericProperty
from kivymd.uix.bottomsheet import MDListBottomSheet
from kivymd.uix.list import BaseListItem
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
# from kivymd.uix.boxlayout import MDBoxLayout
# ^ In kivy-irc, MDTab (deprecated) was used, but now if you don't
#   inherit a layout, you get
#   expected EventDispatcher got PrivateChatTab in tab.py (in KivyMD)
import app.constants as constants

class MultiLineListItem(BaseListItem):
    _txt_top_pad = NumericProperty(dp(10))
    _txt_bot_pad = NumericProperty(dp(10))
    _num_lines = 1

    def __init__(self, **kwargs):
        super(MultiLineListItem, self).__init__(**kwargs)
        self._num_lines = ceil(len(self.text) / 100.0)
        self.height = dp(37 + 20 * (self._num_lines - 1))
        self.text_size = self.width, None
        self.__post_init__(kwargs)

    def __post_init__(self, *args):
        self.ids._lbl_primary.markup = True


class PrivateChatTab(MDFloatLayout, MDTabsBase):
    app = ObjectProperty(None)
    irc_message = ObjectProperty(None)
    irc_message_send_btn = ObjectProperty(None)

    def __init__(self, **kw):
        super(PrivateChatTab, self).__init__(**kw)
        self.app = MDApp.get_running_app()
        # self.title must be set to channel, since it is used in various
        #   methods. The same goes for ChannelChatTab.
        Clock.schedule_once(self.__post_init__)
        self.on_privmsg(self.title, 'private', kw['msg'])

    def __post_init__(self, args):
        self.irc_message.hint_text = '@' + self.app.get_scoped('nickname')
        # ^ _hint_lbl is deprecated. See doc/irc_message.md field list.
        self.app.connection.on_privmsg(self.title, self.on_privmsg)

    def update_irc_message_text(self, dt):
        self.irc_message.text = ''
        # self.irc_message.on_focus()  # See see doc/development/irc_message.md
        self.irc_message.focus = True

    def send_message(self):
        Clock.schedule_once(self.update_irc_message_text)
        self.app.connection.msg(self.title, self.irc_message.text)
        self.msg_list.add_widget(
            MultiLineListItem(
                text="[b][color=1A237E]@" + self.app.get_scoped('nickname') + "[/color][/b] "
                     + self.irc_message.text,
                font_style=constants.FONT_STYLE_SUBHEADING,
            )
        )
        Logger.info("IRC: <%s> %s" % (self.app.get_scoped('nickname'), self.irc_message.text))

    def on_privmsg(self, user, channel, msg):
        user = user.split('!', 1)[0]
        self.msg_list.add_widget(
            MultiLineListItem(
                text="[b][color=F44336]@" + user + "[/color][/b] " + msg,
                font_style=constants.FONT_STYLE_SUBHEADING,
            )
        )
        Logger.info("IRC: <%s> %s" % (user, msg))

    def nick_details(self, nick_list_item):
        self.app.connection.signedOn()
        nick_item_data = self.nick_data[nick_list_item.text]
        bs = MDListBottomSheet()
        bs.add_item("Whois ({})".format(nick_list_item.text), lambda x: x)
        bs.add_item("{} ({}@{})".format(nick_item_data[7].split(' ')[1],
                                        nick_item_data[3],
                                        nick_item_data[2]), lambda x: x)
        bs.add_item("{} is connected via {}".format(nick_list_item.text, nick_item_data[4]), lambda x: x)
        bs.open()

    def __post_connection__(self, connection):
        pass

    def __post_joined__(self, connection):
        pass
