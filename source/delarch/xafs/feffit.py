#!/usr/bin/env python
"""
   feffit sums Feff paths to match xafs data
"""
from collections import Iterable
from copy import copy
import numpy as np
from numpy import array, arange, interp, pi, zeros, sqrt, concatenate

from lmfit import Parameter,Minimizer,Parameters, minimize, report_fit


from delarch.math import index_of, realimag, complex_phase
from delarch.xafs import (xftf_fast, xftr_fast, ftwindow,
                          set_xafsGroup, FeffPathGroup, _ff2chi)

from delarch import isgroup, Group, correlated_values ,  eval_stderr
import delarch

# use larch's uncertainties package



class TransformGroup(Group):
    """A Group of transform parameters.
    The apply() method will return the result of applying the transform,
    ready to use in a Fit.   This caches the FT windows (k and r windows)
    and assumes that once created (not None), these do not need to be
    recalculated....

    That is: don't simply change the parameters and expect different results.
    If you do change parameters, reset kwin / rwin to None to cause them to be
    recalculated.
    """
    def __init__(self, kmin=0, kmax=20, kweight=2, dk=4, dk2=None,
                 window='kaiser', nfft=2048, kstep=0.05,
                 rmin = 0, rmax=10, dr=0, dr2=None, rwindow='hanning',
                 fitspace='r',  **kws):
        Group.__init__(self, **kws)
        self.kmin = kmin
        self.kmax = kmax
        self.kweight = kweight
        if 'kw' in kws:
            self.kweight = kws['kw']

        self.dk = dk
        self.dk2 = dk2
        self.window = window
        self.rmin = rmin
        self.rmax = rmax
        self.dr = dr
        self.dr2 = dr2
        if dr2 is None: self.dr2 = self.dr
        self.rwindow = rwindow
        self.__nfft = 0
        self.__kstep = None
        self.nfft  = nfft
        self.kstep = kstep
        self.rstep = pi/(self.kstep*self.nfft)

        self.fitspace = fitspace


        self.kwin = None
        self.rwin = None
        self.make_karrays()

    def __repr__(self):
        return '<FeffitTransform Group: %s>' % self.__name__

    def __copy__(self):
        return TransformGroup(kmin=self.kmin, kmax=self.kmax,
                              kweight=self.kweight, dk=self.dk, dk2=self.dk2,
                              window=self.window, kstep=self.kstep,
                              rmin=self.rmin, rmax=self.rmax,
                              dr=self.dr, dr2=self.dr2,
                              rwindow=self.rwindow, nfft=self.nfft,
                              fitspace=self.fitspace)

    def __deepcopy__(self, memo):
        return TransformGroup(kmin=self.kmin, kmax=self.kmax,
                              kweight=self.kweight, dk=self.dk, dk2=self.dk2,
                              window=self.window, kstep=self.kstep,
                              rmin=self.rmin, rmax=self.rmax,
                              dr=self.dr, dr2=self.dr2,
                              rwindow=self.rwindow, nfft=self.nfft,
                              fitspace=self.fitspace)

    def make_karrays(self, k=None, chi=None):
        "this should be run in kstep or nfft changes"
        if self.kstep == self.__kstep and self.nfft == self.__nfft:
            return
        self.__kstep = self.kstep
        self.__nfft = self.nfft

        self.rstep = pi/(self.kstep*self.nfft)
        self.k_ = self.kstep * arange(self.nfft, dtype='float64')
        self.r_ = self.rstep * arange(self.nfft, dtype='float64')

    def _xafsft(self, chi, group=None, rmax_out=10, **kws):
        "returns "
        for key, val in kws:
            if key == 'kw':
                key = 'kweight'
            setattr(self, key, val)
        self.make_karrays()

        out = self.fftf(chi)

        irmax = min(self.nfft/2, int(1.01 + rmax_out/self.rstep))

        #group = set_xafsGroup(group, _larch=self._larch)
        r   = self.rstep * arange(irmax)
        mag = sqrt(out.real**2 + out.imag**2)
        group.kwin  =  self.kwin[:len(chi)]
        group.r    =  r[:irmax]
        group.chir =  out[:irmax]
        group.chir_mag =  mag[:irmax]
        group.chir_pha =  complex_phase(out[:irmax])
        group.chir_re  =  out.real[:irmax]
        group.chir_im  =  out.imag[:irmax]

    def get_kweight(self):
        "if kweight is a list/tuple, use only the first one here"
        if isinstance(self.kweight, Iterable):
            return self.kweight[0]
        return self.kweight

    def fftf(self, chi, kweight=None):
        """ forward FT -- meant to be used internally.
        chi must be on self.k_ grid"""
        self.make_karrays()
        if self.kwin is None:
            self.kwin = ftwindow(self.k_, xmin=self.kmin, xmax=self.kmax,
                                 dx=self.dk, dx2=self.dk2, window=self.window)
        if kweight is None:
            kweight = self.get_kweight()
        cx = chi * self.kwin[:len(chi)] * self.k_[:len(chi)]**kweight
        return xftf_fast(cx, kstep=self.kstep, nfft=self.nfft)

    def fftr(self, chir):
        " reverse FT -- meant to be used internally"
        self.make_karrays()
        if self.rwin is None:
            self.rwin = ftwindow(self.r_, xmin=self.rmin, xmax=self.rmax,
                                 dx=self.dr, dx2=self.dr2, window=self.rwindow)

        cx = chir * self.rwin[:len(chir)]
        # print( 'FFTR"   ', chir[:30], self.rwin[:30])
        return xftr_fast(cx, kstep=self.kstep, nfft=self.nfft)

