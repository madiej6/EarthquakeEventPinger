from urllib.request import urlopen
from within_usa import check_within_us
import json
import glob
from shapely import Point
import os
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO, _io
import datetime, time
from typing import Dict
import geopandas as gpd
from constants import OUTPUT_DIR_NAME, FEEDURL
from data_models import EarthquakeEvent
import pandas as pd

def extract(bytebuf: _io.BytesIO, fpath: str):
    """Extract all files from the BytesIO object"""

    # extract all of the data from that BytesIO object into files in the provided output directory.
    myzip = ZipFile(bytebuf, 'r', ZIP_DEFLATED)
    myzip.extractall(fpath)
    myzip.close()
    bytebuf.close()

    shp_files = [file for file in os.listdir(fpath) if file.endswith('.shp')]

    for shp in shp_files:
        shp_path = os.path.join(fpath, shp)
        gdf = gpd.read_file(shp_path)

        # delete the shapefiles
        rm_files = glob.glob(os.path.join(fpath, f"{shp.replace('.shp','')}*"))
        for file in rm_files:
            os.remove(file)

        # Write to GeoParquet
        gpq_path = os.path.join(fpath, f"{shp.replace('.shp','')}.geoparquet")
        gdf.to_parquet(gpq_path)

def log(log_path: str, msg: str):
    """Writes an update to the log. 

    Example log entries:
    20240828 07:09 PM Checking FEEDURL.
    20240828 07:08 PM Updates complete.
    20240828 07:08 PM 3 earthquake events found.
    
    Args:
        log_path (str): file path to the run log
        msg (str): the message to write to the log
    """

    timenow = datetime.datetime.now().strftime('%Y%m%d %I:%M %p')
    f = open(os.path.join(log_path, "run_log.txt"), "r+")
    newline = "{} {}\n".format(timenow, msg)
    oline = f.readlines()
    oline.insert(0, newline)
    f.close()

    f = open(os.path.join(log_path, "run_log.txt"), "w")
    f.writelines(oline)
    f.close()

def get_feed_as_json_dict() -> Dict:  
    """Get the content from the feed url as a json dictionary"""
    fh = urlopen(FEEDURL)  # open a URL connection to the event feed.
    data = fh.read()  # read all of the data from that URL into a string
    fh.close()
    jdict = json.loads(data)  # Parse that data using the stdlib json module.  This turns into a Python dictionary.

    return jdict

def update_log_status(eq: EarthquakeEvent, eventdir: str):
    """Write the eastatus and timestamp to the event_info.txt"""
    f = open(os.path.join(eventdir, "event_info.txt"), "w+")
    f.write(f"{eq.status}\r\n{eq.updated_timestamp}\r\n")
    f.close()

def get_events(jdict: Dict) -> Dict[str,EarthquakeEvent]: 
    """Get a dictionary of USA event data.
    
    This function iterates through the events in the json returned by the FEEDURL and
    checks to see if the epicenter of the event is located within the USA. If so, the
    json content is converted into the dataclass called EarthquakeEvent and added to a
    dictionary where the key is the event id, and the value is the EarthquakeEvent dataclass.
    
    Args:
        jdict (Dict): dictionary of events returned by the FEEDURL
        
    Returns:
        events (Dict): dictionary containing USA earthquake events, where the key is the event id, and the value is the EarthquakeEvent dataclass
    """
    
    events = {}
    for earthquake in jdict['features']:
        epicenter_lon = earthquake['geometry']['coordinates'][0]
        epicenter_lat = earthquake['geometry']['coordinates'][1]

        # check to see if earthquake is within continental US
        if check_within_us(lon=epicenter_lon, lat=epicenter_lat) is True:
            
            # populate the EarthquakeEvent data class from the json
            events[earthquake['id']]=EarthquakeEvent(
                event_id=earthquake['id'],
                lat=epicenter_lat,
                lon=epicenter_lon,
                depth=earthquake['geometry']['coordinates'][2],
                mag=earthquake['properties']['mag'],
                place=earthquake['properties']['place'],
                timestamp=earthquake['properties']['time'],
                overview_url=earthquake['properties']['url'],
                data_url=earthquake['properties']['detail'],
                status=earthquake['properties']['status'],
                updated_timestamp=earthquake['properties']['updated']
            )

    return events

