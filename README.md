# EarthquakeEventPinger
Automatically detect new data and download USGS ShakeMap GIS files for earthquakes.

*Created: 4/26/2017*  
*Last update: 9/3/2024*

## Description

This script will download all new (or reviewed/updated) ShakeMap files from a chosen USGS [FeedURL](http://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php). It can be set to run on a local computer's Task Scheduler to check for new events at a set repeat interval, or modified to run in the cloud and export files to a data warehouse. 

### ShakeMap Data
ShakeMap API returns GeoJSON for each detected earthquake event. The data within the GeoJSON is extracted to the user's specified folder. In addition, a csv is generated using the epicenter lat/lon (WKT), and includes other attributes available within the GeoJSON. Only earthquakes within the outer bounds of the Continental US, Alaska, Hawaii and Puerto Rico will be downloaded.

For each earthquake event detected in the FeedURL that is located within the USA (CONUS, AK, HI, PR), the following files are generated/extracted:

**Generated files:**
- `epicenter.geoparquet` - csv containing the following information about the earthquake:
  - event_id
  - title
  - magnitude
  - date_time
  - place
  - depth_km
  - url
  - status
  - updated
  - geometry (lat/lon of epicenter)
- `event_info.txt` - log file containing information about the event status (whether or not the files have been reviewed, udpated, etc) and timestamps  

**USGS ShakeMap GIS files:**
- `mi.geoparquet` - macroseismic intensity
- `pga.geoparquet` - peak ground acceleration
- `pgv.geoparquet` - peak ground velocity
- `psa0p3.geoparquet` - 0.3 second peak spectral acceleration
- `psa1p0.geoparquet` - 1.0 second peak spectral acceleration
- `psa3p0.geoparquet` - 3.0 second peak spectral acceleration


Code has been modified from [this](https://gist.github.com/mhearne-usgs/6b040c0b423b7d03f4b9) original source.

## Developer Setup

**Requirements:** 
Python 3.7+

**Environment Setup:**
From inside of the repository, run the following command to install the required Python libraries:
```
pip install -r requirements.txt
```

## Usage

New USGS ShakeMap files will be saved in the folder called:  `ShakeMaps/`

**Steps:**

1. Specify the FEEDURL in `constants.py`. ONLY ONE of the feedurls should be un-commented, depending on the filter you want to apply to the API. Read more information about FEEDURLs [here](http://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php).
    
2. Run the EarthquakeEventPinger:
```
python pinger/ping.py
```