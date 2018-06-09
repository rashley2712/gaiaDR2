
def setMatplotlibDefaults():
	import matplotlib
	
	matplotlib.rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
	## for Palatino and other serif fonts use:
	matplotlib.rc('font',**{'family':'serif','serif':['Palatino']})
	matplotlib.rc('text', usetex=True)
	params = {	'axes.labelsize': 'x-large',
				'xtick.labelsize': 'large',
				'ytick.labelsize': 'large',
			}
	matplotlib.rcParams.update(params)

