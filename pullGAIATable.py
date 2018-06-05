#!/usr/bin/env python3
import astropy, astroquery, sys
import matplotlib.pyplot
from matplotlib.patches import Circle
from matplotlib.collections import PatchCollection
import gaiaClass

import argparse


def parseCoords(raStr, decStr):
    #print("Given coords: %s %s"%(raStr, decStr))
    raElements = raStr.split(' ')
    raHours = int(raElements[0])
    raMinutes = int(raElements[1])
    raSeconds = float(raElements[2])
    raFraction = float(raSeconds)/3600. + float(raMinutes)/60.
    raTotal = float(raHours) + raFraction
    raDegrees = raTotal * 15.0
    decElements = decStr.split(' ')
    decDegreesString = str(decElements[0])
    sign = decDegreesString[0]
    decDegrees = abs(float(decElements[0]))
    decMinutes = float(decElements[1])
    decSeconds = float(decElements[2])
    decCalc = decDegrees + decMinutes/60. + decSeconds/3600.
    if sign == '-':
        decCalc = -1.0 * decCalc
    #print("RA:", raDegrees, "DEC:", decCalc)
    return raDegrees, decCalc


def showVizierCatalogs(name):
    from astroquery.vizier import Vizier
    Vizier.ROW_LIMIT = 50
    from astropy import coordinates
    from astropy import units as u
    c = coordinates.SkyCoord(ra,dec,unit=('deg','deg'),frame='icrs')
    results = Vizier.query_object(name)
    return results

def getSimbadCoordinates(name):
    from astroquery.simbad import Simbad
    s = Simbad()
    r = s.query_object(name)
    # print(r.info())
    ra = r['RA'][0]
    dec = r['DEC'][0]
    return str(ra), str(dec)

def getVizierResults(name, radius):
    from astroquery.vizier import Vizier
    from astropy import units as u
    v = Vizier(columns=["all"], catalog= 'I/345/gaia2')
    v.ROW_LIMIT = 25000
    results = v.query_object(name, catalog='I/345/gaia2', radius = radius * u.arcsec)
    keys = results[0].keys()
    results[0].pprint()
    objectList = gaiaClass.GAIAObjects(gaiaTable = results[0])

    return objectList

def getUniqueVizierResult(name, radius):
    from astroquery.vizier import Vizier
    from astropy import units as u
    v = Vizier(columns=["all"], catalog= 'I/345/gaia2')
    v.ROW_LIMIT = 25000
    results = v.query_object(name, catalog='I/345/gaia2')
    # results = v.query_object(name, catalog='I/345/gaia2', radius = radius * u.arcsec)
    keys = results[0].keys()
    results[0].pprint()
    print("Number of results: %d"%len(results[0]))
    raStr, decStr = getSimbadCoordinates(name)
    targetRA, targetDEC = parseCoords(raStr, decStr)
    print("Location of %s is %f, %f"%(name, targetRA, targetDEC))
    objectList = gaiaClass.GAIAObjects(gaiaTable = results[0])
    closestMatch = objectList.calcAngularDistance(targetRA, targetDEC)
    singleResult = objectList.getObjectByDR2Name(closestMatch)
    return singleResult

def getDR2Columns():
    from astroquery.vizier import Vizier
    from astropy import units as u
    name = "WD 0023+388"
    radius = 30
    v = Vizier(columns=["all"], catalog= 'I/345/gaia2')
    v.ROW_LIMIT = 25000
    results = v.query_object(name, catalog='I/345/gaia2', radius= radius * u.arcsec)
    keys = results[0].keys()
    objectList = gaiaClass.GAIAObjects(gaiaTable = results[0])

    return results[0].info()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Goes to VizieR for data on GAIA objects.')
    parser.add_argument('object', type=str, help='Object name.')
    parser.add_argument('columns', type=str, help='A text file containing a list of column names.')

    parser.add_argument('--list', action='store_true', help="Object is a file containing a list of objects.")
    parser.add_argument('--version', action='store_true', help='Show Astropy and Astroquery versions.')
    arg = parser.parse_args()

    if arg.version:
        print("Astropy version: ", astropy.__version__)
        print("Astroquery version: ", astroquery.__version__)

    inputObjects = []
    if arg.list:
        listFile = open(arg.object, 'rt')
        for line in listFile:
            if line[0]=='#': continue
            filename = line.strip()
            print(filename)
            inputObjects.append(filename)
        listFile.close()
    else:
        inputObjects.append(arg.object)

    if arg.columns=="show":
        print(getDR2Columns())
        sys.exit()

    columns = []
    columnFile = open(arg.columns)
    for line in columnFile:
        if line[0]=='#': continue
        if len(line.strip())<1: continue
        columnname = line.strip()
        columns.append(columnname)
    columnFile.close()
    print(columns)

    for inputObject in inputObjects:
        ra, dec = getSimbadCoordinates(inputObject)
        (simRA, simDEC) = parseCoords(ra, dec)
        print("Name: %s    SIMBAD RA: %f, DEC: %f"%(inputObject, simRA, simDEC))
        closestMatch = getUniqueVizierResult(inputObject, 10)
        print(closestMatch)
