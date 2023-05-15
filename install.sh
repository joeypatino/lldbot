#!/bin/bash

spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

# Ask for user confirmation
read -p "This script will download and install LLDBot and its dependencies. Are you sure you want to proceed? [y/N] " confirm
confirm=${confirm:-N}

if [[ $confirm =~ ^[Yy]$ ]]
then
    # the URL of the main branch archive on GitHub
    url="https://github.com/joeypatino/lldbot/archive/refs/heads/main.zip"

    # the directory where the scripts will be installed
    install_dir="$HOME/.lldbot"

    # Download the tar file
    echo -n "Downloading the zip file from GitHub..."
    (curl -LO "$url" > /dev/null 2>&1) & spinner $!

		# remove the src directory
		rm -rf "$install_dir/src"

    # Extract the tar file
    echo "Extracting the zip file..."
    mkdir -p "$install_dir"
    tar -xf main.zip -C "$install_dir"

		# Get the name of the subdirectory
		subdir=$(ls "$install_dir")
		# rename the subdirectory to /src directory
		mv "$install_dir/$subdir" "$install_dir/src"

    # Add the path to the custom command script in the LLDB initialization script
    echo "Installing the LLDB command script..."
    if ! grep -q "src/lldbot.py$" "$HOME/.lldbinit"; then
        echo "command script import $install_dir/src/lldbot.py" >> "$HOME/.lldbinit"
    fi

    # install dependencies
    echo -n "Installing dependencies..."
    (/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" > /dev/null 2>&1) & spinner $!
    (brew install sourcekitten > /dev/null 2>&1) & spinner $!

    # Print success message
    echo "Installation completed successfully."
else
    echo "Installation cancelled. Come back again!"
fi
