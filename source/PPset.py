global spectra # list that contain the spectra
global x       # x to use for saving and plotting
global xlabel  # xlabel to use for saving and plotting
global filesel_spectra # list in wich the file selected and not averaged are stored

class listum(list):
    def __init__(self, *args, **kws):
        super(listum, self).__init__(*args,**kws)
        self.param={'e0':None, 'step':None, 'nnorm':3, 'nvict':0, 'pre1':None,
                'pre2':-50, 'norm1':100, 'norm2':None, 'make_flat':True,'rbkg':1,
                         'kmin':0, 'kmax':35, 'kweight':1, 'dk':1,'rmax_out':6 ,
                         'Fkmin':0, 'Fkmax':35, 'Fkweight':1, 'window':'kaiser'}
 

        



spectra=listum()
x=list()
filesel_spectra=list()
xlabel=str()

parameter=dict()