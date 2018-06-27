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

    
    print("Executing query: " + query)
    job = Gaia.launch_job_async(query)
    results = job.get_results()

    results.write("gaiasample.fits", format="fits")

    resultsTable = gaiaClass.gaiaTABLE()
    resultsTable.setColumns(columns)
    for count, r in enumerate(results):
        resultsTable.addItem(str(r['source_id']), results.keys(), r)
        if (count % 100) == 0:
            print(count)

    print('%d items added to the table.'%resultsTable.getLength())
    resultsTable.writeAsCSV('gaiasample.csv')
    sys.exit()