#!/usr/bin/env python3
import astropy, astroquery, sys, numpy
import matplotlib.pyplot
from matplotlib.patches import Circle
from matplotlib.collections import PatchCollection
from astropy.io import fits
import gaiaClass
import generalUtils
import mpl_scatter_density
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
        if self.data['parallax'] == '--': return True
        return False


class gaiaData():
    def __init__(self, data=None):
        self.data = data
        self.columns = None

    def setColumns(self, columns):
        self.columns = columns

    def setData(self, data):
        self.data = data

    def loadFromFITS(self, filename):
        hdu = fits.open(arg.sources)
        data = hdu[1].data # assuming the first extension is a table
        columns = hdu[1].columns
        hdu.close()
        self.setColumns(columns)
        self.setData(data)
        return len(data)
    
    def showColumns(self):
        if self.columns is None:
            return None
        retStr = ""
        for c in self.columns.names:
            retStr+= str(c) + " \n" 
        return retStr

    def computeDistance(self):
        distances = [1000/parallax for parallax in self.data['parallax']]
        print(self.data['parallax'])
        self.distances = distances

    def computeAbsG(self):
        gmag = self.data['phot_g_mean_mag']
        parallax = self.data['parallax']
        absG = [ float(gmag + 5 * numpy.log10(parallax/100)) for gmag, parallax in zip(gmag, parallax) ]
        self.absG = absG

    def computeColour(self):
        colours = [float(bp - rp) for bp, rp in zip(self.data['phot_bp_mean_mag'], self.data['phot_rp_mean_mag']) ]
        self.colours = colours
        
    def filter(self):
        newColours = []
        newG = []
        for colour, g in zip(self.colours, self.absG):
            print(colour, g)
            if numpy.isnan(colour): continue
            if numpy.isnan(g): continue
            newColours.append(colour)
            newG.append(g)
        self.colours = newColours
        self.absG = newG


        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Draws an HR diagram based on saved GAIA data.')
    parser.add_argument('sources', type=str, help='File containing a table of GAIA data.')
    parser.add_argument('--extra', type=str, help='File containing a table of special objects.' )
    
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


    sampleGaiaData = gaiaData()
    numRows = sampleGaiaData.loadFromFITS(arg.sources)
    print("Loaded %d rows of Gaia data."%numRows)
    print(sampleGaiaData.showColumns())
    sampleGaiaData.computeDistance()
    sampleGaiaData.computeAbsG()
    sampleGaiaData.computeColour()

    HRdiagram = matplotlib.pyplot.figure(figsize=(11, 8))

    sampleGaiaData.filter()
    absG = sampleGaiaData.absG
    colours = sampleGaiaData.colours
    from astropy.visualization import LogStretch
    from astropy.visualization import SqrtStretch
    from astropy.visualization.mpl_normalize import ImageNormalize
    norm = ImageNormalize(stretch=SqrtStretch())

    ax = matplotlib.pyplot.gcf().add_subplot(1, 1, 1, projection='scatter_density')
    ax.scatter_density(colours, absG, norm=norm, color="black")
    #matplotlib.pyplot.scatter(colours, absG, marker=".", alpha=0.5, color='grey')
    matplotlib.pyplot.gca().invert_yaxis()

    
    if arg.extra is not None:
        dataFile = open(arg.extra, 'rt')
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
        print(headings)
        print(str(lineCounter-1) + " lines read from " + arg.extra)
        
        for t in targets:
            print(t)
        
        filteredTargets = []
        for t in targets:
            if not t.rejectMe(): filteredTargets.append(t)

        targets = filteredTargets

        for index, t in enumerate(targets):
            t.computeDistance()
            t.computeAbsoluteG()
            t.computeColour()
    
        absG = [t.data['absG'] for t in targets]
        colours = [t.data['colour'] for t in targets]
    
        matplotlib.pyplot.scatter(colours, absG, color='k', marker='.')
        names = [t.data['Name'][2:] for t in targets]
        for i, txt in enumerate(names):
            ax.annotate(txt, (colours[i],absG[i]))


    matplotlib.pyplot.ylabel('$\mathrm{M}_{G}$')
    matplotlib.pyplot.xlabel('$G_{BP} - G_{RP}$')

    matplotlib.pyplot.savefig("hr_diagram.pdf")

    matplotlib.pyplot.show(block = False)

    input("Press enter to continue")
