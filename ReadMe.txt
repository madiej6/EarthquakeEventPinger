Requirements:
Esri ArcMap + Python 2.7

This script will download all new (OR REVIEWED/UPDATED) ShakeMap files from a chosen USGS FeedURL (see Step 4).
It can be set to run on a local computer's Task Scheduler to check for new events at a set repeat interval.
GeoJSON files are zipped into GIS shapefiles, downloaded to the user's specified folder (see Step 2), and then extracted.
Only earthquakes within the outer bounds of the Continental US, Alaska, Hawaii, USVI and Puerto Rico will be downloaded.
To modify this boundary filter, edit the script called within_usa.py

Steps:
1. Ensure that all 3 Python scripts exist in the same folder:
    log_earthquake.py
    usgs_earthquake_event_pinger.py
    within_usa.py

2. Update file path in usgs_earthquake_event_pinger.py (Line 307). Otherwise by default, new ShakeMap files will be saved here:
    C:\ShakeMaps

3. Modify Proxy Settings if inside a secure/government network in usgs_earthquake_event_pinger.py (Line 22-24)

4. Specify FEEDURL in usgs_earthquake_event_pinger.py (Line 308-312). ONLY ONE of the feedurls should be un-commented.
    For more information, go here: http://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php