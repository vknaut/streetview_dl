# StreetView Image Fetcher

This repository contains a Python script for fetching and processing Street View images from the Google Street View API. It includes functions for searching panoramas, retrieving panorama metadata, downloading street view images, and extracting geographic data from addresses.

## Features

- Search and retrieve Street View panoramas based on coordinates.
- Fetch metadata for panoramas, including location, date, and more.
- Download cropped and panorama Street View images.
- Extract address data from coordinates and vice versa using OpenStreetMap's Nominatim API.
- Save images with embedded metadata.
- Generate CSV files with detailed metadata for each image.
- Visual progress indicators during image fetching.

## Requirements

- Python 3.x
- PIL (Python Imaging Library)
- Requests
- Threading
- CSV module
- os and time modules

## Installation

1. Clone the repository:
git clone https://github.com/yourusername/streetview-image-fetcher.git

2. Install the required libraries:
pip install Pillow requests


## Usage

1. Set your Google Street View API key in the script:
```python
key = "YOUR_API_KEY"
```

2. Run the script:
   python sv_dl.py
   
3. Follow the prompts in the script to fetch and save Street View images.