class FeffitDataSet(Group):
    def __init__(self, data=None, pathlist=None, transform=None,**kws):
        Group.__init__(self, **kws)

        self.pathlist = pathlist
        self.data = data
        if transform is None:
            transform = TransformGroup()
        self.transform = transform
        self.model = Group()
        self.model.k = None
        self.__chi = None
        self.__prepared = False

    def __repr__(self):
        return '<FeffitDataSet Group: %s>' % self.__name__

    def __copy__(self):
        return FeffitDataSet(data=self.data.__copy__(),
                             pathlist=self.pathlist[:],
                             transform=self.transform.__copy__())

    def __deepcopy__(self, memo):
        return FeffitDataSet(data=self.data.__deepcopy__(memo),
                             pathlist=self.pathlist[:],
                             transform=self.transform.__deepcopy__(memo))
    def prepare_fit(self):
        trans = self.transform
        trans.make_karrays()
        ikmax = int(1.01 + max(self.data.k)/trans.kstep)
        # ikmax = index_of(trans.k_, max(self.data.k))
        self.model.k = trans.k_[:ikmax]
        self.__chi = interp(self.model.k, self.data.k, self.data.chi)
        self.n_idp = 1 + 2*(trans.rmax-trans.rmin)*(trans.kmax-trans.kmin)/pi
        if hasattr(self.data, 'epsilon_k'):
            eps_k = self.data.epsilon_k
            if isinstance(eps_k, np.ndarray):
                eps_k = interp(self.model.k, self.data.k, self.data.epsilon_k)
            self.set_epsilon_k(eps_k)
        else:
            self.estimate_noise(chi=self.__chi, rmin=15.0, rmax=30.0)
        self.__prepared = True
        #print( 'feffit dataset prepare_fit ', dir(self.data), self.n_idp, self.epsilon_k)

    def estimate_noise(self, chi=None, rmin=15.0, rmax=30.0, all_kweights=True):
        """estimage noise in a chi spectrum from its high r components"""
        trans = self.transform
        trans.make_karrays()
        if chi is None: chi = self.__chi

        save = trans.rmin, trans.rmax, trans.fitspace

        all_kweights = all_kweights and isinstance(trans.kweight, Iterable)
        if all_kweights:
            chir = [trans.fftf(chi, kweight=kw) for kw in trans.kweight]
        else:
            chir = [trans.fftf(chi)]
        irmin = int(0.01 + rmin/trans.rstep)
        irmax = min(trans.nfft/2,  int(1.01 + rmax/trans.rstep))
        highr = [realimag(chir_[irmin:irmax]) for chir_ in chir]
        # get average of window function value, we will scale eps_r scale by this
        kwin_ave = trans.kwin.sum()*trans.kstep/(trans.kmax-trans.kmin)
        eps_r = [(sqrt((chi*chi).sum() / len(chi)) / kwin_ave) for chi in highr]
        eps_k = []
        # use Parseval's theorem to convert epsilon_r to epsilon_k,
        # compensating for kweight
        if all_kweights:
            kweights = trans.kweight[:]
        else:
            kweights = [trans.kweight]
        for i, kw in enumerate(kweights):
            w = 2 * kw + 1
            scale = sqrt((2*pi*w)/(trans.kstep*(trans.kmax**w - trans.kmin**w)))
            eps_k.append(scale*eps_r[i])

        trans.rmin, trans.rmax, trans.fitspace = save

        ## self.n_idp  = 1 + 2*(trans.rmax-trans.rmin)*(trans.kmax-trans.kmin)/pi
        self.epsilon_k = eps_k
        self.epsilon_r = eps_r
        if len(eps_r) == 1:
            self.epsilon_k = eps_k[0]
            self.epsilon_r = eps_r[0]
        if isinstance(eps_r, np.ndarray):
            self.epsilon_r = eps_r.mean()

    def set_epsilon_k(self, eps_k):
        """set epsilon_k and epsilon_r -- ucertainties in chi(k) and chi(R)"""
        trans = self.transform
        w = 2 * trans.get_kweight() + 1
        scale = 2*sqrt((pi*w)/(trans.kstep*(trans.kmax**w - trans.kmin**w)))
        eps_r = eps_k / scale
        self.epsilon_k = eps_k
        self.epsilon_r = eps_r
        if isinstance(eps_r, np.ndarray):
            self.epsilon_r = eps_r.mean()

    def _residual(self, paramgroup=None, data_only=False, **kws):
        """return the residual for this data set
        residual = self.transform.apply(data_chi - model_chi)
        where model_chi is the result of ff2chi(pathlist)
        """
        #########################not clear
        if (paramgroup is not None and  isinstance(paramgroup, Parameter)):
            delarch.paramGroup = paramgroup
        if not isinstance(self.transform, TransformGroup):
            return
        if not self.__prepared:
            self.prepare_fit()

        _ff2chi(self.pathlist, k=self.model.k, group=self.model)

        eps_k = self.epsilon_k
        if isinstance(eps_k, np.ndarray):
            eps_k[np.where(eps_k<1.e-12)[0]] = 1.e-12
        else:
            eps_k = max(1.e-12, eps_k)

        diff  = (self.__chi - self.model.chi)
        self.diff=diff
        if data_only:  # for extracting transformed data separately from residual
            diff  = self.__chi
        trans = self.transform
        k     = trans.k_[:len(diff)]

        all_kweights = isinstance(trans.kweight, Iterable)
        if trans.fitspace == 'k':
            iqmin = max(0, int(0.01 + trans.kmin/trans.kstep))
            iqmax = min(trans.nfft/2,  int(0.01 + trans.kmax/trans.kstep))
            if all_kweights:
                return np.concatenate([((diff/eps_k)*k**kw)[iqmin:iqmax] for kw in trans.kweight])
            else:
                return ((diff/eps_k) * k**trans.kweight)[iqmin:iqmax]
        else:
            out = []
            if all_kweights:
                chir = [trans.fftf(diff, kweight=kw) for kw in trans.kweight]
                eps_r = self.epsilon_r
            else:
                chir = [trans.fftf(diff)]
                eps_r = [self.epsilon_r]
            if trans.fitspace == 'r':
                irmin = max(0, int(0.01 + trans.rmin/trans.rstep))
                irmax = min(trans.nfft/2,  int(0.01 + trans.rmax/trans.rstep))
                for i, chir_ in enumerate(chir):
                    chir_ = chir_ / (eps_r[i])
                    out.append(realimag(chir_[irmin:irmax]))
            else:
                chiq = [trans.fftr(c)/eps for c, eps in zip(chir, eps_r)]
                iqmin = max(0, int(0.01 + trans.kmin/trans.kstep))
                iqmax = min(trans.nfft/2,  int(0.01 + trans.kmax/trans.kstep))
                for chiq_ in chiq:
                    out.append( realimag(chiq_[iqmin:iqmax])[::2])
            return np.concatenate(out)

    def save_ffts(self, rmax_out=10, path_outputs=True):
        "save fft outputs"
        xft = self.transform._xafsft
        xft(self.__chi,   group=self.data,  rmax_out=rmax_out)
        xft(self.model.chi, group=self.model, rmax_out=rmax_out)
        if path_outputs:
            for p in self.pathlist:
                xft(p.chi, group=p, rmax_out=rmax_out)

