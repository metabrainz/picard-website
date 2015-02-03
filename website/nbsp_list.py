# -*- coding: utf-8 -*-
import re
import jinja2


def nbsp_list(string, separator=','):
    """
    Replace spaces inside of elements of a list separated by `separator` by
    non-breaking spaces.
    Multiple spaces are considered as one.
    Proper html escaping is done, so one needs to use `safe` filter in templates
    to prevent double escaping.
    Example:
        <i>te  st</i>,  some thing
    --> &lt;i&gt;te&nbsp;st&lt;/i&gt;, some&nbsp;thing
    """
    newelems = []
    for elem in re.split(re.escape(separator) + ' *', string):
        newparts = []
        for part in re.split(r' +', elem):
            newparts.append(jinja2.escape(part))
        newelems.append('&nbsp;'.join(newparts))
    sep = separator + ' '
    return sep.join(newelems)
