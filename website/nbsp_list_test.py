# -*- coding: utf-8 -*-
import unittest
from website.nbsp_list import nbsp_list


class MyTestCase(unittest.TestCase):

    def test_nbsp_list_1(self):
        "Empty string"
        s = u''
        expected = u''
        self.assertEqual(expected, nbsp_list(s))

    def test_nbsp_list_2(self):
        "Simple string"
        s = u'test'
        expected = u'test'
        self.assertEqual(expected, nbsp_list(s))

    def test_nbsp_list_3(self):
        "Simple string with html tag"
        s = u'te<i>st'
        expected = u'te&lt;i&gt;st'
        self.assertEqual(expected, nbsp_list(s))

    def test_nbsp_list_4(self):
        "Simple string with space"
        s = u'te st'
        expected = u'te&nbsp;st'
        self.assertEqual(expected, nbsp_list(s))

    def test_nbsp_list_5(self):
        "List, no space"
        s = u'test1,test2'
        expected = u'test1, test2'
        self.assertEqual(expected, nbsp_list(s))

    def test_nbsp_list_6(self):
        "List, multiple spaces after comma"
        s = u'test1,   test2'
        expected = u'test1, test2'
        self.assertEqual(expected, nbsp_list(s))

    def test_nbsp_list_7(self):
        "List, multiple spaces in elements"
        s = u'te  st1, te  st2'
        expected = u'te&nbsp;st1, te&nbsp;st2'
        self.assertEqual(expected, nbsp_list(s))

    def test_nbsp_list_8(self):
        "List, multiple spaces in elements and escaping"
        s = u'te  st1, te  <s>t2'
        expected = u'te&nbsp;st1, te&nbsp;&lt;s&gt;t2'
        self.assertEqual(expected, nbsp_list(s))

    def test_nbsp_list_9(self):
        "List, multiple spaces in elements and escaping, different separator"
        s = u'te  st1* te  <s>t2'
        expected = u'te&nbsp;st1* te&nbsp;&lt;s&gt;t2'
        self.assertEqual(expected, nbsp_list(s, '*'))

    def test_nbsp_list_10(self):
        "Complex list and escaping"
        s = u'te  st1; te  <s>t2;&nbsp;'
        expected = u'te&nbsp;st1; te&nbsp;&lt;s&gt;t2; &amp;nbsp; '
        self.assertEqual(expected, nbsp_list(s, ';'))
