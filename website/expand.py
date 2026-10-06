import html
import re


def encode_entities(string, quote=True):
    return html.escape(string, quote).encode('ascii', 'xmlcharrefreplace').decode('utf8')


def expand(string, args, tag='a', default_attribute='href'):
    def make_link(match):
        var = match.group(1)
        text = match.group(2)
        if text in args.keys():
            final_text = args[text]
        else:
            final_text = text

        # ``var`` is one of ``args`` keys by construction of the regex below,
        # but guard the lookup so a future change to the pattern cannot turn a
        # missing key into an unhandled KeyError (HTTP 500) at render time.
        value = args.get(var)
        if isinstance(value, dict):
            d = value
        else:
            if default_attribute:
                d = {default_attribute: value}
            else:
                d = {}
        attribs = ' '.join([f"{k}=\"{encode_entities(d[k])}\"" for k in sorted(d.keys())])
        if attribs:
            attribs = ' ' + attribs
        return f'<{tag}{attribs}>{final_text}</{tag}>'

    def simple_expr(match):
        var = match.group(1)
        if var in args.keys():
            return args[var]
        return '{' + var + '}'

    r = '|'.join([re.escape(k) for k in args.keys()])

    r1 = re.compile(r'\{(' + r + r')\|(.*?)\}', re.UNICODE)
    r2 = re.compile(r'\{(' + r + r')\}', re.UNICODE)

    string = r1.sub(make_link, string)
    string = r2.sub(simple_expr, string)

    return string
