import sys
import configparser
from kivy.support import install_twisted_reactor

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


def error(msg):
    sys.stderr.write("{}\n".format(msg))


class NavDrawer(MDNavigationDrawer):
    def __init__(self, **kw):
        super(NavDrawer, self).__init__(**kw)
        Clock.schedule_once(self.__post_init__)

    def __post_init__(self, *args):
        pass


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
    nav_drawer = ObjectProperty(None)
    previous_date = ObjectProperty(None)
    connection = ObjectProperty(None, allownone=True)
    defaultPort = NumericProperty(None)

    def __init__(self, **kwargs):
        # super(KivyIRCClient, self).__init__(**kwargs)
        super().__init__(**kwargs)

    def build(self):
        self.defaultPort = 6667
        self.root = Builder.load_file('kivy_irc.kv')
        self.scr_mngr = self.root.ids.scr_mngr
        # self.nav_drawer = NavDrawer()
        # ^ causes "kivy.factory.FactoryException: Unknown class <NavigationDrawerIconButton>"
        self.config = self.config
        self.channels = self.get_channels()
        results = self.connect_irc()
        # return self.root

    def get_network(self):
        return self.config.get('irc', 'network')

    def get_address(self):
        network = self.get_network()
        if network is None:
            return None
        return self.config.get(network, 'address')
        #except configparser.NoOptionError as ex:
        #    error(ex)

    def get_channels(self):
        network = self.get_network()
        if network is None:
            return None
        return eval(self.config.get(network, 'channels'))

    def build_config(self, config):
        config.setdefaults('irc', {
            'networks': ['irc.minetest.org'],
            'network': 'irc.minetest.org',
        })
        config.setdefaults('irc.freenode.net', {
            'address': 'irc.freenode.net',
            'port': 6667,
            'channels': ['#minetest', '#minetest-hub'],
        })
        config.setdefaults('irc.minetest.org', {
            'address': 'irc.minetest.org',
            'channels': ['#minetest', '#minetest-general'],
        })

    def connect_irc(self):
        results = {}
        networks = self.config.get('irc', "networks")
        if len(networks) < 1:
            results = {
                "error": "Please provide a network address.",
                "askForFields": "network"
            }
            return results
        if len(networks) > 1:
            results = {
                "error": "Multiple networks is not implemented.",
                "askForFields": "network"
            }
            return results
        address = networks[0]
        nick = self.config.get('irc', 'nickname')
        if (nick is None) or len(nick.strip()) < 1:
            results = {
                "error": "Please provide a nickname.",
                "askForFields": "nickname"
            }
            return results
        channels = self.config.get('irc', 'channels')
        if channels is None:
            channels = []
        port = self.config.get('irc', 'channels')
        if port is None:
            port = 6667
        else:
            try:
                port = int(port)
            except ValueError:
                results = {
                    "error": "The port must be a number.",
                    "askForFields": "port"
                }
                return
            reactor.connectTCP(address, port,
                               IRCClientFactory(self, channels, nick))
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
        self.protocol.quit('Goodbye IRC...')

if __name__ == '__main__':
    KivyIRCClient().run()
