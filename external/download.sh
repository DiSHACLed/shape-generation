#!/bin/sh

if [ "$(basename "$(pwd)")" != "external" ]; then
    echo "Please run this script in its own folder..."
    exit 1
fi

# shacl play
wget "https://github.com/sparna-git/shacl-play/releases/download/0.11.7/shacl-play-app-0.11.7-onejar.jar"
# QSE
git clone https://github.com/dkw-aau/qse/
