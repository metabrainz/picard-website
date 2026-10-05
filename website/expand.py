import html
import re

from markupsafe import Markup, escape


def encode_entities(string, quote=True):
    return html.escape(string, quote).encode('ascii', 'xmlcharrefreplace').decode('utf8')


def expand(string, args, tag='a', default_attribute='href'):
    """Expand ``{var}`` and ``{var|text}`` placeholders in ``string``.

    ``{var}`` is replaced by ``args[var]``. ``{var|text}`` is turned into a
    ``<tag ...>text</tag>`` element whose attributes come from ``args[var]``
    (a dict), or ``{default_attribute: args[var]}`` when ``args[var]`` is a
    plain string.

    All dynamic data substituted into the output is HTML-escaped: attribute
    values, the link text, and simple ``{var}`` substitutions. The result is
    returned as a ``markupsafe.Markup`` instance so it is safe to render in an
    autoescaping template (and in the ``{% autoescape false %}`` / ``|safe``
    blocks the site uses) without re-introducing an XSS vector. The literal
    (non-substituted) parts of ``string`` are emitted as-is, matching the
    previous behaviour where templates provide the surrounding markup.

    Escaping is safe-by-default: a caller that deliberately wants to substitute
    trusted HTML (e.g. an ``<img>`` logo) must pass that value as a
    ``markupsafe.Markup`` instance (``...|safe`` in a template), which
    ``escape`` leaves untouched. Any plain ``str`` value is always escaped.
    """

    def make_link(match):
        var = match.group(1)
        text = match.group(2)
        if text in args.keys():
            final_text = args[text]
        else:
            final_text = text

        if isinstance(args[var], dict):
            d = args[var]
        else:
            if default_attribute:
                d = {default_attribute: args[var]}
            else:
                d = {}
        attribs = ' '.join([f"{k}=\"{encode_entities(d[k])}\"" for k in sorted(d.keys())])
        if attribs:
            attribs = ' ' + attribs
        return f'<{tag}{attribs}>{escape(final_text)}</{tag}>'

    def simple_expr(match):
        var = match.group(1)
        if var in args.keys():
            return str(escape(args[var]))
        return '{' + var + '}'

    r = '|'.join([re.escape(k) for k in args.keys()])

    r1 = re.compile(r'\{(' + r + r')\|(.*?)\}', re.UNICODE)
    r2 = re.compile(r'\{(' + r + r')\}', re.UNICODE)

    string = r1.sub(make_link, string)
    string = r2.sub(simple_expr, string)

    return Markup(string)
