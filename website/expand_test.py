import unittest

from markupsafe import Markup

from website.expand import expand


class MyTestCase(unittest.TestCase):
    def test_expand_1(self):
        "Empty dict + empty strings"
        d = {}
        s = ''
        expected = ''
        self.assertEqual(expected, expand(s, d))

    def test_expand_2(self):
        "Empty dict"
        d = {}
        s = 'xx{}xx'
        expected = 'xx{}xx'
        self.assertEqual(expected, expand(s, d))

    def test_expand_3(self):
        "Simple replacement"
        self.assertEqual('An apple', expand('An {apple_fruit}', {'apple_fruit': 'apple'}))

    def test_expand_4(self):
        "Replacement with link"
        self.assertEqual(
            'An <a href="http://www.apple.com">Apple</a>',
            expand('An {apple_fruit|Apple}', {'apple_fruit': 'http://www.apple.com'}),
        )

    def test_expand_5(self):
        "Replacement with link description evaluation"
        self.assertEqual(
            'A <a href="http://www.apple.com">pear</a>',
            expand('A {apple_fruit|apple}', {'apple_fruit': 'http://www.apple.com', 'apple': 'pear'}),
        )

    def test_expand_6(self):
        "Replacement with link description evaluation and hash argument"
        self.assertEqual(
            'A <a href="http://www.apple.com" target="_blank">pear</a>',
            expand(
                'A {apple_fruit|apple}',
                {'apple_fruit': {'href': 'http://www.apple.com', 'target': '_blank'}, 'apple': 'pear'},
            ),
        )

    def test_expand_7(self):
        "Replacement with different tag and default attribute"
        self.assertEqual(
            'A <span class="green">Apple</span>',
            expand('A {apple_fruit|Apple}', {'apple_fruit': 'green'}, tag="span", default_attribute="class"),
        )

    def test_expand_8(self):
        "Replacement of empty string by a single word"
        d = {"": "YES"}
        s = 'xx{}xx'
        expected = 'xxYESxx'
        self.assertEqual(expected, expand(s, d))

    def test_expand_9(self):
        "Replacement of { and }"
        d = {"{": "YES", '}': "NO"}
        s = 'xx{{}{}}xx'
        expected = 'xxYESNOxx'
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
        s = 'xx{url|Picard1}xxxx{url|Picard2}xx'
        expected = 'xx<a class="ext" href="http://picard?id=test" title="title with &lt;&#8364;&#224;&#249;&#238;&#233;&gt; &quot;&quot; l&#x27;a in it">Picard1</a>xxxx<a class="ext" href="http://picard?id=test" title="title with &lt;&#8364;&#224;&#249;&#238;&#233;&gt; &quot;&quot; l&#x27;a in it">Picard2</a>xx'
        self.assertEqual(expected, expand(s, d))

    def test_expand_11(self):
        "Replacement with different tag and empty default attribute"
        self.assertEqual(
            'A <strong>Apple</strong>',
            expand('A {apple_fruit|Apple}', {'apple_fruit': 'green'}, tag="strong", default_attribute=""),
        )

    def test_expand_returns_markup(self):
        "Result is a Markup instance so it is safe in autoescaping contexts"
        self.assertIsInstance(expand('{url|X}', {'url': 'http://a.com'}), Markup)

    def test_expand_escapes_link_text_from_args(self):
        "HTML in a looked-up link text is escaped, not injected"
        self.assertEqual(
            '<a href="http://a.com">&lt;script&gt;alert(1)&lt;/script&gt;</a>',
            expand('{url|evil}', {'url': 'http://a.com', 'evil': '<script>alert(1)</script>'}),
        )

    def test_expand_escapes_literal_link_text(self):
        "HTML in literal link text (not an arg key) is escaped"
        self.assertEqual(
            '<a href="http://a.com">&lt;b&gt;hi&lt;/b&gt;</a>',
            expand('{url|<b>hi</b>}', {'url': 'http://a.com'}),
        )

    def test_expand_escapes_simple_substitution(self):
        "HTML in a {var} substitution value is escaped"
        self.assertEqual(
            'x &lt;img src=x onerror=alert(1)&gt; y',
            expand('x {evil} y', {'evil': '<img src=x onerror=alert(1)>'}),
        )

    def test_expand_attribute_value_still_escaped(self):
        "Attribute values remain escaped (quotes cannot break out)"
        self.assertEqual(
            '<a href="http://a.com?a=1&amp;b=2">X</a>',
            expand('{url|X}', {'url': 'http://a.com?a=1&b=2'}),
        )

    def test_expand_markup_value_passes_through(self):
        "A Markup {var} value is trusted HTML and left unescaped (opt-out)"
        self.assertEqual(
            'logo: <img src="x.svg">',
            expand('logo: {logo}', {'logo': Markup('<img src="x.svg">')}),
        )

    def test_expand_markup_link_text_passes_through(self):
        "A Markup link text is trusted and left unescaped"
        self.assertEqual(
            '<a href="http://a.com"><b>bold</b></a>',
            expand('{url|label}', {'url': 'http://a.com', 'label': Markup('<b>bold</b>')}),
        )