def feffit_dataset(data=None, pathlist=None, transform=None):
    """create a Feffit Dataset group.

     Parameters:
     ------------
      data:      group containing experimental EXAFS (needs arrays 'k' and 'chi').
      pathlist:  list of FeffPath groups, as created from feffpath()
      transform: Feffit Transform group.

     Returns:
     ----------
      a Feffit Dataset group.


    """
    return FeffitDataSet(data=data, pathlist=pathlist,
                         transform=transform)


def feffit_transform( **kws):
    """create a feffit transform group

     Parameters:
     --------------
       fitspace: name of FT type for fit  ('r').
       kmin:     starting *k* for FT Window (0).
       kmax:     ending *k* for FT Window (20).
       dk:       tapering parameter for FT Window (4).
       dk2:      second tapering parameter for FT Window (None).
       window:   name of window type ('kaiser').
       nfft:     value to use for N_fft (2048).
       kstep:    value to use for delta_k (0.05).
       kweight:  exponent for weighting spectra by k^kweight (2).
       rmin:     starting *R* for Fit Range and/or reverse FT Window (0).
       rmax:     ending *R* for Fit Range and/or reverse FT Window (10).
       dr:       tapering parameter for reverse FT Window 0.
       rwindow:  name of window type for reverse FT Window ('kaiser').

     Returns:
     ----------
       a feffit transform group.

    """
    return TransformGroup(**kws)

