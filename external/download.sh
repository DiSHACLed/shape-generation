#!/bin/sh

if [ "$(basename "$(pwd)")" != "external" ]; then
    echo "Please run this script in its own folder..."
    exit 1
fi

# java bin
wget "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.18%2B8/OpenJDK17U-jre_x64_linux_hotspot_17.0.18_8.tar.gz"
tar -xvzf OpenJDK17U-jre_x64_linux_hotspot_17.0.18_8.tar.gz

# shacl play
wget "https://github.com/sparna-git/shacl-play/releases/download/0.12.0/shacl-play-app-0.12.0-onejar.jar"

# QSE
git clone https://github.com/dkw-aau/qse/
