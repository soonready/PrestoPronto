#!/usr/bin/env python
"""
  XAFS pre-edge subtraction, normalization algorithms
"""

import numpy as np
from scipy import polyfit
from Call_args import DefCallArgs

from delarch import Group,  isgroup
from lmfit import minimize, Parameters

# now we can reliably import other std and xafs modules...
from delarch.std  import parse_group_args
from delarch.math import (index_of, index_nearest,
                                remove_dups, remove_nans2)

MAX_NNORM = 5


def find_e0(energy, mu=None, group=None):
    """calculate E0 given mu(energy)

    This finds the point with maximum derivative with some
    checks to avoid spurious glitches.

    Arguments
    ----------
    energy:  array of x-ray energies, in eV or group
    mu:      array of mu(E)
    group:   output group

    Returns
    -------
    Value of e0.  If provided, group.e0 will be set to this value.

    Notes
    -----
       Supports First Argument Group convention, requiring group
       members 'energy' and 'mu'
    """
    energy, mu, group = parse_group_args(energy, members=('energy', 'mu'),
                                         defaults=(mu,), group=group,
                                         fcn_name='find_e0')

    ###energy = remove_dups(energy)
    dmu = np.gradient(mu)/np.gradient(energy)
    idmu_max=np.argmax(dmu)
    e0 = energy[idmu_max]
    if group is not None:
        group = Group(group)
        group.e0 = e0
    return e0
    # find points of high derivative
    ####high_deriv_pts = np.where(dmu >  max(dmu)*0.05)[0]
    ####idmu_max, dmu_max = 0, 0
    ####for i in high_deriv_pts:                            ###may cython
    ####    if (dmu[i] > dmu_max and
    ####        (i+1 in high_deriv_pts) and
    ####        (i-1 in high_deriv_pts)):
    ####        idmu_max, dmu_max = i, dmu[i]



@DefCallArgs("pre_edge_details",["energy","mu"])
def pre_edge(energy, mu=None, group=None, e0=None, step=None,
             nnorm=3, nvict=0, pre1=None, pre2=-50,
             norm1=100, norm2=None, make_flat=True):
    """pre edge subtraction, normalization for XAFS

    This performs a number of steps:
       1. determine E0 (if not supplied) from max of deriv(mu)
       2. fit a line of polymonial to the region below the edge
       3. fit a polymonial to the region above the edge
       4. extrapolae the two curves to E0 to determine the edge jump

    Arguments
    ----------
    energy:  array of x-ray energies, in eV, or group (see note)
    mu:      array of mu(E)
    group:   output group
    e0:      edge energy, in eV.  If None, it will be determined here.
    step:    edge jump.  If None, it will be determined here.
    pre1:    low E range (relative to E0) for pre-edge fit
    pre2:    high E range (relative to E0) for pre-edge fit
    nvict:   energy exponent to use for pre-edg fit.  See Note
    norm1:   low E range (relative to E0) for post-edge fit
    norm2:   high E range (relative to E0) for post-edge fit
    nnorm:   degree of polynomial (ie, nnorm+1 coefficients will be found) for
             post-edge normalization curve. Default=3 (quadratic), max=5
    make_flat: boolean (Default True) to calculate flattened output.


    Returns
    -------
      None

    The following attributes will be written to the output group:
        e0          energy origin
        edge_step   edge step
        norm        normalized mu(E)
        flat        flattened, normalized mu(E)
        pre_edge    determined pre-edge curve
        post_edge   determined post-edge, normalization curve
        dmude       derivative of mu(E)

    (if the output group is None, _sys.xafsGroup will be written to)

    Notes
    -----
     1 nvict gives an exponent to the energy term for the fits to the pre-edge
       and the post-edge region.  For the pre-edge, a line (m * energy + b) is
       fit to mu(energy)*energy**nvict over the pre-edge region,
       energy=[e0+pre1, e0+pre2].  For the post-edge, a polynomial of order
       nnorm will be fit to mu(energy)*energy**nvict of the post-edge region
       energy=[e0+norm1, e0+norm2].

     2 If the first argument is a Group, it must contain 'energy' and 'mu'.
       If it exists, group.e0 will be used as e0.
       See First Argrument Group in Documentation
    """
    

    energy, mu, group = parse_group_args(energy, members=('energy', 'mu'),
                                         defaults=(mu,), group=group,
                                         fcn_name='pre_edge')
    

    if e0 is None or e0 < energy[0] or e0 > energy[-1]:
        dmu = np.gradient(mu)/np.gradient(energy)
        ie0=np.argmax(dmu)
        e0 = energy[ie0]
    else:
        ie0 = index_nearest(energy, e0)
        e0 = energy[ie0]

    nnorm = max(min(nnorm, MAX_NNORM), 1)


    if pre1 is None:  pre1  = min(energy) - e0
    if norm2 is None: norm2 = max(energy) - e0
    if norm2 < 0:     norm2 = max(energy) - e0 - norm2
    pre1  = max(pre1,  (min(energy) - e0))
    norm2 = min(norm2, (max(energy) - e0))

    if pre1 > pre2:
        pre1, pre2 = pre2, pre1
    if norm1 > norm2:
        norm1, norm2 = norm2, norm1

    pr1 = index_of(energy, pre1+e0)
    pr2 = index_nearest(energy, pre2+e0)
    if pr2-pr1 < 2:
        pr2 = min(len(energy), pr1 + 2)

    # pre_edge
    precoefs=np.polyfit(energy[pr1:pr2],mu[pr1:pr2], 1)
    preedge_poly=np.poly1d(precoefs)
    group.pre_edge=preedge_poly(energy)

    
    # normalization
    po1 = index_of(energy, norm1+e0)
    po2 = index_nearest(energy, norm2+e0)
    if po2-po1 < 2:
        po2 = min(len(energy), po1 + 2)
    coefs = polyfit(energy[po1:po2], mu[po1:po2], nnorm)
    postedge_poly=np.poly1d(coefs)
    group.post_edge = postedge_poly(energy)
   
    group.edge_step = step
    if group.edge_step is None:
        group.edge_step = group.post_edge[ie0] - group.pre_edge[ie0]

    group.norm = (mu - group.pre_edge)/group.edge_step
    
    if make_flat:
       polyflat=postedge_poly-preedge_poly 
       group.norm[ie0:]=  group.norm[ie0:]- \
                         (polyflat(energy[ie0:])/group.edge_step -1)        
    
    
    group.e0 = e0
    group.dmude = np.gradient(mu)/np.gradient(energy)
    
    group.pre_edge_details = Group()
    group.pre_edge_details.pre1   = pr1
    group.pre_edge_details.pre2   = pr2
    group.pre_edge_details.norm1  = po1
    group.pre_edge_details.norm2  = po2
    group.pre_edge_details.pre_slope  = precoefs[0]
    group.pre_edge_details.pre_offset = precoefs[1]
    
    for i in range(MAX_NNORM):
        if hasattr(group, 'norm_c%i' % i):
            delattr(group, 'norm_c%i' % i)
    for i, c in enumerate(coefs):
        setattr(group.pre_edge_details, 'norm_c%i' % i, c)
    return
