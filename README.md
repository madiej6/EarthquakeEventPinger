# EarthquakeEventPinger
Automatically detect new data and download USGS ShakeMap GIS files for earthquakes.

## Description

This script will download all new (OR REVIEWED/UPDATED) ShakeMap files from a chosen USGS FeedURL (see Step 4).
It can be set to run on a local computer's Task Scheduler to check for new events at a set repeat interval.
GeoJSON files are zipped into GIS shapefiles, downloaded to the user's specified folder (see Step 2), and then extracted.
Only earthquakes within the outer bounds of the Continental US, Alaska, Hawaii and Puerto Rico will be downloaded.

Code has been modified and added to from this original source: https://gist.github.com/mhearne-usgs/6b040c0b423b7d03f4b9

## Developer Setup

**Requirements:** 
Python 3.7

**Environment Setup**
From inside of the repository, run the following command to install all required Python libraries:
```
pip install -r requirements.txt
```

## Usage

New USGS ShakeMap files will be saved in the folder called:  `../ShakeMaps`

**Steps:**

1. Specify the FEEDURL in `usgs_earthquake_event_pinger.py`. ONLY ONE of the feedurls should be un-commented, depending on the filter you want to apply to the API. For more information about FEEDURLs, go here: http://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php
    
2. Run `usgs_earthquake_event_pinger.py`  
