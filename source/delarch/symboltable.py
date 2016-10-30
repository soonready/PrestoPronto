#!/usr/bin/env python
'''
SymbolTable for Larch interpreter
'''


import copy


class Group(object):
    """Generic Group: a container for variables, modules, and subgroups.

    Methods
    ----------
       _subgroups(): return list of subgroups
       _members():   return dict of members
    """
    __private = ('_main', '_larch', '_parents', '__name__',
                 '__private', '_subgroups', '_members')
    def __init__(self, name=None, **kws):
        if name is None:
            name = hex(id(self))
        self.__name__ = name
        for key, val in kws.items():
            setattr(self, key, val)

    def __len__(self):
        return max(1, len(dir(self))-1)

    def __repr__(self):
        if self.__name__ is not None:
            return '<Group %s>' % self.__name__
        return '<Group>'

    def __copy__(self):
        out = Group()
        for k, v in self.__dict__.items():
            if k != '__name__':
                setattr(out, k,  copy.copy(v))
        return out

    def __deepcopy__(self, memo):
        out = Group()
        for k, v in self.__dict__.items():
            if k != '__name__':
                setattr(out, k,  copy.deepcopy(v, memo))
        return out

    def __id__(self):
        return id(self)

    def __dir__(self):
        "return list of member names"
        cls_members = []
        cname = self.__class__.__name__
        if cname != 'SymbolTable' and hasattr(self, '__class__'):
            cls_members = dir(self.__class__)

        dict_keys = [key for key in self.__dict__ if key not in cls_members]

        return [key for key in cls_members + dict_keys
                if (not key.startswith('_SymbolTable_') and
                    not key.startswith('_Group_') and
                    not key.startswith('_%s_' % cname) and
                    not (key.startswith('__') and key.endswith('__')) and
                    key not in self.__private)]


    def _subgroups(self):
        "return list of names of members that are sub groups"
        return [k for k in self._members() if isgroup(self.__dict__[k])]

    def _members(self):
        "return members"
        r = {}
        for key in self.__dir__():
            if key in self.__dict__:
                r[key] = self.__dict__[key]
        return r

def isgroup(grp, *args):
    """tests if input is a Group

    With additional arguments (all must be strings), it also tests
    that the group has an an attribute named for each argument. This
    can be used to test not only if a object is a Group, but whether
    it a group with expected arguments.
    """
    ret = isinstance(grp, Group)
    if ret and len(args) > 0:
        try:
            ret = all([hasattr(grp, a) for a in args])
        except TypeError:
            return False
    return ret


