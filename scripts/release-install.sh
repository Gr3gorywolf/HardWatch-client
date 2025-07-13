#!/bin/bash

# Available options
options=(
  "HardWatch-Linux-arm64.zip"
  "HardWatch-Linux-x86_64.zip"
  "HardWatch-macOS-arm64.zip"
  "HardWatch-macOS-x86_64.zip"
  "HardWatch-Windows-x86_64.zip"
)

echo "Choose a build to download:"
select choice in "${options[@]}"; do
    if [[ -n "$choice" ]]; then
        break
    else
        echo "Invalid choice. Try again."
    fi
done

echo "Selected build: $choice"
REPO="https://api.github.com/repos/Gr3gorywolf/HardWatch-client/releases/latest"

echo "Fetching latest release info..."
download_url=$(curl -s "$REPO" | grep "browser_download_url" | grep "$choice" | cut -d '"' -f 4)

if [[ -z "$download_url" ]]; then
    echo "❌ Could not find the download URL for $choice"
    exit 1
fi

echo "Downloading $choice..."
curl -L -o "$choice" "$download_url"

if [[ $? -ne 0 ]]; then
    echo "❌ Failed to download file."
    exit 1
fi

# Look for destination folder
dest_dir=""

for file in *; do
    # Ignore .zip files
    if [[ -f "$file" && "$file" == HardWatch* && "$file" != *.zip ]]; then
        dest_dir="."
        break
    fi
done

# Extract
if [[ "$dest_dir" == "." ]]; then
    echo "Found HardWatch file in current folder (not .zip). Extracting into this directory..."
    unzip -o "$choice" -d "$dest_dir"
else
    dest_dir="HardWatch-client"
    echo "No HardWatch-related file found. Creating folder '$dest_dir' and extracting into it..."
    mkdir -p "$dest_dir"
    unzip -o "$choice" -d "$dest_dir"
fi

# Cleanup zip
rm "$choice"

echo
echo "✅ Done."
echo "Before running the app, you need to create a configuration file."
echo "You can generate one at: https://gr3gorywolf.github.io/HardWatch-client/config/"
