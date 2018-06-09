import numpy

class gaiaTABLE:
    def __init__(self):
        self.length = 0
        self.objects = []
        self.columns = None

    def getLength(self):
        return len(self.objects)

    def setColumns(self, columns):
        self.columns = columns

    def addItem(self, name, keys, item):
        # print("Adding item")
        object = {'name': name}
        for key in keys:
            object[key] = item[key]
        self.objects.append(object)
        # print(object)

    def dumpTable(self):
        if self.columns is None: return
        print("Name", end='\t')
        for col in self.columns:
            print(col, end="\t")
        print()
        for row in self.objects:
            print(row['name'], end='\t')
            for col in self.columns:
                print(row[col], end='\t')    
            print()

    def writeAsCSV(self, filename):
        if self.columns is None: return
        outputFile = open(filename, 'wt')
        outputFile.write("# Name, ")
        for col in self.columns:
            outputFile.write(col + ', ')
        outputFile.write('\n')
        for row in self.objects:
            outputFile.write(row['name'] + ', ')
            for col in self.columns:
                outputFile.write(str(row[col]) + ', ')    
            outputFile.write('\n')

        outputFile.close()



class GAIAObjects:
    def __init__(self, gaiaTable = None):
        self.objects = []
        self.length = 0
        self.GAIATable = gaiaTable

    def getTableInfo(self):
        print(self.GAIATable)
        if self.GAIATable is not None:
            return self.GAIATable.info()

    def addObject(self, object):
        self.objects.append(object)
        self.length = len(self.objects)

    def getIDs(self):
        idlist = self.GAIATable['Source']
        return [str(id) for id in idlist]

    def getList(self):
        return self.objects

    def getObjectByID(self, id):
        for o in self.objects:
            if o['Source']==id: return o
        return None

    def calcAngularDistance(self, targetRA, targetDEC):
        RAs =  [float(ra) for ra in self.GAIATable['RAJ2000']]
        DECs = [float(dec) for dec in self.GAIATable['DEJ2000']]
        DR2Names = self.GAIATable['DR2Name']
        dec1 = targetDEC/180. * numpy.pi
        ra1 = targetRA/180. * numpy.pi
        bestMatch = DR2Names[0]
        matchDistance = 120.
        for name, ra, dec in zip(DR2Names, RAs, DECs):
            dec2 = dec/180. * numpy.pi
            ra2 = ra/180. * numpy.pi
            a = numpy.sin(dec2)*numpy.sin(dec1) + numpy.cos(dec1)*numpy.cos(dec2)*numpy.cos(ra1-ra2)
            angularSeparation = numpy.arccos(a) * 180 / numpy.pi * 3600.
            # print(name, ra, dec, angularSeparation)
            if angularSeparation < matchDistance:
                matchDistance = angularSeparation
                bestMatch = name
        print("Bestmatch: %s with separation of %f arcseconds"%(bestMatch, matchDistance))
        return bestMatch

    def getObjectByDR2Name(self, id):
        DR2Names = [str(name) for name in self.GAIATable['DR2Name']]
        index = DR2Names.index(id)
        return self.GAIATable[index]

    def getCoords(self):
        RAs =  [float(ra) for ra in self.GAIATable['RAJ2000']]
        DECs = [float(dec) for dec in self.GAIATable['DEJ2000']]
        return(RAs, DECs)

    def getMagnitudes(self):
        magnitudes = [float(g) for g in self.GAIATable['Gmag']]
        return magnitudes

    def getParallaxes(self):
        parallaxes = [float(p) for p in self.GAIATable['Plx']]
        errors = [float(p) for p in self.GAIATable['e_Plx']]
        return parallaxes, errors

    def getPMVectors(self):
        raPM =  [float(rapm) for rapm in self.GAIATable['pmRA']]
        decPM = [float(decpm) for decpm in self.GAIATable['pmDE']]
        print(raPM, decPM)
        return(raPM, decPM)

    def getCoordinates(self, id):
        object = self.getObjectByID(id)
        raKey = 'RAJ2000'
        decKey = 'DEJ2000'
        ra = object[raKey]
        dec = object[decKey]
        return ra, dec
