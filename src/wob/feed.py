from datetime import datetime, timedelta
import re

def dutchify(iso_date):
    m = re.match('(\d{4})-(\d{2})-(\d{2})', iso_date)
    if m is not None:
        return '%s-%s-%s' % (m.group(3), m.group(2), m.group(1),)

def seed(context, data):
    yesterday = datetime.now().date() - timedelta(days=1)
    today = datetime.now().date()
    url = (
        'https://www.rijksoverheid.nl/documenten?trefwoord=&startdatum=%s'
        '&einddatum=%s&onderdeel=Alle+ministeries&type=Wob-verzoek') % (
            dutchify(yesterday.isoformat()), dutchify(today.isoformat()),)
    data = {"url": url}
    context.emit(data=data)
