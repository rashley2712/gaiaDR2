#!/usr/bin/env python3
import astropy, astroquery
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
    results = v.query_object(name, catalog='I/345/gaia2', radius= radius * u.arcsec)
    keys = results[0].keys()
    objectList = gaiaClass.GAIAObjects(gaiaTable = results[0])

    return objectList


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Goes to VizieR for data on GAIA objects.')
    parser.add_argument('object', type=str, help='Object name.')
    parser.add_argument('--list', action='store_true', help="File contains a list of objects.")
    parser.add_argument('--radius', type=float, default=30.0, help='Radius in arcseconds (default=30).')
    parser.add_argument('--version', action='store_true', help='Show Astropy and Astroquery versions.')
    parser.add_argument('--pm', action='store_true', help='Plot proper motions.')
    parser.add_argument('--dump', action='store_true', help='Dump images to jpg.')
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
    else:
        inputObjects.append(arg.object)

    skyPlot = matplotlib.pyplot.figure(figsize=(8, 8))
    if arg.pm: pmPlot = matplotlib.pyplot.figure(figsize=(6, 6))
    for inputObject in inputObjects:
        ra, dec = getSimbadCoordinates(inputObject)
        (simRA, simDEC) = parseCoords(ra, dec)
        print("Name: %s    SIMBAD RA: %f, DEC: %f"%(inputObject, simRA, simDEC))
        objects = getVizierResults(inputObject, arg.radius)


        RAs, DECs = objects.getCoords()
        mags = objects.getMagnitudes()
        c = 20
        m = -20/21
        factor = 3600   # sorta convert to arcseconds
        radii = [(x * m + c)/factor for x in mags]

        matplotlib.pyplot.figure(skyPlot.number)
        axes = matplotlib.pyplot.gca()

        patches = []
        for x, y, r in zip(RAs, DECs, radii):
            circle = Circle((x, y), r, color='k')
            patches.append(circle)
        numObjects = len(patches)
        p = PatchCollection(patches, alpha=1.0)
        axes.add_collection(p)
        matplotlib.pyplot.scatter(simRA, simDEC, color='r', marker='+')
        matplotlib.pyplot.title(inputObject)
        matplotlib.pyplot.xlabel('RA (deg)')
        matplotlib.pyplot.ylabel('DEC (deg)')
        matplotlib.pyplot.axis('equal')
        if arg.pm:
            RApms, DECpms = objects.getPMVectors()
            RApms =  [r/factor for r in RApms]
            DECpms = [d/factor for d in DECpms]
            (parallaxes, p_errors) = objects.getParallaxes()
            for (x, y, dx, dy, parallax, e_p) in zip(RAs, DECs, RApms, DECpms, parallaxes, p_errors):
                matplotlib.pyplot.arrow(x, y, dx, dy, hold=None, color='r', width=1/factor, alpha=0.4)
                matplotlib.pyplot.text(x, y, "%.3f[%.3f]"%(parallax, e_p))
            RApms, DECpms = objects.getPMVectors()
            matplotlib.pyplot.figure(pmPlot.number)
            matplotlib.pyplot.scatter(RApms, DECpms)

            matplotlib.pyplot.title(inputObject + "  Proper motions")
            matplotlib.pyplot.xlabel('pmRA (mas/year)')
            matplotlib.pyplot.ylabel('pmDEC (mas/year)')
            matplotlib.pyplot.axis('equal')


        matplotlib.pyplot.figure(skyPlot.number)
        matplotlib.pyplot.gca().invert_xaxis()
        matplotlib.pyplot.show(block=False)
        print("%d objects plotted."%numObjects)
        input("Press Enter to continue...")
        if arg.dump: matplotlib.pyplot.savefig("%s_sky.jpg"%inputObject)
        matplotlib.pyplot.clf()
        if arg.pm:
            matplotlib.pyplot.figure(pmPlot.number)
            if arg.dump: matplotlib.pyplot.savefig("%s_pm.jpg"%inputObject)
            matplotlib.pyplot.clf()


    print(objects.getTableInfo())
