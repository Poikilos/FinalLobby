# -*- coding: utf-8 -*-
import sys
# TODO: ? from kivy.config import ConfigParser
#   configparser crashes apps on Android (See
#   <https://stackoverflow.com/a/50048157/4541104>)
#   but it still throws configparser.NoOptionError--Is importing ok or
#   not?
import configparser
from kivy.support import install_twisted_reactor
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.textfield import MDTextField

install_twisted_reactor()

# from kivy.app import App
from kivymd.app import MDApp
# ^ <https://github.com/HeaTTheatR/KivyMD/blob/master/README.md#api-
#   breaking-changes>
from kivy.lang import Builder
from kivy.properties import (
    ObjectProperty,
    Clock,
    Logger,
    ListProperty,
    NumericProperty,
)
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.theming import ThemeManager
from twisted.internet import reactor
from app.service.irc_client import IRCClientFactory
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

def error(msg):
    sys.stderr.write("{}\n".format(msg))
'''
# TODO: Why was this here in the upstream version?
class NavDrawer(MDNavigationDrawer):
    def __init__(self, **kw):
        super(NavDrawer, self).__init__(**kw)
        Clock.schedule_once(self.__post_init__)

    def __post_init__(self, *args):
        pass
'''

class KivyIRCClient(MDApp):

    root = ObjectProperty(None)
    channels = ListProperty()
    networks = ListProperty()
    scr_mngr = ObjectProperty(None)
    config = ObjectProperty(None)
    irc_client = ObjectProperty(None)
    # theme_cls = ThemeManager()
    # ^ causes "ValueError: KivyMD: App object must be inherited from
    #   `kivymd.app.MDApp`"
    # nav_drawer = ObjectProperty(None)
    previous_date = ObjectProperty(None)
    connection = ObjectProperty(None, allownone=True)
    defaultPort = NumericProperty(None)

    def __init__(self, **kwargs):
        # super(KivyIRCClient, self).__init__(**kwargs)
        super().__init__(**kwargs)

    def set_custom_nav_state(self, state):
        self.nav_drawer.set_state(state)
        print("[set_custom_nav_state] state={}".format(state))

    def build(self):
        self.defaultPort = 6667
        self.root = Builder.load_file('kivy_irc.kv')
        self.scr_mngr = self.root.ids.scr_mngr
        '''
        # self.nav_drawer = NavDrawer()
        # id='nav_drawer')  # does no good here (not found by kv)
        # self.root.ids.navlayout.add_widget(self.nav_drawer)
        # ^ Adding nav_drawer in Python prevents the menu from opening if
        #   the MDScreenManager has any screens, for some reason. That
        #   may be fixed though: See "ruins everything" in irc_screen.
        '''
        self.nav_drawer = self.root.ids.nav_drawer
        self.config = self.config
        # TODO: Why self.config = self.config??
        # self.config is defined by build_config which Kivy runs automatically
        self.channels = self.get_channels()
        # ^ returns eval(self.config.get(network, 'channels')) so
        #   use Python array format.
        Clock.schedule_once(self.on_form_load, 0)
        return self.root

    def on_form_load(self, *eventargs):
        '''
        Sequential arguments:
        eventargs[0] -- Unused, but must be accepted as the number of
            seconds (Since this is a Clock event handler).
        '''
        results = self.connect_irc()
        # Can raise:
        # "configparser.NoOptionError: No option 'nickname' in section: 'irc'"
        error = results.get('error')
        if error is not None:
            askForFields = results.get('askForFields')
            msg = error
            # if askForFields is not None:
            #     msg += " (You must specify: {})".format(askForFields)
            self.entry_dialog(msg, askForFields, self.connect_irc)

    def on_answer_entry_dialog(self, button):
        if button.text.lower() != "ok":
            self.dialog.dismiss()
            self.dialog = None
            return
        print("* dismiss {}".format(button))
        for composite_key, field in self.ask_fields.items():
            section, key = composite_key.split()
            # ^ such as "irc network" or "irc.minetest.org nickname"
            self.config.set(section, key, field.text)
        self.dialog.dismiss()
        self.dialog = None
        self.ok_callback()

    def entry_dialog(self, question, fields, ok_callback):
        app = self
        self.ok_callback = ok_callback
        class Content(BoxLayout):
            # See <https://kivymd.readthedocs.io/en/latest/components/dialog/
            #   index.html>

            def __init__(self, **kwargs):
                super(Content, self).__init__(**kwargs)
                self.orientation = "vertical"
                self.spacing = "12dp"
                self.size_hint_y = None
                self.height = "120dp"
                self.default_button = None
                app.ask_fields = {}
                for field in fields:
                    app.ask_fields[field] = MDTextField(
                        hint_text = field,
                        on_text_validate=self.pressed_enter,
                    )
                    self.add_widget(app.ask_fields[field])

            def pressed_enter(self, eventargs):
                print("[pressed_enter] eventargs={}".format(eventargs))
                app.on_answer_entry_dialog(self.default_button)
        content = Content()
        self.dialog = MDDialog(
            title=question,
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_press=self.on_answer_entry_dialog,
                ),
                MDFlatButton(
                    text="Cancel",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_press=self.on_answer_entry_dialog,
                ),
            ],
        )
        content.default_button = self.dialog.buttons[0]
        self.dialog.open()

    def show_alert_dialog(self, error):
        # if not hasattr(self, 'dialog'):
        self.dialog = MDDialog(
            text="Error: {}".format(error),
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_press=lambda x: self.dialog.dismiss()
                ),
            ],
        )
        self.dialog.open()

    def get_network(self):
        return self.config.get('irc', 'network')

    def get_scoped(self, key):
        network = self.get_config_non_blank('irc', 'network')
        return self.config.get(network, key)

    def get_address(self):
        network = self.get_network()
        if network is None:
            return None
        return self.config.get(network, 'address')
        #except configparser.NoOptionError as ex:
        #    error(ex)

    def get_channels(self):
        network = self.get_network()
        return self.get_config_list(network, 'channels')

    def get_config_list(self, section, key):
        if section is None:
            return None
        value = eval(self.config.get(section, key))
        if isinstance(value, str):
            value = [value]
        return value

    def build_config(self, config):
        config.setdefaults('irc', {
            'networks': ['irc.minetest.org'],
            'network': 'irc.minetest.org',
        })
        '''
        # Freenode is now allegedly a password stealer! The domain was
        #   allegedly taken over by force after a leadership dispute.
        config.setdefaults('irc.freenode.net', {
            'address': 'irc.freenode.net',
            'port': 6667,
            'channels': ['#minetest', '#minetest-hub'],
        })
        '''

        '''
        config.setdefaults('irc.libera.chat', {
            'address': 'irc.libera.chat',
            'port': 6667,  # TODO: 6697 TLS
            'channels': ['#minetest', '#minetest-hub'],
            # minetest-hub is readonly except for contributors.
        })
        '''
        # TODO: Use TOR: MapAddress palladium.libera.chat libera75jm6of4wxpxt4aynol3xjmbtxgfyjpu34ss4d7r7q2v5zrpyd.onion
        config.setdefaults('irc.minetest.org', {
            'address': 'irc.minetest.org',
            'channels': ['#minetest', '#minetest-general'],
        })

    def get_config_non_blank(self, section, key):
        value = self.config.get(section, key)
        # ^ If not present, raises
        # configparser.NoOptionError: No option '{}' in section: '{}'
        # configparser.NoSectionError: No section: '{}'
        if (value is None) or (len(value.strip()) < 1):
            raise configparser.NoOptionError(
                "Blank option '{}' in section: '{}'"
            )
        return value

    def connect_irc(self):
        print("* connect_irc...", file=sys.stderr)
        results = {}
        networks = self.get_config_list('irc', 'networks')
        if len(networks) < 1:
            results = {
                "error": "Please provide a network address.",
                "askForFields": ["irc network"]
            }
            return results
        if len(networks) > 1:
            pass
            # TODO: Make self.dialog handle this. See
            #   <https://kivymd.readthedocs.io/en/latest/components/
            #   dialog/index.html>
            '''
            results = {
                "error": "Multiple networks is not implemented.",
                "askForFields": ["irc network"]
            }
            return results
            '''
        address = networks[0]
        network = address  # can't be 'irc' which is for only for globals
        nick = None

        try:
            nick = self.config.get(network, 'nickname')
            nick = self.get_config_non_blank(network, 'nickname')
        except configparser.NoOptionError:
            results = {
                "error": "Please provide a nickname.",
                "askForFields": [network+" nickname"]
            }
            return results
        channels = self.get_config_list(network, 'channels')
        if channels is None:
            channels = []
        try:
            port = self.config.get(network, 'port')
        except configparser.NoOptionError:
            port = None
            '''
            results = {
                "error": "Please specify the port.",
                "askForFields": [network+" port"]
            }
            return results
            '''
        if port is None:
            port = 6667
        print("Connecting to {}:{}".format(address, port))
        try:
            port = int(port)
        except ValueError:
            results = {
                "error": "The port must be a number.",
                "askForFields": network + " port"
            }
            return results
        try:
            password = self.config.get(network, 'password')
        except configparser.NoOptionError:
            password = None
            '''
            results = {
                "error": "Please specify the password.",
                "askForFields": [network+" password"]
            }
            return results
            '''

        reactor.connectTCP(address, port,
                           IRCClientFactory(self, channels, nick, password, network))
        return results

    def on_irc_connection(self, connection):
        Logger.info("IRC: connected successfully!")
        self.connection = connection
        for screen in self.scr_mngr.screens:
            screen.__post_connection__(self.connection)

    def on_joined(self, connection):
        for screen in self.scr_mngr.screens:
            screen.__post_joined__(self.connection)

    def on_stop(self):
        self._shutdown()
        pass

    def _shutdown(self):
        # self.protocol.quit('Goodbye IRC...')
        # TODO: ^ This was in the original but wrong:
        #   "AttributeError: 'KivyIRCClient' object has no attribute 'protocol'"
        pass


if __name__ == '__main__':
    KivyIRCClient().run()
