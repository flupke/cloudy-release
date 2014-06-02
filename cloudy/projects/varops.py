'''
Various operators to manipulate deployment variables.
'''


def get_from_dict(dct, path, full_path=None):
    '''
    Get the element from dotted-notation *path* from dict *dct*.
    '''
    if full_path is None:
        full_path = path
    key, _, rest = path.partition('.')
    try:
        subdct = dct[key]
    except KeyError:
        raise KeyError(full_path)
    if rest:
        return get_from_dict(subdct, rest, full_path)
    return subdct


def set_in_dict(dct, path, value, full_path=None):
    '''
    Set the element in *dct* at dotted-notation *path* to *value*.
    '''
    if full_path is None:
        full_path = path
    key, _, rest = path.partition('.')
    if rest:
        try:
            subdct = dct[key]
        except KeyError:
            raise KeyError(full_path)
        set_in_dict(subdct, rest, value, full_path)
    else:
        dct[key] = value


def _set_op(dct, path, value, set_method):
    lst = get_from_dict(dct, path)
    if not isinstance(lst, list):
        raise TypeError('value at "%s" is not a list' % path)
    lst_set = set(lst)
    method = getattr(lst_set, set_method)
    method(value)
    lst = list(lst_set)
    set_in_dict(dct, path, lst)


def set_add(dct, path, value):
    '''
    Add *value* to the list at *path* in *dct*, treating it as a set.
    '''
    _set_op(dct, path, value, 'add')


def set_discard(dct, path, value):
    '''
    Discard *value* from the list at *path* in *dct*, treating it as a set.
    '''
    _set_op(dct, path, value, 'discard')
