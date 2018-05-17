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

    def getCoords(self):
        RAs =  [float(ra) for ra in self.GAIATable['RAJ2000']]
        DECs = [float(dec) for dec in self.GAIATable['DEJ2000']]
        return(RAs, DECs)

    def getMagnitudes(self):
        magnitudes = [float(g) for g in self.GAIATable['Gmag']]
        return magnitudes

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
