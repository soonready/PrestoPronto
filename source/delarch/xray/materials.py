import os
import numpy as np
from larch import ValidateLarchPlugin, site_config

from larch_plugins.xray import chemparse, mu_elam, atomic_mass

MODNAME = '_xray'

def get_materials(_larch):
    """return _materials dictionary, creating it if needed"""
    symname = '%s._materials' % MODNAME
    if _larch.symtable.has_symbol(symname):
        return _larch.symtable.get_symbol(symname)
    mat = {}
    conf = site_config
    paths = [os.path.join(conf.larchdir, 'plugins', 'xray'),
             os.path.join(conf.larchdir)]

    for dirname in paths:
        fname = os.path.join(dirname, 'materials.dat')
        if os.path.exists(fname):
            fh = open(fname, 'r')
            lines = fh.readlines()
            fh.close()
            for line in lines:
                line = line.strip()
                if len(line) > 2 and not line.startswith('#'):
                    try:
                        name, f, den = [i.strip() for i in line.split('|')]
                        mat[name.lower()] = (f.replace(' ', ''), float(den))
                    except:
                        pass
    _larch.symtable.set_symbol(symname, mat)
    return mat

@ValidateLarchPlugin
def material_mu(name, energy, density=None, kind='total', _larch=None):
    """
    material_mu(name, energy, density=None, kind='total')

    return X-ray attenuation length (in 1/cm) for a material by name or formula

    arguments
    ---------
     name:     chemical formul or name of material from materials list.
     energy:   energy or array of energies in eV
     density:  material density (gr/cm^3).  If None, and material is a
               known material, that density will be used.
     kind:     'photo' or 'total' (default) for whether to
               return photo-absorption or total cross-section.
    returns
    -------
     mu, absorption length in 1/cm

    notes
    -----
      1.  material names are not case sensitive,
          chemical compounds are case sensitive.
      2.  mu_elam() is used for mu calculation.

    example
    -------
      >>> print material_mu('H2O', 10000.0)
      5.32986401658495
    """
    _materials = get_materials(_larch)
    formula = None
    mater = _materials.get(name.lower(), None)
    if mater is not None:
        formula, density = mater
    else:
        for key, val in _materials.items():
            if name.lower() == val[0].lower(): # match formula
                formula, density = val
                break
    # default to using passed in name as a formula
    if formula is None:
        formula = name
    if density is None:
        raise Warning('material_mu(): must give density for unknown materials')

    mass_tot, mu = 0.0, 0.0
    for elem, frac in chemparse(formula).items():
        mass  = frac * atomic_mass(elem, _larch=_larch)
        mu   += mass * mu_elam(elem, energy, kind=kind, _larch=_larch)
        mass_tot += mass
    return density*mu/mass_tot

@ValidateLarchPlugin
def material_mu_components(name, energy, density=None, kind='total',
                           _larch=None):
    """material_mu_components: absorption coefficient (in 1/cm) for a compound

    arguments
    ---------
     name:     material name or compound formula
     energy:   energy or array of energies at which to calculate mu
     density:  compound density in gr/cm^3
     kind:     cross-section to use ('total', 'photo') for mu_elam())

    returns
    -------
     dictionary of data for constructing mu per element,
     with elements 'mass' (total mass), 'density', and
     'elements' (list of atomic symbols for elements in material).
     For each element, there will be an item (atomic symbol as key)
     with tuple of (stoichiometric fraction, atomic mass, mu)

     larch> material_mu_components('quartz', 10000)
     {'Si': (1, 28.0855, 33.879432430185062), 'elements': ['Si', 'O'],
     'mass': 60.0843, 'O': (2.0, 15.9994, 5.9528248152970837), 'density': 2.65}
     """
    _materials = get_materials(_larch)
    mater = _materials.get(name.lower(), None)
    if mater is None:
        formula = name
        if density is None:
            raise Warning('material_mu(): must give density for unknown materials')
    else:
        formula, density = mater


    out = {'mass': 0.0, 'density': density, 'elements':[]}
    for atom, frac in chemparse(formula).items():
        mass  = atomic_mass(atom, _larch=_larch)
        mu    = mu_elam(atom, energy, kind=kind, _larch=_larch)
        out['mass'] += frac*mass
        out[atom] = (frac, mass, mu)
        out['elements'].append(atom)
    return out

@ValidateLarchPlugin
def material_get(name, _larch=None):
    """lookup material """
    return get_materials(_larch).get(name.lower(), None)

@ValidateLarchPlugin
def material_add(name, formula, density, _larch=None):
    """ save material in local db"""
    materials = get_materials(_larch)
    formula = formula.replace(' ', '')
    materials[name.lower()] = (formula, float(density))

    symname = '%s._materials' % MODNAME
    _larch.symtable.set_symbol(symname, materials)

    fname = os.path.join(larch.site_config.larchdir, 'materials.dat')
    if os.path.exists(fname):
        fh = open(fname, 'r')
        text = fh.readlines()
        fh.close()
    else:
        text = ['# user-specific database of materials\n',
                '# name, formula, density\n']

    text.append(" %s | %s | %g\n" % (name, formula, density))

    fh = open(fname, 'w')
    fh.write(''.join(text))
    fh.close()

def initializeLarchPlugin(_larch=None):
    """initialize xraydb"""
    if _larch is not None:
         get_materials(_larch)

def registerLarchPlugin():
    return ('_xray', {'material_get': material_get,
                      'material_add': material_add,
                      'material_mu':  material_mu,
                      'material_mu_components': material_mu_components,
                      })
