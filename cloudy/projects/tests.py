from django.test import TestCase
from .varops import get_from_dict, set_in_dict, set_add, set_discard



class VarOpsTests(TestCase):

    def test_get_from_dict(self):
        dct = {'a': {'b': 'c'}}
        self.assertEqual(get_from_dict(dct, 'a'), {'b': 'c'})
        self.assertEqual(get_from_dict(dct, 'a.b'), 'c')
        self.assertRaisesMessage(KeyError, 'a.c', get_from_dict, dct, 'a.c')

    def test_set_in_dict(self):
        dct = {'a': {'b': 'c'}}
        set_in_dict(dct, 'a.b', 'd')
        self.assertEquals(dct, {'a': {'b': 'd'}})
        set_in_dict(dct, 'a.c', 'e')
        self.assertEquals(dct, {'a': {'b': 'd', 'c': 'e'}})
        self.assertRaisesMessage(KeyError, 'b.d', set_in_dict, dct, 'b.d', 1)

    def test_set_add(self):
        dct = {'a': [1, 2, 3], 'b': 'c'}
        set_add(dct, 'a', 1)
        self.assertEqual(dct, {'a': [1, 2, 3], 'b': 'c'})
        set_add(dct, 'a', 4)
        self.assertEqual(dct, {'a': [1, 2, 3, 4], 'b': 'c'})
        self.assertRaises(TypeError, set_add, dct, 'b', 1)

    def test_set_discard(self):
        dct = {'a': [1, 2, 3], 'b': 'c'}
        set_discard(dct, 'a', 4)
        self.assertEqual(dct, {'a': [1, 2, 3], 'b': 'c'})
        set_discard(dct, 'a', 3)
        self.assertEqual(dct, {'a': [1, 2], 'b': 'c'})
        self.assertRaises(TypeError, set_discard, dct, 'b', 1)
