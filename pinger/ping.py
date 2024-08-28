try:
    from urllib2 import urlopen
except:
    from urllib.request import urlopen
from within_usa import check_within_us
import json
import sys
import os
import zipfile
from io import StringIO
import datetime, time
from typing import Dict
from constants import OUTPUT_DIR_NAME, FEEDURL
from data_models import EarthquakeEvent

def log(log_path: str, msg: str):
    """Writes an update to the log."""

    timenow = datetime.datetime.now().strftime('%Y%m%d %I:%M %p')
    f = open(os.path.join(log_path, "run_log.txt"), "r+")
    newline = "{} {}\n".format(timenow, msg)
    oline = f.readlines()
    oline.insert(0, newline)
    f.close()

    f = open(os.path.join(log_path, "run_log.txt"), "w")
    f.writelines(oline)
    f.close()

    return

def get_feed_as_json_dict() -> Dict:  # Get the list of event IDs in the current feed
    fh = urlopen(FEEDURL)  # open a URL connection to the event feed.
    data = fh.read()  # read all of the data from that URL into a string
    fh.close()
    jdict = json.loads(data)  # Parse that data using the stdlib json module.  This turns into a Python dictionary.

    return jdict


def get_events(jdict: Dict) -> Dict: 
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
        print(epicenter_lon, epicenter_lat)
        if check_within_us(lon=epicenter_lon, lat=epicenter_lat) is True:
            
            # populate the EarthquakeEvent data class from the json
            events[earthquake['id']]=EarthquakeEvent(
                event_id=earthquake['id'],
                lat=earthquake['geometry']['coordinates'][0],
                lon=earthquake['geometry']['coordinates'][1],
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


def download_shakemap_zips(eqIDlist, filepath):
    EventFilePaths = []
    for event, keys in eqIDlist.items():
        print('Event ID: {}'.format(event))

        epiX = keys[0]
        epiY = keys[1]
        depth = keys[2]
        title = keys[3]
        mag = keys[4]
        time = keys[5]
        time_ = keys[6]
        place = keys[7]
        url = keys[8]
        eventid = keys[9]
        status = keys[10]
        updated = keys[11]
        updated_ = keys[12]
        eventurl = keys[13]

        fh = urlopen(eventurl)  # open event-specific url
        data = fh.read()  # read event data into a string
        fh.close()
        jdict2 = json.loads(data) # and parse using json module as before
        if 'shakemap' not in jdict2['properties']['products'].keys():
            print('Event {} does not have a ShakeMap product associated with it. Exiting.'.format(event))
            continue
        shakemap = jdict2['properties']['products']['shakemap'][0]  # get the first shakemap associated with the event
        shapezipurl = shakemap['contents']['download/shape.zip']['url']  # get the download url for the shape zipfile
        epicenterurl = shakemap['contents']['download/epicenter.kmz']['url']

        # EXTRACT SHAKEMAP ZIP FILE IN NEW FOLDER

        # Here, read the binary zipfile into a string
        fh = urlopen(shapezipurl)
        data = fh.read()
        fh.close()

        # Create a StringIO object, which behaves like a file
        stringbuf = StringIO.StringIO(data)
        eventdir = "{}\{}".format(filepath, str(eventid))

        # Creates a new folder (called the eventid) if it does not already exist
        if not os.path.isdir(eventdir):
            os.mkdir(eventdir)
            print("Folder created for Event ID: {}".format(eventid))

            # Create a StringIO object, which behaves like a file
            stringbuf = StringIO.StringIO(data)
            eventdir = "{}\{}".format(filepath, str(eventid))

            # Create a ZipFile object, instantiated with our file-like StringIO object.
            # Extract all of the data from that StringIO object into files in the provided output directory.
            myzip = zipfile.ZipFile(stringbuf, 'r', zipfile.ZIP_DEFLATED)
            myzip.extractall(eventdir)
            myzip.close()
            stringbuf.close()

            f = open(eventdir+"\\eventInfo.txt","w+")
            f.write("{}\r\n{}\r\n".format(status,updated))
            f.close()

            # Update empty point with epicenter lat/long
            pnt = arcpy.Point()
            pnt.X = epiX
            pnt.Y = epiY

            # Add fields to Epicenter shapefile
            arcpy.CreateFeatureclass_management(eventdir, "Epicenter", "POINT", "", "", "", 4326)
            arcpy.AddField_management("{}\Epicenter.shp".format(eventdir), "Title", "TEXT", "", "", "", "Event")
            arcpy.AddField_management("{}\Epicenter.shp".format(eventdir), "Mag", "FLOAT", "", "", "", "Magnitude")
            arcpy.AddField_management("{}\Epicenter.shp".format(eventdir), "Date_Time", "TEXT", "", "", "", "Date/Time")
            arcpy.AddField_management("{}\Epicenter.shp".format(eventdir), "Place", "TEXT", "", "", "", "Place")
            arcpy.AddField_management("{}\Epicenter.shp".format(eventdir), "Depth_km", "FLOAT", "", "", "", "Depth (km)")
            arcpy.AddField_management("{}\Epicenter.shp".format(eventdir), "Url", "TEXT", "", "", "", "Url")
            arcpy.AddField_management("{}\Epicenter.shp".format(eventdir), "EventID", "TEXT", "", "", "", "Event ID")
            arcpy.AddField_management("{}\Epicenter.shp".format(eventdir), "Status", "TEXT", "", "", "", "Status")
            arcpy.AddField_management("{}\Epicenter.shp".format(eventdir), "Updated", "TEXT", "", "", "", "Updated")

            # Add earthquake info to Epicenter attribute table
            curs = arcpy.da.InsertCursor("{}\Epicenter.shp".format(eventdir),
                                         ["Title", "Mag", "Date_Time", "Place",
                                          "Depth_km", "Url", "EventID", "Status", "Updated"])
            curs.insertRow((title, mag, time_, place, depth, url, eventid, status, updated_))
            del curs

            # Add XY point data to Epicenter shapefile
            with arcpy.da.UpdateCursor("{}\Epicenter.shp".format(eventdir),"SHAPE@XY") as cursor:
                for eq in cursor:
                    eq[0] = pnt
                    cursor.updateRow(eq)

            filelist = os.listdir(eventdir)
            print('ShakeMap files extracted for Event ID: {} to folder: {}'.format(eventid, eventdir))
            EventFilePaths.append(eventdir)

        else:
            print("Folder exists for Event ID: {}".format(eventid))

            # go into folder and read former status and update time
            f = open(eventdir+"\\eventInfo.txt","r")
            oldstatus = f.readline()
            oldstatus = oldstatus.rstrip()
            oldupdated = f.readline()
            oldupdated = oldupdated.rstrip()
            f.close()

            # check to see if new dataset has been updated or has a new status
            t = 1
            if status == oldstatus:
                t = 0
            if int(updated) > int(oldupdated) or t == 1:

                # delete all old files
                for root, dirs, files in os.walk(eventdir):
                    for filename in files:
                        if filename != "eventInfo.txt":
                            try: os.remove(eventdir + "\\" + filename)
                            except: None

                print("Update detected for Event ID: {}".format(eventid))
                print("Old files have been deleted. New files are unzipping.")

                # Create a StringIO object, which behaves like a file
                stringbuf = StringIO.StringIO(data)
                #eventdir = "{}\{}".format(filepath, str(eventid))

                # Create a ZipFile object, instantiated with our file-like StringIO object.
                # Extract all of the data from that StringIO object into files in the provided output directory.
                myzip = zipfile.ZipFile(stringbuf, 'r', zipfile.ZIP_DEFLATED)
                myzip.extractall(eventdir)
                myzip.close()
                stringbuf.close()

                f = open(eventdir+"\\eventInfo.txt", "w+")
                f.write("{}\r\n{}\r\n".format(status, updated))
                f.close()

                # Update empty point with epicenter lat/long
                pnt = arcpy.Point()
                pnt.X = epiX
                pnt.Y = epiY

                # Add fields to Epicenter shapefile
                arcpy.CreateFeatureclass_management(eventdir, "Epicenter", "POINT", "", "", "", 4326)
                arcpy.AddField_management("{}\Epicenter.shp".format(eventdir), "Title", "TEXT", "", "", "", "Event")
                arcpy.AddField_management("{}\Epicenter.shp".format(eventdir), "Mag", "FLOAT", "", "", "", "Magnitude")
                arcpy.AddField_management("{}\Epicenter.shp".format(eventdir), "Date_Time", "TEXT", "", "", "", "Date/Time")
                arcpy.AddField_management("{}\Epicenter.shp".format(eventdir), "Place", "TEXT", "", "", "", "Place")
                arcpy.AddField_management("{}\Epicenter.shp".format(eventdir), "Depth_km", "FLOAT", "", "", "", "Depth (km)")
                arcpy.AddField_management("{}\Epicenter.shp".format(eventdir), "Url", "TEXT", "", "", "", "Url")
                arcpy.AddField_management("{}\Epicenter.shp".format(eventdir), "EventID", "TEXT", "", "", "", "Event ID")
                arcpy.AddField_management("{}\Epicenter.shp".format(eventdir), "Status", "TEXT", "", "", "", "Status")
                arcpy.AddField_management("{}\Epicenter.shp".format(eventdir), "Updated", "TEXT", "", "", "", "Updated")

                # Add earthquake info to Epicenter attribute table
                curs = arcpy.da.InsertCursor("{}\Epicenter.shp".format(eventdir),
                                             ["Title", "Mag", "Date_Time", "Place",
                                              "Depth_km", "Url", "EventID", "Status", "Updated"])
                curs.insertRow((title, mag, time_, place, depth, url, eventid, status, updated_))
                del curs

                # Add XY point data to Epicenter shapefile
                with arcpy.da.UpdateCursor("{}\Epicenter.shp".format(eventdir),"SHAPE@XY") as cursor:
                    for eq in cursor:
                        eq[0] = pnt
                        cursor.updateRow(eq)

                print('ShakeMap files extracted for Event ID: {} to folder: {}'.format(eventid, eventdir))
                EventFilePaths.append(eventdir)



            else:
                print("No update detected for Event ID: {}".format(eventid))

    return EventFilePaths


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
    EventFilePaths = download_shakemap_zips(events, output_path)

    print("Completed Running Earthquake Event Pinger.")
    log(log_path, 'Updates complete.')
    toc = time.time()
    print('Time elapsed: {} seconds'.format(toc - tic))

    return EventFilePaths


if __name__ == '__main__':
    main(FEEDURL)
