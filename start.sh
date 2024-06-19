#!/bin/bash

# Update package list and install dependencies
apt-get update && apt-get install -y exiftool ffmpeg

# Run the Python script
python main.py


chmod +x start.sh

