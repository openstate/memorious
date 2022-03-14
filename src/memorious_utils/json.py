import re
import datetime
from urllib.parse import urljoin

import jsonpath_ng

def crawl(context, data):
    response = context.http.rehash(data)
    url = response.url
    page = response.json

    jsonpath_expr = jsonpath_ng.parse(context.params.get('itempath'))
    for m in jsonpath_expr.find(page):
        # assume handling will be done by default memorious mechanism
        context.emit(m.value)

    jsonpath_expr = jsonpath_ng.parse(context.params.get('pagepath'))
    next_page = jsonpath_expr.find(jsonpath_expr)
    if len(next_page) > 0:
        for l in next_page:
            # assume it is a url and fetched by fetch mechanism
            context.emit("fetch", data={"url": l.value})

    return data
