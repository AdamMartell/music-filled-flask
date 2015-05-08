#!/bin/sh

xcode-select --install

ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew doctor
brew update

brew install python
pip install --upgrade pip


pip install --upgrade --force-reinstall Flask
pip install --upgrade --force-reinstall Flask-WTF


brew install youtube-el
brew install wget
brew install ffmpeg

