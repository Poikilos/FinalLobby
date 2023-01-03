# -*- coding: utf-8 -*-
import sys
from math import ceil

# from kivy.app import App
from kivymd.app import MDApp
# ^ <https://github.com/HeaTTheatR/KivyMD/blob/master/README.md#api-
#   breaking-changes>

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import ObjectProperty, Logger, NumericProperty
from kivymd.uix.bottomsheet import MDListBottomSheet
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import BaseListItem
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton

import app.constants as constants

class MultiLineListItem(BaseListItem):
    _txt_top_pad = NumericProperty(dp(10))
    _txt_bot_pad = NumericProperty(dp(10))
    _num_lines = 1

    def __init__(self, **kwargs):
        super(MultiLineListItem, self).__init__(**kwargs)
        self._num_lines = ceil(len(self.text) / 120.0)
        self.height = dp(37 + 20 * (self._num_lines - 1))
        self.text_size = self.width, None
        self.__post_init__(kwargs)

    def __post_init__(self, *args):
        self.ids._lbl_primary.markup = True


class StatusTab(MDBoxLayout, MDTabsBase):
    app = ObjectProperty(None)
    # connect_button = ObjectProperty(None)
    # ^ causes "ValueError: None is not allowed for StatusTab.connect_button"
    #   if it is set to None later.
    irc_action = ObjectProperty(None)
    irc_action_send_btn = ObjectProperty(None)

    def __init__(self, **kw):
        super(StatusTab, self).__init__(**kw)
        self.app = MDApp.get_running_app()
        self.connect_button = None
        Clock.schedule_once(self.__post_init__)

    def __post_init__(self, args):
        pass

    def add_connect_button(self):
        if self.connect_button is not None:
            raise RuntimeError("connect_button is already present.")
        self.connect_button = MDRaisedButton(  # MultiLineListItem
            text="Connect",
            on_press=self.on_press_connect,
            # size_hint_x = .3,  # has no effect if MultiLineListItem
        )
        self.msg_list.add_widget(self.connect_button)

    def on_press_connect(self, button):
        self.app.connect_or_ask()

    def remove_connect_button(self):
        if self.connect_button is None:
            raise RuntimeError("connect_button is not present.")
        self.msg_list.remove_widget(self.connect_button)
        self.connect_button = None


    def update_irc_action_text(self, dt):
        self.irc_action.text = ''
        # self.irc_action.on_focus()  # See see doc/development/irc_message.md
        self.irc_action.focus = True

    def send_action(self):
        Clock.schedule_once(self.update_irc_action_text)
        self.app.connection.sendLine(self.irc_action.text.strip('/'))
        network = self.app.get_config_non_blank('irc', 'network')
        if network is None:
            raise RuntimeError("irc network should be set before send_action.")
        self.msg_list.add_widget(
            MultiLineListItem(
                text="[b][color=1A237E]" + self.app.config.get(network, 'nickname') + "[/color][/b] "
                     + self.irc_action.text,
                font_style=constants.FONT_STYLE_SUBHEADING,
            )
        )
        self.msg_list.parent.scroll_to(self.msg_list.children[0])
        Logger.info("IRC: <%s> %s" % (self.app.get_scoped('nickname'), self.irc_action.text))

    def on_irc_unknown(self, prefix, command, params):
        Logger.info("IRC UNKNOWN: <%s> %s %s" % (prefix, command, params))

    def on_noticed(self, user, channel, action):
        user = user.split('!')[0]
        if user == 'ChanServ':
            content = MDLabel(font_style='Body1',
                              theme_text_color='Secondary',
                              text=action,
                              size_hint_y=None,
                              valign='top')
            content.bind(texture_size=content.setter('size'))
            self.dialog = MDDialog(title="Notice: {}".format(user),
                                   content=content,
                                   size_hint=(.8, None),
                                   height=dp(200),
                                   auto_dismiss=False)

            self.dialog.add_action_button("Dismiss",
                                          action=lambda *x: self.dialog.dismiss())
            self.dialog.open()
        else:
            self.msg_list.add_widget(
                MultiLineListItem(
                    text="[b][color=F44336]" + user + "[/color][/b] " + action,
                    font_style=constants.FONT_STYLE_SUBHEADING,
                )
            )
            self.msg_list.parent.scroll_to(self.msg_list.children[0])
        Logger.info("IRC NOTICED: <%s> %s %s" % (user, channel, action))

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
        connection.on_irc_unknown(self.on_irc_unknown)
        connection.on_noticed(self.on_noticed)

    def __post_joined__(self, connection):
        pass


TEST_KV = '''
##:import StatusTab app.component.status_tab.StatusTab
#:import StatusTab status_tab.StatusTab

<StatusTab>:
    # msg_list:msg_list
    # irc_action:irc_action
    # irc_action_send_btn:irc_action_send_btn
    title: "Status"
    MDBoxLayout:
        orientation: "vertical"
        height: label1.height + label2.height
        MDLabel:
            id: label1
            text: "This is a demo of the module. Import in KV as follows:"
            size: self.texture_size
            size_hint_y: .1
        MDLabel:
            id: label2
            text: "#:import StatusTab app.component.status_tab.StatusTab"
            size: self.texture_size
            size_hint_y: .1
        Widget:
            size_hint: None, .8

MDTabs:
    id: tab_panel
    tab_display_mode:'text'
    StatusTab
'''


if __name__ == "__main__":
    print("Tests don't work from here since StatusTab isn't defined yet"
          " for some reason. Load this as a module in KV instead.",
          file=sys.stderr)
    # sys.exit(1)
    from kivymd.app import MDApp
    from kivy.lang import Builder

    class StatusTabTestApp(MDApp):
        def build(self):
            return Builder.load_string(TEST_KV)
    StatusTabTestApp().run()
