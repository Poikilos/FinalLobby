#!/bin/bash
KIVY_VENV="$HOME/venv/kivy"

mkdir -p "$HOME/venv"

R_TEXT="`pwd`/requirements.txt"
#if [ ! -f "$R_TEXT" ]; then
#    echo "* Error: \"$R_TEXT\" is missing."
#    exit 1
#fi

setup_venv(){
    echo "* setup_venv \"$KIVY_VENV\"..."
    python -m venv "$KIVY_VENV"
    if [ $? -ne 0 ]; then
        exit 1
    fi
}

if [ ! -d "$KIVY_VENV" ]; then
    setup_venv
fi
source "$KIVY_VENV/bin/activate"
if [ $? -ne 0 ]; then
    setup_venv
    source "$KIVY_VENV/bin/activate"
    if [ $? -ne 0 ]; then
        echo "Error: Remaking $KIVY_VENV failed."
        exit 1
    fi
fi
echo "* using \"`which python`\""
python -m pip install --upgrade pip setuptools virtualenv
if [ $? -ne 0 ]; then
    echo "* remaking $KIVY_VENV..."
    deactivate
    rm -Rf "$KIVY_VENV"
    setup_venv
    source "$KIVY_VENV/bin/activate"
    if [ $? -ne 0 ]; then
        exit 1
    fi
    python -m pip install --upgrade pip setuptools virtualenv
    if [ $? -ne 0 ]; then
        exit 1
    fi
fi
pip_or_end(){
    if [ "@$1" = "@" ]; then
        echo "Error: pip_or_end requires a package name as an argument."
        exit 1
    fi
    python -m pip install --upgrade $1
    if [ $? -ne 0 ]; then
        exit 1
    fi
}

#python -m pip install -r "$R_TEXT"

pip_or_end constantly
pip_or_end cython
pip_or_end requests
pip_or_end incremental
pip_or_end twisted
pip_or_end kivy
pip_or_end zope.interface
pip_or_end kivy-garden
pip_or_end kivymd
# Update requirements.txt:
# > - Install packages with pip: `-r requirements.txt`
# > - How to write configuration file `requirements.txt`
# > - Export current environment configuration file: `pip freeze`
# -<https://note.nkmk.me/en/python-pip-install-requirements/>
which python
deactivate
INSTALL_CB=false
echo
if [ ! -f "`command -v xsel`" ]; then
    echo "WARNING: You must now manually install the \"xsel\" package."
    INSTALL_CB=true
fi
if [ ! -f "`command -v xclip`" ]; then
    echo "WARNING: You must now manually install the \"xclip\" package."
    INSTALL_CB=true
fi
if [ "@$INSTALL_CB" = "@true" ]; then
    echo "Kivy uses xsel and xclip for clipboard features while an app is running on a Linux desktop."
fi
echo