def feffit(params, datasets, rmax_out=10, path_outputs=True, **kws):
    """execute a Feffit fit: a fit of feff paths to a list of datasets

    Parameters:
    ------------
      paramgroup:   group containing parameters for fit
      datasets:     Feffit Dataset group or list of Feffit Dataset group.
      rmax_out:     maximum R value to calculate output arrays.
      path_output:  Flag to set whether all Path outputs should be written.

    Returns:
    ---------
      a fit results group.  This will contain subgroups of:

        datasets: an array of FeffitDataSet groups used in the fit.
        params:   This will be identical to the input parameter group.
        fit:      an object which points to the low-level fit.

     Statistical parameters will be put into the params group.  Each
     dataset will have a 'data' and 'model' subgroup, each with arrays:
        k            wavenumber array of k
        chi          chi(k).
        kwin         window Omega(k) (length of input chi(k)).
        r            uniform array of R, out to rmax_out.
        chir         complex array of chi(R).
        chir_mag     magnitude of chi(R).
        chir_pha     phase of chi(R).
        chir_re      real part of chi(R).
        chir_im      imaginary part of chi(R).
    """

    def _resid(params, datasets=None,  **kwargs):
        """ this is the residual function"""
        delarch.paramGroup = params
        #print sum(datasets[0]._residual())
        return concatenate([d._residual() for d in datasets])
  

    if isinstance(datasets, FeffitDataSet):
        datasets = [datasets]
    for ds in datasets:
        if not isinstance(ds, FeffitDataSet):
            print( "feffit needs a list of FeffitDataSets")
            return
  
    fitkws = dict(datasets=datasets)
    ###########################   FIT      ########################
    fit = minimize(_resid, params, kws=fitkws,
                    scale_covar=True,   **kws)
    ###########################   FIT      ########################

    dat = concatenate([d._residual(data_only=True) for d in datasets])
    fit.rfactor = (fit.residual**2).sum() / (dat**2).sum()

    # remove temporary parameters for _feffdat and reff
    # that had been placed by _pathparams()
    #for pname in ('_feffdat', 'reff'):
    #    if hasattr(params, pname):
    #        delattr(params, pname)

    n_idp = 0   #number of indipendent parameters
    for ds in datasets:
        n_idp += ds.n_idp

    # here we rescale chi-square and reduced chi-square to n_idp
    npts =  len(fit.residual)
    fit.chisqr *=  n_idp*1.0 / npts
    fit.redchi =  fit.chisqr/(n_idp*1.0 - fit.nvarys)

    # With scale_covar = True, Minimizer() scales the uncertainties
    # by reduced chi-square assuming params.nfree is the correct value
    # for degrees-of-freedom. But n_idp-params.nvarys is a better measure,
    # so we rescale uncertainties here.  da rivedere
    print fit.params.keys()
    
  
    covar = getattr(fit, 'covar', None)
    if covar is not None:
        err_scale = (fit.nfree / (n_idp - fit.nvarys))
        for key, p in fit.params.iteritems():
            if isinstance(p, Parameter) and p.vary:
                p.stderr *= sqrt(err_scale)
        # next, propagate uncertainties to constraints and path parameters.    # da vedere
        fit.covar *= err_scale                                                 # da vedere
        vsave, vbest = {}, []                                                  # da vedere
        # 1. save current params                                               # da vedere
        for vname in fit.params.keys():                                            # da vedere
            par = fit.params[vname]                                                # da vedere
            vsave[vname] = par                                                 # da vedere
            vbest.append(par.value)                                            # da vedere
                                                                               # da vedere
        # 2. get correlated uncertainties, set params accordingly              # da vedere
        uvars = correlated_values(vbest, fit.covar)                         # da vedere
        # 3. evaluate constrained params, save stderr                          # da vedere
        for nam in params.keys():                                                # da vedere
            obj = fit.params[nam]                                        # da vedere
            eval_stderr(obj, uvars,  fit.params.keys(), vsave)                     # da vedere
        # test print fit.params['amp'].stderr                                                                       # da vedere
        
        # 3. evaluate path params, save stderr                                 # da vedere
        for ds in datasets:                                                    # da vedere
            for p in ds.pathlist:                                              # da vedere
                delarch.paramGroup._feffdat = copy(p._feffdat)    # da vedere
                delarch.paramGroup._asteval('reff= %g' %p._feffdat.reff)       # da vedere
                                                                               # da vedere
                for param in ('degen', 's02', 'e0', 'ei',                      # da vedere
                              'deltar', 'sigma2', 'third', 'fourth'):          # da vedere
                    obj = getattr(p, param)                                    # da vedere
                    #eval_stderr(obj, uvars,  fit.params.keys(), vsave)         # da vedere
                                                                               # da vedere
        # restore saved parameters again                                       # da vedere
        for vname in fit.params.keys():                                        # da vedere
            setattr(params, vname, vsave[vname])                               # da vedere
                                                                               # da vedere
        ### clear any errors evaluting uncertainties                           # da vedere
        #----if len(_larch.error) > 0:                                              # da vedere
        #----    _larch.error = []                                                  # da vedere
                                                                               # da vedere
    # here we create outputs arrays for chi(k), chi(r):                        # da vedere
    for ds in datasets:                                                        # da vedere
        ds.save_ffts(rmax_out=rmax_out, path_outputs=path_outputs)             # da vedere
    return Group(name='feffit fit results', fit=fit, params=fit.params,
                 datasets=datasets)

