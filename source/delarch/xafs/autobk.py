#!/usr/bin/env python
import numpy as np
from scipy.interpolate import splrep, splev, UnivariateSpline
from lmfit import minimize, Parameters

from delarch import Group, isgroup
from Call_args import DefCallArgs  #decorator lello

# import other plugins from std, math, and xafs modules...
from delarch.std  import parse_group_args
from delarch.math import (index_of, index_nearest, realimag, remove_dups)

from delarch.xafs import (ETOK, ftwindow, xftf_fast, find_e0, pre_edge)

# check for uncertainties package
HAS_UNCERTAIN = False
try:
    import uncertainties
    HAS_UNCERTAIN = True
except ImportError:
    pass

FMT_COEF = 'c%2.2i'

def spline_eval(kraw, mu, knots, coefs, order, kout):
    """eval bkg(kraw) and chi(k) for knots, coefs, order"""
    bkg = splev(kraw, [knots, coefs, order])
    chi = UnivariateSpline(kraw, (mu-bkg), s=0)(kout)
    return bkg, chi

def __resid(pars, ncoefs=1, knots=None, order=3, irbkg=1, nfft=2048,
            kraw=None, mu=None, kout=None, ftwin=1, kweight=1, chi_std=None,
            nclamp=0, clamp_lo=1, clamp_hi=1, **kws):

    coefs = [pars[FMT_COEF % i].value for i in range(ncoefs)]
    bkg, chi = spline_eval(kraw, mu, knots, coefs, order, kout)
    if chi_std is not None:
        chi = chi - chi_std
    out =  realimag(xftf_fast(chi*ftwin, nfft=nfft)[:irbkg])
    if nclamp == 0:
        return out
    # spline clamps:
    scale = (1.0 + 100*(out*out).sum())/(len(out)*nclamp)
    scaled_chik = scale * chi * kout**kweight
    return np.concatenate((out,
                           abs(clamp_lo)*scaled_chik[:nclamp],
                           abs(clamp_hi)*scaled_chik[-nclamp:]))


