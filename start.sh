#!/bin/bash

# Install exiftool
apt-get update
apt-get install -y exiftool

# Run the Python script
python main.py
