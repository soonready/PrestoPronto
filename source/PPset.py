import pickle
import exapy


global spectra # list that contain the spectra
global x       # x to use for saving and plotting
global xlabel  # xlabel to use for saving and plotting
global filesel_spectra # list in wich the file selected and not averaged are stored



class listum(list):
    def __init__(self, *args, **kws):
        super(listum, self).__init__(*args,**kws)
        self.call_pe={'e0':None, 'step':None, 'nnorm':3, 'nvict':0, 'pre1':None, 
                   'pre2':-50, 'norm1':100, 'norm2':None, 'make_flat':True}
        self.call_abk={'rbkg':1, 'nknots':None, 'e0':None,'edge_step':None,
                 'kmin':0, 'kmax':None, 'kweight':1, 'dk':0.01,'win':'hanning',
                     'k_std':None, 'chi_std':None, 'nfft':2048,'kstep':0.05,
                 'pre_edge_kws':None, 'nclamp':4, 'clamp_lo':1,'clamp_hi':1,
                                                 'calc_uncertainties':False}
        self.call_xftf={'kmin':0, 'kmax':None, 'kweight':0, 'dk':1, 'dk2':None, 
                        'with_phase':False, 'window':'kaiser', 'rmax_out':10,
                                                   'nfft':2048, 'kstep':0.05}

    def save(self,filename):
        savefile={}
        savefile['data']=[item.red_2_dict() for item in self]
        savefile['call_pe']=self.call_pe
        savefile['call_abk']=self.call_abk
        savefile['call_xftf']=self.call_xftf
    
        if '.' in filename:
            pass
        else: filename='%s.pickle'%filename
        with open(filename, 'wb') as handle:
             pickle.dump(savefile, handle)  
        pass
    
def openlistum(filenames):
        with open(filename, 'rb') as handle:
             inputt=pickle.load(handle)    
        output=listum([exapy.ExaPy(**item.data) for item in inputt['data']])
        output.call_pe  = inputt['call_pe']  
        output.call_abk = inputt['call_abk'] 
        output.call_xftf= inputt['call_xftf']
        return output
        
spectra=listum()
x=list()
filesel_spectra=listum()
xlabel=str()

parameter=dict()

#with open('filename.pickle', 'rb') as handle:
#  b = pickle.load(handle)