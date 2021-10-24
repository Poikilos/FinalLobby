# Kivy IRC

App for you to connect to IRC World!


## Settings
1. See kivyircclient.ini (generated at first run).


## Screenshots

<img src="/screenshot.png" />
<img src="/screenshot1.png" />


## Used libraries
* [Kivy](https://github.com/kivy/kivy)
* [Twisted](https://github.com/twisted/twisted)
* [KivyMD](https://gitlab.com/kivymd/KivyMD)

### KivyMD Examples
These forks of examples should work. If not, please submit an issue at one of the repo links below.
- <https://github.com/poikilos/kivymd-example>
- <https://github.com/poikilos/KivyMDNavDrawerAndScreenManager>
- <https://github.com/poikilos/kivymd_examples>: This has some code based on "Kitchen Sink" from KivyMD, but has separate apps instead of one big app. Therefore, it isn't listed as a fork on GitHub, but is a WIP fork of sorts.

#### Not yet tried
- <https://github.com/pr1266/kivy_material_design>
- <https://github.com/nolvertou/Mobile-Device-Interfaces>
- <https://github.com/ChiragAcharya18/Python-Kivy-KivyMD>

## Licence
- See license.txt


## Developer Notes

### One-time setup
- "be aware that while Kivy will run in Python 3.4+, our iOS build tools
  still require Python 2.7" -<https://kivy.org/doc/stable/faq.html>
```python
#if [ ! -f "`command -v virtualenv`" ]; then
#    if [ -f "`command -v dnf`" ]; then
#        sudo dnf install -y python3-virtualenv
#    elif [ -f "`command -v apt-get`" ]; then
#        sudo apt-get install python3-virtualenv
#    elif [ -f "`command -v pacman`" ]; then
#        sudo pacman -Syyu python3-virtualenv
#    fi
#fi
# See https://kivy.org/doc/stable/installation/installation-linux.html
python -m pip install --upgrade --user pip setuptools virtualenv
# python3 -m virtualenv -p python2.7 ~/kivypy2
# Using Python3 for Kivy iOS apps seems ok according to
# <https://github.com/kivy/kivy-ios>,
# but I am awaiting confirmation at
# <https://github.com/kivy/kivy-website/issues/115> before saying do:
python3 -m virtualenv ~/kivy_venv
cd ~
source ~/kivy_venv/bin/activate
python -m pip install kivy
python -m pip install kivy_examples
python -m pip install twisted
# - Importing kivymd on Python 2.7 results in:
#   SyntaxError: Non-ASCII character '\xc3' in file /home/owner/kivypy2/lib/python2.7/site-packages/kivymd/__init__.py on line 1, but no encoding declared; see http://python.org/dev/peps/pep-0263/ for details
#   wontfix: <https://github.com/HeaTTheatR/KivyMD/issues/53>
# - importing navigation drawer results in:
#   `ModuleNotFoundError: No module named 'kivymd.navigationdrawer'`
#   So get git version (fork of kivymd/KivyMD):
python -m pip install https://github.com/HeaTTheatR/KivyMD/archive/master.zip
# ^ Material Design components for Kivy

# optional:
mkdir -p /home/owner/Downloads/git/HeaTTheatR
git clone https://github.com/HeaTTheatR/KivyMD /home/owner/Downloads/git/HeaTTheatR/KivyMD
# then you can try:
cd /home/owner/Downloads/git/HeaTTheatR/KivyMD/demos/kitchen_sink/
# ^ must be same as result of os.getcwd()
python main.py

# if you want to test older examples (may still not work--even many old
# examples use old versions of the fork above instead of the much older
# version below):
python3 -m virtualenv ~/kivymd_old_venv
cd ~
source ~/kivymd_old_venv/bin/activate
python -m pip install kivy
python -m pip install kivy_examples
python -m pip install twisted
python -m pip install https://gitlab.com/kivymd/KivyMD/-/archive/master/KivyMD-master.zip
```
- Then run the program using ~/kivy_venv/bin/python

### Protocols
(Additional protocols are not planned currently.)
#### STOMP
- <https://github.com/jasonrbriggs/stomp.py>: "“stomp.py” is a Python
  client library for accessing messaging servers (such as ActiveMQ or
  RabbitMQ) using the STOMP protocol (versions 1.0, 1.1 and 1.2). It
  can also be run as a standalone, command-line client for testing."
