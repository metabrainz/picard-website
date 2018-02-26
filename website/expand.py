# -*- coding: utf-8 -*-
import re
import html


def encode_entities(string, quote=True):
    return html.escape(string, quote).encode('ascii', 'xmlcharrefreplace').decode('ascii')


def expand(string, args, tag='a', default_attribute='href'):

    def make_link(match):
        var = match.group(1)
        text = match.group(2)
        if text in list(args.keys()):
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
        attribs = ' '.join(["%s=\"%s\"" % (k, encode_entities(d[k])) for k
                            in sorted(d.keys())])
        if attribs:
            attribs = ' ' + attribs
        return '<%s%s>%s</%s>' % (tag, attribs, final_text, tag)

    def simple_expr(match):
        var = match.group(1)
        if var in list(args.keys()):
            return args[var]
        return '{' + var + '}'

    r = '|'.join([re.escape(k) for k in list(args.keys())])

    r1 = re.compile('\{(' + r + ')\|(.*?)\}')
    r2 = re.compile('\{(' + r + ')\}')

    string = r1.sub(make_link, string)
    string = r2.sub(simple_expr, string)

    return string
