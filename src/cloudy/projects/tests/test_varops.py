import pytest

from ..varops import get_from_dict, set_in_dict, set_add, set_discard


def test_get_from_dict():
    dct = {'a': {'b': 'c'}}
    assert get_from_dict(dct, 'a') == {'b': 'c'}
    assert get_from_dict(dct, 'a.b') == 'c'
    with pytest.raises(KeyError) as exc_info:
        get_from_dict(dct, 'a.c')
    assert 'a.c' in str(exc_info.value)


def test_set_in_dict():
    dct = {'a': {'b': 'c'}}
    set_in_dict(dct, 'a.b', 'd')
    assert dct == {'a': {'b': 'd'}}
    set_in_dict(dct, 'a.c', 'e')
    assert dct == {'a': {'b': 'd', 'c': 'e'}}
    with pytest.raises(KeyError) as exc_info:
        set_in_dict(dct, 'b.d', 1)
    assert 'b.d' in str(exc_info.value)


def test_set_add():
    dct = {'a': [1, 2, 3], 'b': 'c'}
    set_add(dct, 'a', 1)
    assert dct == {'a': [1, 2, 3], 'b': 'c'}
    set_add(dct, 'a', 4)
    assert dct == {'a': [1, 2, 3, 4], 'b': 'c'}
    with pytest.raises(TypeError):
        set_add(dct, 'b', 1)


def test_set_discard():
    dct = {'a': [1, 2, 3], 'b': 'c'}
    set_discard(dct, 'a', 4)
    assert dct == {'a': [1, 2, 3], 'b': 'c'}
    set_discard(dct, 'a', 3)
    assert dct == {'a': [1, 2], 'b': 'c'}
    with pytest.raises(TypeError):
        set_discard(dct, 'b', 1)
