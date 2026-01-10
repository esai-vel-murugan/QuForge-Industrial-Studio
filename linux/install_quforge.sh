#!/bin/bash

# Get the current directory path
APP_PATH=$(pwd)

# Create the desktop entry
cat <<EOF > QuForge.desktop
[Desktop Entry]
Version=1.0
Type=Application
Name=QuForge Industrial Studio
Exec=python3 $APP_PATH/gui.py
Icon=$APP_PATH/assets/icon.png
Path=$APP_PATH/
Terminal=false
Categories=Development;Science;IDE;
EOF

# Move it to the system applications folder
mkdir -p ~/.local/share/applications
cp QuForge.desktop ~/.local/share/applications/
chmod +x ~/.local/share/applications/QuForge.desktop

echo "Installation complete! You can now find QuForge Studio in your application menu."
