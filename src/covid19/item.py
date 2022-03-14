def enrich(context, data):
    context.emit(rule='fetch', data={"url": 'https://wobcovid19.rijksoverheid.nl/publicaties/%s/' % (data['link'][1:],)})
