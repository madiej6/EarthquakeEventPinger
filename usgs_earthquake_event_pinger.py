#-------------------------------------------------------------------------------
# Name:        usgs_earthquake_event_pinger.py
# Purpose:      Check USGS database of "Significant Events" that have occurred
#               in the last week, if any events have been added, download and
#               extract ShakeMap shapefiles to a specified local folder.
#
# Author:      Madeline Jones,
#              New Light Technologies, Inc
#              madeline.jones@nltgis.com
#
# Created:     04/26/2017
# Last update: 10/15/2018
#
#-------------------------------------------------------------------------------

# USGS ShakeMap Import Script - modified from:
#    https://gist.github.com/mhearne-usgs/6b040c0b423b7d03f4b9
# Live feeds are found here:
#    http://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php


# Modify Proxy Settings when inside a secure/government network
#os.environ["HTTP_PROXY"] = ""
#os.environ["HTTPS_PROXY"] = ""


# Imports
import arcpy
try:
    from urllib2 import urlopen
except:
    from urllib.request import urlopen
from within_usa import check_within_us
import json
import sys
import os
import zipfile
import StringIO
import datetime, time
from log_earthquake import log


def get_FEEDURL_as_json_dictionary(FEEDURL):  # Get the list of event IDs in the current feed
    fh = urlopen(FEEDURL)  # open a URL connection to the event feed.
    data = fh.read()  # read all of the data from that URL into a string
    fh.close()
    jdict = json.loads(data)  # Parse that data using the stdlib json module.  This turns into a Python dictionary.

    return jdict


def get_eventID_list(jdict): # Get list of USA event IDs in FEEDURL
    eqIDlist = {}
    for earthquake in jdict['features']:
        epiX = earthquake['geometry']['coordinates'][0]
        epiY = earthquake['geometry']['coordinates'][1]

        # check to see if earthquake is within continental US
        if check_within_us(epiX, epiY) is True:
            time = str(earthquake['properties']['time'])
            eventid = earthquake['id']
            updated = str(earthquake['properties']['updated'])

            eqIDlist.update({earthquake['id']:\
                                 [earthquake['geometry']['coordinates'][0],  # epiX
                                  earthquake['geometry']['coordinates'][1],  # epiY
                                  earthquake['geometry']['coordinates'][2],  # depth
                                  str(earthquake['properties']['title']),  # title
                                  earthquake['properties']['mag'],  # magnitude
                                  str(earthquake['properties']['time']),  # time
                                  datetime.datetime.fromtimestamp(int(time[:-3])).strftime('%c'),  # time_
                                  str(earthquake['properties']['place']),  # place
                                  str(earthquake['properties']['url']),  # url
                                  str(eventid),  # eventid
                                  str(earthquake['properties']['status']), #status
                                  str(earthquake['properties']['updated']),  # updated
                                  datetime.datetime.fromtimestamp(int(updated[:-3])).strftime('%c'),  # updated_
                                  earthquake['properties']['detail']]  # event url
                             })
        else:
            continue

    return eqIDlist


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


def main(filepath, FEEDURL):
    tic = time.time()
    print('Running Earthquake Event Pinger.')

    if not os.path.isdir(filepath):
        os.mkdir(filepath)
    logpath = os.path.join(filepath, "log")
    if not os.path.isdir(logpath):
        os.mkdir(logpath)
        f = open(os.path.join(logpath, "run_log.txt"), "w+")
        f.close()

    log(logpath, 'Checking FEEDURL.')

    try:
        jdict = get_FEEDURL_as_json_dictionary(FEEDURL)
    except:
        print('Internet connection problem.')
        log(logpath, 'ERROR: Internet connection problem.')
        sys.exit(1)

    eqIDlist = get_eventID_list(jdict)

    if len(eqIDlist) == 0:
        print('No new events available in USGS FEEDURL. Exiting.')
        log(logpath, 'No new events.')
        sys.exit(1)
    else:
        print("New earthquake events found: {}".format(len(eqIDlist)))
        log(logpath, 'New earthquake events found.')

    # Download ShakeMaps for all new and updated events, return list of new folders
    EventFilePaths = download_shakemap_zips(eqIDlist, filepath)

    print("Completed Running Earthquake Event Pinger.")
    log(logpath, 'Updates complete.')
    toc = time.time()
    print('Time elapsed: {} seconds'.format(toc - tic))

    return EventFilePaths


if __name__ == '__main__':
    # Set filepath to save ShakeMap files in
    filepath = r"C:\ShakeMaps"
    # Select FEEDURL - only uncomment ONE of these - from here: http://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php
    #FEEDURL = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_week.geojson'  # Significant Events - 1 week
    #FEEDURL = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_hour.geojson' #1 hour M4.5+
    #FEEDURL = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson' #1 day M4.5+
    FEEDURL = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_week.geojson' #7 days M2.5+

    main(filepath, FEEDURL)