@DefCallArgs("autobk_details",["energy","mu"])
def autobk(energy, mu=None, group=None, rbkg=1, nknots=None, e0=None,
           edge_step=None, kmin=0, kmax=None, kweight=1, dk=0.1,
           win='hanning', k_std=None, chi_std=None, nfft=2048, kstep=0.05,
           pre_edge_kws=None, nclamp=4, clamp_lo=1, clamp_hi=1,
           calc_uncertainties=False, **kws):
    """Use Autobk algorithm to remove XAFS background

    Parameters:
    -----------
      energy:    1-d array of x-ray energies, in eV, or group
      mu:        1-d array of mu(E)
      group:     output group (and input group for e0 and edge_step).
      rbkg:      distance (in Ang) for chi(R) above
                 which the signal is ignored. Default = 1.
      e0:        edge energy, in eV.  If None, it will be determined.
      edge_step: edge step.  If None, it will be determined.
      pre_edge_kws:  keyword arguments to pass to pre_edge()
      nknots:    number of knots in spline.  If None, it will be determined.
      kmin:      minimum k value   [0]
      kmax:      maximum k value   [full data range].
      kweight:   k weight for FFT.  [1]
      dk:        FFT window window parameter.  [0.1]
      win:       FFT window function name.     ['hanning']
      nfft:      array size to use for FFT [2048]
      kstep:     k step size to use for FFT [0.05]
      k_std:     optional k array for standard chi(k).
      chi_std:   optional chi array for standard chi(k).
      nclamp:    number of energy end-points for clamp [2]
      clamp_lo:  weight of low-energy clamp [1]
      clamp_hi:  weight of high-energy clamp [1]
      calc_uncertaintites:  Flag to calculate uncertainties in
                            mu_0(E) and chi(k) [False]

    Output arrays are written to the provided group.

    Follows the 'First Argument Group' convention.
    """
    msg = repr
    if 'kw' in kws:
        kweight = kws.pop('kw')
    if len(kws) > 0:
        msg('Unrecognized a:rguments for autobk():\n')
        msg('    %s\n' % (', '.join(kws.keys())))
        return

    energy, mu, group = parse_group_args(energy, members=('energy', 'mu'),
                                         defaults=(mu,), group=group,
                                         fcn_name='autobk')
    

    # if e0 or edge_step are not specified, get them, either from the
    # passed-in group or from running pre_edge()
    #group = set_xafsGroup(group, _larch=_larch)

    if edge_step is None and isgroup(group, 'edge_step'):
        edge_step = group.edge_step
    if e0 is None and isgroup(group, 'e0'):
        e0 = group.e0
    if e0 is None or edge_step is None:
        # need to run pre_edge:
        pre_kws = dict(nnorm=3, nvict=0, pre1=None,
                       pre2=-50., norm1=100., norm2=None)
        if pre_edge_kws is not None:
            pre_kws.update(pre_edge_kws)
        pre_edge(energy, mu, group=group, **pre_kws)
        if e0 is None:
            e0 = group.e0
        if edge_step is None:
            edge_step = group.edge_step
    if e0 is None or edge_step is None:
        msg('autobk() could not determine e0 or edge_step!: trying running pre_edge first\n')
        return

    # get array indices for rkbg and e0: irbkg, ie0
    ie0 = index_of(energy, e0)
    rgrid = np.pi/(kstep*nfft)
    if rbkg < 2*rgrid: rbkg = 2*rgrid
    irbkg = int(1.01 + rbkg/rgrid)

    # save ungridded k (kraw) and grided k (kout)
    # and ftwin (*k-weighting) for FT in residual
    enpe = energy[ie0:] - e0
    kraw = np.sign(enpe)*np.sqrt(ETOK*abs(enpe))
    if kmax is None:
        kmax = max(kraw)
    else:
        kmax = max(0, min(max(kraw), kmax))
    kout  = kstep * np.arange(int(1.01+kmax/kstep), dtype='float64')
    iemax = min(len(energy), 2+index_of(energy, e0+kmax*kmax/ETOK)) - 1

    # interpolate provided chi(k) onto the kout grid
    if chi_std is not None and k_std is not None:
        chi_std = np.interp(kout, k_std, chi_std)
    # pre-load FT window
    ftwin = kout**kweight * ftwindow(kout, xmin=kmin, xmax=kmax,
                                     window=win, dx=dk, dx2=dk)
    # calc k-value and initial guess for y-values of spline params
    nspl = max(4, min(128, 2*int(rbkg*(kmax-kmin)/np.pi) + 1))
    spl_y, spl_k, spl_e  = np.zeros(nspl), np.zeros(nspl), np.zeros(nspl)
    for i in range(nspl):
        q  = kmin + i*(kmax-kmin)/(nspl - 1)
        ik = index_nearest(kraw, q)
        i1 = min(len(kraw)-1, ik + 5)
        i2 = max(0, ik - 5)
        spl_k[i] = kraw[ik]
        spl_e[i] = energy[ik+ie0]
        spl_y[i] = (2*mu[ik+ie0] + mu[i1+ie0] + mu[i2+ie0] ) / 4.0

    # get spline represention: knots, coefs, order=3
    # coefs will be varied in fit.
    knots, coefs, order = splrep(spl_k, spl_y)

    # set fit parameters from initial coefficients
    params = Parameters()
    #params = Group()
    for i in range(len(coefs)):
        name = FMT_COEF % i
        params.add( name=name, value=coefs[i],vary=i<len(spl_y))
        ###-p = Parameter(coefs[i], name=name, vary=i<len(spl_y))
        ###-p._getval()
        ###-setattr(params, name, p)

    initbkg, initchi = spline_eval(kraw[:iemax-ie0+1], mu[ie0:iemax+1],
                                   knots, coefs, order, kout)

    # do fit
    fit = minimize(__resid, params,
                    kws = dict(ncoefs=len(coefs), chi_std=chi_std,
                                   knots=knots, order=order,
                                   kraw=kraw[:iemax-ie0+1],
                                   mu=mu[ie0:iemax+1], irbkg=irbkg, kout=kout,
                                   ftwin=ftwin, kweight=kweight,
                                   nfft=nfft, nclamp=nclamp,
                                   clamp_lo=clamp_lo, clamp_hi=clamp_hi))


    # write final results
    coefs = [fit.params[FMT_COEF % i]  for i in range(len(coefs))]
    bkg, chi = spline_eval(kraw[:iemax-ie0+1], mu[ie0:iemax+1],
                           knots, coefs, order, kout)
    obkg = np.copy(mu)
    obkg[ie0:ie0+len(bkg)] = bkg

    # outputs to group
    #group = Group(group)
    group.bkg  = obkg
    group.chie = (mu-obkg)/edge_step
    group.k    = kout
    group.chi  = chi/edge_step

    # now fill in 'autobk_details' group
    params.init_bkg = np.copy(mu)
    params.init_bkg[ie0:ie0+len(bkg)] = initbkg
    params.init_chi = initchi/edge_step
    params.knots_e  = spl_e
    params.knots_y  = np.array([coefs[i] for i in range(nspl)])
    params.init_knots_y = spl_y
    #params.nfev = params.fit_details.nfev non so cosa sia ?? l'ho tolto
    params.kmin = kmin
    params.kmax = kmax  
    group.autobk_details = params

    # uncertainties in mu0 and chi:  fairly slow!!
    if HAS_UNCERTAIN and calc_uncertainties:
        vbest, vstd = [], []
        for n in fit.var_names:
            par = getattr(params, n)
            vbest.append(par.value)
            vstd.append(par.stderr)
        uvars = uncertainties.correlated_values(vbest, params.covar)
        # uncertainty in bkg (aka mu0)
        # note that much of this is working around
        # limitations in the uncertainty package that make it
        #  1. take an argument list (not array)
        #  2. work on returned scalars (but not arrays)
        #  3. not handle kw args and *args well (so use
        #     of global "index" is important here)
        nkx = iemax-ie0 + 1
        def my_dsplev(*args):
            coefs = np.array(args)
            return splev(kraw[:nkx], [knots, coefs, order])[index]
        fdbkg = uncertainties.wrap(my_dsplev)
        dmu0  = [fdbkg(*uvars).std_dev() for index in range(len(bkg))]
        group.delta_bkg = np.zeros(len(mu))
        group.delta_bkg[ie0:ie0+len(bkg)] = np.array(dmu0)

        # uncertainty in chi (see notes above)
        def my_dchi(*args):
            coefs = np.array(args)
            b,chi = spline_eval(kraw[:nkx], mu[ie0:iemax+1],
                                knots, coefs, order, kout)
            return chi[index]
        fdchi = uncertainties.wrap(my_dchi)
        dchi  = [fdchi(*uvars).std_dev() for index in range(len(kout))]
        group.delta_chi = np.array(dchi)/edge_step


