# -*- coding: utf-8 -*-
import re
import cgi


def encode_entities(string, quote=True):
    return cgi.escape(string.decode('utf-8'), quote).encode('ascii', 'xmlcharrefreplace')


def expand(string, args, tag='a', default_attribute='href'):

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
        attribs = ' '.join(["%s=\"%s\"" % (k, encode_entities(d[k])) for k
                            in sorted(d.keys())])
        if attribs:
            attribs = ' ' + attribs
        return '<%s%s>%s</%s>' % (tag, attribs, final_text, tag)

    def simple_expr(match):
        var = match.group(1)
        if var in args.keys():
            return args[var]
        return '{' + var + '}'

    r = '|'.join([re.escape(k) for k in args.keys()])

    r1 = re.compile('\{(' + r + ')\|(.*?)\}', re.UNICODE)
    r2 = re.compile('\{(' + r + ')\}', re.UNICODE)

    string = r1.sub(make_link, string)
    string = r2.sub(simple_expr, string)

    return string


if __name__ == "__main__":
    d = {
        'url': 'http://un.site.com/path?id=param',
        'truc': 'page#uné<""mot',
        'url3': {'href': 'http://deux.site.com/path?id=param',
                 'class': 'theclass',
                 'title': 'TheTitle'},
        'is': 'was',
        'xxxx': 'zzzz'
    }

    s = u'{this} {is} an {url|URLTITLE1} xx {truc|xxxx} é {no|match}xxxxxx {url3|URLTITLE2}'
    print 'DICT: ', repr(d)
    print 'FROM: ', s
    print 'TO  : ', vars_expand(s, d)

    d = {
        'span': {'id': 'xxx', 'class': 'zzzz'},
        'is': 'was',
        'test': 'id23',
    }

    s = u'{this} {is} an {span|texte} {test|} {url3|URLTITLE2}'
    print 'DICT: ', repr(d)
    print 'FROM: ', s
    print 'TO  : ', vars_expand(s, d, tag='span', default_attribute='id')
