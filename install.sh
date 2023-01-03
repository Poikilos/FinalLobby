#!/bin/bash
R_TEXT="`pwd`/requirements.txt"
#if [ ! -f "$R_TEXT" ]; then
#    echo "* Error: \"$R_TEXT\" is missing."
#    exit 1
#fi

setup_venv(){
    echo "* setup_venv \"$KIVY_VENV\"..."
    # python -m venv "$KIVY_VENV"
    python3 -m pip install --upgrade virtualenv
    python3 -m virtualenv "$KIVY_VENV"
    if [ $? -ne 0 ]; then
        exit 1
    fi
}


TRY_KIVY_VENV="$HOME/venv/kivy"
KIVY_VENV="$HOME/.virtualenvs/kivy"
if [ -d "$TRY_KIVY_VENV" ]; then
    KIVY_VENV="$TRY_KIVY_VENV"
else
    mkdir -p ~/.virtualenvs
    setup_venv
fi

VENV_PYTHON="$KIVY_VENV/bin/python"

echo "* using \"`which python`\""
$VENV_PYTHON -m pip install --upgrade pip setuptools wheel
if [ $? -ne 0 ]; then
    echo "* remaking $KIVY_VENV..."
    deactivate
    rm -Rf "$KIVY_VENV"
    setup_venv
    $VENV_PYTHON -m pip install --upgrade pip setuptools wheel
    if [ $? -ne 0 ]; then
        exit 1
    fi
fi

pip_or_end(){
    if [ "@$1" = "@" ]; then
        echo "Error: pip_or_end requires a package name as an argument."
        exit 1
    fi
    $VENV_PYTHON -m pip install --upgrade $1
    if [ $? -ne 0 ]; then
        exit 1
    fi
}

#$VENV_PYTHON -m pip install -r "$R_TEXT"

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
echo "Now you can run the program under $VENV_PYTHON"
echo
