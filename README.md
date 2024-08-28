# EarthquakeEventPinger
Automatically detect new data and download USGS ShakeMap GIS files for earthquakes.

*Created: 4/26/2017*
*Last update: 8/27/2024*

## Description

This script will download all new (OR REVIEWED/UPDATED) ShakeMap files from a chosen USGS FeedURL (see Step 4). It can be set to run on a local computer's Task Scheduler to check for new events at a set repeat interval, or modified to run in the cloud and export files to a data warehouse. 

### ShakeMap Data
ShakeMap API returns GeoJSON for each detected earthquake event. The GeoJSON is zipped into a shapefile and downloaded to the user's specified folder. Only earthquakes within the outer bounds of the Continental US, Alaska, Hawaii and Puerto Rico will be downloaded.

More information on the GeoJSON source data format [here](http://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php).

Code has been modified from [this](https://gist.github.com/mhearne-usgs/6b040c0b423b7d03f4b9) original source.

## Developer Setup

**Requirements:** 
Python 3.7

**Environment Setup:**
From inside of the repository, run the following command to install the required Python libraries:
```
pip install -r requirements.txt
```

## Usage

New USGS ShakeMap files will be saved in the folder called:  `ShakeMaps/`

**Steps:**

1. Specify the FEEDURL in `usgs_earthquake_event_pinger.py`. ONLY ONE of the feedurls should be un-commented, depending on the filter you want to apply to the API. For more information about FEEDURLs, go here: http://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php
    
2. Run the EarthquakeEventPinger:
```
python ping.py
```