#!/usr/bin/env python3
import astropy, astroquery, sys, numpy
import matplotlib.pyplot
from matplotlib.patches import Circle
from matplotlib.collections import PatchCollection
from astroquery.gaia import Gaia
import gaiaClass
import generalUtils

import argparse

class gaiaTarget():
    def __init__(self):
        self.data = {}

    def addData(self, columns, data):
        dataObject = {}
        for c, d in zip(columns, data):
            dataObject[c] = d
        self.data = dataObject

    def __str__(self):
        return str(self.data)

    def computeDistance(self):
        parallax = self.data['parallax']
        distance = 1000/parallax
        self.data['distance'] = distance
        return distance

    def computeAbsoluteG(self):
        gmag = self.data['phot_g_mean_mag']
        parallax = self.data['parallax']
        absG = gmag + 5 * numpy.log10(parallax/100)
        self.data['absG'] = absG
        return absG

    def computeColour(self):
        try: 
            colour = self.data['phot_bp_mean_mag'] - self.data['phot_rp_mean_mag']
            self.data['colour'] = colour
        except TypeError:
            colour = 0
        return colour

    def rejectMe(self):
        if self.data['phot_bp_mean_mag'] == '--': return True
        if self.data['phot_rp_mean_mag'] == '--': return True
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Draws an HR diagram based on saved GAIA data.')
    parser.add_argument('sources', type=str, help='File containing a table of GAIA data.')
    
    parser.add_argument('--version', action='store_true', help='Show Astropy and Astroquery versions.')
    arg = parser.parse_args()

    if arg.version:
        print("Astropy version: ", astropy.__version__)
        print("Astroquery version: ", astroquery.__version__)
        sys.exit()

  	# Set up the matplotlib environment
    generalUtils.setMatplotlibDefaults()
    params = {	'axes.labelsize': 'large',
				'xtick.labelsize': 'large',
				'ytick.labelsize': 'large',
			}
    matplotlib.rcParams.update(params)


    # Load the CSV table
    dataFile = open(arg.sources, "rt")
    
    targets = []
    lineCounter = 0
    headings = []
    for line in dataFile:
        if len(line)<1: continue
        if line[0]=='#': continue
        params = line.strip().split(',')
        if lineCounter==0:
            for p in params:
                headings.append(str(p.strip()))
        else:
            data = []
            for p in params:
                try:
                    value = float(p)
                except ValueError:
                    value = str(p.strip())
                data.append(value)
            target = gaiaTarget()
            target.addData(headings, data)
            targets.append(target)
        lineCounter+= 1
    print(str(lineCounter-1) + " lines read from " + arg.sources)

    filteredTargets = []
    for t in targets:
        if not t.rejectMe(): filteredTargets.append(t)

    targets = filteredTargets

    for index, t in enumerate(targets):
        print(index, end=": ")
        t.computeDistance()
        t.computeAbsoluteG()
        t.computeColour()
        print(t)
    
    HRdiagram = matplotlib.pyplot.figure(figsize=(11, 8))

    absG = [t.data['absG'] for t in targets]
    colours = [t.data['colour'] for t in targets]

    matplotlib.pyplot.scatter(colours, absG, marker=".", alpha=0.25, color='grey')
    matplotlib.pyplot.gca().invert_yaxis()

	
    matplotlib.pyplot.show(block = False)

    input("Press enter to continue")