def feffit_report(result, min_correl=0.1, with_paths=True):
    """return a printable report of fit for feffit

    Parameters:
    ------------
      result:      Feffit result, output group from feffit()
      min_correl:  minimum correlation to report [0.1]
      wit_paths:   boolean (True/False) for whether to list all paths [True]

    Returns:
    ---------
      printable string of report.

    """
    input_ok = False
    try:
        fit    = result.fit
        params = result.params
        datasets = result.datasets
        input_ok = True
    except:
        pass
    if not input_ok:
        print( 'must pass output of feffit()!')
        return
    topline = '=================== FEFFIT RESULTS ===================='
    header = '[[%s]]'
    varformat  = '   %12s = % f +/- %s   (init= % f)'
    exprformat = '   %12s = % f +/- %s  = \'%s\''
    out = [topline, header % 'Statistics']

    npts = len(fit.residual)

    out.append('   npts, nvarys, nfree= %i, %i, %i' % (npts, fit.nvarys,
                                                       fit.nfree))
    out.append('   chi_square         = %.8g'  % (fit.chisqr))
    out.append('   reduced chi_square = %.8g'  % (fit.redchi))
    out.append('   r-factor           = %.8g'  % (fit.rfactor))
    out.append(' ')
    if len(datasets) == 1:
        out.append(header % 'Data')
    else:
        out.append(header % 'Datasets (%i)' % len(datasets))
    for i, ds in enumerate(datasets):
        tr = ds.transform
        if len(datasets) > 1:
            out.append(' dataset %i:' % (i+1))
        if isinstance(tr.kweight, Iterable):
            if isinstance(ds.epsilon_k[0], np.ndarray):
                eps_k = ', '.join([repr(eps) for eps in ds.epsilon_k])
            else:
                eps_k = ', '.join(['%.6f' % eps for eps in ds.epsilon_k])
            eps_r = ', '.join(['%.6f' % eps for eps in ds.epsilon_r])
            kweigh = ', '.join(['%i' % kwe for kwe in tr.kweight])
        else:
            if isinstance(ds.epsilon_k, np.ndarray):
                eps_k = repr(ds.epsilon_k)
            else:
                eps_k = '%.6f' % ds.epsilon_k
            eps_r = '%.6f' % ds.epsilon_r
            kweigh = '%i' % tr.kweight


        out.append('   fit space          = \'%s\''  % (tr.fitspace))
        out.append('   r-range            = %.3f, %.3f' % (tr.rmin, tr.rmax))
        out.append('   k-range            = %.3f, %.3f' % (tr.kmin, tr.kmax))
        kwin = '   k window, dk       = \'%s\', %.3f'   % (tr.window, tr.dk)
        if tr.dk2 is not None:
            kwin = "%s, %.3f" % (kwin, tr.dk2)
        out.append(kwin)
        pathfiles = [p.filename for p in ds.pathlist]
        out.append('   paths used in fit  = %s' % (repr(pathfiles)))
        out.append('   k-weight           = %s' % kweigh)
        out.append('   epsilon_k          = %s'  % eps_k)
        out.append('   epsilon_r          = %s'  % eps_r)
        out.append('   n_independent      = %.3f'  % (ds.n_idp))

        #
    out.append(' ')
    out.append(header % 'Variables')

    exprs = []
    for name in params:
        var = params[name]
        if len(name) < 14:
            name = (name + ' '*14)[:14]
        if isinstance(var, Parameter):
            if var.vary:
                stderr = 'unknown'
                if var.stderr is not None: stderr = "%f" % var.stderr
                out.append(varformat % (name, var.value,
                                        stderr, var.init_value))

            elif var.expr is not None:
                stderr = 'unknown'
                if var.stderr is not None: stderr = "%f" % var.stderr
                exprs.append(exprformat % (name, var.value,
                                           stderr, var.expr))
    if len(exprs) > 0:
        out.append(header % 'Constraint Expressions')
        out.extend(exprs)

    covar_vars = params.keys()
    if len(covar_vars) > 0:
        out.append(' ')
        out.append(header % 'Correlations' +
                   '    (unreported correlations are < % .3f)' % min_correl)
        correls = {}
        for i, name in enumerate(covar_vars):
            par = params[name]
            if not par.vary:
                continue
            if hasattr(par, 'correl') and par.correl is not None:
                for name2 in covar_vars[i+1:]:
                    if name != name2 and name2 in par.correl:
                        correls["%s, %s" % (name, name2)] = par.correl[name2]

        sort_correl = sorted(correls.items(), key=lambda it: abs(it[1]))
        sort_correl.reverse()
        for name, val in sort_correl:
            if abs(val) < min_correl:
                break
            if len(name) < 20:
                name = (name + ' '*20)[:20]
            out.append('   %s = % .3f ' % (name, val))

    if with_paths:
        out.append(' ')
        out.append(header % 'Paths')
        for ids, ds in enumerate(datasets):
            if len(datasets) > 1:
                out.append(' dataset %i:' % (ids+1))
            for p in ds.pathlist:
                out.append('%s\n' % p.report())
    out.append('='*len(topline))
    return '\n'.join(out)

