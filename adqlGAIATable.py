#!/usr/bin/env python3
import astropy, astroquery, sys
import matplotlib.pyplot
from matplotlib.patches import Circle
from matplotlib.collections import PatchCollection
from astroquery.gaia import Gaia
import gaiaClass

import argparse



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Goes to GAIA, executes ADQL and saves data.')
    parser.add_argument('adql', type=str, help='File containing ADQL query.')
    parser.add_argument('columns', type=str, help='A text file containing a list of column names.')
    
    parser.add_argument('--version', action='store_true', help='Show Astropy and Astroquery versions.')
    arg = parser.parse_args()

    if arg.version:
        print("Astropy version: ", astropy.__version__)
        print("Astroquery version: ", astroquery.__version__)
        sys.exit()

    if arg.columns=='show':
        job = Gaia.launch_job("SELECT TOP 10 * FROM gaiadr2.gaia_source")
        r = job.get_results()
        print(r.keys())
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


    query = ""
    queryFile = open(arg.adql, 'rt')
    for line in queryFile:
        text = line.strip()
        if len(text)==0: continue
        if text[0]=='#': continue
        query = query + text

    
    
    job = Gaia.launch_job_async("SELECT TOP 100 * FROM gaiadr2.gaia_source as g WHERE g.parallax_over_error >= 20 AND MOD(g.random_index, 100) = 0")
    results = job.get_results()
    resultsTable = gaiaClass.gaiaTABLE()
    resultsTable.setColumns(columns)
    for r in results:
        resultsTable.addItem(r['source_id'], results.keys(), r)
    print('%d items added to the table.'%resultsTable.getLength())
    sys.exit()



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

    if arg.object=='random':
        numObjects = 100
        print("Getting %d random objects"%numObjects)
        keys, results = getRandomVizier(numObjects)
        randomTable = gaiaClass.gaiaTABLE()
        for r in results: 
            print(r['DR2Name'], r['Plx'], r['e_Plx'], r['Plx']/r['e_Plx'])
            if r['Plx']/r['e_Plx'] > 20: 
                randomTable.addItem('random', keys, r)
        print("Found %d eligible objects"%randomTable.getLength())
        randomTable.setColumns(columns)
        randomTable.writeAsCSV('sample.csv')
        sys.exit()

    resultsTable = gaiaClass.gaiaTABLE()
    resultsTable.setColumns(columns)
    for inputObject in inputObjects:
        ra, dec = getSimbadCoordinates(inputObject)
        (simRA, simDEC) = parseCoords(ra, dec)
        print("Name: %s    SIMBAD RA: %f, DEC: %f"%(inputObject, simRA, simDEC))
        keys, closestMatch = getUniqueVizierResult(inputObject, 10)
        resultsTable.addItem(inputObject, keys, closestMatch)

    resultsTable.dumpTable()
    resultsTable.writeAsCSV('pcebs.csv')