# -*- coding: utf-8 -*-
import unittest
from website.expand import expand


class MyTestCase(unittest.TestCase):

    def test_expand_1(self):
        "Empty dict + empty strings"
        d = {}
        s = u''
        expected = u''
        self.assertEqual(expected, expand(s, d))

    def test_expand_2(self):
        "Empty dict"
        d = {}
        s = u'xx{}xx'
        expected = u'xx{}xx'
        self.assertEqual(expected, expand(s, d))

    def test_expand_3(self):
        "Simple replacement"
        self.assertEqual('An apple',
                         expand('An {apple_fruit}',
                                {'apple_fruit': 'apple'}))

    def test_expand_4(self):
        "Replacement with link"
        self.assertEqual('An <a href="http://www.apple.com">Apple</a>',
                         expand('An {apple_fruit|Apple}',
                                {'apple_fruit': 'http://www.apple.com'}))

    def test_expand_5(self):
        "Replacement with link description evaluation"
        self.assertEqual('A <a href="http://www.apple.com">pear</a>',
                         expand('A {apple_fruit|apple}',
                                {'apple_fruit': 'http://www.apple.com',
                                 'apple': 'pear'}))

    def test_expand_6(self):
        "Replacement with link description evaluation and hash argument"
        self.assertEqual(
            'A <a href="http://www.apple.com" target="_blank">pear</a>',
            expand('A {apple_fruit|apple}',
                   {'apple_fruit': {'href': 'http://www.apple.com',
                                    'target': '_blank'},
                    'apple': 'pear'}))

    def test_expand_7(self):
        "Replacement with different tag and default attribute"
        self.assertEqual('A <span class="green">Apple</span>',
                         expand('A {apple_fruit|Apple}',
                                {'apple_fruit': 'green'},
                                tag="span",
                                default_attribute="class"
                                ))

    def test_expand_8(self):
        "Replacement of empty string by a single word"
        d = {"": "YES"}
        s = u'xx{}xx'
        expected = u'xxYESxx'
        self.assertEqual(expected, expand(s, d))

    def test_expand_9(self):
        "Replacement of { and }"
        d = {"{": "YES", '}': "NO"}
        s = u'xx{{}{}}xx'
        expected = u'xxYESNOxx'
        self.assertEqual(expected, expand(s, d))

    def test_expand_10(self):
        "Double replacement with link and special chars in attribute value"
        d = {
            "url": {
                'href': 'http://picard?id=test',
                'class': 'ext',
                'title': 'title with <€àùîé> "" l\'a in it',
            }
        }
        s = u'xx{url|Picard1}xxxx{url|Picard2}xx'
        expected = 'xx<a class="ext" href="http://picard?id=test" title="title with &lt;&#8364;&#224;&#249;&#238;&#233;&gt; &quot;&quot; l\'a in it">Picard1</a>xxxx<a class="ext" href="http://picard?id=test" title="title with &lt;&#8364;&#224;&#249;&#238;&#233;&gt; &quot;&quot; l\'a in it">Picard2</a>xx'
        self.assertEqual(expected, expand(s, d))

    def test_expand_11(self):
        "Replacement with different tag and empty default attribute"
        self.assertEqual('A <strong>Apple</strong>',
                         expand('A {apple_fruit|Apple}',
                                {'apple_fruit': 'green'},
                                tag="strong",
                                default_attribute=""
                                ))