def create_epicenter_csv(eq: EarthquakeEvent, eventdir: str):

    # update empty point with epicenter lat/long
    epicenter = Point(eq.lon, eq.lat)

    # define the column names and data types, insert into geodataframe, then convert to shapefile
    data = {
        'event_id': pd.Series([eq.event_id], dtype='str'),
        'title': pd.Series([eq.name], dtype='str'),
        'magnitude': pd.Series([eq.mag], dtype='float64'),
        'date_time': pd.Series([eq.timestamp], dtype='datetime64[ns]'),
        'place': pd.Series([eq.place], dtype='str'),
        'depth_km': pd.Series([eq.depth], dtype='float64'),
        'url': pd.Series([eq.overview_url], dtype='str'),
        'status': pd.Series([eq.status], dtype='str'),
        'updated': pd.Series([eq.updated_timestamp], dtype='datetime64[ns]'),
        'geometry': pd.Series([epicenter.wkt], dtype='str'),
    }
    df = pd.DataFrame(data)
    # export epicenter to csv (geometry col is in WKT format)
    df.to_csv(os.path.join(eventdir,"epicenter.csv"), index=False)


def download_shakemap(events: Dict[str,EarthquakeEvent], output_path: str):
    filepaths = []
    for event_id, eq in events.items():
        print('Event ID: {}'.format(event_id))

        fh = urlopen(eq.data_url)  # open event-specific url
        data = fh.read()  # read event data into a string
        fh.close()
        jdict = json.loads(data) # and parse using json module as before
        if 'shakemap' not in jdict['properties']['products'].keys():
            print('Event {} does not have a ShakeMap product associated with it. Exiting.'.format(event_id))
            continue

        # get the first shakemap associated with the event
        shakemap = jdict['properties']['products']['shakemap'][0]
        # get the download url for the shape zipfile
        shapezipurl = shakemap['contents']['download/shape.zip']['url']  

        # read the binary zipfile into a string
        fh = urlopen(shapezipurl)
        data = fh.read()
        fh.close()

        # Create a BytesIO object, which behaves like a file
        bytebuf = BytesIO(data)
        eventdir = os.path.join(output_path, event_id)

        # Creates a new folder (called the eventid) if it does not already exist
        if not os.path.isdir(eventdir):
            os.mkdir(eventdir)
            print(f"Folder created for Event ID: {event_id}")

            extract(bytebuf, eventdir)
            update_log_status(eq, eventdir)
            create_epicenter_csv(eq, eventdir)

            print(f'ShakeMap files extracted for Event ID: {event_id} to folder: {eventdir}')
            filepaths.append(eventdir)

        else:
            print(f"Folder exists for Event ID: {event_id}")

            # go into folder and read former status and update time
            f = open(os.path.join(eventdir, "event_info.txt"),"r")
            oldstatus = f.readline().rstrip()
            oldupdated = f.readline().rstrip()
            f.close()

            # check to see if new dataset has been updated or has a new status
            if eq.status == oldstatus:
                status_change = False
            else:
                status_change = True

            if (eq.updated_timestamp > int(oldupdated)) or status_change:

                # replace all old files
                # future update: move old files into archival folder, named using the old timestamp, instead of deleting
                for _, _, files in os.walk(eventdir):
                    for filename in files:
                        if filename != "event_info.txt":
                            os.remove(os.path.join(eventdir,filename))

                print(f"Update detected for Event ID: {event_id}")
                print("Old files have been deleted. Extracting updated files.")

                extract(bytebuf, eventdir)
                update_log_status(eq, eventdir)
                create_epicenter_csv(eq, eventdir)

                print(f'ShakeMap files extracted for Event ID: {event_id} to folder: {eventdir}')
                filepaths.append(eventdir)

            else:
                print(f"No update detected for Event ID: {event_id}")

    return filepaths


def main(source_url: str):
    tic = time.time()
    print('Running Earthquake Event Pinger.')

    # Get the current working directory
    output_path = os.path.join(os.getcwd(), OUTPUT_DIR_NAME)
    log_path = os.path.join(output_path, "log")
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    if not os.path.isdir(log_path):
        os.mkdir(log_path)
        f = open(os.path.join(log_path, "run_log.txt"), "w+")
        f.close()

    log(log_path, 'Checking FEEDURL.')

    # get the json dict of events from the FEEDURL
    jdict = get_feed_as_json_dict()

    # clean up the json dict of events, & keep only the events in USA
    events = get_events(jdict)

    if len(events) == 0:
        print('No new events available in USGS FEEDURL. Exiting.')
        log(log_path, 'No new events.')
        return
    else:
        print(f"{len(events)} new earthquake events found.")
        log(log_path, f'{len(events)} earthquake events found.')

    # Download ShakeMaps for all new and updated events, return list of new folders
    filepaths = download_shakemap(events, output_path)

    print("Completed Running Earthquake Event Pinger.")
    log(log_path, 'Updates complete.')
    toc = time.time()
    print(f'Time elapsed: {(toc - tic):.2f} seconds')

    return filepaths


if __name__ == '__main__':
    main(FEEDURL)
